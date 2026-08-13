# -*- coding: utf-8 -*-
import os
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3-flash-preview"
CANDIDATE_MODELS = [
    os.getenv("GEMINI_MODEL", "").strip(),
    DEFAULT_MODEL,
    "gemini-3.1-flash-lite",
]
CANDIDATE_MODELS = [name for name in CANDIDATE_MODELS if name]
_resolved_model_name = None

SYSTEM_INSTRUCTION = """คุณเป็นครูสอนภาษาชวีเดนชาวสวีเดนผู้ใจดีและใจเย็นที่พูดภาษาไทยได้คล่องแคล่วและเป็นธรรมชาติ หน้าที่ของคุณคือช่วยคนไทยเรียนรู้ภาษาชวีเดน ตอบคำถามของนักเรียนเกี่ยวกับคำศัพท์ ไวยากรณ์ การออกเสียง หรือช่วยพวกเขาฝึกบทสนทนาโต้ตอบ
แนวทางการตอบคำถาม:
1. อธิบายไวยากรณ์หรือคำศัพท์เป็นภาษาไทยอย่างสั้นกระชับเข้าใจง่าย
2. เสนอประโยคตัวอย่างภาษาสวีเดน คำอ่านภาษาไทยในวงเล็บ และคำแปลภาษาไทยเสมอ
3. หากนักเรียนพูดภาษาสวีเดนมา ให้ช่วยตรวจทานความถูกต้อง แนะนำข้อบกพร่องด้วยความสุภาพ และแก้ไขให้ถูกต้อง
4. ให้กำลังใจและชื่นชมความพยายามในการเรียนรู้ของนักเรียนเสมอ"""

MOCK_RESPONSES = [
    {
        "keywords": ["สวัสดี", "hej", "god morgon", "ทักทาย", "hello", "hi"],
        "reply": "Hej! ยินดีต้อนรับสู่บทเรียนภาษาชวีเดนครับ! สระชวีเดนที่ควรจำให้แม่นคือ Å (ออ), Ä (แอร์), และ Ö (เออ) ลองพูดคำว่า **Hej** (เฮย์) ที่แปลว่าสวัสดีดูสิครับ มีอะไรอยากให้ครูอธิบายเพิ่มไหม?"
    },
    {
        "keywords": ["ชื่ออะไร", "heter", "ชื่อ", "name"],
        "reply": "ในภาษาสวีเดน หากต้องการถามว่าคุณชื่ออะไร จะพูดว่า **Vad heter du?** (ว็อด เฮีย-เตอร ดู) และตอบว่า **Jag heter [ชื่อของคุณ]** (ย็อก เฮีย-เตอร...) ลองแนะนำตัวกับครูเป็นภาษาสวีเดนดูสิครับ!"
    },
    {
        "keywords": ["ตัวเลข", "นับเลข", "หนึ่ง", "สอง", "สาม", "1", "2", "3", "เลข", "number"],
        "reply": "ตัวเลข 1 ถึง 5 ในภาษาสวีเดนเขียนและออกเสียงดังนี้ครับ:\n* 1 = **en** (เอ็น) หรือ **ett** (เอ็ต) *(ขึ้นกับคำนาม)*\n* 2 = **två** (โว)\n* 3 = **tre** (เทรีย)\n* 4 = **fyra** (ฟิว-ระ)\n* 5 = **fem** (เฟ็ม)\nลองทายดูเล่นๆ สิครับว่า **två + tre** จะได้เท่าไหร่ในภาษาสวีเดน?"
    },
    {
        "keywords": ["สี", "color", "röd", "blå", "แดง", "เหลือง", "น้ำเงิน"],
        "reply": "สีสันที่ใช้บ่อยในภาษาสวีเดน เช่น:\n* **röd** (เริด) = สีแดง\n* **blå** (บลอ) = สีน้ำเงิน/ฟ้า\n* **gul** (กูล) = สีเหลือง\n* **grön** (เกริน) = สีเขียว\n* **vit** (วีท) = สีขาว\nคุณชอบสีไหนเป็นพิเศษไหมครับ? ลองเขียนตอบครูเป็นภาษาสวีเดนดูนะ!"
    },
    {
        "keywords": ["ไวยากรณ์", "grammar", "en", "ett", "เพศ", "คำนาม"],
        "reply": "ไวยากรณ์สวีเดนมีจุดเด่นคือคำนามมี 2 กลุ่ม คือ **En** (เช่น en bok - หนังสือ) และ **Ett** (เช่น ett hus - บ้าน) เวลาทำให้เป็นรูปชี้เฉพาะเจาะจง ให้สลับคำกลุ่มนี้ไปต่อท้ายคำนาม เช่น en bok -> **boken** (หนังสือเล่มนั้น) หรือ ett hus -> **huset** (บ้านหลังนั้น) เข้าใจง่ายใช่ไหมครับ?"
    },
    {
        "keywords": ["ขอบคุณ", "tack", "thank"],
        "reply": "**Tack så mycket!** (ทัก ซอ มึค-เคะ) แปลว่าขอบคุณมากๆ ครับ! และถ้ามีคนขอบคุณเรา เราจะตอบว่า **Var så god** (วาร์ ซอ กูด) แปลว่าด้วยความยินดีครับ!"
    },
    {
        "keywords": ["สบายดีไหม", "mår", "läget", "how are you"],
        "reply": "สบายดีครับ! ในภาษาสวีเดนจะถามว่า **Hur mår du?** (ฮูร์ มอร์ ดู) หรือ **Hur är läget?** (ฮูร์ แอ แลดเจ็ต) และมักจะตอบว่า **Jag mår bra, tack!** (ย็อก มอร์ บรา, ทัก!) แปลว่าฉันสบายดี ขอบคุณครับ"
    }
]

DEFAULT_FALLBACK = "Hej! ครูยินดีตอบคำถามเกี่ยวกับภาษาชวีเดนครับ (ขณะนี้อยู่ใน Sandbox Mode ลองถามเรื่อง 'คำศัพท์ทักทาย', 'ตัวเลข', 'สี', 'ไวยากรณ์ En/Ett' หรือตั้งค่า GEMINI_API_KEY เพื่อคุยกับครูแบบ AI อัจฉริยะจริงๆ ได้เลยครับ!)"


def _format_gemini_history(chat_history):
    """Gemini requires history to start with a user turn and then alternate.

    The app always seeds chat with an assistant greeting, which the API rejects
    if it is sent as the first history item.
    """
    formatted = []
    prior_messages = chat_history[:-1] if chat_history else []
    for item in prior_messages:
        content = (item.get("content") or "").strip()
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


def _is_missing_model_error(error):
    text = str(error).lower()
    return "404" in text or "not found" in text or "is not supported" in text


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
        client = genai.Client(api_key=api_key.strip())
        history = _history_as_contents(_format_gemini_history(chat_history))
        system_instruction = SYSTEM_INSTRUCTION
        if lesson_context:
            system_instruction += f"\n\nบริบทบทเรียนปัจจุบันที่ผู้เรียนกำลังศึกษา: {lesson_context}"

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        )
        model_names = []
        if _resolved_model_name:
            model_names.append(_resolved_model_name)
        for name in CANDIDATE_MODELS:
            if name not in model_names:
                model_names.append(name)

        last_error = None
        for model_name in model_names:
            try:
                chat = client.chats.create(
                    model=model_name,
                    history=history,
                    config=config,
                )
                response = chat.send_message(message)
                _resolved_model_name = model_name
                return response.text
            except Exception as error:
                last_error = error
                if not _is_missing_model_error(error):
                    break

        return (
            " เกิดข้อผิดพลาดในการเชื่อมต่อกับ Gemini API: "
            f"{last_error}\n\n"
            "(ตรวจสอบ GEMINI_API_KEY ในไฟล์ .env หรือ Streamlit secrets แล้วรีสตาร์ทแอป)"
        )

    message_lower = message.lower()
    for item in MOCK_RESPONSES:
        if any(kw in message_lower for kw in item["keywords"]):
            return item["reply"]

    return DEFAULT_FALLBACK
