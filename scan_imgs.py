"""快速扫描所有图片"""
from pathlib import Path

DB = Path('C:/Users/Administrator/Desktop/建筑数据库')
IMG_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}

grand = 0, 0.0
for item in sorted(DB.iterdir()):
    if not item.is_dir():
        continue
    imgs = [f for f in item.rglob('*') if f.is_file() and f.suffix.lower() in IMG_EXTS]
    files = [f for f in item.rglob('*') if f.is_file()]
    s = sum(f.stat().st_size for f in files) / 1024 / 1024
    grand = grand[0] + len(files), grand[1] + s
    if imgs:
        total_img_mb = sum(f.stat().st_size for f in imgs) / 1024 / 1024
        print(f'{item.name}/')
        print(f'  Total: {len(files)} files, {s:.1f} MB')
        print(f'  Images: {len(imgs)}, {total_img_mb:.1f} MB')
        for img in imgs[:5]:
            print(f'    {img.name} ({img.stat().st_size/1024/1024:.1f}MB)')
        if len(imgs) > 5:
            print(f'    ... +{len(imgs)-5} more')

print()
print(f'Grand: {grand[0]} files, {grand[1]:.1f} MB')
