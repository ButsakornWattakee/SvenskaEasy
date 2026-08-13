import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print("Line 635 to 645:")
for i in range(634, 645):
    print(f"{i+1}: {repr(lines[i])}")

print("\nLine 925 to 940:")
for i in range(924, 940):
    print(f"{i+1}: {repr(lines[i])}")
