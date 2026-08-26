import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

import config
import db_helper
from content_utils import page_context, reload_word_image_index
from routers import admin, ai_tutor, auth, dashboard, lessons, profile, quiz, settings, vocabulary
from templating import templates


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db_helper.init_db()
    reload_word_image_index()
    yield


app = FastAPI(
    title="SvenskaEasy Platform",
    description="ระบบเรียนภาษาสวีเดนออนไลน์ (FastAPI + Tailwind)",
    version="3.0.1",
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)


@app.middleware("http")
async def no_store_html(request: Request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("content-type", "")
    if "text/html" in content_type:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)


@app.get("/")
def root_entry(request: Request):
    from routers.dashboard import root_page

    return root_page(request)


app.include_router(dashboard.router)


@app.get("/forgot-password", response_class=HTMLResponse)
@app.get("/auth/forgot-password/", response_class=HTMLResponse)
def forgot_password_alias(request: Request):
    from routers.auth import forgot_password_page

    return forgot_password_page(request)
app.include_router(lessons.router)
app.include_router(quiz.router)


@app.api_route("/quiz/{lesson_id}/retry", methods=["GET", "POST"])
def quiz_retry_alias(request: Request, lesson_id: int):
    from routers.quiz import retry_quiz

    return retry_quiz(request, lesson_id)
app.include_router(ai_tutor.router)
app.include_router(vocabulary.router)
app.include_router(profile.router)
app.include_router(settings.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": "svenskaeasy"}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code != 404:
        return HTMLResponse(str(exc.detail), status_code=exc.status_code)
    ctx = page_context(request, "404")
    ctx["flash_message"] = None
    return templates.TemplateResponse(
        request=request,
        name="404.html",
        context=ctx,
        status_code=404,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
