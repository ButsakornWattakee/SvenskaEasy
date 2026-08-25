# -*- coding: utf-8 -*-
from fastapi.templating import Jinja2Templates

from content_utils import (
    CEFR_LEVELS,
    THEMES,
    asset_url,
    format_tutor_reply,
    lesson_questions,
    pronunciation_only,
    render_markdown,
    shuffled,
    thai_gloss_only,
    word_image_url,
)

templates = Jinja2Templates(directory="templates")
templates.env.auto_reload = True
templates.env.cache = None
templates.env.filters["md"] = render_markdown
templates.env.filters["tutor_html"] = format_tutor_reply
templates.env.filters["asset"] = asset_url
templates.env.filters["questions"] = lesson_questions
templates.env.filters["shuffle"] = shuffled
templates.env.filters["word_image"] = word_image_url
templates.env.filters["pronunciation"] = pronunciation_only
templates.env.filters["thai_gloss"] = thai_gloss_only
templates.env.globals["cefr_levels"] = CEFR_LEVELS
templates.env.globals["cefr_level_items"] = [
    {"key": key, **meta} for key, meta in CEFR_LEVELS.items()
]
templates.env.globals["theme_items"] = [
    {"key": key, **meta} for key, meta in THEMES.items()
]
