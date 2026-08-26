# -*- coding: utf-8 -*-
import os
import re
from html import unescape

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-flash-lite-latest"
# 2.5/2.0 Flash are 404 for new Google AI Studio keys; 3-flash-preview is a 20/day free-tier trap.
UNAVAILABLE_MODELS = {
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
}
PREFERRED_MODELS = [
    DEFAULT_MODEL,
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-flash-latest",
]
_resolved_model_name = None


def _candidate_models() -> list[str]:
    names: list[str] = []
    env_model = (os.getenv("GEMINI_MODEL") or "").strip()
    if env_model and env_model not in UNAVAILABLE_MODELS and env_model not in names:
        names.append(env_model)
    for name in PREFERRED_MODELS:
        if name and name not in names and name not in UNAVAILABLE_MODELS:
            names.append(name)
    return names

SYSTEM_INSTRUCTION = """คุณเป็นครูสอนภาษาสวีเดนชาวสวีเดนผู้ใจดีและใจเย็น ที่พูดภาษาไทยได้คล่อง หน้าที่คือช่วยคนไทยเรียนคำศัพท์ ไวยากรณ์ การออกเสียง และฝึกบทสนทนา

จัดข้อความให้อ่านง่ายเสมอ:
- เปิดด้วยประโยคไทยสั้นๆ ไม่เกิน 2 บรรทัด ห้ามยัดทุกอย่างในย่อหน้าเดียว
- คำสวีเดนใส่ **ตัวหนา** เท่านั้น ห้ามตัวหนาคำไทย
- คำหรือประโยคตัวอย่างใช้บล็อกอ้างอิง 3 บรรทัดแบบนี้เป๊ะ (มีบรรทัดว่างก่อนและหลัง):

> **Hej**
> (เฮย์)
> สวัสดี

- รายการคำศัพท์ใช้ bullet:
- **röd** (เริด) — สีแดง
- ถ้าอธิบายไวยากรณ์ ให้แยกหัวข้อสั้นๆ แล้วตามด้วยตัวอย่าง 1 ก้อน
- ปิดด้วยคำถามชวนฝึก 1 ประโยค
- อย่าใช้ตารางเว้นแต่จำเป็นจริงๆ"""

MOCK_RESPONSES = [
    {
        "keywords": ["สวัสดี", "hej", "god morgon", "ทักทาย", "hello", "hi"],
        "reply": """คำทักทายที่ใช้บ่อยที่สุดในภาษาสวีเดนคือคำนี้ครับ

> **Hej**
> (เฮย์)
> สวัสดี

สระพิเศษที่ควรจำให้แม่น:

- **Å** (ออ)
- **Ä** (แอร์)
- **Ö** (เออ)

ลองทักครูว่า **Hej** ดูสิครับ มีอะไรอยากถามต่อไหม?""",
    },
    {
        "keywords": ["ชื่ออะไร", "heter", "ชื่อ", "name"],
        "reply": """เวลาอยากถามชื่อในภาษาสวีเดน ใช้ประโยคนี้ครับ

> **Vad heter du?**
> (ว็อด เฮีย-เตอร ดู)
> คุณชื่ออะไร?

เวลาตอบ ใส่ชื่อตัวเองต่อท้าย:

> **Jag heter …**
> (ย็อก เฮีย-เตอร …)
> ฉันชื่อ …

ลองแนะนำตัวกับครูเป็นภาษาสวีเดนดูสิครับ!""",
    },
    {
        "keywords": ["ตัวเลข", "นับเลข", "หนึ่ง", "สอง", "สาม", "1", "2", "3", "เลข", "number"],
        "reply": """ตัวเลข 1 ถึง 5 ในภาษาสวีเดนออกเสียงแบบนี้ครับ

- **en** (เอ็น) / **ett** (เอ็ต) — หนึ่ง (เลือกตามคำนาม)
- **två** (โว) — สอง
- **tre** (เทรีย) — สาม
- **fyra** (ฟิว-ระ) — สี่
- **fem** (เฟ็ม) — ห้า

ลองทายสิครับว่า **två** + **tre** เท่ากับอะไรในภาษาสวีเดน?""",
    },
    {
        "keywords": ["สี", "color", "röd", "blå", "แดง", "เหลือง", "น้ำเงิน"],
        "reply": """สีพื้นฐานที่เจอบ่อยในภาษาสวีเดนมีดังนี้ครับ

- **röd** (เริด) — สีแดง
- **blå** (บลอ) — สีน้ำเงิน / ฟ้า
- **gul** (กูล) — สีเหลือง
- **grön** (เกริน) — สีเขียว
- **vit** (วีท) — สีขาว

คุณชอบสีไหนเป็นพิเศษ? ลองตอบครูเป็นภาษาสวีเดนดูนะครับ""",
    },
    {
        "keywords": ["ไวยากรณ์", "grammar", "en", "ett", "เพศ", "คำนาม"],
        "reply": """คำนามสวีเดนแบ่งเป็น 2 กลุ่ม คือ **en** กับ **ett**

กลุ่ม **en**

> **en bok** → **boken**
> (เอน บุค → บุคเคน)
> หนังสือ → หนังสือเล่มนั้น

กลุ่ม **ett**

> **ett hus** → **huset**
> (เอ็ต ฮูส → ฮูเซ็ต)
> บ้าน → บ้านหลังนั้น

จำง่ายๆ ว่าคำนำหน้าจะย้ายไปต่อท้ายคำนามเมื่อชี้เฉพาะ ลองยกคำนามมาให้ครูช่วยจัดกลุ่มได้เลยครับ""",
    },
    {
        "keywords": ["ขอบคุณ", "tack", "thank"],
        "reply": """คำว่าขอบคุณในภาษาสวีเดนใช้บ่อยมากครับ

> **Tack så mycket!**
> (ทัก ซอ มึค-เคะ)
> ขอบคุณมากๆ

ถ้ามีคนขอบคุณเรา ตอบว่า:

> **Var så god**
> (วาร์ ซอ กูด)
> ด้วยความยินดี

ลองพิมพ์ **Tack** กลับมาหาครูดูสิครับ!""",
    },
    {
        "keywords": ["สบายดีไหม", "mår", "läget", "how are you"],
        "reply": """ถามว่าสบายดีไหมในภาษาสวีเดนมี 2 แบบที่ใช้บ่อยครับ

> **Hur mår du?**
> (ฮูร์ มอร์ ดู)
> คุณสบายดีไหม?

หรือแบบกันเอง:

> **Hur är läget?**
> (ฮูร์ แอ แลดเจ็ต)
> เป็นไงบ้าง?

คำตอบมาตรฐาน:

> **Jag mår bra, tack!**
> (ย็อก มอร์ บรา ทัก)
> ฉันสบายดี ขอบคุณครับ

วันนี้คุณมาร์บราไหมครับ?""",
    },
]

DEFAULT_FALLBACK = """Hej! ครูพร้อมตอบคำถามภาษาสวีเดนครับ

ตอนนี้อยู่โหมดจำลอง ลองถามเรื่องใดเรื่องหนึ่งได้เลย:

- คำทักทาย
- ตัวเลข
- สี
- ไวยากรณ์ **en** / **ett**

หรือไปตั้งค่า GEMINI_API_KEY ที่หน้าตั้งค่า เพื่อคุยกับครู AI จริงได้เลยครับ"""


def _plain_content(text: str) -> str:
    """Gemini history should be plain text, not chat HTML."""
    plain = re.sub(r"<br\s*/?>", "\n", text or "", flags=re.I)
    plain = re.sub(r"<[^>]+>", "", plain)
    return unescape(plain).strip()


def _format_gemini_history(chat_history):
    """Gemini requires history to start with a user turn and then alternate.

    The app always seeds chat with an assistant greeting, which the API rejects
    if it is sent as the first history item.
    """
    formatted = []
    prior_messages = chat_history[:-1] if chat_history else []
    for item in prior_messages:
        content = _plain_content(item.get("content") or "")
        if not content:
            continue
        role = "user" if item.get("role") == "user" else "model"
        if formatted and formatted[-1]["role"] == role:
            formatted[-1]["parts"][0] += "\n" + content
        else:
            formatted.append({"role": role, "parts": [content]})

    while formatted and formatted[0]["role"] == "model":
        formatted.pop(0)
    return formatted


def _error_text(error) -> str:
    return str(error or "").lower()


def _is_missing_model_error(error):
    text = _error_text(error)
    return (
        "404" in text
        or "not_found" in text
        or "not found" in text
        or "no longer available" in text
    )


def _is_quota_error(error):
    text = _error_text(error)
    return (
        "429" in text
        or "resource_exhausted" in text
        or "quota" in text
        or "rate limit" in text
        or "rate-limit" in text
    )


def _is_unavailable_error(error):
    text = _error_text(error)
    return "503" in text or "unavailable" in text or "high demand" in text


def _is_auth_error(error):
    text = _error_text(error)
    return (
        "api key not valid" in text
        or "api_key_invalid" in text
        or "invalid api key" in text
        or "permission_denied" in text
    )


def _is_timeout_error(error):
    text = _error_text(error)
    return "timeout" in text or "timed out" in text or "deadline" in text


def _should_try_next_model(error):
    if _is_auth_error(error):
        return False
    return (
        _is_quota_error(error)
        or _is_missing_model_error(error)
        or _is_unavailable_error(error)
        or _is_timeout_error(error)
    )


def _friendly_gemini_error(error) -> str:
    if _is_quota_error(error):
        return (
            "โควต้า Gemini ฟรีของโมเดลนี้เต็มแล้วครับ "
            "ครูสลับโมเดลให้แล้วยังใช้ต่อไม่ได้ในรอบนี้ "
            "รอสัก 1 นาทีแล้วลองใหม่ หรือรอโควต้ารีเซ็ตเที่ยงคืนเวลาแปซิฟิก "
            "(ดูโควต้าได้ที่ https://ai.dev/rate-limit)"
        )
    return (
        "เชื่อมต่อครู AI ไม่สำเร็จในตอนนี้ครับ\n\n"
        f"{error}\n\n"
        "ตรวจ GEMINI_API_KEY ที่ Railway Variables แล้ว Redeploy"
    )


def _send_with_model(client, model_name, history, message, system_instruction):
    contents = list(history or [])
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system_instruction),
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError(f"empty response from {model_name}")
    return text


def _history_as_contents(formatted_history):
    return [
        types.Content(role=item["role"], parts=[types.Part(text=item["parts"][0])])
        for item in formatted_history
    ]


def get_ai_response(user_prompt, chat_history=None, api_key=None, lesson_context=""):
    global _resolved_model_name

    if chat_history is None:
        chat_history = []

    message = user_prompt

    if api_key and len(api_key.strip()) > 10:
        client = genai.Client(
            api_key=api_key.strip(),
            http_options=types.HttpOptions(timeout=20_000),
        )
        history = _history_as_contents(_format_gemini_history(chat_history))
        system_instruction = SYSTEM_INSTRUCTION
        if lesson_context:
            system_instruction += f"\n\nบริบทบทเรียนปัจจุบันที่ผู้เรียนกำลังศึกษา: {lesson_context}"

        model_names = []
        if _resolved_model_name and _resolved_model_name not in UNAVAILABLE_MODELS:
            model_names.append(_resolved_model_name)
        for name in _candidate_models():
            if name not in model_names:
                model_names.append(name)

        last_error = None
        for model_name in model_names:
            try:
                text = _send_with_model(
                    client, model_name, history, message, system_instruction
                )
                _resolved_model_name = model_name
                return text
            except Exception as error:
                last_error = error
                if _should_try_next_model(error):
                    if _resolved_model_name == model_name:
                        _resolved_model_name = None
                    continue
                break

        return _friendly_gemini_error(last_error)

    message_lower = message.lower()
    for item in MOCK_RESPONSES:
        if any(kw in message_lower for kw in item["keywords"]):
            return item["reply"]

    return DEFAULT_FALLBACK
