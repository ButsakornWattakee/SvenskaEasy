import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Remove the stray `        }` line from Section 1
text = text.replace('\n        }\n**มิติการเปลี่ยนรูป', '\n\n**มิติการเปลี่ยนรูป')

with open('lessons_data.py', 'w', encoding='utf-8') as f:
    f.write(text)

import lessons_data
print("Lesson 14 cleaned and tested successfully!")
