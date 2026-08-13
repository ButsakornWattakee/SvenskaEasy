import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'sections', text)]
for m in matches:
    print('--- match ---')
    print(text[max(0, m-100):min(len(text), m+300)])
