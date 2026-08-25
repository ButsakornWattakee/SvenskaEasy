from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

import db_helper
from content_utils import is_admin, page_context, set_flash
from templating import templates

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_class=HTMLResponse)
def settings_page(request: Request):
    ctx = page_context(request, "settings")
    if not is_admin(ctx["user"]):
        return RedirectResponse(url="/dashboard", status_code=303)
    api_key = request.session.get("api_key") or db_helper.get_app_setting("GEMINI_API_KEY")
    ctx["api_key"] = api_key or ""
    ctx["is_api_connected"] = bool(api_key)
    return templates.TemplateResponse(request=request, name="settings.html", context=ctx)


@router.post("/save")
def settings_save(request: Request, api_key: str = Form("")):
    ctx = page_context(request, "settings")
    if not is_admin(ctx["user"]):
        return RedirectResponse(url="/dashboard", status_code=303)
    api_key_clean = api_key.strip()
    request.session["api_key"] = api_key_clean
    if api_key_clean:
        db_helper.save_app_setting("GEMINI_API_KEY", api_key_clean)
        set_flash(request, "บันทึก API Key เรียบร้อยแล้ว", "success")
    else:
        set_flash(request, "ล้างค่า API Key แล้ว — ครู AI จะทำงานในโหมดจำลอง", "info")
    return RedirectResponse(url="/settings", status_code=303)
