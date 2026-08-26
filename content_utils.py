# -*- coding: utf-8 -*-
"""Shared template context, lesson helpers, and markdown rendering."""
from __future__ import annotations

import random
import re
from pathlib import Path
from urllib.parse import quote

import markdown as md

import db_helper
import lessons_data

WORD_IMAGE_DIR = Path("static/word_images")
_WORD_IMAGE_INDEX: dict[str, str] | None = None

CEFR_LEVELS = {
    "Beginner": {"th": "ง่าย", "label": "ง่าย — Beginner", "cefr": "A1.1", "emoji": "🟢"},
    "Elementary": {"th": "กลาง", "label": "กลาง — Elementary", "cefr": "A1.2 / A2", "emoji": "🟡"},
    "Intermediate": {"th": "ยาก", "label": "ยาก — Intermediate", "cefr": "A2.2 / B1", "emoji": "🔴"},
}
THAI_TO_CEFR = {meta["th"]: key for key, meta in CEFR_LEVELS.items()}

THEMES = {
    "night": {"label": "ราตรีสวีเดน", "emoji": "🌙", "mode": "dark"},
    "aurora": {"label": "แสงเหนือ", "emoji": "🌌", "mode": "dark"},
    "fjord": {"label": "ฟยอร์ด", "emoji": "🌊", "mode": "dark"},
    "dawn": {"label": "เช้าสตอกโฮล์ม", "emoji": "☀️", "mode": "light"},
    "midsummer": {"label": "มิดซัมเมอร์", "emoji": "🌼", "mode": "light"},
}


def normalize_theme(value: str | None) -> str:
    raw = (value or "").strip().lower()
    return raw if raw in THEMES else "night"

_MD = md.Markdown(
    extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    output_format="html5",
)


def render_markdown(text: str | None) -> str:
    if not text:
        return ""
    _MD.reset()
    return _MD.convert(str(text))


_HTML_MARK = re.compile(
    r"</?(?:p|div|ul|ol|li|br|h[1-6]|blockquote|strong|em|span|table|thead|tbody|tr|td|th)\b",
    re.I,
)
_TUTOR_TERM = re.compile(
    r"<strong>([^<]+)</strong>(?:\s*\(([^)]+)\))?",
    re.I,
)
_BARE_PRON = re.compile(r'(?<!tutor-ipa">)\(([^)]{1,48})\)')


def format_tutor_reply(text: str | None) -> str:
    """Turn tutor markdown (or leftover HTML) into readable chat HTML."""
    raw = (text or "").strip()
    if not raw:
        return ""
    if _HTML_MARK.search(raw):
        html = re.sub(r"(?:<br\s*/?>\s*){2,}", "</p><p>", raw, flags=re.I)
        if not re.match(r"\s*<", html):
            html = f"<p>{html}</p>"
    else:
        html = render_markdown(raw)
    return _decorate_tutor_html(html)


def _decorate_tutor_html(html: str) -> str:
    def term(match: re.Match) -> str:
        word = match.group(1).strip().strip('"“”\'')
        if not re.search(r"[A-Za-zÅÄÖåäö]", word):
            return match.group(0)
        pron = (match.group(2) or "").strip()
        pron_html = f'<span class="tutor-ipa">({pron})</span>' if pron else ""
        return f'<span class="tutor-term"><span class="tutor-sv">{word}</span>{pron_html}</span>'

    html = re.sub(
        r"<p><strong>([^<]*[\u0E00-\u0E7F][^<]*)</strong></p>",
        r"<h3>\1</h3>",
        html,
        flags=re.I,
    )
    html = _TUTOR_TERM.sub(term, html)
    html = _example_lists_to_cards(html)
    html = _mark_example_quotes(html)
    html = _mark_bare_pronunciation(html)
    return html


def _mark_example_quotes(html: str) -> str:
    def quote(match: re.Match) -> str:
        attrs = match.group(1) or ""
        if "tutor-example" in attrs:
            return match.group(0)
        class_attr = re.search(r'class=["\']([^"\']*)["\']', attrs, re.I)
        if class_attr:
            return match.group(0).replace(
                class_attr.group(0),
                f'class="{class_attr.group(1)} tutor-example"',
                1,
            )
        return f'<blockquote class="tutor-example"{attrs}>'

    return re.sub(r"<blockquote(\s[^>]*)?>", quote, html, flags=re.I)


def _example_lists_to_cards(html: str) -> str:
    """Turn numbered Swedish examples (word / pronunciation / Thai) into cards."""

    def convert(match: re.Match) -> str:
        items = re.findall(r"<li>([\s\S]*?)</li>", match.group(1), flags=re.I)
        if len(items) < 2:
            return match.group(0)
        tripletish = 0
        for item in items:
            has_term = "tutor-term" in item or "<strong>" in item.lower()
            has_pron = "(" in item
            has_break = "<br" in item.lower() or item.count("<p>") > 1
            if has_term and has_pron and has_break:
                tripletish += 1
        if tripletish < max(2, (len(items) + 1) // 2):
            return match.group(0)
        cards = []
        for item in items:
            body = re.sub(r"</?p>", "", item.strip(), flags=re.I)
            cards.append(f'<blockquote class="tutor-example">{body}</blockquote>')
        return "\n".join(cards)

    html = re.sub(r"<ol>\s*([\s\S]*?)\s*</ol>", convert, html, flags=re.I)
    return html


def _mark_bare_pronunciation(html: str) -> str:
    """Wrap leftover (คำอ่าน) on its own line, including inside example cards."""

    def maybe(match: re.Match) -> str:
        inner = match.group(1).strip()
        if not inner or not re.search(r"[\u0E00-\u0E7F]", inner):
            return match.group(0)
        if any(ch in inner for ch in "/\\"):
            return match.group(0)
        return f'<span class="tutor-ipa">({inner})</span>'

    return _BARE_PRON.sub(maybe, html)


def lesson_questions(lesson: dict | None) -> list:
    if not lesson:
        return []
    return lesson.get("quiz") or lesson.get("questions") or []


def lesson_vocab(lesson: dict | None) -> list:
    if not lesson:
        return []
    if lesson.get("detailed_vocab"):
        return [prepare_vocab_item(item) for item in lesson["detailed_vocab"]]

    seen: set[str] = set()
    items: list[dict] = []

    def _add(swedish: str, pronunciation: str, thai: str, example: str = "") -> None:
        key = swedish.strip().lower()
        if not key or key in seen:
            return
        seen.add(key)
        thai_clean = thai_gloss_only(thai)
        lesson_level = (lesson or {}).get("level", "Beginner")
        pron = pronunciation_only(pronunciation) or swedish.strip()
        raw_example = (example or "").strip()
        example_thai = "" if is_redundant_vocab_example(raw_example, swedish, pron, thai_clean) else raw_example
        items.append(
            {
                "swedish": swedish.strip(),
                "pronunciation": pron,
                "thai": thai_clean,
                "pos": "คำศัพท์บทเรียน",
                "level": CEFR_LEVELS.get(lesson_level, CEFR_LEVELS["Beginner"])["th"],
                "example_swedish": f"{swedish.strip().capitalize()}.",
                "example_thai": example_thai,
            }
        )

    for tp in lesson.get("typing_practice") or []:
        _add(tp.get("swedish", ""), tp.get("clue", ""), tp.get("thai", ""), tp.get("explanation", ""))
    for mp in lesson.get("matching_practice") or []:
        _add(mp.get("swedish", ""), mp.get("swedish", ""), mp.get("thai", ""))
    return items


def asset_url(path: str | None) -> str:
    if not path:
        return ""
    raw = str(path).replace("\\", "/")
    if raw.startswith("http://") or raw.startswith("https://") or raw.startswith("data:"):
        return raw
    if raw.startswith("/static/"):
        return raw
    if raw.startswith("static/"):
        return "/" + raw
    if raw.startswith("/assets/"):
        return "/static" + raw
    if raw.startswith("assets/"):
        return "/static/" + raw
    return "/static/assets/" + raw.lstrip("/")


def _build_word_image_index() -> dict[str, str]:
    index: dict[str, str] = {}
    if not WORD_IMAGE_DIR.exists():
        return index
    for path in WORD_IMAGE_DIR.iterdir():
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            continue
        url = "/static/word_images/" + quote(path.name)
        stem = path.stem.strip().lower()
        index[stem] = url
        index[stem.replace("_", " ")] = url
        index[stem.replace(" ", "_")] = url
    return index


def word_image_index() -> dict[str, str]:
    global _WORD_IMAGE_INDEX
    if _WORD_IMAGE_INDEX is None:
        _WORD_IMAGE_INDEX = _build_word_image_index()
    return _WORD_IMAGE_INDEX


def reload_word_image_index() -> dict[str, str]:
    global _WORD_IMAGE_INDEX
    _WORD_IMAGE_INDEX = _build_word_image_index()
    return _WORD_IMAGE_INDEX


def persist_word_image_file(swedish: str, image_bytes: bytes) -> str:
    WORD_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    safe = (swedish or "").strip().lower().replace(" ", "_").replace("/", "_")
    path = WORD_IMAGE_DIR / f"{safe}.png"
    path.write_bytes(image_bytes)
    reload_word_image_index()
    return f"/static/word_images/{quote(path.name)}"


def remove_word_image_file(swedish: str) -> None:
    safe = (swedish or "").strip().lower().replace(" ", "_").replace("/", "_")
    path = WORD_IMAGE_DIR / f"{safe}.png"
    if path.exists():
        path.unlink()
    reload_word_image_index()


def matching_game_words() -> list[dict]:
    items = []
    seen = set()
    for lesson in lessons_data.LESSONS:
        for mp in lesson.get("matching_practice") or []:
            swedish = (mp.get("swedish") or "").strip()
            key = swedish.lower()
            if not key or key in seen:
                continue
            seen.add(key)
            items.append(
                {
                    "swedish": swedish,
                    "thai": mp.get("thai", ""),
                    "image_path": mp.get("image_path", ""),
                    "lesson_id": lesson.get("id"),
                    "lesson_title": lesson.get("title", ""),
                }
            )
    return sorted(items, key=lambda item: item["swedish"].lower())


def _image_lookup_keys(swedish: str) -> list[str]:
    raw = (swedish or "").strip().lower()
    if not raw:
        return []
    keys = [raw, raw.replace(" ", "_"), raw.replace("_", " ")]
    if raw.startswith("en "):
        keys.append(raw[3:])
        keys.append("en_" + raw[3:])
    if raw.startswith("ett "):
        keys.append(raw[4:])
        keys.append("ett_" + raw[4:])
    keys.append("en_" + raw)
    keys.append("ett_" + raw)
    keys.append("en " + raw)
    keys.append("ett " + raw)
    seen: set[str] = set()
    ordered: list[str] = []
    for key in keys:
        if key and key not in seen:
            seen.add(key)
            ordered.append(key)
    return ordered


def word_image_url(swedish: str | None, fallback: str | None = None) -> str:
    """Mongo-exported picture for a Swedish word, else the lesson asset path."""
    index = word_image_index()
    for key in _image_lookup_keys(swedish or ""):
        if key in index:
            return index[key]
    return asset_url(fallback)


def normalize_cefr_level(level: str | None) -> str | None:
    if not level:
        return None
    raw = str(level).strip()
    if raw.lower() in {"all", "ทั้งหมด"}:
        return "all"
    if raw in CEFR_LEVELS:
        return raw
    if raw in THAI_TO_CEFR:
        return THAI_TO_CEFR[raw]
    return None


def filter_vocab_by_level(items: list | None, cefr_level: str | None) -> list:
    if not items:
        return []
    normalized = normalize_cefr_level(cefr_level)
    if not normalized or normalized == "all":
        return list(items)
    thai = CEFR_LEVELS[normalized]["th"]
    return [
        item
        for item in items
        if (item.get("level") or "") in {thai, normalized}
    ]


def attach_word_images(items: list | None) -> list:
    result = []
    for item in items or []:
        row = dict(item)
        row["image_url"] = word_image_url(row.get("swedish"), row.get("image_path"))
        result.append(row)
    return result


def normalize_ids(values) -> list[int]:
    result: list[int] = []
    for value in values or []:
        try:
            result.append(int(value))
        except (TypeError, ValueError):
            continue
    return result


def is_admin(user) -> bool:
    if not user or user.get("is_guest"):
        return False
    role = str(user.get("role") or "").strip().lower()
    username = str(user.get("username") or "").strip().lower()
    return role == "admin" or username == "admin"


def role_label(user) -> str:
    if not user:
        return "แขก"
    if user.get("is_guest"):
        return "ผู้เรียน (แขก)"
    role = user.get("role") or "Student"
    if role == "Admin":
        return "ผู้ดูแลระบบ"
    return "ผู้เรียน"


_NAV_ICONS = {
    "home": "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1h-2z",
    "book": "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
    "quiz": "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
    "vocab": "M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129",
    "chat": "M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z",
    "user": "M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z",
    "cog": "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z",
    "shield": "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
    "users": "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z",
    "plus": "M12 4v16m8-8H4",
    "trash": "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16",
    "image": "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z",
}

STUDENT_NAV = [
    ("dashboard", "/dashboard", "แดชบอร์ด", _NAV_ICONS["home"]),
    ("lessons", "/lessons", "บทเรียน", _NAV_ICONS["book"]),
    ("quiz", "/quiz", "แบบทดสอบ", _NAV_ICONS["quiz"]),
    ("vocabulary", "/vocabulary", "คลังคำศัพท์", _NAV_ICONS["vocab"]),
    ("ai_tutor", "/ai-tutor", "ครู AI", _NAV_ICONS["chat"]),
    ("profile", "/profile", "โปรไฟล์", _NAV_ICONS["user"]),
]

ADMIN_NAV = [
    ("admin", "/admin", "แดชบอร์ดผู้ดูแลระบบ", _NAV_ICONS["shield"]),
    ("admin_new", "/admin/users/new", "เพิ่มผู้ใช้งานใหม่เข้าระบบ", _NAV_ICONS["plus"]),
    ("admin_users", "/admin/users", "จัดการลบผู้ใช้งานและกู้คืนข้อมูล", _NAV_ICONS["users"]),
    ("admin_game_images", "/admin/game-images", "จัดการรูปภาพเกมจับคู่คำศัพท์", _NAV_ICONS["image"]),
    ("admin_vocab_images", "/admin/vocab-images", "เพิ่ม/จัดการรูปภาพคลังคำศัพท์", _NAV_ICONS["image"]),
    ("profile", "/profile", "โปรไฟล์ส่วนตัว", _NAV_ICONS["user"]),
]

ADMIN_PREVIEW_NAV = [
    ("lessons", "/lessons", "ดูบทเรียน", _NAV_ICONS["book"]),
    ("vocabulary", "/vocabulary", "ดูคลังคำศัพท์", _NAV_ICONS["vocab"]),
]


def nav_for(user) -> list:
    return list(ADMIN_NAV) if is_admin(user) else list(STUDENT_NAV)


def home_url_for(user) -> str:
    return "/admin" if is_admin(user) else "/dashboard"


def ensure_user(request) -> dict:
    user = request.session.get("user")
    if not user:
        user = {
            "username": "guest",
            "display_name": "ผู้เรียนทั่วไป (Guest)",
            "role": "Guest Student",
            "is_guest": True,
        }
        request.session["user"] = user
    return user


def completed_for(request, username: str) -> list[int]:
    user = request.session.get("user") or {}
    if user.get("is_guest"):
        return normalize_ids(request.session.get("guest_completed", []))
    return normalize_ids(db_helper.get_user_completed_lessons(username))


def quiz_scores_for(request, username: str) -> dict:
    user = request.session.get("user") or {}
    if user.get("is_guest"):
        raw = request.session.get("guest_quiz_scores", {}) or {}
    else:
        raw = db_helper.get_user_quiz_scores(username) or {}
    scores: dict = {}
    for key, value in (raw or {}).items():
        try:
            store_key = int(key)
        except (TypeError, ValueError):
            store_key = key
        if isinstance(value, dict):
            scores[store_key] = value
        elif isinstance(value, (int, float)):
            scores[store_key] = {
                "earned": value,
                "total": 100,
                "score_pct": float(value),
            }
        else:
            scores[store_key] = {"earned": 0, "total": 0, "score_pct": 0.0}
    return scores


def mark_complete(request, username: str, lesson_id: int) -> None:
    user = request.session.get("user") or {}
    lesson_id = int(lesson_id)
    if user.get("is_guest"):
        completed = set(completed_for(request, username))
        completed.add(lesson_id)
        request.session["guest_completed"] = list(completed)
        return
    db_helper.mark_lesson_completed(username, lesson_id)


def save_score(request, username: str, lesson_id: int, earned: int, total: int, score_pct: float) -> None:
    user = request.session.get("user") or {}
    payload = {"earned": earned, "total": total, "score_pct": score_pct}
    if user.get("is_guest"):
        scores = request.session.get("guest_quiz_scores", {}) or {}
        scores[str(lesson_id)] = payload
        request.session["guest_quiz_scores"] = scores
        return
    db_helper.save_quiz_score(username, lesson_id, earned, total, score_pct)


def page_context(request, current_page: str, **extra) -> dict:
    user = ensure_user(request)
    username = user.get("username", "guest")
    if user and not user.get("is_guest"):
        try:
            import presence

            presence.beat(username)
        except Exception:
            pass
    completed = completed_for(request, username)
    total = len(lessons_data.LESSONS)
    flash_message = request.session.pop("flash_message", None)
    flash_type = request.session.pop("flash_type", None)
    theme = normalize_theme(request.session.get("theme") or request.cookies.get("ls_theme"))
    request.session["theme"] = theme
    import achievements as achievements_mod

    admin_user = is_admin(user)
    badges = achievements_mod.badge_payload(completed, total, for_admin=admin_user)
    ctx = {
        "user": user,
        "current_level": request.session.get("current_level", "Beginner"),
        "current_page": current_page,
        "completed_lessons": completed,
        "completed_count": len(completed),
        "total_lessons": total,
        "progress_pct": int((len(completed) / total) * 100) if total else 0,
        "flash_message": flash_message,
        "flash_type": flash_type,
        "initials": _initials(user.get("display_name") or user.get("username") or "G"),
        "cefr_levels": CEFR_LEVELS,
        "active_level": "all",
        "has_avatar": bool(request.session.get("has_avatar")) and not user.get("is_guest"),
        "avatar_url": (
            f"/profile/avatar?v={request.session.get('avatar_rev', 0)}"
            if request.session.get("has_avatar") and not user.get("is_guest")
            else ""
        ),
        "is_admin": admin_user,
        "earned_achievements": badges["earned_achievements"],
        "top_achievement": badges["top_achievement"],
        "role_label": role_label(user),
        "nav_items": nav_for(user),
        "preview_nav_items": ADMIN_PREVIEW_NAV if is_admin(user) else [],
        "home_url": home_url_for(user),
        "show_learner_tools": not is_admin(user),
        "theme": theme,
        "theme_mode": THEMES[theme]["mode"],
        "theme_items": [{"key": key, **meta} for key, meta in THEMES.items()],
    }
    ctx.update(extra)
    return ctx


def set_flash(request, message: str, flash_type: str = "info") -> None:
    request.session["flash_message"] = message
    request.session["flash_type"] = flash_type


def shuffled(seq):
    items = list(seq or [])
    random.shuffle(items)
    return items


def pronunciation_only(text: str | None) -> str:
    """Show only Thai phonetic reading, never the Swedish spelling."""
    raw = str(text or "").strip()
    if "[" in raw and "]" in raw:
        start = raw.find("[")
        end = raw.find("]", start)
        if end > start:
            return raw[start + 1 : end].strip()
    return raw


def is_redundant_vocab_example(
    text: str | None,
    swedish: str = "",
    pronunciation: str = "",
    thai: str = "",
) -> bool:
    """True when the 'example' is just a gloss that repeats the word/reading."""
    raw = str(text or "").strip()
    if not raw:
        return True
    lowered = raw.lower()
    if "แปลว่า" in raw:
        return True
    if re.search(r"\[[^\]]+\]", raw):
        return True
    if lowered.startswith("คำศัพท์หมวด"):
        return True
    thai_l = str(thai or "").strip().lower()
    if thai_l and lowered == thai_l:
        return True
    sw = str(swedish or "").strip().lower()
    pron = str(pronunciation or "").strip()
    if sw and sw in lowered and pron and pron in raw:
        return True
    return False


def prepare_vocab_item(item: dict) -> dict:
    """Normalize a vocab row for display: Thai-only reading, no repeated gloss."""
    row = dict(item)
    swedish = (row.get("swedish") or "").strip()
    row["swedish"] = swedish
    row["thai"] = thai_gloss_only(row.get("thai"))
    row["pronunciation"] = pronunciation_only(row.get("pronunciation") or swedish)
    if is_redundant_vocab_example(
        row.get("example_thai"), swedish, row["pronunciation"], row.get("thai")
    ):
        row["example_thai"] = ""
    return row


def thai_gloss_only(text: str | None) -> str:
    """Show only the Thai meaning, stripping Swedish hints in parentheses."""
    raw = str(text or "").strip()
    if " (" in raw:
        return raw.split(" (")[0].strip()
    return raw


def _is_vocab_summary_section(subtitle: str | None) -> bool:
    text = subtitle or ""
    return "ตารางสรุปคำศัพท์" in text or "Key Vocabulary" in text


def parse_markdown_table(content: str | None) -> list[list[str]]:
    rows: list[list[str]] = []
    for raw in (content or "").splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells):
            continue
        rows.append(cells)
    return rows


def vocab_rows_from_table(content: str | None) -> list[dict]:
    table = parse_markdown_table(content)
    if len(table) < 2:
        return []
    body = table[1:]
    items = []
    seen: set[str] = set()
    for cells in body:
        padded = (cells + ["", "", "", ""])[:4]
        swedish = re.sub(r"[*_`]", "", padded[0]).strip()
        key = swedish.lower()
        if not key or key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "swedish": swedish,
                "pronunciation": padded[1].strip(" []"),
                "thai": padded[2],
                "note": padded[3],
            }
        )
    return items


def lesson_for_view(lesson: dict | None) -> dict:
    """Copy a lesson and attach display-only pronunciation/thai fields."""
    if not lesson:
        return {}
    view = dict(lesson)
    typing_rows = []
    for item in lesson.get("typing_practice") or []:
        row = dict(item)
        row["pronunciation_text"] = pronunciation_only(item.get("clue") or item.get("swedish"))
        typing_rows.append(row)
    matching_rows = []
    for item in lesson.get("matching_practice") or []:
        row = dict(item)
        row["thai_gloss"] = thai_gloss_only(item.get("thai"))
        matching_rows.append(row)
    if typing_rows:
        view["typing_practice"] = typing_rows
    if matching_rows:
        view["matching_practice"] = matching_rows

    sections = []
    seen_vocab = False
    for sec in lesson.get("sections") or []:
        item = dict(sec)
        if _is_vocab_summary_section(item.get("subtitle")):
            if seen_vocab:
                continue
            seen_vocab = True
            item["vocab_rows"] = vocab_rows_from_table(item.get("content") or "")
        sections.append(item)
    view["sections"] = sections
    return view


def _initials(name: str) -> str:
    parts = re.findall(r"[A-Za-zก-๙0-9]+", name or "")
    if not parts:
        return "SV"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][:1] + parts[1][:1]).upper()
