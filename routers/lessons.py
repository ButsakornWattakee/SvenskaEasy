from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

import lessons_data
from content_utils import lesson_for_view, lesson_questions, mark_complete, page_context, set_flash
from templating import templates

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("", response_class=HTMLResponse)
def lessons_default(request: Request):
    active_id = request.session.get("active_lesson_id", 1)
    return RedirectResponse(url=f"/lessons/{active_id}", status_code=303)


@router.get("/{lesson_id}", response_class=HTMLResponse)
def lesson_detail(request: Request, lesson_id: int):
    ctx = page_context(request, "lessons")
    lesson = next((l for l in lessons_data.LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        lesson = lessons_data.LESSONS[0]
        lesson_id = lesson["id"]

    request.session["active_lesson_id"] = lesson_id
    lesson_ids = [l["id"] for l in lessons_data.LESSONS]
    curr_idx = lesson_ids.index(lesson_id) if lesson_id in lesson_ids else 0

    ctx.update(
        {
            "lesson": lesson_for_view(lesson),
            "prev_lesson_id": lesson_ids[curr_idx - 1] if curr_idx > 0 else None,
            "next_lesson_id": lesson_ids[curr_idx + 1] if curr_idx < len(lesson_ids) - 1 else None,
            "is_completed": lesson_id in ctx["completed_lessons"],
            "question_count": len(lesson_questions(lesson)),
            "all_lessons": lessons_data.LESSONS,
        }
    )
    return templates.TemplateResponse(request=request, name="lesson.html", context=ctx)


@router.post("/{lesson_id}/complete")
def mark_lesson_complete(request: Request, lesson_id: int):
    ctx = page_context(request, "lessons")
    username = ctx["user"].get("username", "guest")
    mark_complete(request, username, lesson_id)
    set_flash(request, "บันทึกว่าเรียนบทนี้เสร็จแล้ว — สุดยอด!", "success")
    return RedirectResponse(url=f"/lessons/{lesson_id}", status_code=303)
