from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import lessons_data
import db_helper

router = APIRouter(prefix="/quiz", tags=["quiz"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def quiz_default(request: Request):
    active_id = request.session.get("active_lesson_id", 1)
    return RedirectResponse(url=f"/quiz/{active_id}", status_code=303)

@router.get("/{lesson_id}", response_class=HTMLResponse)
def quiz_detail(request: Request, lesson_id: int):
    user = request.session.get("user")
    if not user:
        user = {"username": "guest", "display_name": "ผู้เรียนทั่วไป (Guest)", "role": "Guest Student", "is_guest": True}
        request.session["user"] = user

    current_level = request.session.get("current_level", "Beginner")

    lesson = next((l for l in lessons_data.LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        lesson = lessons_data.LESSONS[0]

    quiz_result = request.session.get(f"quiz_result_{lesson_id}")

    return templates.TemplateResponse(request=request, name="quiz.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "quiz",
        "lessons": lessons_data.LESSONS,
        "current_lesson": lesson,
        "quiz_result": quiz_result,
        "is_final_exam": False
    })

@router.post("/{lesson_id}/submit")
async def submit_quiz(request: Request, lesson_id: int):
    form_data = await request.form()
    user = request.session.get("user")
    username = user.get("username", "guest") if user else "guest"

    lesson = next((l for l in lessons_data.LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        return RedirectResponse(url="/quiz", status_code=303)

    questions = lesson.get("questions", [])
    earned = 0
    total = len(questions)
    user_answers = {}

    for idx, q in enumerate(questions):
        user_ans = form_data.get(f"q_{idx}", "").strip()
        user_answers[f"q_{idx}"] = user_ans
        expected_ans = q.get("answer", "").strip()

        # Case-insensitive comparison for text answers
        if user_ans.lower() == expected_ans.lower():
            earned += 1

    score_pct = round((earned / total) * 100, 1) if total > 0 else 0

    quiz_result = {
        "earned": earned,
        "total": total,
        "score_pct": score_pct,
        "user_answers": user_answers
    }

    request.session[f"quiz_result_{lesson_id}"] = quiz_result

    # Save to database
    db_helper.save_quiz_score(username, lesson_id, earned, total, score_pct)

    return RedirectResponse(url=f"/quiz/{lesson_id}", status_code=303)

import random

@router.get("/exam/start", response_class=HTMLResponse)
def final_exam_page(request: Request):
    user = request.session.get("user")
    if not user:
        user = {"username": "guest", "display_name": "ผู้เรียนทั่วไป (Guest)", "role": "Guest Student", "is_guest": True}

    current_level = request.session.get("current_level", "Beginner")

    # Aggregate questions across all lessons
    all_questions = []
    for l in lessons_data.LESSONS:
        all_questions.extend(l.get("questions", []))

    # Pick 10 random questions (seeded or sampled)
    if not request.session.get("exam_questions_999"):
        selected_questions = random.sample(all_questions, min(10, len(all_questions))) if all_questions else []
        request.session["exam_questions_999"] = selected_questions
    else:
        selected_questions = request.session["exam_questions_999"]

    exam_lesson = {
        "id": 999,
        "title": "ข้อสอบวัดผลรวมระดับหลักสูตร (Comprehensive Final Exam)",
        "questions": selected_questions
    }

    quiz_result = request.session.get("quiz_result_999")

    return templates.TemplateResponse(request=request, name="quiz.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "quiz",
        "lessons": lessons_data.LESSONS,
        "current_lesson": exam_lesson,
        "quiz_result": quiz_result,
        "is_final_exam": True
    })

@router.post("/999/submit")
async def submit_exam(request: Request):
    form_data = await request.form()
    user = request.session.get("user")
    username = user.get("username", "guest") if user else "guest"

    questions = request.session.get("exam_questions_999", [])
    earned = 0
    total = len(questions)
    user_answers = {}

    for idx, q in enumerate(questions):
        user_ans = form_data.get(f"q_{idx}", "").strip()
        user_answers[f"q_{idx}"] = user_ans
        expected_ans = q.get("answer", "").strip()
        if user_ans.lower() == expected_ans.lower():
            earned += 1

    score_pct = round((earned / total) * 100, 1) if total > 0 else 0

    quiz_result = {
        "earned": earned,
        "total": total,
        "score_pct": score_pct,
        "user_answers": user_answers
    }

    request.session["quiz_result_999"] = quiz_result
    db_helper.save_quiz_score(username, 999, earned, total, score_pct)

    return RedirectResponse(url="/quiz/exam/start", status_code=303)

