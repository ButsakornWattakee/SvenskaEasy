from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import db_helper

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = request.session.get("user")
    current_level = request.session.get("current_level", "Beginner")
    if user and not user.get("is_guest"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="auth/login.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "login",
        "error_message": None
    })

@router.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    user_db = db_helper.get_user(username)
    current_level = request.session.get("current_level", "Beginner")
    if not user_db:
        return templates.TemplateResponse(request=request, name="auth/login.html", context={
            "user": None,
            "current_level": current_level,
            "current_page": "login",
            "error_message": "ไม่พบชื่อผู้ใช้นี้ในระบบ"
        })
    
    if user_db.get("is_deleted"):
        return templates.TemplateResponse(request=request, name="auth/login.html", context={
            "user": None,
            "current_level": current_level,
            "current_page": "login",
            "error_message": "บัญชีผู้ใช้นี้ถูกลบออกจากระบบชั่วคราว"
        })

    if db_helper.verify_password(password, user_db.get("password", "")):
        request.session["user"] = {
            "username": user_db["username"],
            "display_name": user_db.get("display_name", username),
            "role": user_db.get("role", "Student"),
            "is_guest": False
        }
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        return templates.TemplateResponse(request=request, name="auth/login.html", context={
            "user": None,
            "current_level": current_level,
            "current_page": "login",
            "error_message": "รหัสผ่านไม่ถูกต้อง"
        })

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    user = request.session.get("user")
    current_level = request.session.get("current_level", "Beginner")
    return templates.TemplateResponse(request=request, name="auth/register.html", context={
        "user": user,
        "current_level": current_level,
        "current_page": "register",
        "error_message": None
    })

@router.post("/register")
def register_post(request: Request, username: str = Form(...), display_name: str = Form(...), password: str = Form(...)):
    current_level = request.session.get("current_level", "Beginner")
    if db_helper.get_user(username):
        return templates.TemplateResponse(request=request, name="auth/register.html", context={
            "user": None,
            "current_level": current_level,
            "current_page": "register",
            "error_message": "ชื่อผู้ใช้นี้มีในระบบแล้ว กรุณาใช้ชื่ออื่น"
        })

    success = db_helper.register_user(username, password, display_name)
    if success:
        request.session["user"] = {
            "username": username,
            "display_name": display_name,
            "role": "Student",
            "is_guest": False
        }
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        return templates.TemplateResponse(request=request, name="auth/register.html", context={
            "user": None,
            "current_level": current_level,
            "current_page": "register",
            "error_message": "เกิดข้อผิดพลาดในการลงทะเบียน"
        })

@router.post("/guest")
def guest_login(request: Request):
    request.session["user"] = {
        "username": "guest",
        "display_name": "ผู้เรียนทั่วไป (Guest)",
        "role": "Guest Student",
        "is_guest": True
    }
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)
