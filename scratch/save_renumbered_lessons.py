import sys
import re
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

import lessons_data

lessons = list(lessons_data.LESSONS)

kongruens_lesson = None
other_lessons = []

for l in lessons:
    if 'kongruens' in l['title'].lower():
        kongruens_lesson = l
    else:
        other_lessons.append(l)

insert_idx = -1
for idx, l in enumerate(other_lessons):
    if 'Frågesatser' in l['title'] or l['id'] == 15:
        insert_idx = idx + 1
        break

if insert_idx != -1:
    other_lessons.insert(insert_idx, kongruens_lesson)

# Renumber all lessons 1 to 25
for new_id, l in enumerate(other_lessons, 1):
    l['id'] = new_id
    l['title'] = re.sub(r'บทที่\s*\d+\s*:', f'บทที่ {new_id} :', l['title'])

# Re-serialize LESSONS in lessons_data.py file
# Read original lessons_data.py lines up to LESSONS = [
with open('lessons_data.py', 'r', encoding='utf-8') as f:
    text = f.read()

# We can update lessons_data.py cleanly by re-writing the LESSONS list
import pprint

# Let's inspect where LESSONS = [ starts and ends
start_idx = text.find('LESSONS = [')
end_marker = '\n# PRACTICE DATA'
if end_marker not in text:
    end_marker = '\nPRACTICE_DATA = {'
end_idx = text.find(end_marker)

header = text[:start_idx]
footer = text[end_idx:]

import json

# Format LESSONS neatly in python code
formatted_lessons_py = "LESSONS = " + json.dumps(other_lessons, ensure_ascii=False, indent=4)

new_full_text = header + formatted_lessons_py + "\n" + footer

with open('lessons_data.py', 'w', encoding='utf-8') as f:
    f.write(new_full_text)

print("Saved renumbered lessons_data.py! Testing import...")

import ast
ast.parse(new_full_text)
print("AST Parse SUCCESSFUL!")
