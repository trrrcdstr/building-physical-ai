"""
scan_cad.py — 扫描CAD文件，尝试提取门/窗/家具对象
"""
import json
from pathlib import Path
import sys

# Try ezdxf first
try:
    import ezdxf
    HAS_EZDXF = True
    print('[OK] ezdxf available')
except ImportError:
    HAS_EZDXF = False
    print('[--] ezdxf not available, will use text-based parsing')

DB = Path('C:/Users/Administrator/Desktop/建筑数据库')

def try_parse_dxf(dwg_path):
    """尝试用ezdxf解析DXF/DWG"""
    if not HAS_EZDXF:
        return None
    try:
        if dwg_path.suffix.lower() == '.dxf':
            doc = ezdxf.readfile(str(dwg_path))
        else:
            # 二进制DWG不支持，尝试其他方法
            return None
        msp = doc.modelspace()
        entities = []
        for e in msp:
            etype = e.dxftype()
            if etype in ['INSERT', 'LINE', 'ARC', 'CIRCLE', 'LWPOLYLINE']:
                try:
                    if etype == 'INSERT':
                        entities.append({'type': 'block', 'name': e.get('name', 'unknown'), 'layer': e.dxf.layer})
                    elif etype == 'LINE':
                        entities.append({'type': 'line', 'layer': e.dxf.layer})
                except:
                    pass
        return {'entities': len(entities), 'blocks': [e for e in entities if e.get('type') == 'block']}
    except Exception as e:
        return {'error': str(e)[:50]}

def scan_dir(path):
    results = []
    for item in sorted(path.iterdir()):
        if item.is_file():
            ext = item.suffix.lower()
            if ext in ['.dwg', '.dxf']:
                size = item.stat().st_size / 1024 / 1024
                result = {'file': item.name, 'path': str(item), 'size_mb': round(size, 1), 'ext': ext}
                if ext == '.dxf':
                    parse = try_parse_dxf(item)
                    if parse:
                        result['parsed'] = parse
                elif ext == '.dwg':
                    result['note'] = 'DWG binary (R2004) - needs LibreCAD conversion'
                results.append(result)
    return results

print()
print('=== 山水庭院 CAD ===')
shanshui = DB / '山水庭院'
if shanshui.exists():
    r = scan_dir(shanshui)
    for f in r:
        print(f"  {f['file']} ({f['size_mb']}MB) {f.get('note','')}")
        if f.get('parsed'):
            p = f['parsed']
            print(f"    -> {p.get('entities',0)} entities")
else:
    print('  目录不存在')

print()
print('=== 南沙星河东悦湾 CAD ===')
ns_dirs = [d for d in DB.iterdir() if '南沙' in d.name or '星河' in d.name]
if not ns_dirs:
    ns_dirs = [d for d in DB.iterdir() if d.is_dir()]
print(f'  搜索到: {[d.name for d in ns_dirs]}')
for ns_dir in ns_dirs:
    files = [f for f in ns_dir.rglob('*') if f.is_file() and f.suffix.lower() in ['.dwg', '.dxf']]
    print(f'  {ns_dir.name}/: {len(files)} CAD文件')
    for f in files[:10]:
        size = f.stat().st_size/1024/1024
        result = {'file': f.name, 'size_mb': round(size, 1), 'ext': f.suffix.lower()}
        print(f"    {f.name} ({size:.1f}MB)")
        if f.suffix.lower() == '.dxf':
            parse = try_parse_dxf(f)
            if parse:
                print(f"      -> {parse}")

print()
print('=== 效果图(JPG) ===')
img_dir_names = ['家庭装修', '厨卫装修', '山水庭院', '翠湖香颂', '效果图']
img_dirs = [d for d in DB.iterdir() if d.is_dir() and any(x in d.name for x in img_dir_names)]
for d in img_dirs:
    imgs = [f for f in d.rglob('*') if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
    total_mb = sum(f.stat().st_size for f in imgs) / 1024 / 1024
    print(f'  {d.name}/: {len(imgs)} 图片, {total_mb:.1f}MB')
    for img in imgs[:5]:
        print(f"    {img.name} ({img.stat().st_size/1024/1024:.1f}MB)")
    if len(imgs) > 5:
        print(f"    ... 还有{len(imgs)-5}张")
