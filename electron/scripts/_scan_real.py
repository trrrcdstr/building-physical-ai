import os
from pathlib import Path

base = Path(r"C:\Users\Administrator\Desktop\设计数据库")
print(f"Base: {base}")
print(f"Exists: {base.exists()}")
print()

total = 0
for cat_dir in sorted(base.iterdir()):
    if not cat_dir.is_dir():
        continue
    print(f"\n=== {cat_dir.name} ===")

    cat_total = 0
    # List immediate children
    for item in sorted(cat_dir.iterdir()):
        if item.is_dir():
            jpg_files = list(item.glob("*.jpg")) + list(item.glob("*.JPG")) + list(item.glob("*.jpeg"))
            print(f"  [DIR] {item.name}: {len(jpg_files)} jpg files")
            cat_total += len(jpg_files)
        else:
            if item.suffix.lower() in ['.jpg', '.jpeg']:
                print(f"  [FILE] {item.name}")
                cat_total += 1

    print(f"  => Subtotal: {cat_total} jpg files")
    total += cat_total

print(f"\n=== GRAND TOTAL: {total} jpg files ===")
