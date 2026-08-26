from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

import db_helper
import lessons_data
from content_utils import home_url_for, is_admin, page_context, quiz_scores_for
from templating import templates

router = APIRouter(tags=["dashboard"])


@router.get("/")
def root_page(request: Request):
    user = request.session.get("user") or {}
    if user and not user.get("is_guest"):
        return RedirectResponse(url=home_url_for(user), status_code=303)
    return RedirectResponse(url="/auth/login", status_code=303)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    ctx = page_context(request, "dashboard")
    if is_admin(ctx["user"]):
        return RedirectResponse(url="/admin", status_code=303)
    username = ctx["user"].get("username", "guest")
    quiz_scores = quiz_scores_for(request, username)

    lessons_by_level = {
        "Beginner": [l for l in lessons_data.LESSONS if l.get("level") == "Beginner"],
        "Elementary": [l for l in lessons_data.LESSONS if l.get("level") == "Elementary"],
        "Intermediate": [l for l in lessons_data.LESSONS if l.get("level") == "Intermediate"],
    }

    score_values = []
    for item in (quiz_scores or {}).values():
        if isinstance(item, dict):
            score_values.append(float(item.get("score_pct", 0) or 0))
        elif isinstance(item, (int, float)):
            score_values.append(float(item))
    avg_score = round(sum(score_values) / len(score_values), 1) if score_values else 0.0

    api_key = request.session.get("api_key") or db_helper.get_app_setting("GEMINI_API_KEY")
    ctx.update(
        {
            "lessons_by_level": lessons_by_level,
            "average_score": avg_score,
            "is_api_connected": bool(api_key),
        }
    )
    return templates.TemplateResponse(request=request, name="dashboard.html", context=ctx)


@router.post("/set-level")
def set_level(request: Request, selected_level: str = Form(...)):
    from content_utils import normalize_cefr_level

    level = normalize_cefr_level(selected_level) or "all"
    request.session["current_level"] = level
    referer = request.headers.get("referer") or "/dashboard"
    if "/vocabulary" in (referer or ""):
        if level == "all":
            return RedirectResponse(url="/vocabulary", status_code=303)
        return RedirectResponse(url=f"/vocabulary?level={level}", status_code=303)
    return RedirectResponse(url=referer, status_code=303)


def _apply_theme(request: Request, theme: str):
    from content_utils import normalize_theme

    chosen = normalize_theme(theme)
    request.session["theme"] = chosen
    referer = request.headers.get("referer") or "/dashboard"
    if "/set-theme" in (referer or ""):
        referer = "/dashboard"
    response = RedirectResponse(url=referer, status_code=303)
    response.set_cookie("ls_theme", chosen, max_age=365 * 24 * 3600, samesite="lax")
    return response


@router.get("/set-theme")
def set_theme_get(request: Request, theme: str = "night"):
    return _apply_theme(request, theme)


@router.post("/set-theme")
def set_theme(request: Request, theme: str = Form(...)):
    return _apply_theme(request, theme)


@router.get("/presence")
@router.post("/presence")
def presence_ping(request: Request):
    user = request.session.get("user") or {}
    if user.get("is_guest") or not user.get("username"):
        return JSONResponse({"ok": False, "online": False})
    import presence

    presence.beat(user["username"])
    return JSONResponse({"ok": True, "online": True})
