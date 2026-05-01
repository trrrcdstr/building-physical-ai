# -*- coding: utf-8 -*-
"""
提取本邦PDF中所有图片（项目案例图片）
"""
import fitz
import os
import hashlib

pdf_path = r'C:\Users\Administrator\Desktop\广州本邦工程顾问有限公司图册（酒店、商业）.pdf'
out_dir = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\benbang_images'
os.makedirs(out_dir, exist_ok=True)

doc = fitz.open(pdf_path)

# 提取所有图片
image_info = []
for page_idx, page in enumerate(doc):
    imgs = page.get_images(full=True)
    for img_idx, img in enumerate(imgs):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image_size = len(image_bytes)
        
        # 生成文件名
        fname = f"p{page_idx+1:02d}_img{img_idx+1:02d}.{image_ext}"
        fpath = os.path.join(out_dir, fname)
        with open(fpath, 'wb') as f:
            f.write(image_bytes)
        
        image_info.append({
            'page': page_idx + 1,
            'file': fname,
            'ext': image_ext,
            'size_kb': round(image_size / 1024, 1),
            'width': base_image.get('width'),
            'height': base_image.get('height')
        })
        print(f"Page {page_idx+1}: {fname} ({base_image.get('width')}x{base_image.get('height')}, {image_size//1024}KB)")

doc.close()

# 保存图片清单
import json
with open(os.path.join(out_dir, 'image_list.json'), 'w', encoding='utf-8') as f:
    json.dump(image_info, f, ensure_ascii=False, indent=2)

print(f"\n共提取 {len(image_info)} 张图片 -> {out_dir}")