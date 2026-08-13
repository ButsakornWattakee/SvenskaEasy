import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('lessons_data.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

stack = []
for idx, line in enumerate(lines):
    # Ignore content inside triple quotes or strings simplified
    in_string = False
    i = 0
    while i < len(line):
        char = line[i]
        if char == '"' or char == "'":
            # Simple toggle for brackets tracking
            pass
        if char in '{[':
            stack.append((char, idx + 1, line.strip()))
        elif char in '}]':
            if not stack:
                print(f"Unmatched closing '{char}' at line {idx+1}")
            else:
                top, top_line, top_content = stack.pop()
                expected = '}' if top == '{' else ']'
                if char != expected:
                    print(f"Mismatch at line {idx+1}: got '{char}', expected '{expected}' (opened by '{top}' at line {top_line}: {top_content[:40]})")
                    stack.append((top, top_line, top_content)) # push back
                    break
        i += 1
