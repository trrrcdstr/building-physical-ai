# -*- coding: utf-8 -*-
import os
import json

def scan_folder(path, name):
    if not os.path.exists(path):
        return {'name': name, 'path': path, 'error': 'path not exists'}
    
    result = {
        'name': name,
        'path': path,
        'files': [],
        'total_size_mb': 0,
        'categories': {},
        'subfolders': {}
    }
    
    total_size = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                size = os.path.getsize(full_path)
                total_size += size
                
                ext = os.path.splitext(f)[1].lower()
                rel_path = os.path.relpath(root, path)
                
                file_info = {
                    'name': f,
                    'extension': ext,
                    'size_kb': round(size / 1024, 1),
                    'folder': rel_path if rel_path != '.' else 'root'
                }
                result['files'].append(file_info)
                
                # 分类统计
                cat = ext.replace('.', '') if ext else 'other'
                if cat not in result['categories']:
                    result['categories'][cat] = {'count': 0, 'size_mb': 0}
                result['categories'][cat]['count'] += 1
                result['categories'][cat]['size_mb'] += size / 1024 / 1024
                
                # 子文件夹统计
                if rel_path != '.':
                    subfolder = rel_path.split(os.sep)[0]
                    if subfolder not in result['subfolders']:
                        result['subfolders'][subfolder] = {'count': 0, 'size_mb': 0}
                    result['subfolders'][subfolder]['count'] += 1
                    result['subfolders'][subfolder]['size_mb'] += size / 1024 / 1024
            except:
                pass
    
    result['total_size_mb'] = round(total_size / 1024 / 1024, 1)
    result['file_count'] = len(result['files'])
    
    for cat in result['categories']:
        result['categories'][cat]['size_mb'] = round(result['categories'][cat]['size_mb'], 1)
    
    for sf in result['subfolders']:
        result['subfolders'][sf]['size_mb'] = round(result['subfolders'][sf]['size_mb'], 1)
    
    return result

if __name__ == '__main__':
    folders = [
        (r'C:\Users\Administrator\Desktop\设计数据库', '设计数据库'),
        (r'C:\Users\Administrator\Desktop\沙发软装', '沙发软装'),
        (r'C:\Users\Administrator\Desktop\室内家居场景jpg', '室内家居场景jpg')
    ]
    
    results = []
    for path, name in folders:
        print('Scanning:', name)
        r = scan_folder(path, name)
        results.append(r)
        print('  Files:', r.get('file_count', 0), 'Size:', r.get('total_size_mb', 0), 'MB')
        if r.get('categories'):
            print('  Categories:', list(r['categories'].keys()))
        if r.get('subfolders'):
            print('  Subfolders:', list(r['subfolders'].keys()))
    
    output_path = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\design_data_catalog.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print('\nSaved to:', output_path)
