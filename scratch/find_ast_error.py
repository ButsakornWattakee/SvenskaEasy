import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

try:
    ast.parse(code)
    print("ast.parse SUCCESS! No Python syntax errors found.")
except SyntaxError as e:
    print(f"SyntaxError: {e}")
    print(f"Line {e.lineno}, offset {e.offset}: {e.text}")
