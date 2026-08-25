from urllib.parse import quote

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

import achievements
import db_helper
import lessons_data
import vocabulary_data
from content_utils import (
    is_admin,
    matching_game_words,
    page_context,
    persist_word_image_file,
    remove_word_image_file,
    set_flash,
    word_image_url,
)
from image_utils import crop_avatar
from templating import templates

router = APIRouter(prefix="/admin", tags=["admin"])


def _admin_ctx(request: Request, current_page: str):
    ctx = page_context(request, current_page)
    if not is_admin(ctx["user"]):
        dest = "/auth/login" if ctx["user"].get("is_guest") else "/dashboard"
        return None, RedirectResponse(url=dest, status_code=303)
    return ctx, None


@router.get("", response_class=HTMLResponse)
def admin_home(request: Request):
    ctx, denied = _admin_ctx(request, "admin")
    if denied:
        return denied

    users_list = achievements.attach_user_badges(db_helper.get_all_users(), len(lessons_data.LESSONS))
    deleted_users = db_helper.get_deleted_users()
    admins = [u for u in users_list if str(u.get("role") or "").lower() == "admin"]
    students = [u for u in users_list if str(u.get("role") or "").lower() != "admin"]
    total_completed = sum(len(u.get("completed_lessons") or []) for u in users_list)
    api_key = request.session.get("api_key") or db_helper.get_app_setting("GEMINI_API_KEY")
    import presence

    online_users = presence.online_snapshot()
    ctx.update(
        {
            "users_list": users_list,
            "admins": admins,
            "students": students,
            "deleted_count": len(deleted_users),
            "total_completed": total_completed,
            "db_online": db_helper.is_mongodb_online(),
            "is_api_connected": bool(api_key),
            "online_users": online_users,
            "online_count": len(online_users),
        }
    )
    return templates.TemplateResponse(request=request, name="admin/home.html", context=ctx)


@router.get("/users", response_class=HTMLResponse)
def admin_users(request: Request):
    ctx, denied = _admin_ctx(request, "admin_users")
    if denied:
        return denied
    import presence

    users_list = achievements.attach_user_badges(db_helper.get_all_users(), len(lessons_data.LESSONS))
    for row in users_list:
        name = row.get("username") or ""
        row["is_online"] = presence.is_online(name)
        row["presence_label"] = presence.last_seen_label(name, row.get("last_active"))
    ctx["users_list"] = users_list
    ctx["deleted_users"] = db_helper.get_deleted_users()
    ctx["online_users"] = presence.online_snapshot()
    return templates.TemplateResponse(request=request, name="admin/users.html", context=ctx)


@router.get("/presence")
def admin_presence(request: Request):
    ctx, denied = _admin_ctx(request, "admin")
    if denied:
        return JSONResponse({"ok": False, "online": []}, status_code=403)
    import presence

    rows = presence.online_snapshot()
    return JSONResponse({"ok": True, "count": len(rows), "online": rows})


@router.get("/trash", response_class=HTMLResponse)
def admin_trash_redirect(request: Request):
    return RedirectResponse(url="/admin/users#trash", status_code=303)


@router.get("/users/new", response_class=HTMLResponse)
def admin_new_user(request: Request):
    ctx, denied = _admin_ctx(request, "admin_new")
    if denied:
        return denied
    return templates.TemplateResponse(request=request, name="admin/new_user.html", context=ctx)


@router.post("/users/new")
def admin_create_user(
    request: Request,
    username: str = Form(...),
    display_name: str = Form(""),
    email: str = Form(""),
    password: str = Form(...),
    role: str = Form("Student"),
):
    ctx, denied = _admin_ctx(request, "admin_new")
    if denied:
        return denied

    username_clean = username.strip()
    display_clean = (display_name or username_clean).strip()
    email_clean = (email or f"{username_clean}@svenskaeasy.local").strip()
    role_clean = "Admin" if role == "Admin" else "Student"

    if len(username_clean) < 3:
        set_flash(request, "ชื่อผู้ใช้ต้องมีอย่างน้อย 3 ตัวอักษร", "danger")
        return RedirectResponse(url="/admin/users/new", status_code=303)
    if len(password) < 4:
        set_flash(request, "รหัสผ่านต้องมีอย่างน้อย 4 ตัวอักษร", "danger")
        return RedirectResponse(url="/admin/users/new", status_code=303)

    success, msg = db_helper.create_user(
        username_clean, email_clean, password, role=role_clean, display_name=display_clean
    )
    if success:
        set_flash(request, f"สร้างบัญชี {username_clean} ({role_clean}) แล้ว", "success")
        return RedirectResponse(url="/admin/users", status_code=303)
    set_flash(request, msg or "สร้างบัญชีไม่สำเร็จ", "danger")
    return RedirectResponse(url="/admin/users/new", status_code=303)


@router.get("/game-images", response_class=HTMLResponse)
def admin_game_images(request: Request, word: str = ""):
    ctx, denied = _admin_ctx(request, "admin_game_images")
    if denied:
        return denied
    words = matching_game_words()
    selected = (word or "").strip() or (words[0]["swedish"] if words else "")
    current = next((item for item in words if item["swedish"] == selected), words[0] if words else None)
    mongo_img = db_helper.get_game_image(selected) if selected else None
    ctx.update(
        {
            "words": words,
            "selected_word": selected,
            "current": current,
            "has_custom": bool(mongo_img),
            "current_image_url": (
                f"/admin/media/game?word={quote(selected)}"
                if mongo_img
                else (word_image_url(selected, current.get("image_path") if current else None) if selected else "")
            ),
        }
    )
    return templates.TemplateResponse(request=request, name="admin/game_images.html", context=ctx)


def _vocab_admin_words():
    return vocabulary_data.all_vocabulary()


def _normalize_vocab_level(level: str) -> str:
    raw = (level or "").strip()
    mapping = {
        "Beginner": "ง่าย",
        "Elementary": "กลาง",
        "Intermediate": "ยาก",
        "ง่าย": "ง่าย",
        "กลาง": "กลาง",
        "ยาก": "ยาก",
    }
    return mapping.get(raw, "ง่าย")


@router.get("/vocab-images", response_class=HTMLResponse)
@router.get("/images", response_class=HTMLResponse)
def admin_vocab_images(request: Request, word: str = ""):
    ctx, denied = _admin_ctx(request, "admin_vocab_images")
    if denied:
        return denied
    words = _vocab_admin_words()
    selected = (word or "").strip() or (words[0]["swedish"] if words else "")
    current = next((item for item in words if item["swedish"] == selected), None)
    if current is None:
        current = next((item for item in words if item["swedish"].lower() == selected.lower()), words[0] if words else None)
        if current:
            selected = current["swedish"]
    mongo_img = db_helper.get_vocab_image(selected) if selected else None
    ctx.update(
        {
            "words": words,
            "selected_word": selected,
            "current": current,
            "is_custom_word": bool(current and current.get("is_custom")),
            "has_custom": bool(mongo_img),
            "current_image_url": (
                f"/admin/media/vocab?word={quote(selected)}"
                if mongo_img
                else (word_image_url(selected) if selected else "")
            ),
            "pos_options": vocabulary_data.VOCAB_POS_OPTIONS,
            "vocab_categories": vocabulary_data.vocab_categories(),
            "cefr_level_choices": [
                {"key": "ง่าย", "label": "ง่าย — Beginner"},
                {"key": "กลาง", "label": "กลาง — Elementary"},
                {"key": "ยาก", "label": "ยาก — Intermediate"},
            ],
        }
    )
    return templates.TemplateResponse(request=request, name="admin/vocab_images.html", context=ctx)


@router.get("/media/game")
def admin_media_game(request: Request, word: str = ""):
    ctx, denied = _admin_ctx(request, "admin_game_images")
    if denied:
        return denied
    data = db_helper.get_game_image(word) if word else None
    if not data:
        return Response(status_code=404)
    return Response(content=data, media_type="image/png")


@router.get("/media/vocab")
def admin_media_vocab(request: Request, word: str = ""):
    ctx, denied = _admin_ctx(request, "admin_vocab_images")
    if denied:
        return denied
    data = db_helper.get_vocab_image(word) if word else None
    if not data:
        return Response(status_code=404)
    return Response(content=data, media_type="image/png")


@router.post("/delete-user")
def delete_user(request: Request, username: str = Form(...)):
    ctx, denied = _admin_ctx(request, "admin_users")
    if denied:
        return denied
    if username == ctx["user"].get("username"):
        set_flash(request, "ไม่สามารถลบบัญชีที่กำลังใช้งานอยู่ได้", "danger")
        return RedirectResponse(url="/admin/users", status_code=303)
    db_helper.delete_user(username)
    set_flash(request, f"ย้ายผู้ใช้ {username} ไปถังขยะแล้ว", "success")
    return RedirectResponse(url="/admin/users", status_code=303)


@router.post("/restore-user")
def restore_user(request: Request, username: str = Form(...)):
    ctx, denied = _admin_ctx(request, "admin_users")
    if denied:
        return denied
    db_helper.restore_user(username)
    set_flash(request, f"กู้คืนผู้ใช้ {username} แล้ว", "success")
    return RedirectResponse(url="/admin/users", status_code=303)


@router.post("/delete-user-permanent")
def delete_user_permanent(request: Request, username: str = Form(...)):
    ctx, denied = _admin_ctx(request, "admin_users")
    if denied:
        return denied
    db_helper.delete_user_permanently(username)
    set_flash(request, f"ลบผู้ใช้ {username} ถาวรแล้ว", "success")
    return RedirectResponse(url="/admin/users", status_code=303)


@router.post("/game-images")
async def save_game_image(
    request: Request,
    word: str = Form(...),
    zoom: float = Form(1.0),
    offset_x: float = Form(0.0),
    offset_y: float = Form(0.0),
    image_file: UploadFile = File(...),
):
    ctx, denied = _admin_ctx(request, "admin_game_images")
    if denied:
        return denied
    contents = await image_file.read()
    if not contents:
        set_flash(request, "กรุณาเลือกไฟล์รูปภาพ", "danger")
        return RedirectResponse(url=f"/admin/game-images?word={quote(word)}", status_code=303)
    try:
        cropped = crop_avatar(contents, zoom, offset_x, offset_y)
    except Exception:
        set_flash(request, "อ่านไฟล์รูปไม่สำเร็จ", "danger")
        return RedirectResponse(url=f"/admin/game-images?word={quote(word)}", status_code=303)
    db_helper.save_game_image(word, cropped)
    persist_word_image_file(word, cropped)
    set_flash(request, f"บันทึกรูปเกมจับคู่สำหรับ {word} แล้ว", "success")
    return RedirectResponse(url=f"/admin/game-images?word={quote(word)}", status_code=303)


@router.post("/game-images/delete")
def delete_game_image(request: Request, word: str = Form(...)):
    ctx, denied = _admin_ctx(request, "admin_game_images")
    if denied:
        return denied
    db_helper.delete_game_image(word)
    remove_word_image_file(word)
    set_flash(request, f"ลบรูปเกมของ {word} แล้ว", "success")
    return RedirectResponse(url=f"/admin/game-images?word={quote(word)}", status_code=303)


@router.post("/vocab-images")
@router.post("/upload-image")
async def save_vocab_image(
    request: Request,
    word: str = Form(...),
    zoom: float = Form(1.0),
    offset_x: float = Form(0.0),
    offset_y: float = Form(0.0),
    image_file: UploadFile = File(...),
):
    ctx, denied = _admin_ctx(request, "admin_vocab_images")
    if denied:
        return denied
    contents = await image_file.read()
    if not contents:
        set_flash(request, "กรุณาเลือกไฟล์รูปภาพ", "danger")
        return RedirectResponse(url=f"/admin/vocab-images?word={quote(word)}", status_code=303)
    try:
        cropped = crop_avatar(contents, zoom, offset_x, offset_y)
    except Exception:
        set_flash(request, "อ่านไฟล์รูปไม่สำเร็จ", "danger")
        return RedirectResponse(url=f"/admin/vocab-images?word={quote(word)}", status_code=303)
    db_helper.save_vocab_image(word, cropped)
    persist_word_image_file(word, cropped)
    set_flash(request, f"บันทึกรูปคลังคำศัพท์สำหรับ {word} แล้ว", "success")
    return RedirectResponse(url=f"/admin/vocab-images?word={quote(word)}", status_code=303)


@router.post("/vocab-images/delete")
def delete_vocab_image(request: Request, word: str = Form(...)):
    ctx, denied = _admin_ctx(request, "admin_vocab_images")
    if denied:
        return denied
    db_helper.delete_vocab_image(word)
    remove_word_image_file(word)
    set_flash(request, f"ลบรูปคลังคำศัพท์ของ {word} แล้ว", "success")
    return RedirectResponse(url=f"/admin/vocab-images?word={quote(word)}", status_code=303)


@router.post("/vocab-images/words")
async def add_vocab_word(
    request: Request,
    swedish: str = Form(...),
    thai: str = Form(...),
    pronunciation: str = Form(""),
    pos: str = Form("คำนาม (substantiv)"),
    level: str = Form("ง่าย"),
    category: str = Form(""),
    example_swedish: str = Form(""),
    example_thai: str = Form(""),
    zoom: float = Form(1.0),
    offset_x: float = Form(0.0),
    offset_y: float = Form(0.0),
    image_file: UploadFile | None = File(None),
):
    ctx, denied = _admin_ctx(request, "admin_vocab_images")
    if denied:
        return denied

    swedish_clean = (swedish or "").strip()
    thai_clean = (thai or "").strip()
    if len(swedish_clean) < 1 or len(swedish_clean) > 80:
        set_flash(request, "คำสวีเดนต้องยาว 1–80 ตัวอักษร", "danger")
        return RedirectResponse(url="/admin/vocab-images", status_code=303)
    if len(thai_clean) < 1:
        set_flash(request, "กรอกคำแปลภาษาไทย", "danger")
        return RedirectResponse(url="/admin/vocab-images", status_code=303)

    if vocabulary_data.is_builtin_vocab_word(swedish_clean):
        set_flash(request, f"คำ “{swedish_clean}” มีในคลังอยู่แล้ว — เลือกจากรายการด้านล่างเพื่อจัดการรูป", "warning")
        return RedirectResponse(url=f"/admin/vocab-images?word={quote(swedish_clean)}", status_code=303)

    existing_custom = next(
        (
            item
            for item in db_helper.list_custom_vocab_words()
            if (item.get("swedish") or "").strip().lower() == swedish_clean.lower()
        ),
        None,
    )
    if existing_custom:
        set_flash(request, f"คำ “{swedish_clean}” ถูกเพิ่มไว้แล้ว — สามารถอัปโหลดรูปด้านล่างได้", "warning")
        return RedirectResponse(url=f"/admin/vocab-images?word={quote(existing_custom.get('swedish') or swedish_clean)}", status_code=303)

    saved, msg = db_helper.save_custom_vocab_word(
        {
            "swedish": swedish_clean,
            "thai": thai_clean,
            "pronunciation": (pronunciation or "").strip() or swedish_clean,
            "pos": (pos or "").strip() or "คำนาม (substantiv)",
            "level": _normalize_vocab_level(level),
            "category": (category or "").strip() or "เพิ่มโดยผู้ดูแลระบบ",
            "example_swedish": (example_swedish or "").strip(),
            "example_thai": (example_thai or "").strip() or thai_clean,
        }
    )
    if not saved:
        set_flash(request, msg or "เพิ่มคำศัพท์ไม่สำเร็จ", "danger")
        return RedirectResponse(url="/admin/vocab-images", status_code=303)

    if image_file and image_file.filename:
        contents = await image_file.read()
        if contents:
            try:
                cropped = crop_avatar(contents, zoom, offset_x, offset_y)
                db_helper.save_vocab_image(swedish_clean, cropped)
                persist_word_image_file(swedish_clean, cropped)
            except Exception:
                set_flash(request, f"เพิ่มคำ “{swedish_clean}” แล้ว แต่บันทึกรูปไม่สำเร็จ", "warning")
                return RedirectResponse(url=f"/admin/vocab-images?word={quote(swedish_clean)}", status_code=303)

    set_flash(request, f"เพิ่มคำศัพท์ “{swedish_clean}” แล้ว — แสดงในคลังคำศัพท์ทันที", "success")
    return RedirectResponse(url=f"/admin/vocab-images?word={quote(swedish_clean)}", status_code=303)


@router.post("/vocab-images/words/delete")
def delete_vocab_word(request: Request, word: str = Form(...)):
    ctx, denied = _admin_ctx(request, "admin_vocab_images")
    if denied:
        return denied
    swedish_clean = (word or "").strip()
    if vocabulary_data.is_builtin_vocab_word(swedish_clean):
        set_flash(request, "ไม่สามารถลบคำศัพท์ตั้งต้นของหลักสูตรได้", "danger")
        return RedirectResponse(url=f"/admin/vocab-images?word={quote(swedish_clean)}", status_code=303)
    if not db_helper.delete_custom_vocab_word(swedish_clean):
        set_flash(request, "ไม่พบคำศัพท์ที่เพิ่มเองนี้", "danger")
        return RedirectResponse(url="/admin/vocab-images", status_code=303)
    db_helper.delete_vocab_image(swedish_clean)
    remove_word_image_file(swedish_clean)
    set_flash(request, f"ลบคำศัพท์ “{swedish_clean}” ออกจากคลังแล้ว", "success")
    return RedirectResponse(url="/admin/vocab-images", status_code=303)
