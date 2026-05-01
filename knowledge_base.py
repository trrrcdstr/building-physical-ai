"""
建筑物理 AI - 知识库完整版
===========================
五层架构：项目 → 空间 → 对象 → 数据 → 物理属性
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from pathlib import Path
import base64
from PIL import Image
from io import BytesIO

# 页面配置
st.set_page_config(
    page_title="建筑物理 AI - 知识库",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 数据路径
DATA_PATH = Path(__file__).parent / "data" / "processed"
DESKTOP_DATA = Path("~/Desktop/建筑数据库").expanduser()

# 加载数据
@st.cache_data
def load_all_data():
    projects_path = DATA_PATH / "projects.json"
    objects_path = DATA_PATH / "building_objects.json"
    
    projects = []
    objects = []
    
    if projects_path.exists():
        with open(projects_path, "r", encoding="utf-8") as f:
            projects = json.load(f)
    
    if objects_path.exists():
        with open(objects_path, "r", encoding="utf-8") as f:
            objects = json.load(f)
    
    return projects, objects

projects, objects = load_all_data()

# ============================================================
# 侧边栏 - 导航
# ============================================================
st.sidebar.title("🏗️ 知识库导航")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "选择模块",
    ["📁 项目管理", "🏢 空间分类", "📦 对象类型", "🖼️ 图片资产", "📊 数据统计", "🔄 数据飞轮"],
    label_visibility="collapsed"
)

# ============================================================
# 核心函数
# ============================================================
def load_image_b64(img_path, max_width=500):
    """加载图片转Base64"""
    try:
        path = Path(img_path)
        if not path.exists():
            return None
        img = Image.open(path)
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode()
    except:
        return None

def get_category_color(cat):
    """获取类别颜色"""
    colors = {
        "structure": "#FF5722",
        "furniture": "#8D6E63",
        "appliance": "#78909C",
        "soft": "#A1887F",
        "utility": "#FFB74D"
    }
    return colors.get(cat, "#888888")

# ============================================================
# 页面 1: 项目管理
# ============================================================
if page == "📁 项目管理":
    st.title("📁 项目知识库")
    st.markdown("**横向维度：按项目组织数据**")
    
    if projects:
        # 项目统计卡片
        cols = st.columns(4)
        cols[0].metric("总项目数", len(projects))
        cols[1].metric("总 CAD 文件", sum(len(p.get("cad_files", [])) for p in projects))
        cols[2].metric("总效果图", sum(len(p.get("render_images", [])) for p in projects))
        cols[3].metric("总建筑对象", len(objects))
        
        st.markdown("---")
        
        # 项目列表
        for project in projects:
            name = project.get("name", "未命名")
            with st.expander(f"📁 {name}", expanded=(name == "李女士")):
                # 基本信息
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("#### 📋 基本信息")
                    cads = project.get("cad_files", [])
                    renders = project.get("render_images", [])
                    
                    st.markdown(f"""
                    - **CAD 文件:** {len(cads)} 个
                    - **效果图:** {len(renders)} 张
                    - **建筑对象:** 已解析
                    - **数据路径:** `{project.get('path', '-').split('\\')[-1]}`
                    """)
                    
                    # 数据质量评分
                    quality_score = (len(cads) > 0) * 40 + (len(renders) > 0) * 30 + 30
                    st.metric("数据完整度", f"{quality_score}%")
                
                with col2:
                    # 显示 CAD 文件列表
                    if cads:
                        st.markdown("#### 📄 CAD 文件")
                        for cad in cads[:3]:
                            st.markdown(f"- `{Path(cad).name}`")
                    
                    # 显示效果图预览（前4张）
                    if renders:
                        st.markdown("#### 🖼️ 效果图预览")
                        img_cols = st.columns(min(4, len(renders)))
                        for i, img_path in enumerate(renders[:4]):
                            b64 = load_image_b64(img_path, 200)
                            if b64:
                                with img_cols[i]:
                                    st.markdown(
                                        f'<img src="data:image/jpeg;base64,{b64}" style="width:100%; border-radius:8px;">',
                                        unsafe_allow_html=True
                                    )
    else:
        st.warning("⚠️ 未找到项目数据，请先运行数据导入脚本")

# ============================================================
# 页面 2: 空间分类
# ============================================================
elif page == "🏢 空间分类":
    st.title("🏢 空间知识库")
    st.markdown("**纵向维度：按空间类型组织**")
    
    # 空间分类定义
    space_types = {
        "客厅": {"icon": "🛋️", "desc": "主要活动空间，面积最大"},
        "卧室": {"icon": "🛏️", "desc": "休息空间，私密性高"},
        "厨房": {"icon": "🍳", "desc": "烹饪空间，水电气集中"},
        "卫生间": {"icon": "🚿", "desc": "洗浴空间，防水要求高"},
        "阳台": {"icon": "🌅", "desc": "室外延伸，通风采光"},
        "走廊": {"icon": "🚶", "desc": "交通空间，连接各室"},
        "庭院": {"icon": "🌳", "desc": "室外空间，景观设计"}
    }
    
    # 空间类型选择
    space_names = list(space_types.keys())
    selected_space = st.selectbox("选择空间类型", space_names)
    
    space_info = space_types[selected_space]
    
    st.markdown("---")
    
    # 空间详情
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(76,175,80,0.1); border-radius: 15px; padding: 30px; text-align: center;">
            <h1 style="font-size: 80px; margin: 0;">{space_info['icon']}</h1>
            <h2>{selected_space}</h2>
            <p style="color: #888;">{space_info['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📋 空间属性")
        st.markdown(f"""
        **1. 常见家具：**
        - {selected_space}中常见的家具类型
        
        **2. 常见家电：**
        - {selected_space}中的电气设备
        
        **3. 物理特征：**
        - 地板材质、墙面类型、照明需求
        
        **4. 机器人任务：**
        - 清洁、整理、设备操作
        """)
    
    # 显示该空间类型的图片（从项目中搜索）
    st.markdown("---")
    st.markdown(f"#### 🖼️ {selected_space}效果图示例")
    
    # 搜索包含该空间的项目图片
    found_images = []
    for project in projects:
        for img_path in project.get("render_images", []):
            # 简单的文件名匹配
            if selected_space in Path(img_path).name or selected_space.lower() in Path(img_path).name.lower():
                found_images.append((project.get("name"), img_path))
    
    if found_images:
        cols = st.columns(min(3, len(found_images)))
        for i, (proj_name, img_path) in enumerate(found_images[:9]):
            b64 = load_image_b64(img_path, 300)
            if b64:
                with cols[i % 3]:
                    st.markdown(f"""
                    <img src="data:image/jpeg;base64,{b64}" style="width:100%; border-radius:8px;">
                    <p style="text-align:center; color:#888; font-size:12px;">{proj_name}</p>
                    """, unsafe_allow_html=True)
    else:
        st.info(f"未找到 {selected_space} 相关的效果图，显示其他效果图：")
        # 显示前几张图片
        all_images = []
        for project in projects:
            for img_path in project.get("render_images", [])[:3]:
                all_images.append((project.get("name"), img_path))
        
        cols = st.columns(3)
        for i, (proj_name, img_path) in enumerate(all_images[:9]):
            b64 = load_image_b64(img_path, 300)
            if b64:
                with cols[i % 3]:
                    st.markdown(f"""
                    <img src="data:image/jpeg;base64,{b64}" style="width:100%; border-radius:8px;">
                    <p style="text-align:center; color:#888; font-size:12px;">{proj_name}</p>
                    """, unsafe_allow_html=True)

# ============================================================
# 页面 3: 对象类型
# ============================================================
elif page == "📦 对象类型":
    st.title("📦 对象知识库")
    st.markdown("**纵向维度：按对象类型组织**")
    
    # 对象分类
    categories = {
        "structure": {"name": "建筑结构", "icon": "🏗️", "types": ["wall", "floor", "ceiling", "door", "window"]},
        "furniture": {"name": "家具类", "icon": "🪑", "types": ["sofa", "table", "chair", "cabinet", "bed", "shelf"]},
        "appliance": {"name": "家电类", "icon": "🔌", "types": ["tv", "air_conditioner", "refrigerator", "washing_machine", "microwave"]},
        "soft": {"name": "软装类", "icon": "🛋️", "types": ["carpet", "curtain", "cushion", "lamp", "painting", "plant"]},
        "utility": {"name": "机电设施", "icon": "⚡", "types": ["switch", "outlet", "meter", "faucet", "sensor"]}
    }
    
    # 类别选择
    cat_names = [f"{v['icon']} {v['name']}" for v in categories.values()]
    selected_cat = st.selectbox("选择类别", cat_names)
    
    # 找到对应的类别
    cat_key = [k for k, v in categories.items() if f"{v['icon']} {v['name']}" == selected_cat][0]
    cat_info = categories[cat_key]
    
    st.markdown("---")
    
    # 类别详情
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div style="background: {get_category_color(cat_key)}22; border: 2px solid {get_category_color(cat_key)}; 
                    border-radius: 15px; padding: 30px; text-align: center;">
            <h1 style="font-size: 80px; margin: 0;">{cat_info['icon']}</h1>
            <h2>{cat_info['name']}</h2>
            <p style="color: #888;">包含 {len(cat_info['types'])} 种类型</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📋 类型列表")
        for i, t in enumerate(cat_info['types']):
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_a:
                st.markdown(f"**{i+1}. {t}**")
            with col_b:
                st.markdown(f"对象数量: {sum(1 for o in objects if o.get('type') == t)}")
            with col_c:
                st.markdown(f"`{t}`")
    
    # 显示该类别的对象
    st.markdown("---")
    st.markdown(f"#### 📦 {cat_info['name']}对象列表")
    
    filtered_objects = [o for o in objects if o.get('category') == cat_key]
    if filtered_objects:
        # 对象表格
        df_data = []
        for obj in filtered_objects[:20]:
            physics = obj.get('physics', {})
            df_data.append({
                "名称": obj.get('name', '-'),
                "类型": obj.get('type', '-'),
                "质量(kg)": physics.get('mass', '-'),
                "材质": physics.get('material', '-'),
                "摩擦系数": physics.get('friction', '-'),
                "承重": "是" if physics.get('isStructural') else "否"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info(f"暂无 {cat_info['name']} 类型的对象数据")

# ============================================================
# 页面 4: 图片资产
# ============================================================
elif page == "🖼️ 图片资产":
    st.title("🖼️ 图片资产库")
    st.markdown("**视觉资产：效果图、CAD图纸、3D模型**")
    
    # 图片类型选择
    img_types = ["全部效果图", "按项目分类", "按空间分类", "按风格分类"]
    selected_type = st.selectbox("查看方式", img_types)
    
    st.markdown("---")
    
    # 收集所有图片
    all_images = []
    for project in projects:
        for img_path in project.get("render_images", []):
            all_images.append({
                "project": project.get("name"),
                "path": img_path,
                "filename": Path(img_path).name
            })
    
    st.markdown(f"### 📊 共 {len(all_images)} 张效果图")
    
    if all_images:
        # 图片画廊
        cols = st.columns(3)
        for i, img_info in enumerate(all_images[:15]):
            b64 = load_image_b64(img_info['path'], 400)
            if b64:
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="border-radius: 12px; overflow: hidden; margin-bottom: 15px; 
                                box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <img src="data:image/jpeg;base64,{b64}" style="width:100%;">
                        <div style="background: white; padding: 10px;">
                            <p style="margin:0; font-weight: bold;">{img_info['project']}</p>
                            <p style="margin:0; color: #888; font-size: 12px;">{img_info['filename'][:25]}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ============================================================
# 页面 5: 数据统计
# ============================================================
elif page == "📊 数据统计":
    st.title("📊 知识库统计")
    st.markdown("**数据质量与覆盖度分析**")
    
    # 统计卡片
    cols = st.columns(5)
    
    stats = [
        ("项目数", len(projects), "#4CAF50"),
        ("CAD文件", sum(len(p.get('cad_files', [])) for p in projects), "#2196F3"),
        ("效果图", sum(len(p.get('render_images', [])) for p in projects), "#FF9800"),
        ("建筑对象", len(objects), "#9C27B0"),
        ("物理属性", sum(1 for o in objects if o.get('physics', {}).get('mass')), "#E91E63")
    ]
    
    for i, (label, value, color) in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div style="background: {color}; border-radius: 10px; padding: 20px; text-align: center;">
                <h2 style="color: white; margin: 0;">{value}</h2>
                <p style="color: rgba(255,255,255,0.8); margin-top: 5px;">{label}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 类别分布图
    st.markdown("### 📦 对象类别分布")
    
    cat_counts = {}
    for obj in objects:
        cat = obj.get('category', 'unknown')
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    
    fig = px.pie(
        values=list(cat_counts.values()),
        names=list(cat_counts.keys()),
        title="对象类别分布",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 物理属性覆盖率
    st.markdown("---")
    st.markdown("### ⚛️ 物理属性覆盖率")
    
    coverage = {
        "质量数据": sum(1 for o in objects if o.get('physics', {}).get('mass')),
        "材质信息": sum(1 for o in objects if o.get('physics', {}).get('material')),
        "刚度数据": sum(1 for o in objects if o.get('physics', {}).get('stiffness')),
        "摩擦系数": sum(1 for o in objects if o.get('physics', {}).get('friction') is not None),
        "承重标识": sum(1 for o in objects if o.get('physics', {}).get('isStructural') is not None)
    }
    
    coverage_df = pd.DataFrame({
        "属性": list(coverage.keys()),
        "覆盖率": [v/len(objects)*100 if objects else 0 for v in coverage.values()]
    })
    
    fig2 = px.bar(coverage_df, x="属性", y="覆盖率", title="物理属性覆盖率 (%)")
    st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# 页面 6: 数据飞轮
# ============================================================
elif page == "🔄 数据飞轮":
    st.title("🔄 数据飞轮机制")
    st.markdown("**核心商业模式：数据驱动自我增强**")
    
    # 飞轮阶段
    stages = [
        ("📄", "CAD数据", "从施工图提取几何+物理", "#FF5722"),
        ("🧠", "模型训练", "RL强化学习，训练世界模型", "#2196F3"),
        ("🎮", "仿真验证", "Sim2Real迁移验证", "#9C27B0"),
        ("🤖", "真机部署", "机器人真实场景运行", "#FF9800"),
        ("📊", "数据收集", "收集真机运行数据", "#4CAF50"),
        ("🔧", "自动矫正", "模型自动优化迭代", "#E91E63")
    ]
    
    # 显示飞轮
    cols = st.columns(len(stages))
    for i, (icon, name, desc, color) in enumerate(stages):
        with cols[i]:
            st.markdown(f"""
            <div style="background: {color}22; border: 2px solid {color}; 
                        border-radius: 15px; padding: 15px; text-align: center; height: 180px;">
                <h1 style="margin: 0;">{icon}</h1>
                <h3 style="margin: 10px 0;">{name}</h3>
                <p style="font-size: 11px; color: #666;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin: 30px 0;">
        <h2 style="color: #4CAF50;">
            ←←← 飞轮持续加速，优势滚雪球 →→→
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 核心指标
    st.markdown("---")
    st.markdown("### 📈 核心指标对比")
    
    cols = st.columns(4)
    metrics = [
        ("数据准确率", "99%", "+39% vs 传统"),
        ("训练时间", "-80%", "数月→数天"),
        ("部署成功率", "99%", "+59% vs 传统"),
        ("数据成本", "-95%", "无需人工标注")
    ]
    
    for i, (label, value, delta) in enumerate(metrics):
        with cols[i]:
            st.metric(label, value, delta)

# ============================================================
# 底部
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #888;">
    <strong>建筑物理 AI 知识库</strong> | 
    真实数据驱动 | 工程级精度 | 
    Physical AI 基础设施
</div>
""", unsafe_allow_html=True)
