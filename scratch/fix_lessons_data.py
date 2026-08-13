import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print("Line 930 was:", repr(lines[929]))

# Fix line 930 which had `    },เคอะ",` -> `    },`
if 'เคอะ' in lines[929]:
    lines[929] = '    },\n'

with open('lessons_data.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Line 930 fixed.")

try:
    import lessons_data
    print(f"Successfully imported lessons_data! Loaded {len(lessons_data.LESSONS)} lessons.")
except Exception as e:
    print(f"Import error: {e}")
