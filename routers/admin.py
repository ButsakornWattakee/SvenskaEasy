from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import db_helper
import vocabulary_data

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def admin_page(request: Request):
    user = request.session.get("user")
    if not user or user.get("role") != "Admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    current_level = request.session.get("current_level", "Beginner")
    users_list = db_helper.get_all_users()

    return templates.TemplateResponse(request=request, name="admin.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "admin",
        "users_list": users_list,
        "vocab_items": vocabulary_data.FULL_VOCABULARY_LIST
    })

@router.post("/delete-user")
def delete_user(request: Request, username: str = Form(...)):
    user = request.session.get("user")
    if not user or user.get("role") != "Admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    db_helper.delete_user(username)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/restore-user")
def restore_user(request: Request, username: str = Form(...)):
    user = request.session.get("user")
    if not user or user.get("role") != "Admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    db_helper.restore_user(username)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/upload-image")
async def upload_vocab_image(request: Request, word: str = Form(...), image_file: UploadFile = File(...)):
    user = request.session.get("user")
    if not user or user.get("role") != "Admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    if image_file:
        os.makedirs("static/assets/custom_vocab", exist_ok=True)
        filename = f"{word.lower().replace(' ', '_')}_{image_file.filename}"
        filepath = os.path.join("static/assets/custom_vocab", filename)

        contents = await image_file.read()
        with open(filepath, "wb") as f:
            f.write(contents)

        db_helper.save_custom_vocab_image(word, f"/static/assets/custom_vocab/{filename}")

    return RedirectResponse(url="/admin", status_code=303)
