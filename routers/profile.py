from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import achievements
import db_helper
import lessons_data

router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def profile_page(request: Request):
    user = request.session.get("user")
    if not user:
        user = {"username": "guest", "display_name": "ผู้เรียนทั่วไป (Guest)", "role": "Guest Student", "is_guest": True}
        request.session["user"] = user

    username = user.get("username", "guest")
    current_level = request.session.get("current_level", "Beginner")

    completed_lessons = db_helper.get_user_completed_lessons(username)
    quiz_scores = db_helper.get_user_quiz_scores(username)

    # Evaluate achievements
    user_achievements = achievements.evaluate_achievements(
        completed_lessons=completed_lessons,
        quiz_scores=quiz_scores,
        total_lessons=len(lessons_data.LESSONS)
    )

    # Format quiz history table
    quiz_history = []
    for l_id, data in quiz_scores.items():
        lesson = next((l for l in lessons_data.LESSONS if l["id"] == l_id), None)
        title = lesson["title"] if lesson else f"บทเรียนที่ {l_id}"
        quiz_history.append({
            "lesson_id": l_id,
            "title": title,
            "earned": data.get("earned", 0),
            "total": data.get("total", 0),
            "score_pct": data.get("score_pct", 0)
        })

    return templates.TemplateResponse(request=request, name="profile.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "profile",
        "achievements": user_achievements,
        "quiz_history": quiz_history
    })
