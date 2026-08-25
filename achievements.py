# -*- coding: utf-8 -*-
"""
achievements.py  —  SvenskaEasy Achievement System
Defines all achievement badges and provides helper functions to compute
which achievements a student has earned based on completed lesson count.
"""

# Each achievement:
#   id          — unique key
#   title_en    — English badge name
#   title_th    — Thai badge name
#   description — short Thai description
#   icon        — emoji icon
#   required    — lessons needed (int, or "all" resolved at runtime)
#   color       — accent colour for the card
ACHIEVEMENT_DEFINITIONS = [
    {
        "id": "first_step",
        "title_en": "First Step",
        "title_th": "ก้าวแรก",
        "description": "เรียนบทแรกสำเร็จแล้ว เยี่ยมมาก!",
        "icon": "🥉",
        "frame": "bronze",
        "required": 1,
        "color": "#cd7f32",
    },
    {
        "id": "getting_started",
        "title_en": "Getting Started",
        "title_th": "เริ่มต้นได้ดี",
        "description": "เรียนครบ 3 บทเรียนแล้ว ไปต่อเลย!",
        "icon": "🥈",
        "frame": "silver",
        "required": 3,
        "color": "#c0c7d1",
    },
    {
        "id": "on_a_roll",
        "title_en": "On a Roll",
        "title_th": "ฮอตแรง",
        "description": "เรียนครบ 5 บทเรียนแล้ว กำลังร้อนแรงเลย!",
        "icon": "🥇",
        "frame": "gold",
        "required": 5,
        "color": "#FECB00",
    },
    {
        "id": "halfway",
        "title_en": "Halfway There",
        "title_th": "ครึ่งทางแล้ว",
        "description": "เรียนครบ 10 บทเรียน ยังไม่หยุดนะ!",
        "icon": "🏅",
        "frame": "gold",
        "required": 10,
        "color": "#4aa3df",
    },
    {
        "id": "dedicated",
        "title_en": "Dedicated Learner",
        "title_th": "นักเรียนขยัน",
        "description": "เรียนครบ 15 บทเรียน ความมุ่งมั่นของคุณน่าชื่นชม!",
        "icon": "🎖️",
        "frame": "royal",
        "required": 15,
        "color": "#9b59b6",
    },
    {
        "id": "almost_there",
        "title_en": "Almost There",
        "title_th": "ใกล้ถึงแล้ว",
        "description": "เรียนครบ 20 บทเรียน เกือบถึงจุดหมายแล้ว!",
        "icon": "⭐",
        "frame": "royal",
        "required": 20,
        "color": "#1abc9c",
    },
    {
        "id": "swedish_master",
        "title_en": "Swedish Master",
        "title_th": "ปรมาจารย์สวีเดน",
        "description": "เรียนครบ 25 บทเรียน คุณคือผู้เชี่ยวชาญ!",
        "icon": "👑",
        "frame": "legend",
        "required": 25,
        "color": "#e67e22",
    },
    {
        "id": "legend",
        "title_en": "Legend",
        "title_th": "ตำนาน",
        "description": "เรียนครบทุกบทเรียน คุณคือตำนานแห่ง SvenskaEasy!",
        "icon": "🏆",
        "frame": "legend",
        "required": "all",  # resolved dynamically against total_lessons
        "color": "#004B87",
    },
]


def get_all_achievements(total_lessons: int) -> list:
    """Return a copy of all achievement definitions with 'required' resolved
    for the 'all' sentinel value.

    Args:
        total_lessons: Total number of lessons in the app.

    Returns:
        List of achievement dicts, each with an integer 'required' field.
    """
    result = []
    for ach in ACHIEVEMENT_DEFINITIONS:
        a = dict(ach)
        if a["required"] == "all":
            a["required"] = total_lessons
        result.append(a)
    return result


def get_earned_achievements(completed_count: int, total_lessons: int) -> list:
    """Return the list of achievements the student has earned.

    Args:
        completed_count: Number of lessons completed by the student.
        total_lessons:   Total number of lessons available in the app.

    Returns:
        List of earned achievement dicts (subset of all achievements).
    """
    return [
        a for a in get_all_achievements(total_lessons)
        if completed_count >= a["required"]
    ]


def get_newly_earned(prev_count: int, new_count: int, total_lessons: int) -> list:
    """Return achievements that were just unlocked by going from prev_count to new_count.

    Args:
        prev_count:    Lesson count before the latest completion.
        new_count:     Lesson count after the latest completion.
        total_lessons: Total lessons in the app.

    Returns:
        List of newly unlocked achievement dicts (may be empty).
    """
    all_ach = get_all_achievements(total_lessons)
    return [
        a for a in all_ach
        if prev_count < a["required"] <= new_count
    ]


def badge_payload(completed, total_lessons: int, *, for_admin: bool = False) -> dict:
    """Earned medals for UI: chips after a name, and a frame on the avatar."""
    if for_admin:
        return {"earned_achievements": [], "top_achievement": None}
    if isinstance(completed, int):
        count = completed
    else:
        count = len(completed or [])
    earned = get_earned_achievements(count, total_lessons)
    return {
        "earned_achievements": earned,
        "top_achievement": earned[-1] if earned else None,
    }


def attach_user_badges(users, total_lessons: int) -> list:
    for row in users or []:
        role = str(row.get("role") or "").lower()
        payload = badge_payload(row.get("completed_lessons") or [], total_lessons, for_admin=role == "admin")
        row.update(payload)
    return users


def evaluate_achievements(completed_lessons, quiz_scores, total_lessons):
    completed_count = len(completed_lessons) if isinstance(completed_lessons, (list, set)) else 0
    all_ach = get_all_achievements(total_lessons)
    result = []
    for ach in all_ach:
        item = dict(ach)
        item["unlocked"] = completed_count >= item["required"]
        result.append(item)
    return result

