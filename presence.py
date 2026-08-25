# -*- coding: utf-8 -*-
"""In-memory presence with throttled DB persistence."""
from __future__ import annotations

import time
from datetime import datetime, timezone

import db_helper

ONLINE_WINDOW = 70
PERSIST_EVERY = 20

_last_seen: dict[str, float] = {}
_last_persist: dict[str, float] = {}


def beat(username: str | None) -> None:
    name = (username or "").strip()
    if not name or name.lower() == "guest":
        return
    now = time.time()
    _last_seen[name] = now
    if now - _last_persist.get(name, 0) >= PERSIST_EVERY:
        _last_persist[name] = now
        try:
            db_helper.update_last_active(name)
        except Exception:
            pass


def drop(username: str | None) -> None:
    name = (username or "").strip()
    if name:
        _last_seen.pop(name, None)


def seconds_ago(username: str) -> float | None:
    ts = _last_seen.get(username)
    if ts is None:
        return None
    return max(0.0, time.time() - ts)


def is_online(username: str) -> bool:
    ago = seconds_ago(username)
    return ago is not None and ago <= ONLINE_WINDOW


def online_usernames() -> list[str]:
    now = time.time()
    return sorted(name for name, ts in _last_seen.items() if now - ts <= ONLINE_WINDOW)


def online_snapshot() -> list[dict]:
    rows = []
    try:
        import achievements
        import lessons_data

        total_lessons = len(lessons_data.LESSONS)
    except Exception:
        achievements = None
        total_lessons = 0
    for name in online_usernames():
        user = db_helper.get_user(name) or {}
        if user.get("is_deleted"):
            continue
        ago = seconds_ago(name) or 0
        role = user.get("role") or "Student"
        earned = []
        if achievements is not None:
            payload = achievements.badge_payload(
                user.get("completed_lessons") or [],
                total_lessons,
                for_admin=str(role).lower() == "admin",
            )
            earned = [
                {
                    "id": item["id"],
                    "icon": item.get("icon") or "🏅",
                    "title_th": item["title_th"],
                    "title_en": item["title_en"],
                    "color": item.get("color") or "#FECB00",
                }
                for item in payload["earned_achievements"]
            ]
        rows.append(
            {
                "username": name,
                "display_name": user.get("display_name") or name,
                "role": role,
                "seconds_ago": int(ago),
                "earned_achievements": earned,
            }
        )
    rows.sort(key=lambda item: (0 if str(item["role"]).lower() == "admin" else 1, item["display_name"].lower()))
    return rows


def last_seen_label(username: str, last_active: str | None = None) -> str:
    if is_online(username):
        return "ออนไลน์"
    raw = last_active or ""
    if not raw:
        return "ออฟไลน์"
    try:
        seen = datetime.fromisoformat(raw)
        if seen.tzinfo is None:
            seen = seen.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        minutes = int((now - seen).total_seconds() / 60)
        if minutes < 1:
            return "เพิ่งออฟไลน์"
        if minutes < 60:
            return f"ออฟไลน์ {minutes} นาทีที่แล้ว"
        hours = minutes // 60
        if hours < 24:
            return f"ออฟไลน์ {hours} ชม. ที่แล้ว"
        return f"ออฟไลน์ {hours // 24} วันที่แล้ว"
    except Exception:
        return "ออฟไลน์"
