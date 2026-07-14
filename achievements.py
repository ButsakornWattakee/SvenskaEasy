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
        "icon": "🌱",
        "required": 1,
        "color": "#27ae60",
    },
    {
        "id": "getting_started",
        "title_en": "Getting Started",
        "title_th": "เริ่มต้นได้ดี",
        "description": "เรียนครบ 3 บทเรียนแล้ว ไปต่อเลย!",
        "icon": "⭐",
        "required": 3,
        "color": "#f39c12",
    },
    {
        "id": "on_a_roll",
        "title_en": "On a Roll",
        "title_th": "ฮอตแรง",
        "description": "เรียนครบ 5 บทเรียนแล้ว กำลังร้อนแรงเลย!",
        "icon": "🔥",
        "required": 5,
        "color": "#e74c3c",
    },
    {
        "id": "halfway",
        "title_en": "Halfway There",
        "title_th": "ครึ่งทางแล้ว",
        "description": "เรียนครบ 10 บทเรียน ยังไม่หยุดนะ!",
        "icon": "🏅",
        "required": 10,
        "color": "#3498db",
    },
    {
        "id": "dedicated",
        "title_en": "Dedicated Learner",
        "title_th": "นักเรียนขยัน",
        "description": "เรียนครบ 15 บทเรียน ความมุ่งมั่นของคุณน่าชื่นชม!",
        "icon": "📚",
        "required": 15,
        "color": "#9b59b6",
    },
    {
        "id": "almost_there",
        "title_en": "Almost There",
        "title_th": "ใกล้ถึงแล้ว",
        "description": "เรียนครบ 20 บทเรียน เกือบถึงจุดหมายแล้ว!",
        "icon": "💪",
        "required": 20,
        "color": "#16a085",
    },
    {
        "id": "swedish_master",
        "title_en": "Swedish Master",
        "title_th": "ปรมาจารย์สวีเดน",
        "description": "เรียนครบ 25 บทเรียน คุณคือผู้เชี่ยวชาญ!",
        "icon": "👑",
        "required": 25,
        "color": "#e67e22",
    },
    {
        "id": "legend",
        "title_en": "Legend",
        "title_th": "ตำนาน",
        "description": "เรียนครบทุกบทเรียน คุณคือตำนานแห่ง SvenskaEasy!",
        "icon": "🇸🇪",
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
