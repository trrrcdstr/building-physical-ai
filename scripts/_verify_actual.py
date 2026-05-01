import os
from pathlib import Path

base = Path(r"C:\Users\Administrator\Desktop\设计数据库")

print(f"Base exists: {base.exists()}")
print()

total = 0
for cat in sorted(base.iterdir()):
    if not cat.is_dir():
        continue
    print(f"\n=== {cat.name} (category) ===")
    cat_total = 0

    for sub in sorted(cat.iterdir()):
        if sub.is_dir():
            jpg = list(sub.glob("*.jpg")) + list(sub.glob("*.JPG")) + list(sub.glob("*.jpeg"))
            if jpg:
                print(f"  {sub.name}/: {len(jpg)} jpg")
                cat_total += len(jpg)
        else:
            if sub.suffix.lower() in ['.jpg', '.jpeg']:
                print(f"  {sub.name} (root file): 1 jpg")
                cat_total += 1

    # Also check root level jpg files
    root_jpg = list(cat.glob("*.jpg")) + list(cat.glob("*.JPG"))
    if root_jpg:
        print(f"  (root): {len(root_jpg)} jpg")
        cat_total += len(root_jpg)

    print(f"  -> Category total: {cat_total}")
    total += cat_total

print(f"\n=== GRAND TOTAL: {total} jpg files ===")
