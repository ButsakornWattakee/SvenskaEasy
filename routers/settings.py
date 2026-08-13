from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import db_helper

router = APIRouter(prefix="/settings", tags=["settings"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def settings_page(request: Request):
    user = request.session.get("user")
    if not user:
        user = {"username": "guest", "display_name": "ผู้เรียนทั่วไป (Guest)", "role": "Guest Student", "is_guest": True}
        request.session["user"] = user

    current_level = request.session.get("current_level", "Beginner")
    api_key = request.session.get("api_key") or db_helper.get_app_setting("GEMINI_API_KEY")

    return templates.TemplateResponse(request=request, name="settings.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "settings",
        "api_key": api_key
    })

@router.post("/save")
def settings_save(request: Request, api_key: str = Form("")):
    api_key_clean = api_key.strip()
    request.session["api_key"] = api_key_clean
    if api_key_clean:
        db_helper.save_app_setting("GEMINI_API_KEY", api_key_clean)

    return RedirectResponse(url="/settings", status_code=303)
