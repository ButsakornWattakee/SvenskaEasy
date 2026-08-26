# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import db_helper
import lessons_data
from content_utils import (
    asset_url,
    format_tutor_reply,
    is_redundant_vocab_example,
    lesson_questions,
    lesson_vocab,
    prepare_vocab_item,
    pronunciation_only,
    render_markdown,
    word_image_url,
)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db_helper, "FALLBACK_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr(db_helper, "DELETED_FALLBACK_FILE", str(tmp_path / "deleted.json"))
    monkeypatch.setattr(db_helper, "SETTINGS_FILE", str(tmp_path / "settings.json"))
    monkeypatch.setattr(db_helper, "FALLBACK_CUSTOM_VOCAB_PATH", str(tmp_path / "custom_vocab.json"))
    monkeypatch.setattr(db_helper, "FALLBACK_VOCAB_IMAGES_PATH", str(tmp_path / "vocab_images.json"))
    monkeypatch.setattr(db_helper, "_cached_client", None)
    monkeypatch.setattr(db_helper, "get_db_client", lambda: (None, "offline"))
    monkeypatch.setattr(db_helper, "get_db_client_direct", lambda: (None, "offline"))
    monkeypatch.setattr(db_helper, "is_mongodb_online", lambda: False)
    monkeypatch.setattr(db_helper, "is_mongodb_online_cached", lambda: False)
    db_helper.init_db()

    from main import app

    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_redirects_to_login(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (303, 307)
    assert response.headers["location"].endswith("/auth/login")
    login = client.get("/auth/login")
    assert login.status_code == 200
    assert "เข้าสู่ระบบ" in login.text


def test_dashboard_uses_tailwind(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    html = response.text
    assert "cdn.tailwindcss.com" in html
    assert "SvenskaEasy" in html
    assert "mesh-bg" in html
    assert "theme-on-dark" in html
    assert "20260826-ai-chat" in html
    assert "sidebar-wordmark" in html
    assert "sidebar-profile" in html
    assert "Svenska som andraspråk" in html
    assert "nav-icon" in html
    assert "toggleNav" in html


def test_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert "เข้าสู่ระบบ" in response.text
    assert "SvenskaEasy" in response.text
    assert "LearnSwedish" not in response.text
    assert "ลืมรหัสผ่าน" in response.text
    assert "/auth/forgot-password" in response.text
    assert "theme-on-dark" in response.text
    css = client.get("/static/css/app.css?v=20260826-ai-chat")
    assert css.status_code == 200
    assert "--text-muted:" in css.text
    assert "[data-theme=\"aurora\"]" in css.text
    assert "[data-theme=\"midsummer\"]" in css.text
    assert ".flashcard-back .flash-word" in css.text
    assert "text-on-dark" in css.text


def test_forgot_password_resets_with_matching_email(client):
    client.post(
        "/auth/register",
        data={"username": "resetme", "display_name": "Reset Me", "password": "oldpass", "email": "resetme@gmail.com"},
        follow_redirects=True,
    )
    client.post("/auth/logout")

    page = client.get("/auth/forgot-password")
    assert page.status_code == 200
    assert "ลืมรหัสผ่าน" in page.text

    mismatch = client.post(
        "/auth/forgot-password",
        data={"username": "resetme", "email": "wrong@gmail.com"},
        follow_redirects=True,
    )
    assert "ไม่พบบัญชีที่ตรงกับชื่อผู้ใช้และอีเมลนี้" in mismatch.text

    verify = client.post(
        "/auth/forgot-password",
        data={"username": "resetme", "email": "resetme@gmail.com"},
        follow_redirects=False,
    )
    assert verify.status_code == 303
    assert verify.headers["location"].endswith("/auth/reset-password")

    reset_page = client.get("/auth/reset-password")
    assert reset_page.status_code == 200
    assert "resetme" in reset_page.text.lower()
    assert "data-password-toggle" in reset_page.text
    assert reset_page.text.count("data-password-toggle") >= 2

    mismatch_pw = client.post(
        "/auth/reset-password",
        data={"password": "newpass", "password_confirm": "other"},
        follow_redirects=True,
    )
    assert "ไม่ตรงกัน" in mismatch_pw.text

    saved = client.post(
        "/auth/reset-password",
        data={"password": "newpass", "password_confirm": "newpass"},
        follow_redirects=False,
    )
    assert saved.status_code == 303
    assert saved.headers["location"].endswith("/auth/login")

    old_login = client.post(
        "/auth/login",
        data={"username": "resetme", "password": "oldpass"},
        follow_redirects=True,
    )
    assert "รหัสผ่านไม่ถูกต้อง" in old_login.text

    new_login = client.post(
        "/auth/login",
        data={"username": "resetme", "password": "newpass"},
        follow_redirects=False,
    )
    assert new_login.status_code == 303


def test_register_login_and_progress(client):
    register = client.post(
        "/auth/register",
        data={"username": "anna", "display_name": "Anna", "password": "pass123", "email": "anna@gmail.com"},
        follow_redirects=False,
    )
    assert register.status_code == 303

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert "Anna" in dashboard.text

    complete = client.post("/lessons/1/complete", follow_redirects=False)
    assert complete.status_code == 303
    lesson = client.get("/lessons/1")
    assert "เรียนจบแล้ว" in lesson.text or "เรียนเสร็จสิ้นแล้ว" in lesson.text


def test_lesson_renders_markdown(client):
    response = client.get("/lessons/1")
    assert response.status_code == 200
    assert "Å" in response.text or "åtta" in response.text
    assert "<table" in response.text or "tack" in response.text
    title = "ตารางสรุปคำศัพท์ คำอ่าน และสำนวนสำคัญประจำบท"
    assert response.text.count(title) == 1
    assert "vocab-card" in response.text
    assert "vocab-summary" in response.text


def test_quiz_has_questions_and_grades(client, monkeypatch):
    from routers import quiz as quiz_router

    monkeypatch.setattr(quiz_router.random, "shuffle", lambda seq: None)

    page = client.get("/quiz/1")
    assert page.status_code == 200
    assert "ข้อที่ 1" in page.text

    lesson = next(l for l in lessons_data.LESSONS if l["id"] == 1)
    questions = lesson_questions(lesson)
    assert len(questions) >= 3

    payload = {f"q_{idx}": q["answer"] for idx, q in enumerate(questions)}
    submit = client.post("/quiz/1/submit", data=payload, follow_redirects=True)
    assert submit.status_code == 200
    assert "100" in submit.text


def test_quiz_retry_after_fail_reshuffles(client):
    page = client.get("/quiz/1")
    assert page.status_code == 200
    count = len(set(re.findall(r'name="q_(\d+)"', page.text)))
    assert count >= 3
    payload = {f"q_{idx}": "คำตอบที่ไม่ถูก" for idx in range(count)}
    failed = client.post("/quiz/1/submit", data=payload, follow_redirects=True)
    assert failed.status_code == 200
    assert "ทดสอบอีกครั้ง" in failed.text
    assert "เฉลย:" in failed.text

    retry = client.post("/quiz/1/retry", follow_redirects=True)
    assert retry.status_code == 200
    assert "ตรวจคำตอบและบันทึกคะแนน" in retry.text
    assert "ทดสอบอีกครั้ง" not in retry.text
    assert "เฉลย:" not in retry.text


def test_final_exam_route(client):
    response = client.get("/quiz/exam")
    assert response.status_code == 200
    assert "ข้อสอบ" in response.text


def test_vocabulary_and_search_markup(client):
    response = client.get("/vocabulary")
    assert response.status_code == 200
    assert "hej" in response.text.lower()
    assert "vocabSearchInput" in response.text
    assert "flashcard-back" in response.text
    assert "flash-word" in response.text
    assert "คลิกเพื่อดูคำแปล" in response.text
    assert 'class="flashcard-face flashcard-back theme-on-dark overflow-hidden"' in response.text
    cards = re.findall(r'<div class="flashcard vocab-flash".*?</div>\s*</div>\s*</div>', response.text, re.S)
    apelsin = next((card for card in cards if ">apelsin<" in card.lower()), "")
    assert apelsin
    front, back = apelsin.split("flashcard-back", 1)
    assert "อปเปลซีน" in front
    assert "apelsin [" not in front.lower()
    assert "ส้ม" in back
    assert "อปเปลซีน" not in back
    assert "แปลว่า" not in back
    assert "apelsin" not in back.lower()


def test_vocabulary_filters_by_cefr_level(client):
    beginner = client.get("/vocabulary?level=Beginner")
    assert beginner.status_code == 200
    assert "hej" in beginner.text.lower()
    assert "ง่าย — Beginner" in beginner.text
    assert "แฟลชการ์ด" in beginner.text
    assert "ตาราง" in beginner.text
    assert beginner.text.count("vocab-entry") < client.get("/vocabulary?level=all").text.count("vocab-entry")

    hard = client.get("/vocabulary?level=Intermediate")
    assert hard.status_code == 200
    assert "sjuksköterska" in hard.text.lower()
    assert "ยาก — Intermediate" in hard.text
    assert hard.text.count("vocab-entry") < beginner.text.count("vocab-entry")


def test_ai_chat_sandbox(client, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    import db_helper

    monkeypatch.setattr(db_helper, "get_app_setting", lambda key, default=None: default)
    response = client.post("/api/ai-chat", json={"message": "hej สวัสดี"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    html = body["reply_html"]
    assert "Hej" in html or "สวัสดี" in html or "เฮย์" in html
    assert "tutor-term" in html
    assert "tutor-example" in html or "<ul>" in html or "<li>" in html
    page = client.get("/ai-tutor")
    assert page.status_code == 200
    assert "tutor-prose" in page.text
    assert "tutor-term" in page.text
    assert "aiChatForm" in page.text
    js = client.get("/static/js/main.js?v=20260826-ai-chat")
    assert js.status_code == 200
    assert "/api/ai-chat" in js.text


def test_tutor_reply_is_easy_to_scan():
    html = format_tutor_reply(
        "คำทักทายพื้นฐาน\n\n> **Hej**\n> (เฮย์)\n> สวัสดี\n\n- **röd** (เริด) — สีแดง"
    )
    assert '<span class="tutor-sv">Hej</span>' in html
    assert '<span class="tutor-ipa">(เฮย์)</span>' in html
    assert '<span class="tutor-sv">röd</span>' in html
    assert "tutor-example" in html
    assert "<li>" in html
    assert "**Hej**" not in html

    gemini_style = format_tutor_reply(
        "คำว่า **Hej** ใช้ทักทาย\n\n**ประโยคตัวอย่าง:**\n\n"
        "1. **Hej, hur mår du?**\n(เฮ้, ฮือร์ มัวร์ ดืว?)\nสวัสดี คุณสบายดีไหม?\n\n"
        "2. **Vad heter du?**\n(วอด เฮีย-เทอร์ ดืว?)\nคุณชื่ออะไรครับ?"
    )
    assert '<span class="tutor-sv">Hej</span>' in gemini_style
    assert "tutor-example" in gemini_style
    assert "<h3>" in gemini_style
    assert "ประโยคตัวอย่าง" in gemini_style
    assert 'tutor-sv">ประโยคตัวอย่าง' not in gemini_style


def test_gemini_quota_falls_back_to_another_model(monkeypatch):
    import chat_agent

    class QuotaError(Exception):
        pass

    class FakeResponse:
        text = "คำว่า **Hej** ใช้ทักทายครับ"

    class FakeModels:
        def generate_content(self, model, contents, config):
            if model in ("gemini-3-flash-preview", "gemini-3-flash", "gemini-2.5-flash-lite"):
                raise QuotaError(
                    "429 RESOURCE_EXHAUSTED. Quota exceeded for metric: "
                    "generate_content_free_tier_requests, model: gemini-3-flash"
                )
            if model in ("gemini-2.5-flash",):
                raise QuotaError("404 NOT_FOUND. This model is no longer available to new users.")
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key, **kwargs):
            self.models = FakeModels()

    chat_agent._resolved_model_name = "gemini-3-flash-preview"
    monkeypatch.setattr(chat_agent.genai, "Client", FakeClient)

    reply = chat_agent.get_ai_response("hej", api_key="AIzaSy-test-key-12345")
    assert "Hej" in reply
    assert "429" not in reply
    assert chat_agent._resolved_model_name == "gemini-flash-lite-latest"


def test_gemini_skips_retired_flash_models(monkeypatch):
    import chat_agent

    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    names = chat_agent._candidate_models()
    assert "gemini-2.5-flash-lite" not in names
    assert names[0] == "gemini-flash-lite-latest"
    assert "gemini-3.5-flash-lite" in names


def test_gemini_quota_message_is_readable():
    import chat_agent

    message = chat_agent._friendly_gemini_error(
        "429 RESOURCE_EXHAUSTED You exceeded your current quota"
    )
    assert "โควต้า" in message
    assert "RESOURCE_EXHAUSTED" not in message
    assert "Streamlit" not in message


def test_settings_api_requires_second_pin(client, monkeypatch):
    monkeypatch.delenv("ADMIN_SETTINGS_CODE", raising=False)
    guest = client.get("/settings", follow_redirects=False)
    assert guest.status_code in (303, 307)

    import db_helper

    db_helper.create_user("gateadmin", "gateadmin@learnswedish.local", "pass123", role="Admin", display_name="Gate")
    client.post("/auth/login", data={"username": "gateadmin", "password": "pass123"}, follow_redirects=True)

    home = client.get("/admin")
    assert 'href="/settings"' in home.text
    assert "ตั้งค่า API" in home.text

    page = client.get("/settings")
    assert page.status_code == 200
    assert "ใส่รหัสผ่านก่อน" in page.text
    assert 'name="password"' in page.text
    assert "ADMIN_SETTINGS_CODE" not in page.text
    assert "เข้าสู่หน้าตั้งค่า API" in page.text
    assert 'name="api_key"' not in page.text
    assert "AIza" not in page.text
    alias = client.get("/settings/api")
    assert alias.status_code == 200
    assert 'name="password"' in alias.text

    denied_save = client.post("/settings", data={"intent": "save", "api_key": "AIzaSy-should-not-save"}, follow_redirects=True)
    assert "รหัสผ่าน" in denied_save.text
    assert 'name="api_key"' not in denied_save.text

    client.post("/settings", data={"intent": "lock"}, follow_redirects=True)
    locked = client.get("/settings")
    assert "ใส่รหัสผ่านก่อน" in locked.text
    assert 'name="password"' in locked.text
    assert 'name="api_key"' not in locked.text

    wrong = client.post("/settings", data={"intent": "unlock", "password": "wrong99"}, follow_redirects=True)
    assert "ไม่ถูกต้อง" in wrong.text
    assert 'name="api_key"' not in wrong.text

    opened = client.post("/settings", data={"intent": "unlock", "password": "pass123"}, follow_redirects=True)
    assert opened.status_code == 200
    assert "ตั้งค่า Gemini API" in opened.text
    assert 'name="api_key"' in opened.text
    assert "AIzaSy-should-not-save" not in opened.text

    saved = client.post("/settings", data={"intent": "save", "api_key": "AIzaSy-test-lock-key"}, follow_redirects=True)
    assert saved.status_code == 200
    assert "••••" in saved.text
    assert "AIzaSy-test-lock-key" not in saved.text


def test_settings_unlocks_with_admin_settings_code(client, monkeypatch):
    monkeypatch.setenv("ADMIN_SETTINGS_CODE", "rail-gate-42")
    import db_helper

    db_helper.create_user("codeadmin", "codeadmin@learnswedish.local", "pass123", role="Admin", display_name="Code")
    client.post("/auth/login", data={"username": "codeadmin", "password": "pass123"}, follow_redirects=True)

    page = client.get("/settings")
    assert "ADMIN_SETTINGS_CODE" not in page.text
    assert "Railway" not in page.text
    denied = client.post("/settings", data={"intent": "unlock", "password": "pass123"}, follow_redirects=True)
    assert 'name="api_key"' not in denied.text
    opened = client.post("/settings", data={"intent": "unlock", "password": "rail-gate-42"}, follow_redirects=True)
    assert opened.status_code == 200
    assert "ตั้งค่า Gemini API" in opened.text
    assert 'name="api_key"' in opened.text


def test_admin_requires_admin(client):
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code in (303, 307)
    location = response.headers["location"]
    assert location.endswith("/dashboard") or location.endswith("/auth/login")
    html = client.get("/dashboard").text
    assert "แดชบอร์ดผู้ดูแลระบบ" not in html
    assert "บทเรียน" in html


def test_admin_workspace_is_separate(client):
    client.post(
        "/auth/register",
        data={"username": "boss", "display_name": "Boss", "password": "pass123", "email": "boss@gmail.com"},
        follow_redirects=True,
    )
    import db_helper

    db_helper.create_user("superadmin", "superadmin@learnswedish.local", "pass123", role="Admin", display_name="Super")
    client.post("/auth/logout")
    logged = client.post("/auth/login", data={"username": "superadmin", "password": "pass123"}, follow_redirects=False)
    assert logged.status_code == 303
    assert logged.headers["location"].endswith("/admin")

    home = client.get("/admin", follow_redirects=True)
    assert home.status_code == 200
    assert "แดชบอร์ดผู้ดูแลระบบ" in home.text
    assert "เพิ่มผู้ใช้งานใหม่เข้าระบบ" in home.text
    assert "จัดการลบผู้ใช้งานและกู้คืนข้อมูล" in home.text
    assert "จัดการรูปภาพเกมจับคู่คำศัพท์" in home.text
    assert "เพิ่ม/จัดการรูปภาพคลังคำศัพท์" in home.text
    assert "โปรไฟล์ส่วนตัว" in home.text
    assert "แบบทดสอบ" not in home.text

    admin_profile = client.get("/profile")
    assert admin_profile.status_code == 200
    assert "เหรียญตราความสำเร็จ" not in admin_profile.text
    assert "เรียนจบ" not in admin_profile.text
    assert "ประวัติแบบทดสอบ" not in admin_profile.text
    assert "is-admin-frame" in admin_profile.text
    assert 'title="ผู้ดูแลระบบ"' in admin_profile.text
    assert "👑" in admin_profile.text

    live = client.get("/admin/presence")
    assert live.status_code == 200
    payload = live.json()
    assert payload["ok"] is True
    assert "online" in payload
    assert any(u["username"] == "superadmin" for u in payload["online"])
    home_live = client.get("/admin")
    assert "ผู้ใช้ออนไลน์ตอนนี้" in home_live.text

    student_dash = client.get("/dashboard", follow_redirects=False)
    assert student_dash.status_code in (303, 307)
    assert student_dash.headers["location"].endswith("/admin")


def test_admin_can_add_custom_vocabulary_word(client):
    db_helper.create_user("lexadmin", "lexadmin@learnswedish.local", "pass123", role="Admin", display_name="Lex")
    client.post("/auth/login", data={"username": "lexadmin", "password": "pass123"}, follow_redirects=True)

    page = client.get("/admin/vocab-images")
    assert page.status_code == 200
    assert "เพิ่มคำศัพท์ใหม่" in page.text
    assert 'action="/admin/vocab-images/words"' in page.text

    created = client.post(
        "/admin/vocab-images/words",
        data={
            "swedish": "lagom",
            "thai": "พอดี / ไม่มากไม่น้อย",
            "pronunciation": "ลา-กอม",
            "pos": "คำคุณศัพท์ (adjektiv)",
            "level": "กลาง",
            "category": "วัฒนธรรม",
            "example_swedish": "Lagom är bäst.",
            "example_thai": "พอดีคือดีที่สุด",
        },
        follow_redirects=False,
    )
    assert created.status_code == 303
    assert "lagom" in created.headers.get("location", "").lower()

    admin_page = client.get("/admin/vocab-images?word=lagom")
    assert "lagom" in admin_page.text.lower()
    assert "เพิ่มเอง" in admin_page.text
    assert "ลบคำศัพท์ที่เพิ่มเอง" in admin_page.text

    vocab = client.get("/vocabulary?level=all")
    assert vocab.status_code == 200
    assert "lagom" in vocab.text.lower()
    assert "พอดี" in vocab.text

    duplicate = client.post(
        "/admin/vocab-images/words",
        data={"swedish": "hej", "thai": "สวัสดีซ้ำ", "pronunciation": "เฮ", "pos": "คำอุทาน (interjektion)", "level": "ง่าย"},
        follow_redirects=True,
    )
    assert "มีในคลังอยู่แล้ว" in duplicate.text

    client.post("/auth/logout")
    denied = client.post(
        "/admin/vocab-images/words",
        data={"swedish": "nejtack", "thai": "ไม่ล่ะ ขอบคุณ", "level": "ง่าย"},
        follow_redirects=False,
    )
    assert denied.status_code in (303, 307)


def test_404_page(client):
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404
    assert "404" in response.text


def test_helpers_unit():
    lesson = next(l for l in lessons_data.LESSONS if l["id"] == 1)
    assert lesson_questions(lesson)
    assert lesson_vocab(lesson)
    assert pronunciation_only("apelsin [อปเปลซีน]") == "อปเปลซีน"
    assert is_redundant_vocab_example("apelsin [อปเปลซีน] แปลว่า ส้ม", "apelsin", "อปเปลซีน", "ส้ม")
    cleaned = prepare_vocab_item({
        "swedish": "apelsin",
        "pronunciation": "apelsin [อปเปลซีน]",
        "thai": "ส้ม",
        "example_thai": "apelsin [อปเปลซีน] แปลว่า ส้ม",
    })
    assert cleaned["pronunciation"] == "อปเปลซีน"
    assert cleaned["example_thai"] == ""
    assert asset_url("assets/lesson_1_1.png") == "/static/assets/lesson_1_1.png"
    html = render_markdown("**tack** และตาราง\n\n| a | b |\n| --- | --- |\n| 1 | 2 |")
    assert "<strong>tack</strong>" in html
    assert "<table>" in html


def test_word_images_pair_mongo_exports_to_current_words():
    pairs = {
        "hej": "hej",
        "tack": "tack",
        "katt": "katt",
        "äpple": "äpple",
        "god morgon": "god_morgon",
        "flicka": "flicka",
        "röd": "röd",
    }
    for swedish, filename_part in pairs.items():
        url = word_image_url(swedish)
        assert url, f"missing image for {swedish}"
        assert "/static/word_images/" in url
        assert filename_part in unquote(url)


def test_vocabulary_page_shows_paired_pictures(client):
    response = client.get("/vocabulary")
    assert response.status_code == 200
    html = response.text
    assert "/static/word_images/" in html
    assert "hej" in html.lower()
    assert "vocab-entry" in html


def test_lesson_matching_prefers_word_picture(client):
    response = client.get("/lessons/1")
    assert response.status_code == 200
    assert "/static/word_images/" in response.text


def test_typing_prompt_uses_thai_item_number(client):
    html = client.get("/lessons/1").text
    start = html.find('id="typingPane"')
    end = html.find('id="matchPane"')
    pane = html[start:end]
    assert "ข้อที่ 1:" in pane
    assert "ขอบคุณ" in pane
    assert "ในภาษาสวีเดน" in pane
    assert "คำใบ้:" not in pane
    assert "คำตอบคือ" not in pane


def test_matching_thai_under_image_swedish_choices(client):
    html = client.get("/lessons/1").text
    start = html.find('id="matchPane"')
    pane = html[start:]
    assert "ขอบคุณ" in pane
    assert "ตัวเลือกคำภาษาสวีเดน" in pane
    assert "ตรวจการจับคู่" in pane
    assert "match-thai" in pane
    assert "match-check-btn" in pane
    assert "แตะภาพที่ต้องการ" in pane
    assert re.search(r">\s*tack\s*<", pane, flags=re.I)
    assert "(Tack" not in pane


def test_theme_can_be_switched(client):
    page = client.get("/auth/login")
    assert page.status_code == 200
    assert 'data-theme="night"' in page.text
    assert "theme-dot" in page.text
    assert "/set-theme?theme=dawn" in page.text
    assert "themeSelect" not in page.text

    home = client.get("/dashboard")
    assert home.status_code == 200
    assert "theme-dot" in home.text
    assert "/set-theme?theme=aurora" in home.text

    switched = client.get(
        "/set-theme?theme=dawn",
        headers={"Referer": "http://testserver/auth/login"},
        follow_redirects=True,
    )
    assert switched.status_code == 200
    assert 'data-theme="dawn"' in switched.text
    assert 'data-theme-mode="light"' in switched.text


def test_cefr_level_select_is_available(client):
    html = client.get("/dashboard").text
    assert 'name="selected_level"' in html
    assert "Beginner" in html
    assert "Elementary" in html
    assert "Intermediate" in html
    assert "ทั้งหมด" in html


def test_profile_avatar_upload_and_resize(client):
    from io import BytesIO

    from PIL import Image

    client.post(
        "/auth/register",
        data={"username": "pixie", "display_name": "Pixie", "password": "pass123", "email": "pixie@gmail.com"},
        follow_redirects=True,
    )
    profile = client.get("/profile")
    assert profile.status_code == 200
    assert "avatar_file" in profile.text
    assert "ซูม" in profile.text

    buf = BytesIO()
    Image.new("RGB", (120, 80), (0, 82, 155)).save(buf, format="PNG")
    uploaded = client.post(
        "/profile",
        data={"zoom": "1.2", "offset_x": "0.1", "offset_y": "-0.1"},
        files={"avatar_file": ("face.png", buf.getvalue(), "image/png")},
        follow_redirects=False,
    )
    assert uploaded.status_code == 303

    avatar = client.get("/profile/avatar")
    assert avatar.status_code == 200
    assert avatar.headers["content-type"].startswith("image/")
    img = Image.open(BytesIO(avatar.content))
    assert img.size == (300, 300)

    dash = client.get("/dashboard")
    assert "/profile/avatar" in dash.text


def test_profile_saves_personal_details(client):
    client.post(
        "/auth/register",
        data={"username": "lina", "display_name": "Lina", "password": "pass123", "email": "lina@gmail.com"},
        follow_redirects=True,
    )
    page = client.get("/profile")
    assert page.status_code == 200
    assert "ข้อมูลส่วนตัว" in page.text
    assert 'name="gender"' in page.text
    assert 'name="birthday"' in page.text
    assert 'name="phone"' in page.text
    assert "avatar-camera-btn" in page.text

    saved = client.post(
        "/profile/details",
        data={
            "display_name": "Lina S",
            "gender": "female",
            "birthday": "1998-05-12",
            "phone": "081-234-5678",
        },
        follow_redirects=False,
    )
    assert saved.status_code == 303

    updated = client.get("/profile")
    html = updated.text
    assert "Lina S" in html
    assert "หญิง" in html
    assert "1998-05-12" in html
    assert "0812345678" in html
    assert "12 พ.ค. 1998" in html
    assert "บันทึกถาวร" in html

    locked = client.post(
        "/profile/details",
        data={
            "display_name": "Lina S",
            "gender": "male",
            "birthday": "2001-01-01",
            "phone": "0812345678",
        },
        follow_redirects=True,
    )
    assert "หญิง" in locked.text
    assert "1998-05-12" in locked.text
    assert "2001-01-01" not in locked.text
    assert "เพศถูกบันทึกถาวรแล้ว" in locked.text
    assert "วันเกิดถูกบันทึกถาวรแล้ว" in locked.text

    guest = client.post("/auth/logout")
    denied = client.post(
        "/profile/details",
        data={"display_name": "X", "gender": "male", "birthday": "2000-01-01", "phone": "0891112233"},
        follow_redirects=False,
    )
    assert denied.status_code in (303, 307)
    assert "/auth/login" in denied.headers.get("location", "")


def test_profile_monthly_name_and_phone_limits(client):
    client.post(
        "/auth/register",
        data={"username": "mina", "display_name": "Mina", "password": "pass123", "email": "mina@gmail.com"},
        follow_redirects=True,
    )
    first = client.post(
        "/profile/details",
        data={
            "display_name": "Mina One",
            "gender": "female",
            "birthday": "1999-03-03",
            "phone": "0891112233",
        },
        follow_redirects=True,
    )
    assert "Mina One" in first.text
    assert "0891112233" in first.text

    second_name = client.post(
        "/profile/details",
        data={
            "display_name": "Mina Two",
            "gender": "female",
            "birthday": "1999-03-03",
            "phone": "0891112233",
        },
        follow_redirects=True,
    )
    assert "Mina Two" in second_name.text

    third_name = client.post(
        "/profile/details",
        data={
            "display_name": "Mina Three",
            "gender": "female",
            "birthday": "1999-03-03",
            "phone": "0891112233",
        },
        follow_redirects=True,
    )
    assert "Mina Two" in third_name.text
    assert "Mina Three" not in third_name.text
    assert "ชื่อที่แสดงเปลี่ยนได้เพียง 2 ครั้งต่อเดือน" in third_name.text

    phone_one = client.post(
        "/profile/details",
        data={
            "display_name": "Mina Two",
            "gender": "female",
            "birthday": "1999-03-03",
            "phone": "0890001111",
        },
        follow_redirects=True,
    )
    assert "0890001111" in phone_one.text

    phone_two = client.post(
        "/profile/details",
        data={
            "display_name": "Mina Two",
            "gender": "female",
            "birthday": "1999-03-03",
            "phone": "0890002222",
        },
        follow_redirects=True,
    )
    assert "0890002222" in phone_two.text

    phone_three = client.post(
        "/profile/details",
        data={
            "display_name": "Mina Two",
            "gender": "female",
            "birthday": "1999-03-03",
            "phone": "0890003333",
        },
        follow_redirects=True,
    )
    assert "0890002222" in phone_three.text
    assert "0890003333" not in phone_three.text
    assert "เบอร์โทรเปลี่ยนได้เพียง 2 ครั้งต่อเดือน" in phone_three.text


def test_earned_achievements_show_after_name_and_on_avatar(client):
    client.post(
        "/auth/register",
        data={"username": "medalist", "display_name": "Medalist", "password": "pass123", "email": "medalist@gmail.com"},
        follow_redirects=True,
    )
    for lesson_id in (1, 2, 3):
        db_helper.mark_lesson_completed("medalist", lesson_id)

    profile = client.get("/profile")
    assert profile.status_code == 200
    html = profile.text
    pill_titles = re.findall(r'class="ach-pill" title="([^"]+)"', html)
    assert pill_titles
    assert all(title.startswith("เริ่มต้นได้ดี") for title in pill_titles)
    assert not any(title.startswith("ก้าวแรก") for title in pill_titles)
    assert "ก้าวแรก" in html
    assert "avatar-medal is-earned" in html or "is-earned" in html
    assert "avatar-medal-pin" in html
    assert "🥈" in html
    assert "is-admin-frame" not in html

    dash = client.get("/dashboard")
    dash_pills = re.findall(r'class="ach-pill" title="([^"]+)"', dash.text)
    assert dash_pills
    assert all(title.startswith("เริ่มต้นได้ดี") for title in dash_pills)
    assert "Hej Medalist" in dash.text

    empty_admin = client.get("/auth/login")
    assert empty_admin.status_code == 200
