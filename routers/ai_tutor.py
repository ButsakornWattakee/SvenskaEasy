from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.concurrency import run_in_threadpool

import chat_agent
import db_helper
import lessons_data
from content_utils import format_tutor_reply, page_context
from templating import templates

router = APIRouter(tags=["ai_tutor"])


@router.get("/ai-tutor", response_class=HTMLResponse)
def ai_tutor_page(request: Request, lesson_id: int | None = None):
    ctx = page_context(request, "ai_tutor")
    chat_history = request.session.get("chat_history", [])
    active_lesson_title = request.session.get("ai_active_lesson")

    if lesson_id:
        lesson = next((l for l in lessons_data.LESSONS if l["id"] == lesson_id), None)
        if lesson:
            active_lesson_title = lesson["title"]
            request.session["ai_active_lesson"] = active_lesson_title
            greeting = (
                f"ยินดีต้อนรับครับ ตอนนี้โฟกัสบท **{lesson['title']}**\n\n"
                "ถามได้เลยทั้งคำศัพท์ ไวยากรณ์ การออกเสียง หรือขอประโยคตัวอย่างในบทนี้ครับ"
            )
            if not chat_history or chat_history[-1].get("content") != greeting:
                chat_history.append({"role": "assistant", "content": greeting})
                request.session["chat_history"] = chat_history

    api_key = request.session.get("api_key") or db_helper.get_app_setting("GEMINI_API_KEY")
    ctx.update(
        {
            "chat_history": _history_for_view(chat_history),
            "active_lesson_title": active_lesson_title,
            "is_api_connected": bool(api_key),
            "lessons": lessons_data.LESSONS,
        }
    )
    return templates.TemplateResponse(request=request, name="ai_tutor.html", context=ctx)


@router.post("/ai-tutor/clear")
def clear_ai_chat(request: Request):
    request.session["chat_history"] = []
    request.session["ai_active_lesson"] = None
    return RedirectResponse(url="/ai-tutor", status_code=303)


@router.post("/api/ai-chat")
async def api_ai_chat(request: Request):
    user_prompt = ""
    content_type = (request.headers.get("content-type") or "").lower()
    try:
        if "application/json" in content_type:
            data = await request.json()
            user_prompt = str((data or {}).get("message") or "")
        else:
            form = await request.form()
            user_prompt = str(form.get("message") or "")
    except Exception:
        user_prompt = ""
    user_prompt = user_prompt.strip()[:2000]
    if not user_prompt:
        return JSONResponse(
            {"status": "error", "reply_html": "<p>กรุณาพิมพ์ข้อความก่อนส่งครับ</p>"},
            status_code=400,
        )

    chat_history = list(request.session.get("chat_history") or [])
    pending = chat_history + [{"role": "user", "content": user_prompt}]
    api_key = request.session.get("api_key") or db_helper.get_app_setting("GEMINI_API_KEY")
    lesson_context = request.session.get("ai_active_lesson") or ""
    try:
        reply = await run_in_threadpool(
            chat_agent.get_ai_response,
            user_prompt,
            pending,
            api_key,
            lesson_context,
        )
    except Exception:
        reply = "ครูติดปัญหาในการตอบตอนนี้ครับ ลองส่งใหม่อีกครั้งได้เลย"
    reply = (reply or "").strip()[:3500]
    chat_history.append({"role": "user", "content": user_prompt})
    chat_history.append({"role": "assistant", "content": reply})
    request.session["chat_history"] = chat_history[-16:]
    return JSONResponse({"status": "success", "reply_html": format_tutor_reply(reply)})


def _history_for_view(chat_history: list) -> list:
    view = []
    for item in chat_history or []:
        row = dict(item)
        if row.get("role") == "assistant":
            row["html"] = format_tutor_reply(row.get("content") or "")
        view.append(row)
    return view
