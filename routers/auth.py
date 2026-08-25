import time

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

import db_helper
from content_utils import home_url_for, page_context, set_flash
from templating import templates

router = APIRouter(prefix="/auth", tags=["auth"])

RESET_TTL_SECONDS = 15 * 60
RESET_MISMATCH_MESSAGE = "ไม่พบบัญชีที่ตรงกับชื่อผู้ใช้และอีเมลนี้"


def _normalize_email(value: str) -> str:
    return (value or "").strip().lower()


def _user_email(user: dict) -> str:
    return _normalize_email((user or {}).get("email") or "")


def _start_password_reset(request: Request, username: str) -> None:
    request.session["password_reset"] = {
        "username": username,
        "expires": int(time.time()) + RESET_TTL_SECONDS,
    }


def _active_reset_username(request: Request) -> str | None:
    data = request.session.get("password_reset") or {}
    username = (data.get("username") or "").strip()
    expires = int(data.get("expires") or 0)
    if not username or time.time() > expires:
        request.session.pop("password_reset", None)
        return None
    return username


def _clear_password_reset(request: Request) -> None:
    request.session.pop("password_reset", None)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = request.session.get("user")
    if user and not user.get("is_guest"):
        return RedirectResponse(url=home_url_for(user), status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context=page_context(request, "login", error_message=None, standalone_auth=True),
    )


@router.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    username_clean = username.strip()
    user_db = db_helper.get_user(username_clean)
    if not user_db:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context=page_context(request, "login", error_message="ไม่พบชื่อผู้ใช้นี้ในระบบ", standalone_auth=True),
        )

    if user_db.get("is_deleted"):
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context=page_context(request, "login", error_message="บัญชีผู้ใช้นี้ถูกลบออกจากระบบชั่วคราว", standalone_auth=True),
        )

    stored_pw = user_db.get("password", "")
    if db_helper.verify_password(password, stored_pw):
        if not db_helper.is_hashed(stored_pw):
            db_helper.update_user_password(username_clean, db_helper.hash_password(password))
        request.session["user"] = {
            "username": user_db["username"],
            "display_name": user_db.get("display_name") or username_clean,
            "role": user_db.get("role", "Student"),
            "is_guest": False,
        }
        request.session["has_avatar"] = bool(user_db.get("avatar"))
        request.session["avatar_rev"] = 1 if user_db.get("avatar") else 0
        request.session.pop("guest_completed", None)
        request.session.pop("guest_quiz_scores", None)
        set_flash(request, f"ยินดีต้อนรับกลับมา, {request.session['user']['display_name']}!", "success")
        return RedirectResponse(url=home_url_for(request.session["user"]), status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context=page_context(request, "login", error_message="รหัสผ่านไม่ถูกต้อง", standalone_auth=True),
    )


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context=page_context(request, "register", error_message=None, standalone_auth=True),
    )


@router.post("/register")
def register_post(
    request: Request,
    username: str = Form(...),
    display_name: str = Form(...),
    password: str = Form(...),
    email: str = Form(""),
):
    username_clean = username.strip()
    display_clean = display_name.strip()
    if len(username_clean) < 3:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context=page_context(request, "register", error_message="ชื่อผู้ใช้ต้องมีอย่างน้อย 3 ตัวอักษร", standalone_auth=True),
        )
    if len(password) < 4:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context=page_context(request, "register", error_message="รหัสผ่านต้องมีอย่างน้อย 4 ตัวอักษร", standalone_auth=True),
        )
    if db_helper.get_user(username_clean):
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context=page_context(request, "register", error_message="ชื่อผู้ใช้นี้มีในระบบแล้ว กรุณาใช้ชื่ออื่น", standalone_auth=True),
        )

    success = db_helper.register_user(username_clean, password, display_clean, email.strip() or None)
    if success:
        request.session["user"] = {
            "username": username_clean,
            "display_name": display_clean,
            "role": "Student",
            "is_guest": False,
        }
        request.session["has_avatar"] = False
        request.session["avatar_rev"] = 0
        set_flash(request, "สมัครสมาชิกสำเร็จ — เริ่มเรียนได้เลย!", "success")
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context=page_context(request, "register", error_message="เกิดข้อผิดพลาดในการลงทะเบียน", standalone_auth=True),
    )


@router.post("/guest")
def guest_login(request: Request):
    request.session["user"] = {
        "username": "guest",
        "display_name": "ผู้เรียนทั่วไป (Guest)",
        "role": "Guest Student",
        "is_guest": True,
    }
    set_flash(request, "กำลังทดลองใช้งานในโหมดแขก — ความก้าวหน้าจะถูกเก็บเฉพาะเซสชันนี้", "info")
    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/logout")
def logout(request: Request):
    user = request.session.get("user") or {}
    if user.get("username") and not user.get("is_guest"):
        try:
            import presence

            presence.drop(user.get("username"))
        except Exception:
            pass
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)


@router.get("/forgot-password", response_class=HTMLResponse)
@router.get("/forgot", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/forgot.html",
        context=page_context(request, "forgot", error_message=None, standalone_auth=True),
    )


@router.post("/forgot-password")
@router.post("/forgot")
def forgot_password_post(request: Request, username: str = Form(...), email: str = Form(...)):
    username_clean = username.strip()
    email_clean = _normalize_email(email)
    user_db = db_helper.get_user(username_clean)
    if (
        not user_db
        or user_db.get("is_deleted")
        or not email_clean
        or _user_email(user_db) != email_clean
    ):
        return templates.TemplateResponse(
            request=request,
            name="auth/forgot.html",
            context=page_context(
                request,
                "forgot",
                error_message=RESET_MISMATCH_MESSAGE,
                standalone_auth=True,
            ),
        )

    _start_password_reset(request, user_db["username"])
    return RedirectResponse(url="/auth/reset-password", status_code=303)


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request):
    username = _active_reset_username(request)
    if not username:
        set_flash(request, "กรุณายืนยันชื่อผู้ใช้และอีเมลก่อนตั้งรหัสใหม่", "warning")
        return RedirectResponse(url="/auth/forgot-password", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="auth/reset.html",
        context=page_context(
            request,
            "reset",
            error_message=None,
            reset_username=username,
            standalone_auth=True,
        ),
    )


@router.post("/reset-password")
def reset_password_post(
    request: Request,
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    username = _active_reset_username(request)
    if not username:
        set_flash(request, "ลิงก์ตั้งรหัสผ่านหมดอายุแล้ว กรุณายืนยันอีกครั้ง", "warning")
        return RedirectResponse(url="/auth/forgot-password", status_code=303)

    if len(password) < 4:
        return templates.TemplateResponse(
            request=request,
            name="auth/reset.html",
            context=page_context(
                request,
                "reset",
                error_message="รหัสผ่านต้องมีอย่างน้อย 4 ตัวอักษร",
                reset_username=username,
                standalone_auth=True,
            ),
        )
    if password != password_confirm:
        return templates.TemplateResponse(
            request=request,
            name="auth/reset.html",
            context=page_context(
                request,
                "reset",
                error_message="รหัสผ่านใหม่ทั้งสองช่องไม่ตรงกัน",
                reset_username=username,
                standalone_auth=True,
            ),
        )

    db_helper.update_user_password(username, db_helper.hash_password(password))
    _clear_password_reset(request)
    set_flash(request, "ตั้งรหัสผ่านใหม่แล้ว — เข้าสู่ระบบด้วยรหัสใหม่ได้เลย", "success")
    return RedirectResponse(url="/auth/login", status_code=303)
