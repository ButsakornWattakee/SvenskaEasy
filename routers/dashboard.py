from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import lessons_data
import db_helper

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    user = request.session.get("user")
    if not user:
        # Default to guest mode
        user = {
            "username": "guest",
            "display_name": "ผู้เรียนทั่วไป (Guest)",
            "role": "Guest Student",
            "is_guest": True
        }
        request.session["user"] = user

    username = user.get("username", "guest")
    current_level = request.session.get("current_level", "Beginner")

    # Group lessons by level
    lessons_by_level = {
        "Beginner": [l for l in lessons_data.LESSONS if l.get("level") == "Beginner"],
        "Elementary": [l for l in lessons_data.LESSONS if l.get("level") == "Elementary"],
        "Intermediate": [l for l in lessons_data.LESSONS if l.get("level") == "Intermediate"]
    }

    # Fetch user progress from DB
    completed_lessons = db_helper.get_user_completed_lessons(username)
    quiz_scores = db_helper.get_user_quiz_scores(username)

    completed_count = len(completed_lessons)
    total_lessons = len(lessons_data.LESSONS)

    if quiz_scores:
        avg_score = round(sum(item.get("score_pct", 0) for item in quiz_scores.values()) / len(quiz_scores), 1)
    else:
        avg_score = 0.0

    api_key = request.session.get("api_key") or db_helper.get_app_setting("GEMINI_API_KEY")

    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "dashboard",
        "lessons_by_level": lessons_by_level,
        "completed_lessons": completed_lessons,
        "completed_count": completed_count,
        "total_lessons": total_lessons,
        "average_score": avg_score,
        "is_api_connected": bool(api_key)
    })

@router.post("/set-level")
def set_level(request: Request, selected_level: str = Form(...)):
    request.session["current_level"] = selected_level
    return RedirectResponse(url="/dashboard", status_code=303)
