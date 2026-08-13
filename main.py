import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import config
from routers import auth, dashboard, lessons, quiz, ai_tutor, vocabulary, profile, settings, admin

app = FastAPI(
    title="LearnSwedish Platform",
    description="ระบบเรียนภาษาสวีเดนออนไลน์ (FastAPI Rebuild)",
    version="2.0.0"
)

# Session middleware for cookie-based session management
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)

# Serve static files (CSS, JS, assets)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(lessons.router)
app.include_router(quiz.router)
app.include_router(ai_tutor.router)
app.include_router(vocabulary.router)
app.include_router(profile.router)
app.include_router(settings.router)
app.include_router(admin.router)

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    user = request.session.get("user")
    current_level = request.session.get("current_level", "Beginner")
    return templates.TemplateResponse(request=request, name="base.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "404",
        "flash_message": "ไม่พบหน้าที่ต้องการ (404 Not Found)",
        "flash_type": "danger"
    }, status_code=404)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
