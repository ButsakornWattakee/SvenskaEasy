import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print("Line 670 to 680:")
for i in range(669, min(680, len(lines))):
    print(f"{i+1}: {repr(lines[i])}")

print("\nLine 2290 to 2300:")
for i in range(2289, min(2300, len(lines))):
    print(f"{i+1}: {repr(lines[i])}")
