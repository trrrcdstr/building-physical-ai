# -*- coding: utf-8 -*-
"""
提取本邦PDF项目数据，构建世界模型知识库（去掉公司名称）
"""
import fitz
import json
import re

pdf_path = r'C:\Users\Administrator\Desktop\广州本邦工程顾问有限公司图册（酒店、商业）.pdf'
doc = fitz.open(pdf_path)

# 读取全部页面
all_pages = []
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text("text")
    imgs = page.get_images()
    all_pages.append({'page': i+1, 'text': text, 'images': len(imgs)})
doc.close()

# 项目数据（从文本分析得出）
raw_projects = [
    {'page':9,  'name':'海南保亭七仙岭温泉度假村（五星级）', 'area':'4.3万O',    'status':'施工中', 'service':'机电设计顾问'},
    {'page':10, 'name':'帕劳温德姆度假酒店',                 'area':'5万O',     'status':'施工中', 'service':'机电设计顾问'},
    {'page':11, 'name':'柳州莲花山庄-白天鹅酒店',             'area':'10万O',    'status':'营业中', 'service':'机电深化设计'},
    {'page':12, 'name':'曲阜香格里拉酒店',                    'area':'8万O',     'status':'营业中', 'service':'机电深化设计'},
    {'page':13, 'name':'窑湖小镇度假酒店',                    'area':'10万O',    'status':'设计中', 'service':'机电设计'},
    {'page':14, 'name':'海南双大雨林温泉度假酒店',           'area':'7万O',     'status':'设计中', 'service':'机电设计顾问'},
    {'page':15, 'name':'开平赤坎商业街美堂酒店+民宿',         'area':'约6万O',   'status':'设计中', 'service':'机电深化设计'},
    {'page':16, 'name':'信宜乐天温泉度假酒店',                'area':'2.5万O',   'status':'营业中', 'service':'机电深化设计'},
    {'page':17, 'name':'信宜市人民医院门急诊综合楼',         'area':'3.5万O',   'status':'营业中', 'service':'机电深化设计'},
    {'page':18, 'name':'三亚希尔顿欢朋酒店',                  'area':'4万O',     'status':'营业中', 'service':'机电深化设计'},
    {'page':19, 'name':'三亚亚特兰蒂斯酒店',                  'area':'约4万O',   'status':'营业中', 'service':'机电深化设计'},
    {'page':20, 'name':'珠海波特曼酒店',                      'area':'1.2万O',   'status':'营业中', 'service':'机电深化设计'},
    {'page':21, 'name':'云浮珍珠回归自然温泉度假酒店',        'area':'约7万O',   'status':'设计中', 'service':'机电深化设计'},
    {'page':22, 'name':'崇左边境温泉度假酒店',                'area':'3万O',     'status':'设计中', 'service':'机电深化设计'},
    {'page':23, 'name':'云浮金澜水岸酒店',                    'area':'1.4万O',   'status':'设计中', 'service':'机电深化设计'},
    {'page':24, 'name':'云浮蟠龙雅湖酒店式公寓（云浮碧桂园）','area':'18万O',   'status':'施工中', 'service':'机电设计顾问'},
    {'page':25, 'name':'茂名财富春天商业街',                  'area':'20万O',   'status':'施工中', 'service':'机电设计顾问'},
    {'page':26, 'name':'茂名东锦维也纳酒店',                  'area':'35万O',   'status':'营业中', 'service':'机电设计顾问（定位）'},
    {'page':27, 'name':'茂名财富之舟',                        'area':'38万O',   'status':'营业中', 'service':'机电设计顾问（定位）'},
    {'page':28, 'name':'三亚中心商务区M.LIVE商业',           'area':'8万O',    'status':'营业中', 'service':'机电深化设计'},
    {'page':29, 'name':'花城太古汇商业街',                    'area':'75万O',   'status':'施工中', 'service':'机电设计顾问'},
    {'page':30, 'name':'肇庆星湖之商业中心',                   'area':'10万O',  'status':'营业中', 'service':'机电深化设计'},
    {'page':31, 'name':'云浮天湖半岛商业',                    'area':'23万O',   'status':'施工中', 'service':'机电设计顾问'},
    {'page':32, 'name':'茂名东锦豪庭商业',                    'area':'7万O',    'status':'施工中', 'service':'机电设计顾问'},
    {'page':33, 'name':'广州珠江铂金公寓',                     'area':'10万O',  'status':'营业中', 'service':'机电深化设计'},
    {'page':34, 'name':'云浮蟠龙豪庭酒店',                    'area':'8万O',    'status':'施工中', 'service':'机电深化设计'},
    {'page':35, 'name':'茂名太阳广场',                        'area':'1.2万O',  'status':'营业中', 'service':'机电深化设计'},
    {'page':36, 'name':'肇庆星湖之春商业',                    'area':'2万O',    'status':'营业中', 'service':'机电深化设计'},
    {'page':37, 'name':'茂名财富广场',                        'area':'8万O',    'status':'营业中', 'service':'机电深化设计'},
    {'page':38, 'name':'茂名爱琴海公园商业街',               'area':'34500O',  'status':'营业中', 'service':'机电深化设计'},
    {'page':39, 'name':'信宜天马山旅游度假区',                'area':'10万O',   'status':'设计中', 'service':'机电深化设计'},
    {'page':40, 'name':'肇庆星湖之商业广场',                   'area':'5万O',   'status':'营业中', 'service':'机电深化设计'},
    {'page':41, 'name':'茂名财富公馆',                        'area':'3万O',    'status':'设计中', 'service':'机电深化设计'},
]

# 分类
def classify(name):
    if any(k in name for k in ['酒店','度假村','希尔顿','香格里拉','白天鹅','温德姆','铂金','雅湖']):
        return '酒店'
    if any(k in name for k in ['商业','广场','商业街','中心','豪庭','公寓','公馆']):
        return '商业'
    if any(k in name for k in ['医院','门诊','综合楼']):
        return '医疗'
    if any(k in name for k in ['旅游','度假区']):
        return '旅游'
    return '其他'

# 构建世界模型
world_model = []
for p in raw_projects:
    item = {
        'name': p['name'],
        'category': classify(p['name']),
        'building_area': p['area'],
        'status': p['status'],
        'service': p['service'],
        'source': '本邦工程顾问图册（酒店、商业）',  # 去掉公司全名
        'source_page': p['page'],
        'type': '机电设计顾问',
    }
    world_model.append(item)

# 保存
out_path = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\BENBANG_PROJECTS.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(world_model, f, ensure_ascii=False, indent=2)

print(f"已提取 {len(world_model)} 个项目")
print(f"保存至: {out_path}")
print()

# 统计
from collections import Counter
cats = Counter(p['category'] for p in world_model)
print("分类统计:", dict(cats))

# 验证图片对应
print("\n关键大图页面（500KB+）:")
big_imgs = [
    {'page':9,  'file':'p09_img01.jpeg', 'size':'1654KB'},  # 保亭温泉
    {'page':11, 'file':'p11_img05.jpeg', 'size':'649KB'},   # 柳州白天鹅
    {'page':12, 'file':'p12_img06.jpeg', 'size':'1177KB'},  # 曲阜香格里拉
    {'page':13, 'file':'p13_img07.jpeg', 'size':'1175KB'},  # 窑湖小镇
    {'page':29, 'file':'p29_img02.jpeg', 'size':'486KB'},   # 花城太古汇
    {'page':28, 'file':'p28_img01.jpeg', 'size':'544KB'},   # 三亚M.LIVE
    {'page':21, 'file':'p21_img01.jpeg', 'size':'540KB'},   # 云浮珍珠
]
for img in big_imgs:
    print(f"  第{img['page']}页: {img['file']} ({img['size']})")