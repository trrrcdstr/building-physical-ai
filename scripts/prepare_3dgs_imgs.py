import os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')

# 目标目录（与train_gaussian_enhanced.py预期的中文场景名一致）
base = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai'
target_dir = os.path.join(base, r'data\gaussian_training\images\室内_办公')
os.makedirs(target_dir, exist_ok=True)

# 源图片（已确认存在的2张办公类高清图）
src_dir = r'C:\Users\Administrator\Desktop\设计数据库\效果图\室内效果图\办公'
src1 = os.path.join(src_dir, '1.jpg')
src2 = os.path.join(src_dir, '2.jpg')

# 复制并重命名为脚本可识别的0000.jpg/0001.jpg
shutil.copy(src1, os.path.join(target_dir, '0000.jpg'))
shutil.copy(src2, os.path.join(target_dir, '0001.jpg'))

print('✅ 图片准备完成：')
print(f'  目标目录：{target_dir}')
print(f'  文件列表：{os.listdir(target_dir)}')
