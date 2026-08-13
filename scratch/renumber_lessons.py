import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

import lessons_data

# Move the Adjektivets kongruens lesson (currently index 8 with id 14) to right after Frågesatser (currently index 15 with id 15)
lessons = list(lessons_data.LESSONS)

kongruens_lesson = None
other_lessons = []

for l in lessons:
    if 'kongruens' in l['title'].lower():
        kongruens_lesson = l
    else:
        other_lessons.append(l)

print(f"Found kongruens lesson: {kongruens_lesson['title']}")
print(f"Other lessons count: {len(other_lessons)}")

# Find position after Frågesatser (id 15)
insert_idx = -1
for idx, l in enumerate(other_lessons):
    if 'Frågesatser' in l['title'] or l['id'] == 15:
        insert_idx = idx + 1
        break

if insert_idx != -1:
    other_lessons.insert(insert_idx, kongruens_lesson)
    print(f"Inserted kongruens lesson at index {insert_idx+1}")

# Now renumber all lessons from 1 to 25
for new_id, l in enumerate(other_lessons, 1):
    old_id = l['id']
    l['id'] = new_id
    # Update title string "บทที่ X :"
    import re
    l['title'] = re.sub(r'บทที่\s*\d+\s*:', f'บทที่ {new_id} :', l['title'])
    print(f"Lesson {new_id:2d} (was ID {old_id:2d}): {l['title']}")

# Verify all IDs are unique
ids = [l['id'] for l in other_lessons]
print("\nVerification of unique IDs:", len(ids) == len(set(ids)), f"Count: {len(ids)}")
