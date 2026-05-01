"""
手动采集的建筑知识数据

来源: ArchDaily, 谷德设计网, 设计中国等
更新: 2026-04-17
"""

PROJECTS = [
    {
        "title": "7 Unbuilt Houses Shaped by Site, Climate, and Constraints",
        "source": "archdaily",
        "url": "https://www.archdaily.com/1040381/7-unbuilt-houses-shaped-by-site-climate-and-constraints",
        "category": "Residential",
        "description": "探索建筑师如何根据场地、气候和限制条件设计住宅项目，包括紧凑型城市住宅、庭院住宅、坡地住宅等类型。",
        "tags": ["residential", "unbuilt", "courtyard", "site", "climate"],
        "architects": ["NAHE Architects", "Various"],
        "locations": ["Kerala", "Cartagena", "Amman", "Tromsø", "Zwolle"],
        "year": 2026,
    },
    {
        "title": "Tennessee Performing Arts Center",
        "source": "archdaily",
        "url": "https://www.archdaily.com/1040756/big-reveals-design-for-tennessee-performing-arts-center-in-nashville-united-states",
        "category": "Cultural",
        "description": "BIG设计的田纳西表演艺术中心，位于纳什维尔东岸，建筑面积307,000平方英尺，预计2027年开工，2030年完工。",
        "tags": ["cultural", "performing arts", "BIG", "Nashville"],
        "architects": ["BIG – Bjarke Ingels Group", "William Rawn Associates", "HASTING Architecture"],
        "locations": ["Nashville", "Tennessee", "United States"],
        "year": 2026,
    },
    {
        "title": "VIHARA住宅",
        "source": "gooood",
        "url": "https://www.gooood.cn/casa-vihara-by-di-frenna-arquitectos.htm",
        "category": "Residential",
        "description": "墨西哥VIHARA住宅，水与植被中的居住原型。",
        "tags": ["residential", "Mexico", "water", "vegetation"],
        "architects": ["Di Frenna Arquitectos"],
        "locations": ["Mexico"],
        "year": 2026,
    },
    {
        "title": "Masala y Maíz餐厅",
        "source": "gooood",
        "url": "https://www.gooood.cn/masala-y-maiz-by-naso.htm",
        "category": "Interior",
        "description": "墨西哥Masala y Maíz餐厅，材料与光影交织的庭院式餐饮空间。",
        "tags": ["interior", "restaurant", "Mexico", "courtyard"],
        "architects": ["Naso"],
        "locations": ["Mexico"],
        "year": 2026,
    },
    {
        "title": "圣克洛蒂尔德花园露天剧场",
        "source": "gooood",
        "url": "https://www.gooood.cn/theatre-in-the-santa-clotilde-gardens-by-scob.htm",
        "category": "Landscape",
        "description": "加泰罗尼亚圣克洛蒂尔德花园露天剧场，面向大海的剧场。",
        "tags": ["landscape", "theater", "Spain", "garden"],
        "architects": ["scob"],
        "locations": ["Catalonia", "Spain"],
        "year": 2026,
    },
    {
        "title": "有花呢喝处小院",
        "source": "gooood",
        "url": "https://www.gooood.cn/vigorous-blooms-courtyard-by-edge-architects.htm",
        "category": "Residential",
        "description": "大理有花呢喝处小院，边缘计划建筑工作室设计，那个有花的地方。",
        "tags": ["residential", "courtyard", "Dali", "China"],
        "architects": ["边缘计划建筑工作室"],
        "locations": ["大理", "云南", "中国"],
        "year": 2026,
    },
    {
        "title": "崎寻茶所",
        "source": "gooood",
        "url": "https://www.gooood.cn/taymeet-at-dvln-village-by-devolution.htm",
        "category": "Interior",
        "description": "福建厦门崎寻茶所，DEVOLUTION退化建筑设计，海风穿堂的在地茶空间。",
        "tags": ["interior", "tea house", "Xiamen", "China"],
        "architects": ["DEVOLUTION退化建筑"],
        "locations": ["厦门", "福建", "中国"],
        "year": 2026,
    },
    {
        "title": "安吉临溪科创中心",
        "source": "gooood",
        "url": "https://www.gooood.cn/anji-linxi-innovation-center-by-gla-architects.htm",
        "category": "Architecture",
        "description": "浙江湖州安吉临溪科创中心，GLA建筑设计，灵动工场的全维实践。",
        "tags": ["innovation center", "Anji", "Zhejiang"],
        "architects": ["GLA建筑设计"],
        "locations": ["湖州", "安吉", "浙江", "中国"],
        "year": 2026,
    },
    {
        "title": "青岛唐岛湾文化艺术中心",
        "source": "gooood",
        "url": "https://www.gooood.cn/qingdao-tangdao-bay-art-center-by-oi-architects.htm",
        "category": "Cultural",
        "description": "青岛唐岛湾文化艺术中心，圆直建筑，城市与海的交界。",
        "tags": ["cultural", "art center", "Qingdao", "China"],
        "architects": ["圆直建筑"],
        "locations": ["青岛", "山东", "中国"],
        "year": 2026,
    },
    {
        "title": "平山小学拆除重建九年一贯制学校",
        "source": "gooood",
        "url": "https://www.gooood.cn/redevelopment-of-pingshan-elementary-school-into-a-nine-year-integrated-school-by-ccdi-dongxiying-studio.htm",
        "category": "Educational",
        "description": "深圳平山小学拆除重建九年一贯制学校，悉地国际-东西影工作室，桥作为风景的锚固。",
        "tags": ["educational", "school", "Shenzhen", "China"],
        "architects": ["悉地国际-东西影工作室"],
        "locations": ["深圳", "广东", "中国"],
        "year": 2026,
    },
]


# 建筑类型定义
ARCHITECTURE_TYPES = {
    "Residential": {
        "name": "住宅建筑",
        "subtypes": ["独栋别墅", "联排住宅", "公寓", "住宅综合体", "集合住宅"],
        "key_elements": ["卧室", "客厅", "厨房", "卫生间", "阳台", "庭院"],
    },
    "Commercial": {
        "name": "商业建筑",
        "subtypes": ["商场", "办公楼", "酒店", "餐厅", "零售店"],
        "key_elements": ["入口", "营业厅", "办公区", "停车场"],
    },
    "Cultural": {
        "name": "文化建筑",
        "subtypes": ["博物馆", "美术馆", "剧院", "图书馆", "展览馆"],
        "key_elements": ["展厅", "公共空间", "服务设施"],
    },
    "Educational": {
        "name": "教育建筑",
        "subtypes": ["学校", "大学", "培训机构", "图书馆"],
        "key_elements": ["教室", "实验室", "操场", "图书馆"],
    },
    "Landscape": {
        "name": "景观设计",
        "subtypes": ["公园", "广场", "庭院", "滨水空间"],
        "key_elements": ["植物", "硬景", "水景", "灯光"],
    },
    "Interior": {
        "name": "室内设计",
        "subtypes": ["住宅室内", "商业室内", "办公室内", "餐饮室内"],
        "key_elements": ["动线", "灯光", "材质", "色彩"],
    },
}


# 设计风格定义
DESIGN_STYLES = {
    "Modern": {
        "name": "现代简约",
        "characteristics": ["简洁线条", "中性色调", "功能主义", "开放空间"],
    },
    "Nordic": {
        "name": "北欧风格",
        "characteristics": ["自然木色", "舒适温馨", "充足采光", "简洁实用"],
    },
    "NewChinese": {
        "name": "新中式",
        "characteristics": ["传统元素", "现代演绎", "对称布局", "意境营造"],
    },
    "Industrial": {
        "name": "工业风",
        "characteristics": ["原始材质", "暴露结构", "粗犷质感", "复古元素"],
    },
    "Japanese": {
        "name": "日式风格",
        "characteristics": ["原木材质", "榻榻米", "收纳极致", "清雅素淡"],
    },
    "Classical": {
        "name": "欧式古典",
        "characteristics": ["雕花装饰", "华丽线条", "对称布局", "厚重材质"],
    },
}


# 材料定义
MATERIALS = {
    "Wood": {"name": "木材", "properties": ["温暖", "自然", "可再生"]},
    "Stone": {"name": "石材", "properties": ["坚固", "耐久", "高端"]},
    "Metal": {"name": "金属", "properties": ["现代", "轻盈", "可塑"]},
    "Glass": {"name": "玻璃", "properties": ["通透", "现代", "采光"]},
    "Concrete": {"name": "混凝土", "properties": ["粗犷", "工业", "清水"]},
    "Brick": {"name": "砖", "properties": ["传统", "温馨", "可回收"]},
    "Fabric": {"name": "织物", "properties": ["柔软", "温馨", "可更换"]},
}


# 空间设计原则
SPACE_PRINCIPLES = {
    "Flow": {"name": "动线设计", "description": "人流物流的自然流动路径"},
    "Light": {"name": "光影设计", "description": "自然光与人工光的运用"},
    "Scale": {"name": "尺度比例", "description": "人体工程学与空间比例"},
    "Hierarchy": {"name": "空间层次", "description": "开合、过渡、序列"},
    "Rhythm": {"name": "节奏韵律", "description": "重复与变化的美感"},
    "Contrast": {"name": "对比统一", "description": "材质、色彩、尺度的对比与协调"},
}
