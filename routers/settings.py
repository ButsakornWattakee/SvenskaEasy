import hmac
import json
import os
import time

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

import db_helper
from content_utils import is_admin, page_context, set_flash
from templating import templates

router = APIRouter(prefix="/settings", tags=["settings"])

PIN_MIN_LEN = 6
UNLOCK_SECONDS = 15 * 60
MAX_FAILS = 5
LOCK_SECONDS = 5 * 60
PIN_HASH_KEY = "SETTINGS_PIN_HASH"


def _admin_or_home(request: Request):
    ctx = page_context(request, "settings")
    if not is_admin(ctx["user"]):
        return None, RedirectResponse(url="/dashboard", status_code=303)
    return ctx, None


def _env_code() -> str:
    return (os.getenv("ADMIN_SETTINGS_CODE") or "").strip()


def _stored_hash() -> str:
    path = db_helper.SETTINGS_FILE
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return str((data or {}).get(PIN_HASH_KEY) or "").strip()
    except Exception:
        return ""


def pin_is_configured() -> bool:
    return bool(_stored_hash() or _env_code())


def _verify_pin(plain: str) -> bool:
    code = (plain or "").strip()
    if len(code) < PIN_MIN_LEN:
        return False
    stored = _stored_hash()
    if stored and db_helper.is_hashed(stored) and db_helper.verify_password(code, stored):
        return True
    env_code = _env_code()
    if env_code and hmac.compare_digest(code, env_code):
        return True
    return False


def _is_unlocked(request: Request) -> bool:
    until = float(request.session.get("settings_unlocked_until") or 0)
    return time.time() < until


def _lock_remaining(request: Request) -> int:
    until = float(request.session.get("settings_pin_lock_until") or 0)
    return max(0, int(until - time.time()))


def _register_failure(request: Request) -> int:
    fails = int(request.session.get("settings_pin_fails") or 0) + 1
    request.session["settings_pin_fails"] = fails
    if fails >= MAX_FAILS:
        request.session["settings_pin_lock_until"] = time.time() + LOCK_SECONDS
        request.session["settings_pin_fails"] = 0
    return fails


def _clear_failures(request: Request) -> None:
    request.session["settings_pin_fails"] = 0
    request.session.pop("settings_pin_lock_until", None)


def _unlock(request: Request) -> None:
    _clear_failures(request)
    request.session["settings_unlocked_until"] = time.time() + UNLOCK_SECONDS


def _mask_api_key(key: str) -> str:
    raw = (key or "").strip()
    if not raw:
        return ""
    if len(raw) <= 4:
        return "••••"
    return ("•" * 8) + raw[-4:]


def _current_api_key(request: Request) -> str:
    return (request.session.get("api_key") or db_helper.get_app_setting("GEMINI_API_KEY") or "").strip()


def _verify_gate_password(ctx: dict, plain: str) -> bool:
    code = (plain or "").strip()
    if not code:
        return False
    if _verify_pin(code):
        return True
    username = (ctx.get("user") or {}).get("username") or ""
    user_db = db_helper.get_user(username) or {}
    return db_helper.verify_password(code, user_db.get("password") or "")


def _api_page(request: Request, ctx: dict):
    if not _is_unlocked(request):
        ctx["settings_lock_seconds"] = _lock_remaining(request)
        return templates.TemplateResponse(request=request, name="settings.html", context=ctx)
    api_key = _current_api_key(request)
    ctx.update(
        {
            "api_key_masked": _mask_api_key(api_key),
            "is_api_connected": bool(api_key),
        }
    )
    return templates.TemplateResponse(request=request, name="settings_api.html", context=ctx)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
@router.get("/api", response_class=HTMLResponse)
@router.get("/api/", response_class=HTMLResponse)
def settings_page(request: Request):
    ctx, denied = _admin_or_home(request)
    if denied:
        return denied
    return _api_page(request, ctx)


@router.post("/unlock")
def settings_unlock(
    request: Request,
    password: str = Form(""),
    pin: str = Form(""),
):
    ctx, denied = _admin_or_home(request)
    if denied:
        return denied
    wait = _lock_remaining(request)
    if wait:
        set_flash(request, f"กรอกรหัสผิดหลายครั้ง กรุณารอ {wait} วินาที", "danger")
        return RedirectResponse(url="/settings", status_code=303)
    if _verify_gate_password(ctx, password or pin):
        _unlock(request)
        set_flash(request, "รหัสผ่านถูกต้อง — เข้าสู่หน้าตั้งค่า API ได้ 15 นาที", "success")
    else:
        fails = _register_failure(request)
        left = MAX_FAILS - fails if fails < MAX_FAILS else 0
        if left:
            set_flash(request, f"รหัสผ่านไม่ถูกต้อง เหลืออีก {left} ครั้ง", "danger")
        else:
            set_flash(request, "กรอกรหัสผิดครบครั้งแล้ว กรุณารอ 5 นาที", "danger")
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/lock")
def settings_lock(request: Request):
    ctx, denied = _admin_or_home(request)
    if denied:
        return denied
    request.session.pop("settings_unlocked_until", None)
    set_flash(request, "ล็อกหน้าตั้งค่า API แล้ว", "info")
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/pin")
def settings_set_pin(
    request: Request,
    new_pin: str = Form(""),
    confirm_pin: str = Form(""),
    admin_password: str = Form(""),
):
    ctx, denied = _admin_or_home(request)
    if denied:
        return denied
    username = (ctx["user"] or {}).get("username") or ""
    user_db = db_helper.get_user(username) or {}
    if not db_helper.verify_password(admin_password, user_db.get("password") or ""):
        set_flash(request, "รหัสผ่านบัญชีผู้ดูแลไม่ถูกต้อง", "danger")
        return RedirectResponse(url="/settings", status_code=303)
    if pin_is_configured() and not _is_unlocked(request):
        set_flash(request, "ต้องใส่รหัสผ่านหน้านี้ก่อนจึงจะเปลี่ยนรหัสได้", "danger")
        return RedirectResponse(url="/settings", status_code=303)
    pin = (new_pin or "").strip()
    if len(pin) < PIN_MIN_LEN:
        set_flash(request, f"รหัสผ่านต้องมีอย่างน้อย {PIN_MIN_LEN} ตัวอักษร", "danger")
        return RedirectResponse(url="/settings", status_code=303)
    if pin != (confirm_pin or "").strip():
        set_flash(request, "รหัสยืนยันไม่ตรงกัน", "danger")
        return RedirectResponse(url="/settings", status_code=303)
    db_helper.save_app_setting(PIN_HASH_KEY, db_helper.hash_password(pin))
    _unlock(request)
    set_flash(request, "บันทึกรหัสผ่านหน้าตั้งค่า API แล้ว", "success")
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/save")
def settings_save(
    request: Request,
    api_key: str = Form(""),
    clear_api_key: str = Form(""),
):
    ctx, denied = _admin_or_home(request)
    if denied:
        return denied
    if not _is_unlocked(request):
        set_flash(request, "กรุณาใส่รหัสผ่านก่อนจึงจะบันทึก API Key ได้", "danger")
        return RedirectResponse(url="/settings", status_code=303)
    current = _current_api_key(request)
    api_key_clean = (api_key or "").strip()
    if clear_api_key:
        request.session["api_key"] = ""
        db_helper.save_app_setting("GEMINI_API_KEY", "")
        set_flash(request, "ล้างค่า API Key แล้ว — ครู AI จะทำงานในโหมดจำลอง", "info")
    elif api_key_clean:
        request.session["api_key"] = api_key_clean
        db_helper.save_app_setting("GEMINI_API_KEY", api_key_clean)
        set_flash(request, "บันทึก API Key เรียบร้อยแล้ว", "success")
    else:
        request.session["api_key"] = current
        set_flash(request, "ไม่ได้เปลี่ยน API Key", "info")
    return RedirectResponse(url="/settings", status_code=303)
