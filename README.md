# SvenskaEasy

แอพเรียนภาษาสวีเดนสำหรับคนไทย สร้างด้วย **FastAPI + Jinja2 + Tailwind CSS**

## สแต็กที่แนะนำ (และใช้อยู่ตอนนี้)

| ชั้น | เทคโนโลยี | เหตุผล |
| --- | --- | --- |
| Backend | FastAPI | เร็ว, session + ฟอร์ม + JSON API สำหรับครู AI |
| Templates | Jinja2 | เนื้อหาบทเรียนเป็น Python data อยู่แล้ว ไม่ต้องย้ายไป SPA |
| UI | Tailwind CSS | ดีไซน์ทันสมัย ปรับ responsive ได้ง่าย |
| ข้อมูลผู้ใช้ | MongoDB + JSON fallback | ทำงานได้แม้ฐานข้อมูลออฟไลน์ |
| ทดสอบ | pytest + TestClient | ครอบคลุมหน้าเว็บ ควิซ และครู AI |

## ฟีเจอร์

- บทเรียน 25 บท (Beginner → Intermediate) พร้อมคำอธิบายภาษาไทย
- ฝึกพิมพ์ / เกมจับคู่คำศัพท์
- ควิซรายบท และข้อสอบวัดผลรวม
- คลังคำศัพท์ + แฟลชการ์ด
- ครู AI (Gemini หรือโหมดจำลอง)
- โปรไฟล์ เหรียญรางวัล แผงแอดมิน

## ติดตั้งและรัน

```bash
pip install -r requirements.txt
```

สร้างไฟล์ `.env` (ไม่บังคับ):

```
SECRET_KEY=change-me
GEMINI_API_KEY=your_key_here
```

รันเซิร์ฟเวอร์:

```bash
py -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

เปิด http://127.0.0.1:8000

บัญชีเริ่มต้นเมื่อใช้ไฟล์สำรอง: `admin` / `admin`

## ทดสอบ

```bash
py -m pytest
```
