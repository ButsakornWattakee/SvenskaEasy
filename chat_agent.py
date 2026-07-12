# -*- coding: utf-8 -*-
import google.generativeai as genai

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

DEFAULT_FALLBACK = "Hej! ครูยินดีตอบคำถามเกี่ยวกับภาษาชวีเดนครับ (ขณะนี้อยู่ใน Sandbox Mode ลองถามเรื่อง 'คำศัพท์ทักทาย', 'ตัวเลข', 'สี', 'ไวยากรณ์ En/Ett' หรือลองนำ Gemini API Key มาใส่ในเมนูตั้งค่าเพื่อคุยกับครูแบบ AI อัจฉริยะจริงๆ ได้เลยครับ!)"

def get_ai_response(api_key, message, chat_history):
    # If api_key is available, use Google Gemini
    if api_key and len(api_key.strip()) > 10:
        try:
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_INSTRUCTION)
            
            # Format history for Gemini API
            formatted_history = []
            for h in chat_history[:-1]:  # Exclude the current message
                formatted_history.append({
                    "role": "user" if h["role"] == "user" else "model",
                    "parts": [h["content"]]
                })
            
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(message)
            return response.text
        except Exception as e:
            return f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อกับ Gemini API: {str(e)}\n\n(คุณสามารถสลับไปรันในโหมดจำลองได้โดยลบ API Key ออก หรือตรวจสอบคีย์ของคุณอีกครั้ง)"
    
    # Sandbox/Mock Mode Fallback
    message_lower = message.lower()
    for item in MOCK_RESPONSES:
        if any(kw in message_lower for kw in item["keywords"]):
            return item["reply"]
            
    return DEFAULT_FALLBACK
