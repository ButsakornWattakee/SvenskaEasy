# -*- coding: utf-8 -*-
import sys
import os
import db_helper

def extract_user_avatar(username):
    print(f"🔍 กำลังตรวจสอบข้อมูลผู้ใช้: {username}...")
    user_data = db_helper.get_user(username)
    
    if not user_data:
        print(f"❌ ไม่พบผู้ใช้ชื่อ '{username}' ในฐานข้อมูล")
        return
        
    avatar_bytes = user_data.get("avatar")
    if not avatar_bytes:
        print(f"ℹ️ ผู้ใช้ '{username}' ยังไม่ได้อัปโหลดรูปภาพโปรไฟล์ (ไม่มีฟิลด์ avatar หรือเป็นค่าว่าง)")
        return
        
    # Check what database mode we are using
    is_online = db_helper.is_mongodb_online()
    db_type = "MongoDB" if is_online else "Local JSON Fallback"
    print(f"📡 แหล่งข้อมูลปัจจุบัน: {db_type}")
    
    # Save the bytes to a local file
    output_filename = f"extracted_{username}_avatar.png"
    try:
        with open(output_filename, "wb") as f:
            f.write(avatar_bytes)
        print(f"✅ ดึงรูปภาพโปรไฟล์สำเร็จ!")
        # Print absolute path as clickable link
        abs_path = os.path.abspath(output_filename)
        print(f"📂 ไฟล์รูปภาพถูกเซฟไว้ที่: file:///{abs_path.replace(os.sep, '/')}")
        print("💡 คุณสามารถคลิกที่ลิงก์ด้านบนเพื่อเปิดดูรูปภาพโปรไฟล์จริงที่เก็บในฐานข้อมูลได้ทันที")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเขียนไฟล์รูปภาพ: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username_arg = sys.argv[1]
    else:
        # Prompt for username if not provided as argument
        print("--- โปรแกรมดึงรูปโปรไฟล์จากฐานข้อมูลเพื่อตรวจสอบ ---")
        username_arg = input("ระบุชื่อผู้ใช้ที่ต้องการดึงรูปภาพ (เช่น admin, ploy): ").strip()
        
    if username_arg:
        extract_user_avatar(username_arg)
    else:
        print("❌ กรุณาระบุชื่อผู้ใช้")
