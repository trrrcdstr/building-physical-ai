"""
import_desktop_db.py
扫描 Desktop/建筑数据库 的所有文件，建立索引
"""
import json
from pathlib import Path

DB_ROOT = Path('C:/Users/Administrator/Desktop/建筑数据库')

def scan_db():
    items = []
    for item in sorted(DB_ROOT.iterdir()):
        if not item.is_dir():
            continue
        files = [f for f in item.rglob('*') if f.is_file() and not f.suffix.lower() in ['.dwl', '.dwl2', '.bak', '.lnk']]
        by_ext = {}
        for f in files:
            ext = f.suffix.lower() or '.unknown'
            by_ext.setdefault(ext, []).append(f)

        total_mb = sum(f.stat().st_size for f in files) / 1024 / 1024
        items.append({
            'name': item.name,
            'path': str(item),
            'total_files': len(files),
            'total_mb': round(total_mb, 1),
            'by_type': {k: len(v) for k, v in by_ext.items()},
            'files': [
                {'name': f.name, 'path': str(f), 'size_mb': round(f.stat().st_size/1024/1024, 2), 'ext': f.suffix.lower()}
                for f in sorted(files)[:20]
            ]
        })
    return items

data = scan_db()

with open('data/processed/desktop_db_index.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'[OK] 索引了 {len(data)} 个数据源')
total_files = sum(d['total_files'] for d in data)
total_mb = sum(d['total_mb'] for d in data)
print(f'     {total_files} 个文件, {total_mb:.1f} MB')
print()
for d in data:
    print(f"  {d['name']}: {d['total_files']}文件 {d['total_mb']}MB")
