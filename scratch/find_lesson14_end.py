import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i in range(915, 945):
    print(f"{i+1}: {repr(lines[i])}")
