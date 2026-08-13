from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import lessons_data
import vocabulary_data

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def vocabulary_page(request: Request, lesson_id: int = None):
    user = request.session.get("user")
    if not user:
        user = {"username": "guest", "display_name": "ผู้เรียนทั่วไป (Guest)", "role": "Guest Student", "is_guest": True}
        request.session["user"] = user

    current_level = request.session.get("current_level", "Beginner")

    # Collect vocabulary items
    vocab_items = []
    if lesson_id:
        lesson = next((l for l in lessons_data.LESSONS if l["id"] == lesson_id), None)
        if lesson and "detailed_vocab" in lesson:
            vocab_items = lesson["detailed_vocab"]

    if not vocab_items:
        # Load default full vocabulary dataset
        vocab_items = vocabulary_data.FULL_VOCABULARY_LIST

    return templates.TemplateResponse(request=request, name="vocabulary.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "vocabulary",
        "vocab_items": vocab_items
    })
