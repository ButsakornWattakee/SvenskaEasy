import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

import lessons_data

print(f"Total lessons count: {len(lessons_data.LESSONS)}")
for idx, l in enumerate(lessons_data.LESSONS):
    print(f"Index {idx+1:2d} | ID: {l['id']:2d} | CEFR: {l['cefr']:9s} | Title: {l['title']}")
