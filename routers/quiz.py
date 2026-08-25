import random

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

import lessons_data
from content_utils import lesson_questions, page_context, save_score, set_flash
from templating import templates

router = APIRouter(prefix="/quiz", tags=["quiz"])


def _prepare_quiz_questions(raw_questions) -> list[dict]:
    prepared = []
    for question in raw_questions or []:
        item = {
            "question": question.get("question", ""),
            "answer": question.get("answer", ""),
            "explanation": question.get("explanation", ""),
            "options": list(question.get("options") or []),
        }
        if item["options"]:
            random.shuffle(item["options"])
        prepared.append(item)
    random.shuffle(prepared)
    return prepared


def _grade(questions, form_data):
    earned = 0
    total = len(questions)
    user_answers = {}
    for idx, q in enumerate(questions):
        user_ans = str(form_data.get(f"q_{idx}", "")).strip()
        user_answers[f"q_{idx}"] = user_ans
        expected_ans = str(q.get("answer", "")).strip()
        if user_ans.lower() == expected_ans.lower():
            earned += 1
    score_pct = round((earned / total) * 100, 1) if total else 0
    return {
        "earned": earned,
        "total": total,
        "score_pct": score_pct,
        "user_answers": user_answers,
    }


@router.get("/exam/start", response_class=HTMLResponse)
@router.get("/exam", response_class=HTMLResponse)
def final_exam_page(request: Request):
    ctx = page_context(request, "quiz")
    all_questions = []
    for lesson in lessons_data.LESSONS:
        all_questions.extend(lesson_questions(lesson))

    if not request.session.get("exam_questions_999"):
        sampled = random.sample(all_questions, min(10, len(all_questions))) if all_questions else []
        selected = _prepare_quiz_questions(sampled)
        request.session["exam_questions_999"] = selected
    else:
        selected = request.session["exam_questions_999"]

    exam_lesson = {
        "id": 999,
        "title": "ข้อสอบวัดผลรวมระดับหลักสูตร (Comprehensive Final Exam)",
        "cefr": "A1–B1",
        "questions": selected,
        "quiz": selected,
    }
    ctx.update(
        {
            "lessons": lessons_data.LESSONS,
            "current_lesson": exam_lesson,
            "quiz_result": request.session.get("quiz_result_999"),
            "is_final_exam": True,
            "questions": selected,
        }
    )
    return templates.TemplateResponse(request=request, name="quiz.html", context=ctx)


@router.post("/exam/submit")
async def submit_exam(request: Request):
    form_data = await request.form()
    ctx = page_context(request, "quiz")
    username = ctx["user"].get("username", "guest")
    questions = request.session.get("exam_questions_999", [])
    quiz_result = _grade(questions, form_data)
    request.session["quiz_result_999"] = quiz_result
    save_score(request, username, 999, quiz_result["earned"], quiz_result["total"], quiz_result["score_pct"])
    set_flash(request, f"ส่งข้อสอบวัดผลรวมแล้ว — ได้ {quiz_result['score_pct']}%", "success")
    return RedirectResponse(url="/quiz/exam", status_code=303)


@router.get("", response_class=HTMLResponse)
def quiz_default(request: Request):
    active_id = request.session.get("active_lesson_id", 1)
    return RedirectResponse(url=f"/quiz/{active_id}", status_code=303)


@router.get("/{lesson_id}", response_class=HTMLResponse)
def quiz_detail(request: Request, lesson_id: int):
    ctx = page_context(request, "quiz")
    lesson = next((l for l in lessons_data.LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        lesson = lessons_data.LESSONS[0]
        lesson_id = lesson["id"]

    result_key = f"quiz_result_{lesson_id}"
    session_key = f"quiz_questions_{lesson_id}"
    quiz_result = request.session.get(result_key)
    if quiz_result:
        questions = request.session.get(session_key) or lesson_questions(lesson)
    else:
        questions = request.session.get(session_key)
        if not questions:
            questions = _prepare_quiz_questions(lesson_questions(lesson))
            request.session[session_key] = questions
    ctx.update(
        {
            "lessons": lessons_data.LESSONS,
            "current_lesson": lesson,
            "quiz_result": quiz_result,
            "is_final_exam": False,
            "questions": questions,
        }
    )
    return templates.TemplateResponse(request=request, name="quiz.html", context=ctx)


@router.post("/{lesson_id}/submit")
async def submit_quiz(request: Request, lesson_id: int):
    if lesson_id == 999:
        return await submit_exam(request)

    form_data = await request.form()
    ctx = page_context(request, "quiz")
    username = ctx["user"].get("username", "guest")
    lesson = next((l for l in lessons_data.LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        return RedirectResponse(url="/quiz", status_code=303)

    questions = request.session.get(f"quiz_questions_{lesson_id}") or lesson_questions(lesson)
    quiz_result = _grade(questions, form_data)
    request.session[f"quiz_result_{lesson_id}"] = quiz_result
    save_score(request, username, lesson_id, quiz_result["earned"], quiz_result["total"], quiz_result["score_pct"])
    set_flash(request, f"ตรวจข้อสอบแล้ว — ได้ {quiz_result['score_pct']}%", "success")
    return RedirectResponse(url=f"/quiz/{lesson_id}", status_code=303)


@router.get("/exam/retry")
@router.post("/exam/retry")
def retry_exam(request: Request):
    request.session.pop("exam_questions_999", None)
    request.session.pop("quiz_result_999", None)
    set_flash(request, "เริ่มข้อสอบชุดใหม่แล้ว — ลำดับข้อและตัวเลือกถูกสลับแล้ว", "info")
    return RedirectResponse(url="/quiz/exam", status_code=303)


@router.get("/{lesson_id}/retry")
@router.post("/{lesson_id}/retry")
def retry_quiz(request: Request, lesson_id: int):
    request.session.pop(f"quiz_questions_{lesson_id}", None)
    request.session.pop(f"quiz_result_{lesson_id}", None)
    set_flash(request, "เริ่มแบบฝึกหัดใหม่แล้ว — ลำดับข้อและตัวเลือกถูกสลับแล้ว", "info")
    return RedirectResponse(url=f"/quiz/{lesson_id}", status_code=303)
