# -*- coding: utf-8 -*-
import os
import sys

# Set UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

base = r'C:\Users\Administrator\Desktop\南沙星河东悦湾'

dwg_files = []
for root, dirs, files in os.walk(base):
    dirs.sort()
    for f in sorted(files):
        fp = os.path.join(root, f)
        size = os.path.getsize(fp) / 1024
        rel = os.path.relpath(fp, base)
        ext = os.path.splitext(f)[1].lower()
        if ext in ('.dwg', '.DWG'):
            dwg_files.append((rel, size, ext))

print(f'Total DWG files: {len(dwg_files)}')
print()
# Sort by size descending
for rel, size, ext in sorted(dwg_files, key=lambda x: -x[1]):
    print(f'{size:8.1f}KB  {rel}')
