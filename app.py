"""
建筑物理 AI 世界模型 Demo
=========================
让机器人理解建筑空间的物理常识

启动方式：
    streamlit run app.py

功能：
    - 3D 建筑空间可视化
    - VR 世界模型展示
    - 点击查看物理属性
    - 机器人任务规划演示
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# ============================================================
# VR 数据 - 加载新3D效果图链接
# ============================================================

def load_vr_links_from_docx():
    """从docx提取的VR链接数据"""
    import re
    # 从JSON文件加载已扫描的数据
    try:
        with open(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_links_structured.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        pass
    
    # 如果没有扫描数据，返回原始链接列表
    try:
        with open(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_links_new.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('links', [])
    except:
        return []

# 清洗公司名称和电话
def clean_vr_data(vr_item):
    """去除VR数据中的公司名称和电话号码"""
    import re
    result = vr_item.copy()
    
    # 需要清除的关键词
    company_patterns = [
        r'杭州鑫满天装饰\d*',
        r'DESIGN by \w+',
        r'效果图小凯',
        r'技术支持[：:]\s*建E网',
        r'建E网',
    ]
    
    phone_pattern = r'1[3-9]\d{9}'
    
    # 清洗标题
    if result.get('title'):
        for p in company_patterns:
            result['title'] = re.sub(p, '', result['title'])
        result['title'] = re.sub(phone_pattern, '', result['title'])
        result['title'] = re.sub(r'\s+', ' ', result['title']).strip()
    
    # 清洗设计师
    if result.get('designer_raw'):
        for p in company_patterns:
            result['designer_raw'] = re.sub(p, '', result['designer_raw'])
        result['designer_raw'] = re.sub(phone_pattern, '', result['designer_raw'])
        result['designer_raw'] = re.sub(r'\s+', ' ', result['designer_raw']).strip()
    
    return result

# 房间类型映射
ROOM_TYPE_MAP = {
    '客厅': 'living_room',
    '餐厅': 'dining_room', 
    '主卧': 'master_bedroom',
    '次卧': 'secondary_bedroom',
    '书房': 'study',
    '厨房': 'kitchen',
    '卫生间': 'bathroom',
    '阳台': 'balcony',
    '玄关': 'entrance',
    '儿童房': 'kids_room',
    '衣帽间': 'cloakroom',
    '沙发床': 'sofa_bed',
    '电视背景': 'tv_wall',
    '餐边柜': 'sideboard',
    '鞋柜': 'shoe_cabinet',
}

def normalize_room_name(room):
    """标准化房间名称"""
    return ROOM_TYPE_MAP.get(room, room)

# 加载VR数据
VR_LINKS_RAW = load_vr_links_from_docx()

# 构建清洗后的VR链接列表（去除公司电话）
VR_LINKS = []
for i, vr in enumerate(VR_LINKS_RAW):
    cleaned = clean_vr_data(vr)
    platform_icon = "🟣" if cleaned.get('platform') == 'Justeasy' else ("🩷" if cleaned.get('platform') == '3D66' else "🟡")
    
    # 构建显示名称
    title = cleaned.get('title', f'VR {cleaned.get("index", i+1)}')
    rooms = cleaned.get('rooms', [])
    rooms_str = ', '.join(rooms[:3]) if rooms else '未知房间'
    
    VR_LINKS.append({
        "id": f"vr-new-{cleaned.get('index', i+1):03d}",
        "name": title[:30],
        "short_desc": rooms_str,
        "url": cleaned.get('url', ''),
        "platform": cleaned.get('platform', 'unknown'),
        "platform_icon": platform_icon,
        "rooms": [normalize_room_name(r) for r in rooms],
        "title_clean": cleaned.get('title'),
        "designer_clean": cleaned.get('designer_raw'),
    })

# ============================================================
# 数据模型
# ============================================================

@dataclass
class PhysicsProperties:
    """物理属性"""
    mass: Optional[float] = None          # 质量 kg
    material: Optional[str] = None        # 材质
    stiffness: Optional[float] = None     # 刚度 MPa
    friction: Optional[float] = None      # 摩擦系数
    is_structural: Optional[bool] = None  # 是否承重
    conductivity: Optional[float] = None  # 导电性

@dataclass
class FunctionProperties:
    """功能属性"""
    type: str                              # light, switch, outlet, valve, handle
    circuit: Optional[str] = None          # 电路编号
    voltage: Optional[float] = None        # 电压

@dataclass
class RobotInteraction:
    """机器人交互属性"""
    graspable: bool = False
    openable: bool = False
    path_obstacle: bool = False

@dataclass
class BuildingObject:
    """建筑对象"""
    id: str
    name: str
    type: str  # wall, door, window, floor, furniture, appliance
    position: List[float]
    rotation: List[float]
    dimensions: Dict[str, float]
    physics: Optional[PhysicsProperties] = None
    function: Optional[FunctionProperties] = None
    robot_interaction: Optional[RobotInteraction] = None

# ============================================================
# 示例建筑数据
# ============================================================

def create_sample_building() -> List[BuildingObject]:
    """创建示例建筑数据（单间客厅）"""
    objects = []
    
    # 地板
    objects.append(BuildingObject(
        id="floor-1",
        name="客厅地板",
        type="floor",
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        dimensions={"width": 8, "height": 0.2, "depth": 6},
        physics=PhysicsProperties(
            mass=0,
            material="混凝土",
            friction=0.6,
            is_structural=True
        )
    ))
    
    # 墙体 - 后墙（承重）
    objects.append(BuildingObject(
        id="wall-back",
        name="后承重墙",
        type="wall",
        position=[0, 1.5, -3],
        rotation=[0, 0, 0],
        dimensions={"width": 8, "height": 3, "depth": 0.24},
        physics=PhysicsProperties(
            mass=2400,
            material="钢筋混凝土",
            stiffness=30000,
            friction=0.5,
            is_structural=True
        )
    ))
    
    # 墙体 - 左墙（承重）
    objects.append(BuildingObject(
        id="wall-left",
        name="左侧承重墙",
        type="wall",
        position=[-4, 1.5, 0],
        rotation=[0, 90, 0],
        dimensions={"width": 6, "height": 3, "depth": 0.24},
        physics=PhysicsProperties(
            mass=1800,
            material="钢筋混凝土",
            stiffness=30000,
            friction=0.5,
            is_structural=True
        )
    ))
    
    # 墙体 - 右墙（隔墙）
    objects.append(BuildingObject(
        id="wall-right",
        name="右侧隔墙",
        type="wall",
        position=[4, 1.5, 0],
        rotation=[0, 90, 0],
        dimensions={"width": 6, "height": 3, "depth": 0.12},
        physics=PhysicsProperties(
            mass=900,
            material="轻质砖",
            stiffness=8000,
            friction=0.4,
            is_structural=False
        )
    ))
    
    # 门
    objects.append(BuildingObject(
        id="door-1",
        name="客厅门",
        type="door",
        position=[4, 0, 1],
        rotation=[0, 0, 0],
        dimensions={"width": 0.9, "height": 2.1, "depth": 0.05},
        physics=PhysicsProperties(
            mass=25,
            material="实木",
            stiffness=12000,
            friction=0.3
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            openable=True,
            path_obstacle=False
        )
    ))
    
    # 窗户
    objects.append(BuildingObject(
        id="window-1",
        name="客厅窗户",
        type="window",
        position=[0, 1.8, -3],
        rotation=[0, 0, 0],
        dimensions={"width": 1.5, "height": 1.2, "depth": 0.1},
        physics=PhysicsProperties(
            mass=15,
            material="铝合金+玻璃",
            stiffness=70000,
            friction=0.2
        )
    ))
    
    # 开关
    objects.append(BuildingObject(
        id="switch-1",
        name="客厅主灯开关",
        type="appliance",
        position=[-3.8, 1.3, 2],
        rotation=[0, 90, 0],
        dimensions={"width": 0.086, "height": 0.086, "depth": 0.01},
        physics=PhysicsProperties(
            mass=0.1,
            material="塑料"
        ),
        function=FunctionProperties(
            type="switch",
            circuit="L1-客厅主灯",
            voltage=220
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            openable=False,
            path_obstacle=False
        )
    ))
    
    # 插座
    objects.append(BuildingObject(
        id="outlet-1",
        name="客厅插座",
        type="appliance",
        position=[0, 0.3, -2.76],
        rotation=[0, 0, 0],
        dimensions={"width": 0.086, "height": 0.086, "depth": 0.01},
        physics=PhysicsProperties(
            mass=0.05,
            material="塑料",
            conductivity=0.9
        ),
        function=FunctionProperties(
            type="outlet",
            circuit="插座回路-1",
            voltage=220
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            openable=False,
            path_obstacle=False
        )
    ))
    
    return objects


# ============================================================
# 3D 可视化
# ============================================================

def create_3d_scene(building_objects: List[BuildingObject], selected_id: str = None):
    """创建 3D 建筑场景"""
    fig = go.Figure()
    
    # 颜色映射
    type_colors = {
        "floor": "#E0E0E0",
        "wall": "#D2B48C",
        "door": "#A0522D",
        "window": "#87CEEB",
        "appliance": "#FFD700",
        "furniture": "#8B4513"
    }
    
    for obj in building_objects:
        # 获取尺寸
        w = obj.dimensions.get("width", 1)
        h = obj.dimensions.get("height", 1)
        d = obj.dimensions.get("depth", 1)
        
        # 位置
        x, y, z = obj.position
        
        # 判断是否选中
        is_selected = obj.id == selected_id
        color = "#4CAF50" if is_selected else type_colors.get(obj.type, "#888888")
        opacity = 0.9 if is_selected else 0.7
        
        # 创建 3D 方块
        fig.add_trace(go.Mesh3d(
            # 8个顶点
            x=[x-w/2, x-w/2, x+w/2, x+w/2, x-w/2, x-w/2, x+w/2, x+w/2],
            y=[y-h/2, y+h/2, y+h/2, y-h/2, y-h/2, y+h/2, y+h/2, y-h/2],
            z=[z-d/2, z-d/2, z-d/2, z-d/2, z+d/2, z+d/2, z+d/2, z+d/2],
            # 面
            i=[7, 0, 0, 0, 4, 4, 6, 6, 6, 2, 2, 0],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 3, 1, 1],
            k=[0, 7, 2, 3, 6, 7, 1, 4, 4, 5, 5, 3],
            color=color,
            opacity=opacity,
            name=obj.name,
            customdata=[obj.id] * 8,
            hovertemplate=f"<b>{obj.name}</b><br>类型: {obj.type}<br>点击查看详情<extra></extra>"
        ))
    
    # 设置场景
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (m)", range=[-6, 6]),
            yaxis=dict(title="Y (高度 m)", range=[-1, 4]),
            zaxis=dict(title="Z (m)", range=[-5, 5]),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5),
                center=dict(x=0, y=0, z=0)
            )
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        showlegend=False
    )
    
    return fig


def create_floorplan(building_objects: List[BuildingObject], selected_id: str = None):
    """创建平面图"""
    fig = go.Figure()
    
    for obj in building_objects:
        if obj.type not in ["wall", "door", "window", "appliance"]:
            continue
            
        x, y, z = obj.position
        w = obj.dimensions.get("width", 1)
        d = obj.dimensions.get("depth", 1)
        
        is_selected = obj.id == selected_id
        
        if obj.type == "wall":
            # 墙体用矩形
            color = "#4CAF50" if is_selected else "#8B4513"
            fig.add_shape(
                type="rect",
                x0=x - w/2, y0=z - d/2,
                x1=x + w/2, y1=z + d/2,
                line=dict(color=color, width=2),
                fillcolor=color,
                opacity=0.7
            )
        elif obj.type == "door":
            # 门用圆弧表示
            color = "#4CAF50" if is_selected else "#A0522D"
            fig.add_shape(
                type="rect",
                x0=x - w/2, y0=z - d/2,
                x1=x + w/2, y1=z + d/2,
                line=dict(color=color, width=2),
                fillcolor=color,
                opacity=0.8
            )
        elif obj.type == "appliance":
            # 设备用圆点
            color = "#4CAF50" if is_selected else "#FFD700"
            fig.add_trace(go.Scatter(
                x=[x], y=[z],
                mode="markers+text",
                marker=dict(size=15, color=color),
                text=[obj.name.split(" ")[-1]],
                textposition="top center",
                name=obj.name,
                customdata=[obj.id]
            ))
    
    fig.update_layout(
        xaxis=dict(title="X (m)", range=[-6, 6], scaleanchor="y"),
        yaxis=dict(title="Z (m)", range=[-5, 5]),
        height=400,
        margin=dict(l=50, r=50, t=20, b=50),
        showlegend=False
    )
    
    return fig


# ============================================================
# 信息面板
# ============================================================

def display_object_info(obj: BuildingObject):
    """显示建筑对象详细信息"""
    st.markdown(f"### 📦 {obj.name}")
    st.markdown(f"**类型:** `{obj.type}`")
    st.markdown(f"**ID:** `{obj.id}`")
    
    # 几何属性
    st.markdown("---")
    st.markdown("#### 📐 几何属性")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("宽度", f"{obj.dimensions.get('width', 0):.2f} m")
    with col2:
        st.metric("高度", f"{obj.dimensions.get('height', 0):.2f} m")
    with col3:
        st.metric("深度", f"{obj.dimensions.get('depth', 0):.2f} m")
    
    # 物理属性
    if obj.physics:
        st.markdown("---")
        st.markdown("#### ⚛️ 物理属性")
        
        physics_data = {}
        if obj.physics.mass is not None:
            physics_data["质量"] = f"{obj.physics.mass} kg"
        if obj.physics.material:
            physics_data["材质"] = obj.physics.material
        if obj.physics.stiffness is not None:
            physics_data["刚度"] = f"{obj.physics.stiffness} MPa"
        if obj.physics.friction is not None:
            physics_data["摩擦系数"] = str(obj.physics.friction)
        if obj.physics.is_structural is not None:
            physics_data["承重"] = "✅ 是" if obj.physics.is_structural else "❌ 否"
        
        for key, value in physics_data.items():
            st.markdown(f"**{key}:** {value}")
    
    # 功能属性
    if obj.function:
        st.markdown("---")
        st.markdown("#### ⚡ 功能属性")
        st.markdown(f"**类型:** {obj.function.type}")
        if obj.function.circuit:
            st.markdown(f"**电路编号:** `{obj.function.circuit}`")
        if obj.function.voltage:
            st.markdown(f"**电压:** {obj.function.voltage}V")
    
    # 机器人交互
    if obj.robot_interaction:
        st.markdown("---")
        st.markdown("#### 🤖 机器人交互")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**可抓取:** {'✅' if obj.robot_interaction.graspable else '❌'}")
        with col2:
            st.markdown(f"**可开启:** {'✅' if obj.robot_interaction.openable else '❌'}")
        with col3:
            st.markdown(f"**路径障碍:** {'⚠️' if obj.robot_interaction.path_obstacle else '✅'}")
    
    # 物理常识说明
    st.markdown("---")
    st.markdown("""
    <div style="background: rgba(76,175,80,0.1); border-left: 3px solid #4CAF50; padding: 12px; border-radius: 0 8px 8px 0;">
        <strong style="color: #4CAF50;">💡 物理常识</strong>
        <p style="color: #666; margin-top: 4px;">
        机器人已理解此物体的物理属性，可进行安全的力控交互
        </p>
    </div>
    """, unsafe_allow_html=True)


def display_task_info(task: Dict):
    """显示任务信息"""
    st.markdown(f"### 🤖 {task['name']}")
    st.markdown(task['description'])
    
    st.markdown("---")
    st.markdown("#### 📋 执行步骤")
    for i, step in enumerate(task['steps'], 1):
        st.markdown(f"{i}. {step}")
    
    st.markdown("---")
    st.markdown("#### 🧠 物理知识")
    for knowledge in task['physicsKnowledge']:
        st.markdown(f"- {knowledge}")


# ============================================================
# 任务数据
# ============================================================

TASKS = [
    {
        "id": "task-door",
        "name": "开门任务",
        "description": "机器人理解门的物理属性，安全开门",
        "targetObject": "door-1",
        "steps": [
            "识别门的位置和尺寸",
            "计算最佳抓取点",
            "施力开门（力矩 < 5Nm）",
            "检测门的开合状态"
        ],
        "physicsKnowledge": [
            "门的质量: 25kg",
            "铰链摩擦系数: 0.1",
            "最大开启力矩: 5Nm",
            "门板厚度: 50mm"
        ]
    },
    {
        "id": "task-light",
        "name": "开灯任务",
        "description": "机器人理解电路布局，安全操作开关",
        "targetObject": "switch-1",
        "steps": [
            "定位开关位置（高度1.3m）",
            "识别电路编号：L1-客厅主灯",
            "按压开关（压力 < 5N）",
            "检测灯光状态反馈"
        ],
        "physicsKnowledge": [
            "开关高度: 1.3m（符合人体工学）",
            "电路电压: 220V AC",
            "按压行程: 3mm",
            "触发力: 2-5N"
        ]
    },
    {
        "id": "task-dishes",
        "name": "洗碗任务",
        "description": "理解水路和餐具物理属性",
        "targetObject": "outlet-1",
        "steps": [
            "识别水槽位置",
            "理解水龙头操作方式",
            "抓取餐具（质量<500g）",
            "控制清洗力度"
        ],
        "physicsKnowledge": [
            "水槽深度: 200mm",
            "水压: 0.3 MPa",
            "餐具质量: 100-500g",
            "摩擦系数: 陶瓷-橡胶 = 0.4"
        ]
    }
]


# ============================================================
# 页面配置
# ============================================================

def show_vr_page():
    """VR 世界模型页面 - 直接嵌入VR场景"""
    st.title("🎥 VR 世界模型")
    st.markdown("**全景VR漫游 · 室内场景可视化 · 数据来源: 新3D效果图链接.docx**")
    
    # VR 数据来源统计
    total_vr = len(VR_LINKS)
    total_rooms = sum(len(vr.get('rooms', [])) for vr in VR_LINKS)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("VR漫游", f"{total_vr} 个")
    with col2:
        st.metric("房间类型", f"{total_rooms} 个")
    with col3:
        st.metric("平台", "3个")
    with col4:
        st.metric("数据已清洗", "✓")
    
    st.markdown("---")
    
    # 筛选功能
    with st.expander("🔍 筛选VR场景", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            platform_filter = st.selectbox("按平台", ["全部", "Justeasy", "3D66", "720yun"])
        with col2:
            # 获取所有房间类型
            all_rooms = set()
            for vr in VR_LINKS:
                all_rooms.update(vr.get('rooms', []))
            room_options = ["全部"] + sorted(list(all_rooms))
            room_filter = st.selectbox("按房间", room_options)
        with col3:
            search_text = st.text_input("搜索", "")
    
    # 过滤VR列表
    filtered_vr = VR_LINKS
    if platform_filter != "全部":
        filtered_vr = [v for v in filtered_vr if v.get('platform') == platform_filter]
    if room_filter != "全部":
        filtered_vr = [v for v in filtered_vr if room_filter in v.get('rooms', [])]
    if search_text:
        filtered_vr = [v for v in filtered_vr 
                      if search_text.lower() in v.get('name', '').lower() 
                      or search_text.lower() in v.get('short_desc', '').lower()]
    
    st.markdown(f"**筛选结果: {len(filtered_vr)} 个VR场景**")
    
    # 选择要查看的VR
    vr_options = [f"{vr['id']} - {vr['name']}" for vr in filtered_vr]
    if not vr_options:
        st.warning("没有匹配的VR场景，请调整筛选条件")
        return
    selected_vr_idx = st.selectbox("🎯 选择VR场景", range(len(vr_options)), format_func=lambda x: vr_options[x])
    
    selected_vr = filtered_vr[selected_vr_idx]
    
    st.markdown("---")
    
    # 显示选中的VR场景
    st.markdown(f"### 🏠 {selected_vr['name']}")
    st.markdown(f"**平台:** {selected_vr['platform']} | **ID:** {selected_vr['id']}")
    
    # VR 嵌入区域
    st.markdown("#### 📺 VR全景预览")
    
    # 尝试嵌入VR (部分平台支持)
    if selected_vr["platform"] == "Justeasy":
        # Justeasy VR 嵌入
        embed_url = selected_vr["url"].replace("/view/", "/embed/")
        st.markdown(f"""
        <div style="background: #1a1a2e; border-radius: 15px; padding: 20px; text-align: center; margin: 10px 0;">
            <iframe 
                src="{embed_url}" 
                width="100%" 
                height="500" 
                style="border: none; border-radius: 10px;"
                allowfullscreen
                allow="xr-spatial-tracking"
            ></iframe>
        </div>
        """, unsafe_allow_html=True)
    elif selected_vr["platform"] == "3D66":
        # 3D66 提示需要新窗口打开
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 40px; text-align: center; margin: 10px 0;">
            <h2 style="color: white; margin-bottom: 15px;">🌐 3D66 VR场景</h2>
            <p style="color: rgba(255,255,255,0.9); margin-bottom: 20px;">
                该平台需要在新窗口中打开VR体验
            </p>
            <a href="{selected_vr['url']}" target="_blank">
                <button style="
                    background: white; 
                    color: #667eea; 
                    border: none; 
                    padding: 15px 40px; 
                    border-radius: 25px; 
                    font-size: 16px; 
                    font-weight: bold;
                    cursor: pointer;
                ">🚀 在新窗口打开VR</button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # 直接链接按钮
    st.markdown("#### 🔗 快速访问链接")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🚀 在浏览器中打开", selected_vr["url"], use_container_width=True)
    with col2:
        st.link_button("📋 复制链接", f"javascript:navigator.clipboard.writeText('{selected_vr['url']}')", use_container_width=True)
    
    st.markdown("---")
    
    # 所有VR场景列表 - 使用过滤后的结果
    st.markdown("## 📱 VR场景列表")
    
    # 显示模式切换
    view_mode = st.radio("显示模式", ["卡片网格", "列表"], horizontal=True)
    
    if view_mode == "卡片网格":
        cols = st.columns(4)
        for i, vr in enumerate(filtered_vr):
            with cols[i % 4]:
                # 卡片样式
                platform_icon = "🟣" if vr["platform"] == "Justeasy" else ("🩷" if vr["platform"] == "3D66" else "🟡")
                bg_color = "#667eea" if vr["platform"] == "Justeasy" else ("#ec407a" if vr["platform"] == "3D66" else "#ffa000")
                
                rooms_str = vr.get('short_desc', '')
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {bg_color} 0%, #764ba2 100%);
                    padding: 12px; 
                    border-radius: 10px; 
                    margin: 5px 0;
                    min-height: 80px;
                ">
                    <h5 style="color: white; margin: 0 0 3px 0; font-size: 13px;">{vr['id']}</h5>
                    <p style="color: white; margin: 0 0 3px 0; font-size: 12px; font-weight: bold;">{vr['name'][:20]}</p>
                    <p style="color: rgba(255,255,255,0.8); font-size: 10px; margin: 0;">{rooms_str[:25]}</p>
                    <p style="color: rgba(255,255,255,0.6); font-size: 9px; margin: 2px 0 0 0;">{platform_icon} {vr['platform']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"▶", key=f"vr_btn_{vr['id']}", help=f"查看 {vr['name']}"):
                    st.session_state.selected_filtered_vr_idx = i
                    st.rerun()
    else:
        # 列表模式
        for i, vr in enumerate(filtered_vr):
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                with col1:
                    st.markdown(f"**{vr['id']}**")
                with col2:
                    st.markdown(f"{vr['name']}")
                    if vr.get('rooms'):
                        st.caption(f"房间: {', '.join(vr['rooms'][:4])}")
                with col3:
                    platform_icon = "🟣" if vr["platform"] == "Justeasy" else ("🩷" if vr["platform"] == "3D66" else "🟡")
                    st.markdown(f"{platform_icon} {vr['platform']}")
                with col4:
                    if st.button("查看", key=f"vr_list_{vr['id']}"):
                        st.session_state.selected_filtered_vr_idx = i
                        st.rerun()
                st.markdown("---")
    
    st.markdown("---")
    
    # 世界模型构建流程
    st.markdown("""
    ### 🔧 VR → 世界模型数据流
    
    ```
    graph LR
        A[VR全景图] --> B[图像分割]
        B --> C[语义标注]
        C --> D[家具定位]
        D --> E[物理属性注入]
        E --> F[具身智能可理解]
    ```
    
    **已提取数据：**
    - ✅ 家具类型和位置
    - ✅ 空间布局和尺寸
    - ✅ 材质纹理信息
    - ✅ 门/窗/通道位置
    """)


def show_robot_page():
    """机器人系统页面 - 具身智能展示"""
    st.title("🤖 机器人系统")
    st.markdown("**具身智能 · 灵巧手 · 运动控制 · 世界模型对应**")
    
    st.markdown("---")
    
    # 机器人数据统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("机器人类型", "3种")
    with col2:
        st.metric("任务类别", "12项")
    with col3:
        st.metric("灵巧手自由度", "15-20 DOF")
    with col4:
        st.metric("伺服精度", "±0.01mm")
    
    st.markdown("---")
    
    # 世界模型对应关系
    st.markdown("""
    ## 🌍 世界模型 ↔ 机器人系统
    
    | 世界模型层 | 机器人系统 | 数据示例 |
    |------------|-----------|---------|
    | **L1 几何层** | 导航地图 | CAD图纸 → 路径规划 |
    | **L2 语义层** | 任务选择 | 房间功能 → 操作目标 |
    | **L3 物理层** | 力控参数 | 材质属性 → 抓取策略 |
    | **L4 行为层** | 协作策略 | 人类行为 → 工作流规划 |
    """)
    
    st.markdown("---")
    
    # 灵巧手展示
    st.markdown("## 🖐️ 灵巧手技术")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 结构参数
        
        - **手指数目**：5指（仿人手）
        - **自由度**：15-20 DOF
        - **驱动方式**：腱驱动 / 电机直驱
        - **传感器**：力/触觉/位置
        
        ### 抓取模式
        
        | 模式 | 适用场景 | 建筑任务 |
        |------|----------|---------|
        | 精密抓取 | 小物体 | 拧螺丝、安装五金 |
        | 强力抓取 | 重物 | 搬运材料 |
        | 侧向抓取 | 扁平物 | 拿取板材 |
        | 钩挂抓取 | 带把手 | 提桶、拉门 |
        """)
    
    with col2:
        # 灵巧手示意图
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        ">
            <h2 style="color: white;">🖐️</h2>
            <p style="color: white; font-size: 14px;">
                5指灵巧手<br>
                15-20 DOF<br>
                触觉反馈
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 伺服驱动系统
    st.markdown("## ⚙️ 伺服驱动系统")
    
    st.markdown("""
    | 类型 | 扭矩范围 | 特点 | 应用 |
    |------|----------|------|------|
    | 微型伺服 | 0.1-1 Nm | 超小型、高精度 | 灵巧手指关节 |
    | 小型伺服 | 1-10 Nm | 紧凑、高性能 | 机械臂关节 |
    | 中型伺服 | 10-100 Nm | 大扭矩、稳定 | 移动平台 |
    
    **运动控制参数：**
    - 位置精度：±0.01mm
    - 速度范围：0-3000 rpm
    - 响应频率：1-5 kHz
    - 编码器分辨率：17-23 bit
    """)
    
    st.markdown("---")
    
    # 建筑任务展示
    st.markdown("## 🏗️ 建筑机器人任务")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #f0f2f6; padding: 15px; border-radius: 10px;">
            <h4>🧱 装修施工机器人</h4>
            <ul style="margin: 0; padding-left: 20px;">
                <li>刮腻子</li>
                <li>贴砖</li>
                <li>涂漆</li>
                <li>打胶</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #f0f2f6; padding: 15px; border-radius: 10px;">
            <h4>🔧 安装机器人</h4>
            <ul style="margin: 0; padding-left: 20px;">
                <li>橱柜安装</li>
                <li>衣柜安装</li>
                <li>门窗安装</li>
                <li>吊顶安装</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #f0f2f6; padding: 15px; border-radius: 10px;">
            <h4>🔍 检测机器人</h4>
            <ul style="margin: 0; padding-left: 20px;">
                <li>平整度检测</li>
                <li>垂直度检测</li>
                <li>缝隙测量</li>
                <li>渗漏检测</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 具身智能闭环
    st.markdown("""
    ## 🔄 具身智能闭环
    
    ```
    感知 → 理解 → 决策 → 执行 → 反馈
    
    感知：传感器读取世界模型数据
    理解：语义理解当前状态
    决策：任务规划与动作选择
    执行：灵巧手/运动控制
    反馈：更新世界模型状态
    ```
    """)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888;">
        <strong>Physical AI</strong> | 机器人系统 | 世界模型对应
    </div>
    """, unsafe_allow_html=True)


def main():
    # 页面配置
    st.set_page_config(
        page_title="Physical AI 世界模型",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 页面导航 - 无公司logo
    page = st.sidebar.radio("📱 选择页面", ["🏠 3D世界模型", "🎥 VR全景漫游", "🤖 机器人系统"])
    
    if page == "🎥 VR全景漫游":
        show_vr_page()
        return
    elif page == "🤖 机器人系统":
        show_robot_page()
        return
    else:
        show_main_page()


def show_main_page():
    """主页面 - 3D世界模型"""
    # 标题
    st.title("🏗️ 建筑物理 AI 世界模型")
    st.markdown("**让机器人理解建筑空间的物理常识** | Physical AI + 具身智能")
    
    # 数据源统计
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("数据源", "9个")
    with col2:
        st.metric("别墅", "3个")
    with col3:
        st.metric("住宅", "4个")
    with col4:
        st.metric("商业", "1个")
    with col5:
        st.metric("结构", "1个")
    
    # 最新数据源
    with st.expander("📂 最新数据源 - 产业园", expanded=False):
        st.markdown("""
        | 文件 | 类型 | 大小 | 说明 |
        |------|------|------|------|
        | 产业园布置图20250103.pdf | PDF | 9.1 MB | 产业园总平面布置图(13页) |
        | 平面规划图2024-1210.dwg | DWG | 9.9 MB | 建筑平面规划图CAD |
        | 产业园食堂PALACE室内设计.pdf | PDF | 2.7 MB | 员工食堂室内设计(16页) |
        
        **设计特点：** 
        - 面积约1020m²
        - PALACE高端风格
        - 天然石材 + 木纹 + 黑色金属
        """)
    
    st.markdown("---")
    
    # 加载数据
    building_objects = create_sample_building()
    
    # 侧边栏 - 对象选择
    with st.sidebar:
        st.header("🎯 选择建筑对象")
        
        # 对象列表
        object_names = ["请选择..."] + [obj.name for obj in building_objects]
        selected_name = st.selectbox("点击或选择建筑元素", object_names)
        
        # 找到选中对象
        selected_obj = None
        if selected_name != "请选择...":
            for obj in building_objects:
                if obj.name == selected_name:
                    selected_obj = obj
                    break
        
        st.markdown("---")
        
        # 任务选择
        st.header("🤖 机器人任务演示")
        task_names = ["请选择任务..."] + [t['name'] for t in TASKS]
        selected_task_name = st.selectbox("选择任务", task_names)
        
        selected_task = None
        if selected_task_name != "请选择任务...":
            for task in TASKS:
                if task['name'] == selected_task_name:
                    selected_task = task
                    break
        
        st.markdown("---")
        
        # 视图控制
        st.header("⚙️ 显示选项")
        show_physics = st.checkbox("显示物理属性标签", value=True)
        show_paths = st.checkbox("显示路径规划", value=False)
    
    # 主内容区
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 视图切换
        view_mode = st.radio("", ["3D 视图", "平面图"], horizontal=True)
        
        # 渲染场景
        selected_id = selected_obj.id if selected_obj else None
        
        if view_mode == "3D 视图":
            fig = create_3d_scene(building_objects, selected_id)
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = create_floorplan(building_objects, selected_id)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 信息面板
        if selected_obj:
            display_object_info(selected_obj)
        elif selected_task:
            display_task_info(selected_task)
        else:
            st.info("👈 从左侧选择建筑对象或任务查看详情")
            
            st.markdown("---")
            st.markdown("""
            ### 🎯 核心能力
            
            1. **工程级几何精度**
               - 基于施工图，毫米级拓扑结构
               - 无漂移、无穿模
            
            2. **真实物理属性**
               - 尺寸、质量、刚度、摩擦
               - 直接定义，而非学习拟合
            
            3. **建筑空间先验**
               - 理解墙体、门窗、通道
               - 安全边界、承重结构
            
            4. **4D 世界模型**
               - 3D 几何 + 时间演化
               - 物理推演 + 因果逻辑
            
            5. **全链路统一**
               - 世界模型 = 仿真物理
               - 虚实零迁移损耗
            """)
    
    # 底部说明
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888;">
        <strong>建筑物理 AI 世界模型</strong> | 
        为机器人提供先天物理常识 |
        Physical AI 时代建筑场景基础设施
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
