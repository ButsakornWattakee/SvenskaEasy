import sys, re

sys.stdout.reconfigure(encoding='utf-8')
with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

lessons = re.findall(r'"id":\s*(\d+),\s*\n\s*"level":\s*"([^"]+)",\s*\n\s*"cefr":\s*"([^"]+)",\s*\n\s*"duration":\s*"([^"]+)",\s*\n\s*"title":\s*"([^"]+)"', content)

for l in lessons:
    print(f"ID: {l[0]} | Level: {l[1]} | CEFR: {l[2]} | Title: {l[4]}")
