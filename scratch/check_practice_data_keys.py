import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

import lessons_data

if hasattr(lessons_data, 'PRACTICE_DATA'):
    print("PRACTICE_DATA keys:", sorted(lessons_data.PRACTICE_DATA.keys()))
