import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

import lessons_data

for l in lessons_data.LESSONS:
    if l['id'] == 14 and 'kongruens' in l['title'].lower():
        print(f"=== Lesson 14: {l['title']} ===")
        for idx, sec in enumerate(l['sections']):
            print(f"\n--- Section {idx+1}: {sec['subtitle']} ---")
            print(sec['content'][:300])
