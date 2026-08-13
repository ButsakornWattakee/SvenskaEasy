import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for i, line in enumerate(lines):
    if '"id":' in line or '"title":' in line or '"cefr":' in line:
        print(f"Line {i+1}: {line.strip()}")
