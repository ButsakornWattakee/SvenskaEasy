from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import lessons_data
import chat_agent
import db_helper

router = APIRouter(tags=["ai_tutor"])
templates = Jinja2Templates(directory="templates")

class ChatRequest(BaseModel):
    message: str

@router.get("/ai-tutor", response_class=HTMLResponse)
def ai_tutor_page(request: Request, lesson_id: int = None):
    user = request.session.get("user")
    if not user:
        user = {"username": "guest", "display_name": "ผู้เรียนทั่วไป (Guest)", "role": "Guest Student", "is_guest": True}
        request.session["user"] = user

    current_level = request.session.get("current_level", "Beginner")
    chat_history = request.session.get("chat_history", [])

    active_lesson_title = request.session.get("ai_active_lesson")

    # If navigated with ?lesson_id=...
    if lesson_id:
        lesson = next((l for l in lessons_data.LESSONS if l["id"] == lesson_id), None)
        if lesson:
            active_lesson_title = lesson["title"]
            request.session["ai_active_lesson"] = active_lesson_title

            # Append initial greeting for this lesson if not already present
            greeting = f"Hej! ยินดีต้อนรับครับ ตอนนี้เรากำลังโฟกัสการเรียนใน **{lesson['title']}** [Swedish]\n\nคุณครูพร้อมตอบทุกคำถาม ไวยากรณ์ สัทศาสตร์ การผันคำ หรือตัวอย่างประโยคในบทนี้แล้วครับ พิมพ์คำถามมาได้เลยครับ!"
            if not chat_history or chat_history[-1].get("content") != greeting:
                chat_history.append({
                    "role": "assistant",
                    "content": greeting
                })
                request.session["chat_history"] = chat_history

    api_key = request.session.get("api_key") or db_helper.get_app_setting("GEMINI_API_KEY")

    return templates.TemplateResponse(request=request, name="ai_tutor.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "ai_tutor",
        "chat_history": chat_history,
        "active_lesson_title": active_lesson_title,
        "is_api_connected": bool(api_key)
    })

@router.post("/ai-tutor/clear")
def clear_ai_chat(request: Request):
    request.session["chat_history"] = []
    request.session["ai_active_lesson"] = None
    return RedirectResponse(url="/ai-tutor", status_code=303)

@router.post("/api/ai-chat")
def api_ai_chat(request: Request, body: ChatRequest):
    chat_history = request.session.get("chat_history", [])
    user_prompt = body.message.strip()

    # Append user prompt to history
    chat_history.append({"role": "user", "content": user_prompt})

    api_key = request.session.get("api_key") or db_helper.get_app_setting("GEMINI_API_KEY")
    lesson_context = request.session.get("ai_active_lesson", "")

    # Call AI chat agent engine
    reply_html = chat_agent.get_ai_response(user_prompt, chat_history, api_key=api_key, lesson_context=lesson_context)

    chat_history.append({"role": "assistant", "content": reply_html})
    request.session["chat_history"] = chat_history

    return JSONResponse({
        "status": "success",
        "reply_html": reply_html
    })
