import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Identify line 638 and line 931
print(f"Line 638: {repr(lines[637])}")
print(f"Line 930: {repr(lines[929])}")
print(f"Line 931: {repr(lines[930])}")
print(f"Line 939: {repr(lines[938])}")

# Construct repaired replacement for line 637 to 938:
# 1. Close line 638 properly in Lesson 8
# 2. Insert Lesson 8's sections and Allemansrätten question start
# 3. Close Lesson 8 properly: `},`
# 4. Keep Lesson 14 (Adjektivets kongruens) as a clean dict item `{\n "id": 14, ... },\n`
# 5. Remove the orphaned tail at lines 931-938.

lesson8_rest = '''            "บรรยายลักษณะสิ่งแวดล้อมธรรมชาติพร้อมคำถอดเสียงภาษาไทย"
        ],
        "sections": [
            {
                "subtitle": "1. สัตว์เลี้ยงและสัตว์ป่าในสวีเดน (Djur i Sverige)",
                "content": """### สัตว์เลี้ยงและสัตว์ป่าสำคัญ
* **en hund** [เอน ฮุนด์] = สุนัข
* **en katt** [เอน คัตต์] = แมว
* **en älg** [เอน แอลก์] = กวางมูส (สัญลักษณ์ประจำชาติ)
* **en björn** [เอน เบยร์น] = หมี
* **en varg** [เอน วาริยิก] = หมาป่า
* **en fågel** [เอน โฟเกล] = นก
"""
            },
            {
                "subtitle": "2. ธรรมชาติและสิทธิสรีภาพในธรรมชาติ (Natur och Allemansrätten)",
                "content": """### สิทธิการเข้าถึงธรรมชาติ (Allemansrätten)
* **en skog** [เอน สกูก] = ป่า
* **en sjö** [เอน เซอ] = ทะเลสาบ
* **ett berg** [เอต แบร์ย] = ภูเขา
* **Allemansrätten** [อัลเลอมันส์แร็ตเตน] = สิทธิในธรรมชาติสำหรับทุกคน
* **Inte störa – inte förstöra** [อินเทอะ สเติร์ยรา – อินเทอะ เฟอร์สเติร์ยรา] = ไม่รบกวน ไม่ทำลาย
"""
            }
        ],
        "questions": [
            {
                "question": "หลักการสำคัญของสิทธิ Allemansrätten ในสวีเดนคืออะไร?",
                "options": [
                    "อินเทอะ สเติร์ยรา – อินเทอะ เฟอร์สเติร์ยรา",
                    "กูด มอร์รอน",
                    "ฮา เอน บรา ดาก"
                ],
                "answer": "อินเทอะ สเติร์ยรา – อินเทอะ เฟอร์สเติร์ยรา",
                "explanation": "Inte störa – inte förstöra ออกเสียงว่า [อินเทอะ สเติร์ยรา – อินเทอะ เฟอร์สเติร์ยรา] หมายถึง ไม่รบกวน ไม่ทำลาย"
            }
        ]
    },
'''

# New lines assembly
new_lines = lines[:637] # up to objectives item 2
new_lines.append(lesson8_rest)

# Add Lesson 14 (from line 639 to 930)
lesson14_lines = lines[638:930] # line 639 ("             {\n") to 930 ("    },\n")
# Clean up first line of lesson 14
if lesson14_lines:
    lesson14_lines[0] = "    {\n"
new_lines.extend(lesson14_lines)

# Skip orphaned tail lines 931-939 (lines index 930 to 938)
new_lines.extend(lines[939:]) # from line 940 (id 9) onwards

with open('lessons_data.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Replacement done. Testing import...")

try:
    sys.path.insert(0, '.')
    import lessons_data
    print(f"SUCCESS! Loaded {len(lessons_data.LESSONS)} lessons cleanly without any syntax errors!")
except Exception as e:
    print(f"FAILED: {e}")
