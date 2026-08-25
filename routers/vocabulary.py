from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import lessons_data
import vocabulary_data
from content_utils import (
    CEFR_LEVELS,
    attach_word_images,
    filter_vocab_by_level,
    lesson_vocab,
    normalize_cefr_level,
    page_context,
)
from templating import templates

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


@router.get("", response_class=HTMLResponse)
def vocabulary_page(request: Request, lesson_id: int | None = None, level: str | None = None):
    ctx = page_context(request, "vocabulary")
    vocab_items = []
    active_lesson = None
    if lesson_id:
        active_lesson = next((l for l in lessons_data.LESSONS if l["id"] == lesson_id), None)
        if active_lesson:
            vocab_items = lesson_vocab(active_lesson)

    if not vocab_items:
        vocab_items = vocabulary_data.all_vocabulary()

    active_level = normalize_cefr_level(level)
    if active_level:
        request.session["current_level"] = active_level
        ctx["current_level"] = active_level
    elif not lesson_id:
        active_level = normalize_cefr_level(request.session.get("current_level"))

    if not lesson_id and active_level and active_level != "all":
        vocab_items = filter_vocab_by_level(vocab_items, active_level)

    vocab_items = attach_word_images(vocab_items)
    level_meta = CEFR_LEVELS.get(active_level or "", {})

    ctx.update(
        {
            "vocab_items": vocab_items,
            "vocab_count": len(vocab_items),
            "active_lesson": active_lesson,
            "active_level": active_level or "all",
            "level_meta": level_meta,
            "cefr_levels": CEFR_LEVELS,
            "lessons": lessons_data.LESSONS,
        }
    )
    return templates.TemplateResponse(request=request, name="vocabulary.html", context=ctx)
