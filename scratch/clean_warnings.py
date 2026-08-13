import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if r'\mathbf' in l or 'Bestmd' in l:
        lines[i] = l.replace(r'\mathbf', r'\\mathbf').replace('Bestmd', 'Bestämd')

with open('lessons_data.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

import ast
with open('lessons_data.py', 'r', encoding='utf-8') as f:
    code = f.read()
ast.parse(code)
print("Cleaned successfully with no warnings or errors!")
