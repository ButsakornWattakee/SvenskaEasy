import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Line 967: {repr(lines[966])}")
print(f"Line 968: {repr(lines[967])}")

# Insert `    },\n` between 967 and 968
lines.insert(967, "    },\n")

with open('lessons_data.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Line inserted. Testing AST parse and import...")

import ast
try:
    with open('lessons_data.py', 'r', encoding='utf-8') as f:
        code = f.read()
    ast.parse(code)
    print("AST parse SUCCESSFUL!")
    
    sys.path.insert(0, '.')
    import lessons_data
    print(f"Import SUCCESSFUL! Loaded {len(lessons_data.LESSONS)} lessons.")
except Exception as e:
    print(f"ERROR: {e}")
