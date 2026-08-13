import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

import lessons_data

for l in lessons_data.LESSONS:
    for idx, sec in enumerate(l['sections']):
        if 'บทสนทนา' in sec['subtitle'] or 'dialog' in sec['subtitle'].lower() or 'dialogue' in sec['subtitle'].lower():
            print(f"Lesson {l['id']} ({sec['subtitle']}): {len(sec['content'])} chars")
            print(sec['content'][:200])
            print("---")
