# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="SvenskaEasy - เว็บไซต์การเรียนภาษาสวีเดนง่ายๆ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import local modules
import importlib
import lessons_data
import css_styles
import chat_agent
import vocabulary_data
import db_helper

# Force reload local modules on each rerun to ensure edits are applied immediately
importlib.reload(lessons_data)
importlib.reload(css_styles)
importlib.reload(chat_agent)
importlib.reload(vocabulary_data)
importlib.reload(db_helper)

# Initialize database
db_helper.init_db()

def get_all_vocabulary():
    # Start with our curated vocabulary list
    vocab_list = list(vocabulary_data.VOCABULARY)
    existing_swedish_words = set(item["swedish"].lower().strip() for item in vocab_list)
    
    # Map levels of lessons to Thai level labels
    for lesson in lessons_data.LESSONS:
        l_level = lesson.get("level", "Beginner")
        l_level_th = "ง่าย"
        if l_level == "Elementary":
            l_level_th = "กลาง"
        elif l_level == "Intermediate":
            l_level_th = "ยาก"
            
        l_cat = lesson["title"].split(" : ")[-1] if " : " in lesson["title"] else "ทั่วไป"
        
        # Extract from typing_practice
        if "typing_practice" in lesson:
            for tp in lesson["typing_practice"]:
                sw = tp["swedish"].strip()
                if sw.lower() not in existing_swedish_words:
                    thai_clean = tp["thai"]
                    if " (" in thai_clean:
                        thai_clean = thai_clean.split(" (")[0]
                    
                    # Try to parse pronunciation clue or use Swedish word as fallback
                    clue = tp.get("clue", sw)
                    
                    vocab_list.append({
                        "swedish": sw,
                        "pronunciation": clue,
                        "thai": thai_clean,
                        "pos": "คำศัพท์แบบฝึกเขียน",
                        "level": l_level_th,
                        "category": l_cat,
                        "example_swedish": f"{sw.capitalize()}.",
                        "example_thai": tp.get("explanation", f"{sw} แปลว่า {thai_clean}")
                    })
                    existing_swedish_words.add(sw.lower())
                    
        # Extract from matching_practice
        if "matching_practice" in lesson:
            for mp in lesson["matching_practice"]:
                sw = mp["swedish"].strip()
                if sw.lower() not in existing_swedish_words:
                    thai_clean = mp["thai"]
                    if " (" in thai_clean:
                        thai_clean = thai_clean.split(" (")[0]
                    
                    vocab_list.append({
                        "swedish": sw,
                        "pronunciation": sw,
                        "thai": thai_clean,
                        "pos": "คำศัพท์แบบฝึกคู่",
                        "level": l_level_th,
                        "category": l_cat,
                        "example_swedish": f"{sw.capitalize()}.",
                        "example_thai": f"คำศัพท์หมวด {l_cat}"
                    })
                    existing_swedish_words.add(sw.lower())
                    
    # Sort the final vocabulary list alphabetically by Swedish spelling
    return sorted(vocab_list, key=lambda x: x["swedish"].lower())

# Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "completed_lessons" not in st.session_state:
    st.session_state.completed_lessons = set()
if "quiz_scores" not in st.session_state:
    st.session_state.quiz_scores = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hej! ยินดีต้อนรับสู่ห้องเรียนภาษาสวีเดนครับ ผมคือครู AI ส่วนตัวของคุณ คุณสามารถถามคำถามเกี่ยวกับไวยากรณ์ คำศัพท์ การออกเสียง หรือลองพิมพ์สนทนาภาษาสวีเดนกับผมได้เลยครับ!"}
    ]
if "api_key" not in st.session_state:
    # Try loading from environment variable first
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")
if "active_lesson_id" not in st.session_state:
    st.session_state.active_lesson_id = 1

# Inject Custom CSS
st.markdown(css_styles.get_custom_css(), unsafe_allow_html=True)

# Login flow
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Elegant Header Card with Swedish theme
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #004B87 0%, #002B5C 100%); 
                        color: white; 
                        padding: 35px 25px; 
                        border-radius: 16px 16px 0 0; 
                        text-align: center; 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2); 
                        border-bottom: 5px solid #FFCD00;">
                <h1 style="margin: 0; font-size: 2.8rem; font-weight: 800; color: #ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🇸🇪 SvenskaEasy</h1>
                <p style="margin: 8px 0 0 0; font-size: 1.25rem; color: #e2e8f0; opacity: 0.9;">เว็บไซต์การเรียนภาษาสวีเดนง่ายๆ</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Form Container
        with st.container(border=True):
            tab_login, tab_register = st.tabs(["🔐 เข้าสู่ระบบ (Login)", "📝 สมัครสมาชิก (Sign Up)"])
            
            with tab_login:
                with st.form("login_form"):
                    st.markdown("<h4 style='margin-bottom: 10px; font-weight: 500;'>เข้าสู่ระบบผู้เรียน</h4>", unsafe_allow_html=True)
                    username = st.text_input("ชื่อผู้ใช้ (Username)", placeholder="กรอกชื่อผู้ใช้ เช่น admin", key="login_username")
                    password = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="กรอกรหัสผ่าน", key="login_password")
                    submit = st.form_submit_button("เข้าสู่ระบบ (Sign In)", use_container_width=True)
                    
                    if submit:
                        username_clean = username.strip()
                        if not username_clean:
                            st.error("กรุณาระบุชื่อผู้ใช้")
                        else:
                            user_data = db_helper.get_user(username_clean)
                            if user_data and user_data.get("password") == password:
                                st.session_state.logged_in = True
                                st.session_state.current_user = username_clean
                                st.session_state.completed_lessons = set(user_data.get("completed_lessons", []))
                                st.session_state.quiz_scores = {str(k): v for k, v in user_data.get("quiz_scores", {}).items()}
                                st.success("เข้าสู่ระบบสำเร็จ!")
                                st.rerun()
                            else:
                                st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
                            
            with tab_register:
                with st.form("register_form"):
                    st.markdown("<h4 style='margin-bottom: 10px; font-weight: 500;'>สร้างบัญชีผู้เรียนใหม่</h4>", unsafe_allow_html=True)
                    reg_username = st.text_input("ชื่อผู้ใช้ใหม่ (New Username)", placeholder="ตัวอักษรภาษาอังกฤษหรือตัวเลข", key="reg_username")
                    reg_email = st.text_input("อีเมล (Email)", placeholder="กรอกอีเมล เช่น user@example.com", key="reg_email")
                    reg_password = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="รหัสผ่านอย่างน้อย 4 ตัวอักษร", key="reg_password")
                    reg_password_confirm = st.text_input("ยืนยันรหัสผ่าน (Confirm Password)", type="password", placeholder="กรอกรหัสผ่านอีกครั้ง", key="reg_password_confirm")
                    submit_reg = st.form_submit_button("สมัครสมาชิก (Sign Up)", use_container_width=True)
                    
                    if submit_reg:
                        new_user = reg_username.strip()
                        new_email = reg_email.strip()
                        new_pass = reg_password
                        new_pass_confirm = reg_password_confirm
                        
                        if not new_user:
                            st.error("กรุณาระบุชื่อผู้ใช้")
                        elif len(new_user) < 3:
                            st.error("ชื่อผู้ใช้ต้องมีความยาวอย่างน้อย 3 ตัวอักษร")
                        elif not new_email or "@" not in new_email or "." not in new_email:
                            st.error("กรุณาระบุอีเมลที่ถูกต้อง")
                        elif len(new_pass) < 4:
                            st.error("รหัสผ่านต้องมีความยาวอย่างน้อย 4 ตัวอักษร")
                        elif new_pass != new_pass_confirm:
                            st.error("รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน")
                        else:
                            success, msg = db_helper.create_user(new_user, new_email, new_pass)
                            if success:
                                st.success("สมัครสมาชิกสำเร็จ! กรุณาสลับไปที่แท็บ 'เข้าสู่ระบบ' เพื่อลงชื่อเข้าใช้งาน")
                            else:
                                st.error(msg)
                            
        st.markdown("<div style='text-align: center; margin-top: 20px; opacity: 0.6; font-size: 0.9rem;'>พัฒนาขึ้นเพื่อช่วยให้คนไทยเข้าใจภาษาสวีเดนได้ง่ายขึ้น</div>", unsafe_allow_html=True)
    st.stop()


# Define navigation links
PAGES = ["Dashboard", "บทเรียนทั้งหมด", "คลังคำศัพท์", "แบบฝึกหัดและควิซ", "คุยกับครู AI", "ตั้งค่าระบบ"]

# Sidebar Navigation
with st.sidebar:
    st.markdown('<div class="sidebar-title"><h1>SvenskaEasy</h1><p>เว็บไซต์การเรียนภาษาสวีเดนง่ายๆ</p></div>', unsafe_allow_html=True)
    
    # Beautiful Swedish Flag banner in HTML
    st.markdown(
        """
        <div style="background-color: #004B87; height: 12px; border-radius: 4px 4px 0 0; position: relative; margin-bottom: 20px;">
            <div style="background-color: #FFCD00; width: 12px; height: 100%; position: absolute; left: 30px;"></div>
            <div style="background-color: #FFCD00; width: 100%; height: 3px; position: absolute; top: 4px;"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Radio navigation styled as menu
    if st.session_state.current_page not in PAGES:
        st.session_state.current_page = PAGES[0]
    selected_page = st.radio("เลือกหน้าต่างใช้งาน:", PAGES, index=PAGES.index(st.session_state.current_page))
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()
        
    st.markdown("---")
    
    # Progress Section
    st.markdown("### ความก้าวหน้าของคุณ (Your Progress)")
    total_lessons = len(lessons_data.LESSONS)
    completed_count = len(st.session_state.completed_lessons)
    progress_percentage = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 0
    
    st.progress(progress_percentage / 100)
    st.write(f"เรียนเสร็จแล้ว {completed_count} จากทั้งหมด {total_lessons} บทเรียน ({progress_percentage}%)")
    
    st.markdown("---")
    
    # Connection status indicator
    if st.session_state.api_key and len(st.session_state.api_key.strip()) > 10:
        st.success("AI Tutor Active (Gemini API)")
    else:
        st.info("Sandbox Mode (โหมดจำลองคำตอบ)")
        
    st.caption("จัดทำขึ้นเพื่อช่วยให้คนไทยเข้าใจภาษาชวีเดนได้ง่ายขึ้น")
    
    st.markdown("---")
    if st.button("ออกจากระบบ (Logout)", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.completed_lessons = set()
        st.session_state.quiz_scores = {}
        st.rerun()

# ----------------- 1. DASHBOARD PAGE -----------------
if st.session_state.current_page == "Dashboard":
    st.markdown("# แดชบอร์ดผู้เรียน (Välkommen!)")
    st.markdown("ยินดีต้อนรับสู่ห้องเรียนภาษาสวีเดนแบบโต้ตอบ ที่นี่คุณจะได้เรียนรู้ทักษะที่จำเป็นและมีครู AI คอยให้ความช่วยเหลือตลอดเวลา")
    
    # Metric Summary Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <span class="sweden-badge">บทเรียน</span>
                <h2 style='margin:10px 0;'>{completed_count} / {total_lessons}</h2>
                <p style='margin:0; opacity: 0.8;'>บทเรียนที่เรียนสำเร็จแล้ว</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    with col2:
        average_score = 0
        if st.session_state.quiz_scores:
            average_score = int(sum(st.session_state.quiz_scores.values()) / len(st.session_state.quiz_scores))
        st.markdown(
            f"""
            <div class="dashboard-card">
                <span class="sweden-badge" style="background-color: #FFCD00; color: #004B87;">คะแนนรวม</span>
                <h2 style='margin:10px 0;'>{average_score}%</h2>
                <p style='margin:0; opacity: 0.8;'>คะแนนเฉลี่ยจากการทำควิซ</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    with col3:
        status_text = "พร้อมตอบคำถาม" if st.session_state.api_key else "โหมดจำลองแอคทีฟ"
        color_badge = "#004B87" if st.session_state.api_key else "#6C757D"
        st.markdown(
            f"""
            <div class="dashboard-card">
                <span class="sweden-badge" style="background-color: {color_badge}; color: white;">สถานะครู AI</span>
                <h2 style='margin:10px 0;'>{status_text}</h2>
                <p style='margin:0; opacity: 0.8;'>แชทบอทช่วยเรียนภาษาสวีเดน</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    st.markdown("### แผนการเรียนรู้ของคุณ (Your Learning Roadmap)")
    
    # We will display lessons grouped by levels: Beginner, Elementary, Intermediate
    levels = ["Beginner", "Elementary", "Intermediate"]
    level_titles_th = {
        "Beginner": "ระดับ Beginner (พื้นฐานเริ่มต้น)",
        "Elementary": "ระดับ Elementary (ระดับพื้นฐาน)",
        "Intermediate": "ระดับ Intermediate (ระดับกลาง)"
    }
    
    for lvl in levels:
        st.markdown(f"### {level_titles_th[lvl]}")
        lvl_lessons = [l for l in lessons_data.LESSONS if l["level"] == lvl]
        
        for lesson in lvl_lessons:
            l_id = lesson["id"]
            is_completed = l_id in st.session_state.completed_lessons
            status_symbol = "✅" if is_completed else "📖"
            
            col_icon, col_text = st.columns([1, 10])
            with col_icon:
                st.markdown(f"<h3 style='margin-top: 5px; text-align: center;'>{status_symbol}</h3>", unsafe_allow_html=True)
            with col_text:
                if st.button(lesson["title"], key=f"dash_lesson_{l_id}", use_container_width=True):
                    st.session_state.active_lesson_id = l_id
                    st.session_state.current_page = "บทเรียนทั้งหมด"
                    st.rerun()
                st.markdown(f"<p style='margin:-12px 0 12px 0; font-size:0.95rem; opacity:0.8;'>{lesson['description']}</p>", unsafe_allow_html=True)

# ----------------- 2. LESSONS PAGE -----------------
elif st.session_state.current_page == "บทเรียนทั้งหมด":
    st.markdown("# บทเรียนภาษาชวีเดน (Svenska lektioner)")
    
    # Find current active lesson
    active_lesson = next((l for l in lessons_data.LESSONS if l["id"] == st.session_state.active_lesson_id), lessons_data.LESSONS[0])
    
    # Map current lesson's level code to name
    level_names = {
        "Beginner": "ง่าย (Beginner)",
        "Elementary": "กลาง (Elementary)",
        "Intermediate": "ยาก (Intermediate)"
    }
    current_level_name = level_names[active_lesson["level"]]
    
    # Select level
    selected_level_name = st.radio(
        "เลือกระดับบทเรียน (Select Level):",
        ["ง่าย (Beginner)", "กลาง (Elementary)", "ยาก (Intermediate)"],
        index=["ง่าย (Beginner)", "กลาง (Elementary)", "ยาก (Intermediate)"].index(current_level_name),
        horizontal=True
    )
    
    # Map back to code
    level_code_map = {
        "ง่าย (Beginner)": "Beginner",
        "กลาง (Elementary)": "Elementary",
        "ยาก (Intermediate)": "Intermediate"
    }
    chosen_level_code = level_code_map[selected_level_name]
    
    # If the user changed the level manually, select the first lesson of that level
    if chosen_level_code != active_lesson["level"]:
        first_lesson_of_level = next((l for l in lessons_data.LESSONS if l["level"] == chosen_level_code), None)
        if first_lesson_of_level:
            st.session_state.active_lesson_id = first_lesson_of_level["id"]
            active_lesson = first_lesson_of_level
            
    # Filter lessons for selected level
    filtered_lessons = [l for l in lessons_data.LESSONS if l["level"] == chosen_level_code]
    filtered_ids = [l["id"] for l in filtered_lessons]
    
    # Find active index in filtered list
    active_filtered_idx = filtered_ids.index(st.session_state.active_lesson_id)
    
    # Selectbox for lessons in this level
    selected_lesson = st.selectbox(
        "เลือกบทเรียนที่ต้องการเรียนรู้:",
        filtered_lessons,
        format_func=lambda x: x["title"],
        index=active_filtered_idx
    )
    st.session_state.active_lesson_id = selected_lesson["id"]
    lesson = selected_lesson
    l_id = lesson["id"]
    
    # Beautiful Header Banner
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #004B87 0%, #005ea8 100%); color: white; padding: 30px; border-radius: 16px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); border-left: 6px solid #FFCD00;">
            <span style="background-color: #FFCD00; color: #004B87; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; text-transform: uppercase;">LEKTION {l_id}</span>
            <h2 style="margin: 10px 0 5px 0; color: #ffffff; font-weight: 700; font-family: 'Outfit', 'Kanit', sans-serif; border: none;">{lesson['title']}</h2>
            <p style="margin: 0; color: #e2e8f0; font-size: 1.1rem; font-style: italic;">{lesson['description']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display the content sections of the selected lesson inside borders
    for sec in lesson["sections"]:
        with st.container(border=True):
            st.markdown(f"### 📖 {sec['subtitle']}")
            st.markdown(sec["content"])
            st.markdown(" ")
        
    st.markdown("---")
    
    # Lesson completion controls
    col_mark, col_next = st.columns([1, 1])
    
    with col_mark:
        is_completed = l_id in st.session_state.completed_lessons
        if is_completed:
            st.success("คุณเรียนจบบทนี้แล้ว!")
        else:
            if st.button("เรียนเสร็จสิ้นแล้ว! (Mark as Completed)", key=f"mark_comp_{l_id}"):
                st.session_state.completed_lessons.add(l_id)
                db_helper.update_user_progress(st.session_state.current_user, st.session_state.completed_lessons)
                st.success("เยี่ยมมาก! ระบบบันทึกความก้าวหน้าของคุณเรียบร้อยแล้ว ลองไปทำแบบฝึกหัดเพื่อทดสอบความรู้กันเถอะ!")
                st.rerun()
                
    with col_next:
        all_ids = [l["id"] for l in lessons_data.LESSONS]
        curr_overall_idx = all_ids.index(st.session_state.active_lesson_id)
        if curr_overall_idx < len(lessons_data.LESSONS) - 1:
            if st.button("ถัดไป (Next Lesson)"):
                st.session_state.active_lesson_id = lessons_data.LESSONS[curr_overall_idx + 1]["id"]
                st.rerun()
        else:
            if st.button("กลับไปยังแดชบอร์ด"):
                st.session_state.current_page = "Dashboard"
                st.rerun()

# ----------------- 2.5 VOCABULARY PAGE -----------------
elif st.session_state.current_page == "คลังคำศัพท์":
    st.markdown("# คลังคำศัพท์ภาษาสวีเดน (Ordbok)")
    st.markdown("ค้นหาคำเขียน คำอ่าน และความหมายของคำศัพท์ภาษาสวีเดนพื้นฐานที่จำเป็น พร้อมตัวอย่างประโยคการใช้งาน")
    
    # Search Box
    search_query = st.text_input(
        "ค้นหาคำศัพท์ (พิมพ์คำเขียน คำอ่านภาษาไทย หรือคำแปลภาษาไทย):",
        placeholder="เช่น hej, สวัสดี, พยาบาล, วี เซส..."
    ).strip().lower()
    
    # Get all compiled vocabulary
    all_vocab_list = get_all_vocabulary()
    
    # Get all unique values for POS and Category to build filters
    pos_types = sorted(list(set(item["pos"] for item in all_vocab_list)))
    categories = sorted(list(set(item["category"] for item in all_vocab_list)))
    
    # Filter Row
    col_level, col_pos, col_cat = st.columns(3)
    with col_level:
        filter_level = st.selectbox("กรองระดับความยาก (Level):", ["ทั้งหมด", "ง่าย", "กลาง", "ยาก"])
    with col_pos:
        filter_pos = st.selectbox("กรองประเภทของคำ (Part of Speech):", ["ทั้งหมด"] + pos_types)
    with col_cat:
        filter_cat = st.selectbox("กรองหมวดหมู่คำศัพท์ (Category):", ["ทั้งหมด"] + categories)
        
    # Search & Filter Logic
    filtered_vocab = []
    for item in all_vocab_list:
        # Match level
        if filter_level != "ทั้งหมด" and item["level"] != filter_level:
            continue
        # Match POS
        if filter_pos != "ทั้งหมด" and item["pos"] != filter_pos:
            continue
        # Match Category
        if filter_cat != "ทั้งหมด" and item["category"] != filter_cat:
            continue
            
        # Match Search Query
        if search_query:
            match_swedish = search_query in item["swedish"].lower()
            match_pron = search_query in item["pronunciation"].lower()
            match_thai = search_query in item["thai"].lower()
            if not (match_swedish or match_pron or match_thai):
                continue
                
        filtered_vocab.append(item)
        
    # Display Results count
    st.markdown(f"**พบคำศัพท์ทั้งหมด {len(filtered_vocab)} คำ**")
    st.markdown("---")
    
    if not filtered_vocab:
        st.info("ไม่พบคำศัพท์ที่ตรงกับการค้นหาและตัวกรองของคุณ ลองเปลี่ยนคำค้นหาหรือตั้งค่าตัวกรองเป็น 'ทั้งหมด' นะครับ")
    else:
        # Display as cards
        for vocab in filtered_vocab:
            # We can wrap it in a container
            with st.container():
                st.markdown(
                    f"""
                    <div class="lesson-section" style="margin-bottom: 15px; border-left: 5px solid #FFCD00 !important;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 1.6rem; font-weight: bold;">{vocab['swedish']}</span>
                            <div>
                                <span class="sweden-badge" style="font-size: 0.75rem; padding: 2px 8px; margin-right: 5px;">{vocab['level']}</span>
                                <span class="thai-badge" style="font-size: 0.75rem; padding: 2px 8px; background-color: #004B87 !important; color: #FFCD00 !important;">{vocab['pos']}</span>
                            </div>
                        </div>
                        <p style="margin: 2px 0;">📂 <b>หมวดหมู่:</b> {vocab['category']}</p>
                        <p style="margin: 2px 0; font-size: 1.1rem;">🗣️ <b>คำอ่านภาษาไทย:</b> <span style="background-color: rgba(255,205,0,0.1); padding: 2px 6px; border-radius: 4px; color: #FFCD00; font-weight: 500;">{vocab['pronunciation']}</span></p>
                        <p style="margin: 2px 0; font-size: 1.2rem;">📝 <b>คำแปล:</b> <b>{vocab['thai']}</b></p>
                        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.05); font-style: italic;">
                            <p style="margin: 2px 0; color: #a1a1aa;">💬 <b>ตัวอย่างประโยค:</b></p>
                            <p style="margin: 2px 0; font-size: 1.05rem;">🇸🇪 {vocab['example_swedish']}</p>
                            <p style="margin: 2px 0; color: #cbd5e1;">🇹🇭 {vocab['example_thai']}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# ----------------- 3. QUIZZES PAGE -----------------
elif st.session_state.current_page == "แบบฝึกหัดและควิซ":
    st.markdown("# แบบฝึกหัดทดสอบความรู้ (Quiz & Övningar)")
    st.markdown("ทำควิซเพื่อทบทวนทักษะของคุณ หลังเรียนจบบทเรียนสลัดควิซเพื่อปลดล็อคบทเรียนถัดไปให้ดียิ่งขึ้น")
    
    if "active_quiz_tab" not in st.session_state:
        st.session_state.active_quiz_tab = 0
        
    lesson_titles = [lesson["title"] for lesson in lessons_data.LESSONS]
    
    selected_quiz_idx = st.selectbox(
        "เลือกควิซจากบทเรียนที่ต้องการทดสอบ:",
        range(len(lesson_titles)),
        format_func=lambda x: f"แบบฝึกหัดสำหรับ: {lesson_titles[x]}",
        index=st.session_state.active_quiz_tab
    )
    st.session_state.active_quiz_tab = selected_quiz_idx
    
    lesson = lessons_data.LESSONS[selected_quiz_idx]
    l_id = lesson["id"]
    
    tab_choice, tab_type, tab_match = st.tabs([
        "แบบทดสอบปรนัย (Multiple Choice)", 
        "แบบทดสอบการพิมพ์ (Typing Practice)", 
        "เกมจับคู่ภาพและคำ (Image Matching)"
    ])
    
    with tab_choice:
        st.markdown(f"### แบบทดสอบแบบเลือกตอบ: {lesson['title']}")
        # Create key based on quiz selection to clean inputs on change
        form_key = f"quiz_form_{l_id}"
        
        with st.form(key=form_key):
            user_selections = []
            for i, q in enumerate(lesson["quiz"]):
                st.markdown(f"**ข้อที่ {i+1}: {q['question']}**")
                
                # Using unique keys for widget persistence
                user_ans = st.radio(
                    "เลือกข้อที่ถูกต้องที่สุด:",
                    q["options"],
                    key=f"q_{l_id}_{i}"
                )
                user_selections.append(user_ans)
                st.markdown(" ")
                
            submit_button = st.form_submit_button(label="ส่งคำตอบ (Submit Answers)")
            
        if submit_button:
            correct_count = 0
            st.markdown("### ผลการทดสอบ (Quiz Results)")
            
            for i, q in enumerate(lesson["quiz"]):
                chosen = user_selections[i]
                is_correct = chosen == q["answer"]
                
                if is_correct:
                    correct_count += 1
                    st.markdown(
                        f"""
                        <div class="quiz-feedback-success">
                            <b>ข้อ {i+1} ถูกต้อง!</b><br>
                            คำตอบที่เลือก: {chosen}<br>
                            <i>คำอธิบาย: {q['explanation']}</i>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="quiz-feedback-error">
                            <b>ข้อ {i+1} ผิดพลาด!</b><br>
                            คำตอบที่คุณเลือก: {chosen}<br>
                            คำตอบที่ถูกต้องคือ: <b>{q['answer']}</b><br>
                            <i>คำอธิบาย: {q['explanation']}</i>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            score_percent = int((correct_count / len(lesson["quiz"])) * 100)
            
            # Save score in session state (only if it's the highest)
            prev_score = st.session_state.quiz_scores.get(str(l_id), 0)
            if score_percent > prev_score:
                st.session_state.quiz_scores[str(l_id)] = score_percent
                db_helper.update_user_quiz_scores(st.session_state.current_user, st.session_state.quiz_scores)
                
            # Automatically mark the lesson as completed if they score >= 60%
            if score_percent >= 60:
                st.session_state.completed_lessons.add(l_id)
                db_helper.update_user_progress(st.session_state.current_user, st.session_state.completed_lessons)
                
            st.markdown(f"### สรุปคะแนน: **{correct_count} จาก {len(lesson['quiz'])} ข้อ ({score_percent}%)**")
            if score_percent == 100:
                st.success("ยอดเยี่ยมมาก! คุณทำคะแนนได้เต็ม 100%")
            elif score_percent >= 60:
                st.success("ยินดีด้วย! คุณผ่านเกณฑ์ทดสอบความรู้ของบทเรียนนี้แล้ว (ผ่านเกณฑ์ 60%)")
            else:
                st.warning("พยายามอีกนิดนะ! ลองกลับไปทบทวนบทเรียนอีกครั้งเพื่อทำคะแนนให้ดียิ่งขึ้นครับ")
                
    with tab_type:
        st.markdown(f"### แบบทดสอบการพิมพ์: {lesson['title']}")
        st.write("คำชี้แจง: ให้พิมพ์คำศัพท์หรือวลีภาษาสวีเดนให้ถูกต้องตรงกับคำแปลภาษาไทยที่กำหนดให้ (พิมพ์ด้วยตัวอักษรพิมพ์เล็กทั้งหมด)")
        
        if "typing_practice" in lesson:
            type_form_key = f"type_form_{l_id}"
            with st.form(key=type_form_key):
                user_typed = []
                for i, tp in enumerate(lesson["typing_practice"]):
                    st.markdown(f"**ข้อที่ {i+1}: แปลคำว่า '{tp['thai']}' เป็นภาษาสวีเดน**")
                    typed_ans = st.text_input(
                        "พิมพ์คำตอบภาษาสวีเดนที่นี่:",
                        key=f"type_{l_id}_{i}",
                        placeholder="..."
                    )
                    user_typed.append(typed_ans)
                    st.markdown(" ")
                submit_type_button = st.form_submit_button(label="ตรวจคำตอบ (Check Answers)")
                
            if submit_type_button:
                type_correct = 0
                st.markdown("### ผลการฝึกพิมพ์ (Typing Practice Results)")
                for i, tp in enumerate(lesson["typing_practice"]):
                    ans_raw = user_typed[i].strip().lower()
                    target_ans = tp["swedish"].strip().lower()
                    
                    is_correct = ans_raw == target_ans
                    
                    missed_specials = False
                    if not is_correct:
                        # Check if they typed English characters instead of Swedish special characters
                        english_base = target_ans.replace('å', 'a').replace('ä', 'a').replace('ö', 'o')
                        if ans_raw == english_base:
                            missed_specials = True
                            
                    if is_correct:
                        type_correct += 1
                        st.markdown(
                            f"""
                            <div class="quiz-feedback-success">
                                <b>ข้อ {i+1} ถูกต้อง!</b><br>
                                คำตอบที่คุณพิมพ์: <code style='font-size:1.1rem; color:#22c55e;'>{user_typed[i]}</code><br>
                                <i>คำอธิบาย: {tp['explanation']}</i>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    elif missed_specials:
                        st.markdown(
                            f"""
                            <div class="quiz-feedback-error" style="border-left: 5px solid #eab308;">
                                <b>ข้อ {i+1} เกือบถูกแล้ว! แต่ลืมใส่สระพิเศษ (å, ä, ö) หรือเปล่า?</b><br>
                                คำตอบที่คุณพิมพ์: <code>{user_typed[i]}</code><br>
                                คำตอบที่ถูกต้องคือ: <b style='font-size:1.1rem;'>{tp['swedish']}</b><br>
                                <i>คำอธิบาย: {tp['explanation']}</i>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div class="quiz-feedback-error">
                                <b>ข้อ {i+1} ยังไม่ถูกต้อง</b><br>
                                คำตอบที่คุณพิมพ์: <code>{user_typed[i]}</code><br>
                                คำตอบที่ถูกต้องคือ: <b style='font-size:1.1rem;'>{tp['swedish']}</b><br>
                                <i>คำอธิบาย: {tp['explanation']}</i>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                type_score_percent = int((type_correct / len(lesson["typing_practice"])) * 100)
                st.markdown(f"### สรุปคะแนนการพิมพ์: **{type_correct} จาก {len(lesson['typing_practice'])} ข้อ ({type_score_percent}%)**")
                if type_score_percent == 100:
                    st.success("สุดยอดมาก! สะกดคำได้ถูกต้องแม่นยำครบถ้วนครับ")
                elif type_score_percent >= 60:
                    st.success("ยินดีด้วย! คุณผ่านการทดสอบฝึกพิมพ์แล้ว")
                else:
                    st.warning("ลองฝึกพิมพ์และสะกดอีกครั้งนะเพื่อความแม่นยำในการเขียนภาษาสวีเดน")
        else:
            st.info("กำลังโหลดข้อมูลแบบฝึกหัดการพิมพ์...")
            
    with tab_match:
        st.markdown(f"### เกมจับคู่คำศัพท์ (Word Matching Game): {lesson['title']}")
        st.write("คำชี้แจง: อ่านคำแปลภาษาไทยด้านล่าง แล้วเลือกคำศัพท์ภาษาสวีเดนที่ถูกต้องสอดคล้องกัน")
        
        if "matching_practice" in lesson:
            mp_list = lesson["matching_practice"]
            choices = ["เลือกคำศัพท์..."] + sorted([item["swedish"] for item in mp_list])
            
            match_form_key = f"match_form_{l_id}"
            with st.form(key=match_form_key):
                col_c1, col_c2, col_c3 = st.columns(3)
                user_matches = {}
                
                # Card 1
                with col_c1:
                    thai_1 = mp_list[0]["thai"]
                    if " (" in thai_1:
                        thai_1 = thai_1.split(" (")[0]
                    
                    image_path_1 = mp_list[0].get("image_path")
                    if image_path_1:
                        st.image(image_path_1, use_container_width=True)
                        
                    st.markdown(
                        f"""
                        <div class="match-card" style="padding: 15px 10px; margin-top: 5px; margin-bottom: 5px;">
                            <span style="font-size: 1.2rem; font-weight: bold;">{thai_1}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    match_1 = st.selectbox(
                        "คำศัพท์ภาษาสวีเดน ข้อที่ 1:",
                        choices,
                        key=f"match_{l_id}_1"
                    )
                    user_matches[mp_list[0]["swedish"]] = match_1
                    
                # Card 2
                with col_c2:
                    thai_2 = mp_list[1]["thai"]
                    if " (" in thai_2:
                        thai_2 = thai_2.split(" (")[0]
                    
                    image_path_2 = mp_list[1].get("image_path")
                    if image_path_2:
                        st.image(image_path_2, use_container_width=True)
                        
                    st.markdown(
                        f"""
                        <div class="match-card" style="padding: 15px 10px; margin-top: 5px; margin-bottom: 5px;">
                            <span style="font-size: 1.2rem; font-weight: bold;">{thai_2}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    match_2 = st.selectbox(
                        "คำศัพท์ภาษาสวีเดน ข้อที่ 2:",
                        choices,
                        key=f"match_{l_id}_2"
                    )
                    user_matches[mp_list[1]["swedish"]] = match_2
                    
                # Card 3
                with col_c3:
                    thai_3 = mp_list[2]["thai"]
                    if " (" in thai_3:
                        thai_3 = thai_3.split(" (")[0]
                    
                    image_path_3 = mp_list[2].get("image_path")
                    if image_path_3:
                        st.image(image_path_3, use_container_width=True)
                        
                    st.markdown(
                        f"""
                        <div class="match-card" style="padding: 15px 10px; margin-top: 5px; margin-bottom: 5px;">
                            <span style="font-size: 1.2rem; font-weight: bold;">{thai_3}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    match_3 = st.selectbox(
                        "คำศัพท์ภาษาสวีเดน ข้อที่ 3:",
                        choices,
                        key=f"match_{l_id}_3"
                    )
                    user_matches[mp_list[2]["swedish"]] = match_3
                    
                submit_match_button = st.form_submit_button(label="ตรวจการจับคู่ (Check Matches)")
                
            if submit_match_button:
                match_correct = 0
                st.markdown("### ผลการจับคู่คำศัพท์ (Matching Results)")
                
                for i, item in enumerate(mp_list):
                    selected = user_matches[item["swedish"]]
                    target = item["swedish"]
                    is_correct = selected == target
                    
                    thai_clean = item["thai"]
                    if " (" in thai_clean:
                        thai_clean = thai_clean.split(" (")[0]
                        
                    # Display feedback and image in adjacent columns
                    col_fb_text, col_fb_img = st.columns([5, 1])
                    with col_fb_text:
                        if selected == "เลือกคำศัพท์...":
                            st.markdown(
                                f"""
                                <div class="quiz-feedback-error" style="border-left: 5px solid #6c757d; margin-top: 5px; margin-bottom: 5px;">
                                    <b>ข้อที่ {i+1} (คำแปล: {thai_clean}): ยังไม่ได้เลือกคำตอบ</b>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        elif is_correct:
                            match_correct += 1
                            st.markdown(
                                f"""
                                <div class="quiz-feedback-success" style="margin-top: 5px; margin-bottom: 5px;">
                                    <b>ข้อที่ {i+1} (คำแปล: {thai_clean}) ถูกต้อง!</b><br>
                                    คุณเลือกคำศัพท์: <code style='font-size:1.1rem; color:#22c55e;'>{selected}</code>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"""
                                <div class="quiz-feedback-error" style="margin-top: 5px; margin-bottom: 5px;">
                                    <b>ข้อที่ {i+1} (คำแปล: {thai_clean}) ผิดพลาด!</b><br>
                                    คุณเลือกคำศัพท์: <code>{selected}</code><br>
                                    คำตอบที่ถูกต้องคือ: <b style='font-size:1.1rem;'>{target}</b>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    with col_fb_img:
                        img_path = item.get("image_path")
                        if img_path:
                            # Render small thumbnail matching the solution
                            st.image(img_path, width=70)
                        
                if match_correct == 3:
                    st.success("สมบูรณ์แบบ! คุณจับคู่คำศัพท์ภาษาสวีเดนได้ถูกต้องทั้งหมดครับ")
                else:
                    st.warning("จับคู่ผิดไปบางข้อ ลองตรวจสอบคำแปลอีกครั้งนะครับ")
        else:
            st.info("กำลังโหลดข้อมูลแบบฝึกหัดการจับคู่คำศัพท์...")
 
# ----------------- 4. AI CHAT PAGE -----------------
elif st.session_state.current_page == "คุยกับครู AI":
    st.markdown("# ถาม-ตอบภาษาสวีเดนกับครู AI (Lär dig svenska)")
    st.markdown("พบปัญหาการออกเสียง ไวยากรณ์ หรืออยากทดสอบบทสนทนา? ถามคุณครู AI ได้เลยทันทีครับ!")
    
    # Connection state layout
    if not st.session_state.api_key:
        st.warning("ขณะนี้อยู่ใน **Sandbox Mode** (โหมดทดลองบอทจำลองคำตอบ) ครู AI จะตอบกลับได้เฉพาะบางหัวข้อจำกัด เช่น คำทักทาย ตัวเลข สี ไวยากรณ์ En/Ett เท่านั้น คุณสามารถเชื่อมต่อคีย์ Gemini API ได้ในเมนู 'ตั้งค่าระบบ' ทางซ้ายมือ เพื่อคุยคุยกับ AI เต็มรูปแบบได้ทันที!")
    else:
        st.success("กำลังเชื่อมต่อผ่าน Gemini API คุยกับครู AI ได้อย่างอิสระไร้ขีดจำกัด!")
        
    # Conversation clear button
    col_chat, col_clear = st.columns([0.8, 0.2])
    with col_clear:
        if st.button("ล้างห้องแชท (Clear Chat)", key="clear_chat"):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hej! ยินดีต้อนรับสู่ห้องเรียนภาษาสวีเดนครับ ผมคือครู AI ส่วนตัวของคุณ คุณสามารถถามคำถามเกี่ยวกับไวยากรณ์ คำศัพท์ การออกเสียง หรือลองพิมพ์สนทนาภาษาสวีเดนกับผมได้เลยครับ!"}
            ]
            st.rerun()
            
    # Draw Chat History using standard chat_message containers
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Chat Input
    if prompt := st.chat_input("พิมพ์คำถามของคุณที่นี่ เช่น 'คำว่า ส้ม ในภาษาสวีเดนคืออะไร?' หรือ 'ช่วยตรวจประโยค Jag äter en äpple หน่อย'"):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Call AI Agent and render response
        with st.chat_message("assistant"):
            with st.spinner("คุณครูกำลังพิมพ์คำตอบสักครู่..."):
                response = chat_agent.get_ai_response(
                    api_key=st.session_state.api_key,
                    message=prompt,
                    chat_history=st.session_state.chat_history
                )
                st.write(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
 
# ----------------- 5. SETTINGS PAGE -----------------
elif st.session_state.current_page == "ตั้งค่าระบบ":
    st.markdown("# ตั้งค่าระบบเชื่อมต่อ AI (System Settings)")
    st.markdown("ตั้งค่าคีย์เชื่อมต่อปัญญาประดิษฐ์เพื่อรับประสบการณ์การตอบคำถามภาษาชวีเดนที่มีคุณภาพสูงสุด")
    
    st.markdown("### ใส่ Google Gemini API Key")
    st.write("แชทบอทใช้บริการ Gemini API ในการตอบคำถาม ซึ่งคีย์นี้จะไม่ถูกบันทึกในเซิร์ฟเวอร์ใดๆ แต่จะเก็บไว้ในหน่วยความจำเซสชั่นของเบราว์เซอร์ของคุณเท่านั้น")
    
    api_key_input = st.text_input(
        "ระบุ Gemini API Key ของคุณ:", 
        value=st.session_state.api_key, 
        type="password",
        placeholder="AIzaSy..."
    )
    
    if st.button("บันทึกการตั้งค่า (Save Settings)", key="save_api"):
        st.session_state.api_key = api_key_input
        st.success("บันทึก API Key เรียบร้อยแล้ว! ระบบพร้อมใช้ AI ในการช่วยสอนทันทีครับ")
        st.rerun()
        
    st.markdown("---")
    st.markdown("### วิธีรับ Gemini API Key ฟรี:")
    st.markdown(
        """
        1. เข้าไปที่เว็บไซด์ [Google AI Studio](https://aistudio.google.com/)
        2. เข้าสู่ระบบด้วยบัญชี Google
        3. คลิกปุ่ม **Create API Key**
        4. คัดลอกรหัสคีย์ (มักขึ้นต้นด้วย `AIzaSy`) นำมาใส่ช่องกรอกด้านบนและกดบันทึก
        """
    )
