import os
from pathlib import Path

# Test actual paths directly
test_files = [
    r"C:\Users\Administrator\Desktop\设计数据库\室内效果图\家庭\1.jpg",
    r"C:\Users\Administrator\Desktop\设计数据库\室内效果图\家庭\家庭_001_20260414_182221.jpg",
    r"C:\Users\Administrator\Desktop\设计数据库\建筑效果图\别墅建筑花园\别墅1.jpg",
    r"C:\Users\Administrator\Desktop\设计数据库\园林效果图\园林.jpg",
]

print("Direct file existence check:")
for f in test_files:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    print(f"  [{'OK' if exists else 'MISSING'}] {os.path.basename(f)} ({size/1024:.0f} KB)")

print()

# Walk the design database and list actual files
base = Path(r"C:\Users\Administrator\Desktop\设计数据库")
for cat_dir in sorted(base.iterdir()):
    if cat_dir.is_dir():
        print(f"\n=== {cat_dir.name} ===")
        for sub_dir in sorted(cat_dir.iterdir()):
            if sub_dir.is_dir():
                files = list(sub_dir.glob("*.jpg")) + list(sub_dir.glob("*.JPG"))
                print(f"  {sub_dir.name}: {len(files)} jpg files")
            else:
                if sub_dir.suffix.lower() == '.jpg':
                    print(f"  {sub_dir.name}: 1 jpg (root)")
