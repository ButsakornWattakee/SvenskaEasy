from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import lessons_data
import db_helper

router = APIRouter(prefix="/lessons", tags=["lessons"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def lessons_default(request: Request):
    active_id = request.session.get("active_lesson_id", 1)
    return RedirectResponse(url=f"/lessons/{active_id}", status_code=303)

@router.get("/{lesson_id}", response_class=HTMLResponse)
def lesson_detail(request: Request, lesson_id: int):
    user = request.session.get("user")
    if not user:
        user = {"username": "guest", "display_name": "ผู้เรียนทั่วไป (Guest)", "role": "Guest Student", "is_guest": True}
        request.session["user"] = user

    username = user.get("username", "guest")
    current_level = request.session.get("current_level", "Beginner")

    lesson = next((l for l in lessons_data.LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        lesson = lessons_data.LESSONS[0]
        lesson_id = lesson["id"]

    request.session["active_lesson_id"] = lesson_id

    # Check prev / next
    lesson_ids = [l["id"] for l in lessons_data.LESSONS]
    curr_idx = lesson_ids.index(lesson_id) if lesson_id in lesson_ids else 0

    prev_id = lesson_ids[curr_idx - 1] if curr_idx > 0 else None
    next_id = lesson_ids[curr_idx + 1] if curr_idx < len(lesson_ids) - 1 else None

    completed_lessons = db_helper.get_user_completed_lessons(username)
    is_completed = lesson_id in completed_lessons

    return templates.TemplateResponse(request=request, name="lesson.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "lessons",
        "lesson": lesson,
        "prev_lesson_id": prev_id,
        "next_lesson_id": next_id,
        "is_completed": is_completed
    })

@router.post("/{lesson_id}/complete")
def mark_lesson_complete(request: Request, lesson_id: int):
    user = request.session.get("user")
    username = user.get("username", "guest") if user else "guest"

    db_helper.mark_lesson_completed(username, lesson_id)
    return RedirectResponse(url=f"/lessons/{lesson_id}", status_code=303)
