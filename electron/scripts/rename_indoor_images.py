# -*- coding: utf-8 -*-
import os
import re
import shutil

base = r"C:\Users\Administrator\Desktop\室内效果图"

# 各类别对应的新命名规则
# 微信图片原名: 微信图片_YYYY-MM-DD_HHMMSS_XXX.jpg
# 新命名: {类别中文名}_{序号3位}.jpg

category_names = {
    "办公": "办公室",
    "地产": "地产",
    "家庭": "家庭",
    "工装": "工装",
    "酒店民俗": "酒店",
    "餐饮": "餐饮",
}

total_renamed = 0
total_errors = 0

for subdir in os.listdir(base):
    subdir_path = os.path.join(base, subdir)
    if not os.path.isdir(subdir_path):
        continue
    if subdir not in category_names:
        continue

    cat_name = category_names[subdir]
    wechat_files = sorted([
        f for f in os.listdir(subdir_path)
        if os.path.isfile(os.path.join(subdir_path, f)) and f.startswith("微信图片")
    ])

    print(f"\n=== {subdir} ({len(wechat_files)}张) ===")

    for i, old_name in enumerate(wechat_files, start=1):
        # 提取时间戳部分
        # 格式: 微信图片_YYYY-MM-DD_HHMMSS_XXX.jpg
        ts_match = re.search(r'(\d{4})-(\d{2})-(\d{2})_(\d{6})_(\d+)\.jpg', old_name)
        if ts_match:
            ts = f"{ts_match.group(1)}{ts_match.group(2)}{ts_match.group(3)}_{ts_match.group(4)}"
        else:
            ts = f"unknown{i:03d}"

        new_name = f"{cat_name}_{i:03d}_{ts}.jpg"
        old_path = os.path.join(subdir_path, old_name)
        new_path = os.path.join(subdir_path, new_name)

        # 避免覆盖
        if os.path.exists(new_path):
            new_name = f"{cat_name}_{i:03d}_{ts}_dup.jpg"
            new_path = os.path.join(subdir_path, new_name)

        try:
            os.rename(old_path, new_path)
            print(f"  {old_name[:40]} -> {new_name}")
            total_renamed += 1
        except Exception as e:
            print(f"  [ERR] {old_name}: {e}")
            total_errors += 1

print(f"\n✅ 完成！重命名: {total_renamed} | 失败: {total_errors}")
