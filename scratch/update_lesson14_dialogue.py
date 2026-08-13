import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

new_dialogue_content = '''### 🛍️ บทสนทนาการซื้อของแต่งห้อง (IKEA Shopping Dialogue)
**สถานการณ์:** Johan และ Sara กำลังเลือกซื้อเฟอร์นิเจอร์และของแต่งห้องในห้าง IKEA เพื่อย้ายเข้าอพาร์ตเมนต์ใหม่

---

#### 🧑‍💼 **Johan (โฮฮัน)**
> 🇸🇪 **Titta på den här soffan, Sara! Den är verkligen bekväm och modern.**  
> 🗣️ *[ทิดตา พัว เดน แฮร์ ซ็อฟฟาน, ซาร่า! เดน แอ แวร์คลิเคน เบ็คแวม อ็อค โมแดร์น]*  
> 🇹🇭 **คำแปล:** ดูโซฟาตัวนี้สิ ซาร่า! มันนุ่มสบายและดูทันสมัยจริงๆ เลย

---

#### 👩‍💼 **Sara (ซาร่า)**
> 🇸🇪 **Ja, men den är alldeles för stor för vårt lilla vardagsrum.**  
> 🗣️ *[ยา, เมน เดน แอ อัลเดเลส เฟอร์ สตูร เฟอร์ วอร์ด ลิลลา วอร์ดักสรูม]*  
> 🇹🇭 **คำแปล:** ใช่ แต่ว่ามันใหญ่เกินไปมากสำหรับห้องนั่งเล่นเล็กๆ ของพวกเรานะ

---

#### 🧑‍💼 **Johan (โฮฮัน)**
> 🇸🇪 **Du har rätt. Vad tycker du om det där runda bordet i trä då?**  
> 🗣️ *[ดู ฮาร์ แร็ต. วา ทึคแคร์ ดู อ็อม เดท แดร์ รุนดา บูร์เด็ต อิ แทร ดัว?]*  
> 🇹🇭 **คำแปล:** คุณพูดถูก แล้วคุณคิดยังไงกับโต๊ะไม้ทรงกลมตัวนั้นล่ะ?

---

#### 👩‍💼 **Sara (ซาร่า)**
> 🇸🇪 **Det är jättefint! Och titta, det har ett ganska billigt pris också.**  
> 🗣️ *[เดท แอ แย็ตเตะฟีนท์! อ็อค ทิตตา, เดท ฮาร์ เอ็ต กันสกา บิลลิกท์ พริส อ็อคซัว]*  
> 🇹🇭 **คำแปล:** มันสวยมากๆ เลย! แล้วดูสิ มันมีราคาค่อนข้างถูกด้วยนะ

---

#### 🧑‍💼 **Johan (โฮฮัน)**
> 🇸🇪 **Perfekt! Vi behöver också två nya stolar till köket.**  
> 🗣️ *[แพร์เฟ็คท์! วี เบอเฮอแวร์ อ็อคซัว ทโว นวา สตูลาร์ ทิล เชอเก็ต]*  
> 🇹🇭 **คำแปล:** ยอดเยี่ยมเลย! พวกเราต้องการเก้าอี้ใหม่อีกสองตัวสำหรับห้องครัวด้วย

---

#### 👩‍💼 **Sara (ซาร่า)**
> 🇸🇪 **De här vita stolarna är väldigt vackra, men är de inte lite hårda att sitta på?**  
> 🗣️ *[ดอม แฮร์ วีตา สตูลาร์นา แอ แวลติกท์ วัคครา, เมน แอ ดอม อินเทอะ ลิเทอะ ฮอร์ดัว อัท ซิตตา พัว?]*  
> 🇹🇭 **คำแปล:** เก้าอี้สีขาวพวกนี้สวยงามมากเลยนะ แต่ว่ามันนั่งแล้วแข็งไปหน่อยไหม?

---

#### 🧑‍💼 **Johan (โฮฮัน)**
> 🇸🇪 **Jo, men vi kan köpa mjuka kuddar och lägga på dem.**  
> 🗣️ *[ยู, เมน วี คาน เชอพา มยูคา คุดดาร์ อ็อค แล็กกา พัว ดอม]*  
> 🇹🇭 **คำแปล:** ใช่ แต่พวกเราสามารถซื้อหมอนนุ่มๆ มาวางไว้บนเก้าอี้ได้นี่นา

---

#### 👩‍💼 **Sara (ซาร่า)**
> 🇸🇪 **Bra idé! Låt oss beställa hemleverans, paketen är för tunga för vår bil.**  
> 🗣️ *[บรา อีเด! ล็อต ออส เบสแตลลา เฮมเลเวอรันส์, พาเคเทน แอ เฟอร์ ทุงงา เฟอร์ วอร์ บีล]*  
> 🇹🇭 **คำแปล:** ความคิดที่ดีมาก! สั่งให้ไปส่งที่บ้านเถอะ พัสดุมันหนักเกินไปสำหรับรถของพวกเรา'''

# Find Section 5 in Lesson 14 and replace content
import re

pattern = r'("subtitle": "5\. บทสนทนาตามสถานการณ์จริง: ซื้อของแต่งห้องที่ IKEA \(Contextual Dialogue\)",\s*"content": """[\s\S]*?""")'

if re.search(pattern, text):
    new_text = re.sub(
        pattern,
        f'"subtitle": "5. บทสนทนาตามสถานการณ์จริง: ซื้อของแต่งห้องที่ IKEA (Contextual Dialogue)",\n                "content": """{new_dialogue_content}"""',
        text
    )
    with open('lessons_data.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESS: Updated Lesson 14 Dialogue content!")
else:
    print("Pattern not found, checking manual string replace...")
