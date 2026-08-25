import base64
import re
from datetime import date, datetime

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response

import achievements
import db_helper
import lessons_data
from content_utils import page_context, quiz_scores_for, set_flash
from image_utils import crop_avatar
from templating import templates

router = APIRouter(prefix="/profile", tags=["profile"])

MONTHLY_CHANGE_LIMIT = 2

GENDER_LABELS = {
    "male": "ชาย",
    "female": "หญิง",
    "other": "ไม่ระบุ",
}
_THAI_MONTHS = (
    "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค.",
)


def _normalize_gender(value: str) -> str:
    raw = (value or "").strip().lower()
    mapping = {
        "male": "male",
        "m": "male",
        "ชาย": "male",
        "female": "female",
        "f": "female",
        "หญิง": "female",
        "other": "other",
        "ไม่ระบุ": "other",
        "อื่นๆ": "other",
    }
    return mapping.get(raw, "")


def _normalize_birthday(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    try:
        parsed = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return ""
    today = date.today()
    if parsed.year < 1900 or parsed > today:
        return ""
    return parsed.isoformat()


def _format_birthday(value: str) -> str:
    iso = _normalize_birthday(value)
    if not iso:
        return ""
    parsed = datetime.strptime(iso, "%Y-%m-%d").date()
    return f"{parsed.day} {_THAI_MONTHS[parsed.month - 1]} {parsed.year}"


def _normalize_phone(value: str) -> str:
    raw = re.sub(r"[\s\-()]", "", (value or "").strip())
    if not raw:
        return ""
    if not re.fullmatch(r"\+?\d{8,15}", raw):
        return "__invalid__"
    return raw


def _change_log(user) -> dict:
    raw = (user or {}).get("profile_change_log") or {}
    if not isinstance(raw, dict):
        raw = {}
    def _as_list(value):
        if isinstance(value, list):
            return [str(item) for item in value if item]
        return []
    return {
        "display_name": _as_list(raw.get("display_name")),
        "phone": _as_list(raw.get("phone")),
    }


def _count_this_month(entries, today: date) -> int:
    prefix = today.strftime("%Y-%m")
    count = 0
    for item in entries or []:
        text = str(item)
        parsed = None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "")).date()
        except ValueError:
            parsed = None
        if parsed and parsed.strftime("%Y-%m") == prefix:
            count += 1
        elif text.startswith(prefix):
            count += 1
    return count


def profile_edit_state(user, today: date | None = None) -> dict:
    today = today or date.today()
    log = _change_log(user)
    gender = _normalize_gender((user or {}).get("gender") or "")
    birthday = _normalize_birthday((user or {}).get("birthday") or "")
    phone = (user or {}).get("phone") or ""
    if phone == "__invalid__":
        phone = ""
    name_used = _count_this_month(log["display_name"], today)
    phone_used = _count_this_month(log["phone"], today)
    phone_remaining = max(0, MONTHLY_CHANGE_LIMIT - phone_used)
    return {
        "gender": gender,
        "birthday": birthday,
        "phone": phone,
        "gender_locked": bool(gender),
        "birthday_locked": bool(birthday),
        "display_name_used": name_used,
        "display_name_remaining": max(0, MONTHLY_CHANGE_LIMIT - name_used),
        "phone_used": phone_used,
        "phone_remaining": phone_remaining,
        "phone_can_edit": (not phone) or phone_remaining > 0,
        "display_name_can_edit": max(0, MONTHLY_CHANGE_LIMIT - name_used) > 0,
        "change_log": log,
    }


def resolve_profile_update(db_user, incoming: dict, now: datetime | None = None) -> dict:
    now = now or datetime.now()
    state = profile_edit_state(db_user, now.date())
    stored_name = ((db_user or {}).get("display_name") or "").strip()
    stored_phone = state["phone"]
    stored_gender = state["gender"]
    stored_birthday = state["birthday"]

    new_name = (incoming.get("display_name") or "").strip() or stored_name
    new_gender = _normalize_gender(incoming.get("gender") or "")
    new_birthday = _normalize_birthday(incoming.get("birthday") or "")
    new_phone = _normalize_phone(incoming.get("phone") or "")

    errors = []
    fields = {
        "display_name": stored_name,
        "gender": stored_gender,
        "birthday": stored_birthday,
        "phone": stored_phone,
    }
    log = {
        "display_name": list(state["change_log"]["display_name"]),
        "phone": list(state["change_log"]["phone"]),
    }
    stamp = now.replace(microsecond=0).isoformat()
    changed = False

    if state["gender_locked"]:
        if new_gender and new_gender != stored_gender:
            errors.append("เพศถูกบันทึกถาวรแล้ว ไม่สามารถแก้ไขได้")
    elif new_gender:
        fields["gender"] = new_gender
        changed = changed or new_gender != stored_gender

    if state["birthday_locked"]:
        if incoming.get("birthday") and new_birthday and new_birthday != stored_birthday:
            errors.append("วันเกิดถูกบันทึกถาวรแล้ว ไม่สามารถแก้ไขได้")
        elif incoming.get("birthday") and not new_birthday:
            errors.append("วันเกิดไม่ถูกต้อง")
    else:
        if incoming.get("birthday") and not new_birthday:
            errors.append("วันเกิดไม่ถูกต้อง")
        elif new_birthday:
            fields["birthday"] = new_birthday
            changed = changed or new_birthday != stored_birthday

    if new_name != stored_name:
        if len(new_name) < 2:
            errors.append("ชื่อที่แสดงต้องมีอย่างน้อย 2 ตัวอักษร")
        elif not state["display_name_can_edit"]:
            errors.append("ชื่อที่แสดงเปลี่ยนได้เพียง 2 ครั้งต่อเดือน")
        else:
            fields["display_name"] = new_name
            log["display_name"].append(stamp)
            changed = True

    if new_phone == "__invalid__":
        errors.append("เบอร์โทรไม่ถูกต้อง — ใช้ตัวเลข 8–15 หลัก")
    elif not stored_phone and new_phone:
        fields["phone"] = new_phone
        changed = True
    elif new_phone != stored_phone:
        if not new_phone:
            fields["phone"] = stored_phone
        elif not state["phone_can_edit"]:
            errors.append("เบอร์โทรเปลี่ยนได้เพียง 2 ครั้งต่อเดือน")
        else:
            fields["phone"] = new_phone
            log["phone"].append(stamp)
            changed = True

    fields["profile_change_log"] = log
    return {
        "ok": not errors,
        "errors": errors,
        "fields": fields,
        "changed": changed,
        "state": state,
    }


def _avatar_bytes(username: str):
    user = db_helper.get_user(username)
    if not user:
        return None
    data = user.get("avatar")
    if not data:
        return None
    if isinstance(data, str):
        try:
            return base64.b64decode(data)
        except Exception:
            return None
    return bytes(data)


@router.get("", response_class=HTMLResponse)
def profile_page(request: Request):
    ctx = page_context(request, "profile")
    username = ctx["user"].get("username", "guest")
    quiz_scores = quiz_scores_for(request, username)

    user_achievements = achievements.evaluate_achievements(
        completed_lessons=ctx["completed_lessons"],
        quiz_scores=quiz_scores,
        total_lessons=len(lessons_data.LESSONS),
    )

    quiz_history = []
    for l_id, data in quiz_scores.items():
        lesson = next((l for l in lessons_data.LESSONS if l["id"] == l_id), None)
        if l_id == 999:
            title = "ข้อสอบวัดผลรวม (Final Exam)"
        else:
            title = lesson["title"] if lesson else f"บทเรียนที่ {l_id}"
        quiz_history.append(
            {
                "lesson_id": l_id,
                "title": title,
                "earned": data.get("earned", 0),
                "total": data.get("total", 0),
                "score_pct": data.get("score_pct", 0),
            }
        )
    quiz_history.sort(key=lambda item: str(item["lesson_id"]))

    db_user = None if ctx["user"].get("is_guest") else db_helper.get_user(username)
    edit_state = profile_edit_state(db_user or {})
    gender = edit_state["gender"]
    birthday = edit_state["birthday"]
    phone = edit_state["phone"]
    can_submit = (
        (not edit_state["gender_locked"])
        or (not edit_state["birthday_locked"])
        or edit_state["display_name_can_edit"]
        or edit_state["phone_can_edit"]
    )
    ctx.update(
        {
            "achievements": user_achievements,
            "quiz_history": quiz_history,
            "phone": phone,
            "email": (db_user or {}).get("email") or "",
            "gender": gender,
            "gender_label": GENDER_LABELS.get(gender, ""),
            "birthday": birthday,
            "birthday_label": _format_birthday(birthday),
            "display_name_value": (db_user or {}).get("display_name") or ctx["user"].get("display_name") or "",
            "today_iso": date.today().isoformat(),
            "gender_locked": edit_state["gender_locked"],
            "birthday_locked": edit_state["birthday_locked"],
            "display_name_can_edit": edit_state["display_name_can_edit"],
            "display_name_remaining": edit_state["display_name_remaining"],
            "phone_can_edit": edit_state["phone_can_edit"],
            "phone_remaining": edit_state["phone_remaining"],
            "monthly_change_limit": MONTHLY_CHANGE_LIMIT,
            "can_submit_profile": can_submit,
        }
    )
    return templates.TemplateResponse(request=request, name="profile.html", context=ctx)


@router.post("/details")
def save_profile_details(
    request: Request,
    display_name: str = Form(""),
    gender: str = Form(""),
    birthday: str = Form(""),
    phone: str = Form(""),
):
    ctx_user = request.session.get("user") or {}
    if ctx_user.get("is_guest") or not ctx_user.get("username"):
        set_flash(request, "กรุณาเข้าสู่ระบบก่อนบันทึกข้อมูลส่วนตัว", "warning")
        return RedirectResponse(url="/auth/login", status_code=303)

    db_user = db_helper.get_user(ctx_user["username"]) or {}
    result = resolve_profile_update(
        db_user,
        {
            "display_name": display_name,
            "gender": gender,
            "birthday": birthday,
            "phone": phone,
        },
    )
    if not result["ok"]:
        set_flash(request, " · ".join(result["errors"]), "danger")
        return RedirectResponse(url="/profile", status_code=303)
    if not result["changed"]:
        set_flash(request, "ข้อมูลเหมือนเดิม ไม่มีการเปลี่ยนแปลง", "info")
        return RedirectResponse(url="/profile", status_code=303)

    saved = db_helper.save_user_profile_fields(ctx_user["username"], result["fields"])
    if not saved:
        set_flash(request, "บันทึกข้อมูลส่วนตัวไม่สำเร็จ", "danger")
        return RedirectResponse(url="/profile", status_code=303)

    ctx_user["display_name"] = result["fields"]["display_name"]
    request.session["user"] = ctx_user
    set_flash(request, "บันทึกข้อมูลส่วนตัวแล้ว", "success")
    return RedirectResponse(url="/profile", status_code=303)


_EMPTY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


@router.get("/avatar")
@router.get("/photo")
def profile_avatar(request: Request):
    user = request.session.get("user") or {}
    if user.get("is_guest") or not user.get("username"):
        return Response(content=_EMPTY_PNG, media_type="image/png")
    data = _avatar_bytes(user["username"])
    if not data:
        return Response(content=_EMPTY_PNG, media_type="image/png")
    return Response(content=data, media_type="image/png", headers={"Cache-Control": "no-store"})


@router.post("")
@router.post("/")
@router.post("/avatar")
@router.post("/photo")
async def upload_avatar(
    request: Request,
    avatar_file: UploadFile = File(...),
    zoom: float = Form(1.0),
    offset_x: float = Form(0.0),
    offset_y: float = Form(0.0),
):
    ctx_user = (request.session.get("user") or {})
    if ctx_user.get("is_guest") or not ctx_user.get("username"):
        set_flash(request, "กรุณาเข้าสู่ระบบก่อนอัปโหลดรูปโปรไฟล์", "warning")
        return RedirectResponse(url="/auth/login", status_code=303)

    contents = await avatar_file.read()
    if not contents:
        set_flash(request, "ไม่พบไฟล์รูปภาพ", "danger")
        return RedirectResponse(url="/profile", status_code=303)
    if len(contents) > 8 * 1024 * 1024:
        set_flash(request, "ไฟล์ใหญ่เกินไป (สูงสุด 8MB)", "danger")
        return RedirectResponse(url="/profile", status_code=303)

    try:
        cropped = crop_avatar(contents, zoom, offset_x, offset_y)
    except Exception:
        set_flash(request, "ไม่สามารถอ่านรูปนี้ได้ กรุณาใช้ไฟล์ PNG หรือ JPG", "danger")
        return RedirectResponse(url="/profile", status_code=303)

    if not db_helper.save_user_avatar(ctx_user["username"], cropped):
        set_flash(request, "บันทึกรูปโปรไฟล์ไม่สำเร็จ", "danger")
        return RedirectResponse(url="/profile", status_code=303)

    request.session["has_avatar"] = True
    request.session["avatar_rev"] = int(request.session.get("avatar_rev") or 0) + 1
    set_flash(request, "บันทึกรูปโปรไฟล์แล้ว", "success")
    return RedirectResponse(url="/profile", status_code=303)
