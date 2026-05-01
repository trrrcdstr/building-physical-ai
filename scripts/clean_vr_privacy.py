# -*- coding: utf-8 -*-
"""清理 VR 数据中的公司名字和隐私信息"""
import json
import re

# 读取 VR 数据
with open(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\web-app\public\data\vr_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 统计需要清理的字段
designer_values = set()
for item in data:
    designer = item.get('designer', '')
    if designer and designer.strip():
        designer_values.add(designer)

print('=== designer 字段值统计 ===\n')
for d in sorted(designer_values):
    count = sum(1 for item in data if item.get('designer') == d)
    print(f'  [{count:3d}] {d}')

print(f'\n总计: {len(data)} 条 VR 数据')
print(f'有 designer 的: {sum(1 for item in data if item.get("designer"))} 条')
print(f'无 designer 的: {sum(1 for item in data if not item.get("designer"))} 条')

# 清理函数
def clean_designer(designer):
    """清理设计师字段中的公司名和隐私信息"""
    if not designer:
        return ''
    
    # 移除公司名
    companies = [
        '杭州鑫满天装饰集团建德分公司',
        '杭州鑫满天装饰DESIGN by Sy',
        '杭州鑫满天装饰：',
        '杭州鑫满天装饰公司',
        '杭州鑫满天装饰',
        '鑫满天装饰',
        '桔子空间',
    ]
    
    result = designer
    for company in companies:
        result = result.replace(company, '')
    
    # 移除手机号 (11位数字)
    result = re.sub(r'\d{11}', '', result)
    
    # 清理特殊字符
    result = result.strip(' :：')
    
    return result

# 清理所有数据
cleaned_count = 0
for item in data:
    original = item.get('designer', '')
    cleaned = clean_designer(original)
    if original != cleaned:
        cleaned_count += 1
    item['designer'] = cleaned

# 保存
with open(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\web-app\public\data\vr_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\n=== 清理完成 ===')
print(f'清理了 {cleaned_count} 条 designer 字段')

# 显示清理后的 designer 值
new_designer_values = set()
for item in data:
    d = item.get('designer', '')
    if d and d.strip():
        new_designer_values.add(d)

print(f'\n清理后 designer 字段值:')
for d in sorted(new_designer_values):
    count = sum(1 for item in data if item.get('designer') == d)
    print(f'  [{count:3d}] {d}')
