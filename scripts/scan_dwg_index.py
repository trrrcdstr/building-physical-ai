"""
DWG文件索引器
扫描建筑数据库中的DWG文件，生成索引
"""
import os
import json
from pathlib import Path
from datetime import datetime

def scan_dwg_files(root_path: str) -> list:
    """扫描DWG文件"""
    dwg_files = []
    
    for root, dirs, files in os.walk(root_path):
        for f in files:
            if f.lower().endswith('.dwg'):
                path = os.path.join(root, f)
                stat = os.stat(path)
                
                # 识别DWG版本
                version = detect_dwg_version(path)
                
                dwg_files.append({
                    'filename': f,
                    'path': path,
                    'size_mb': round(stat.st_size / (1024*1024), 2),
                    'version': version,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'project': extract_project_name(path, root_path)
                })
    
    return dwg_files

def detect_dwg_version(filepath: str) -> str:
    """检测DWG版本"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(6)
            version_map = {
                b'AC1004': 'R9',
                b'AC1006': 'R10',
                b'AC1009': 'R11/R12',
                b'AC1012': 'R13',
                b'AC1014': 'R14',
                b'AC1015': 'R2000',
                b'AC1018': 'R2004',
                b'AC1021': 'R2007',
                b'AC1024': 'R2010',
                b'AC1027': 'R2013',
                b'AC1032': 'R2018',
            }
            for code, ver in version_map.items():
                if header.startswith(code):
                    return ver
            return 'Unknown'
    except:
        return 'Error'

def extract_project_name(filepath: str, root_path: str) -> str:
    """提取项目名称"""
    rel_path = os.path.relpath(filepath, root_path)
    parts = rel_path.split(os.sep)
    if len(parts) > 1:
        return parts[0]
    return 'Unknown'

def main():
    root = r"C:\Users\Administrator\Desktop"
    output_path = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\dwg_index.json"
    
    print("=" * 60)
    print("DWG文件索引器")
    print("=" * 60)
    
    dwg_files = scan_dwg_files(root)
    
    # 统计
    total_size = sum(f['size_mb'] for f in dwg_files)
    versions = {}
    projects = {}
    
    for f in dwg_files:
        v = f['version']
        p = f['project']
        versions[v] = versions.get(v, 0) + 1
        projects[p] = projects.get(p, 0) + 1
    
    print(f"\n找到 {len(dwg_files)} 个DWG文件，总大小 {total_size:.2f} MB")
    
    print("\n版本分布：")
    for v, c in sorted(versions.items(), key=lambda x: -x[1]):
        print(f"  {v}: {c} 个")
    
    print("\n项目分布：")
    for p, c in sorted(projects.items(), key=lambda x: -x[1]):
        print(f"  {p}: {c} 个")
    
    # 保存索引
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    result = {
        'scan_time': datetime.now().isoformat(),
        'total_files': len(dwg_files),
        'total_size_mb': total_size,
        'version_stats': versions,
        'project_stats': projects,
        'files': dwg_files
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n索引已保存: {output_path}")
    print("=" * 60)

if __name__ == '__main__':
    main()
