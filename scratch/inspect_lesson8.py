import sys

sys.stdout.reconfigure(encoding='utf-8')
with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print("Line 625-645:")
for i in range(624, 645):
    print(f"{i+1}: {repr(lines[i])}")

print("\nLine 925-945:")
for i in range(924, 945):
    print(f"{i+1}: {repr(lines[i])}")
