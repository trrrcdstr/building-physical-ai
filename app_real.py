"""
建筑物理 AI 世界模型 Demo - 真实数据版
======================================
使用用户 CAD 施工图和效果图生成场景

启动方式：
    streamlit run app_real.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import base64
from PIL import Image
from io import BytesIO

# 数据路径
DATA_PATH = Path(__file__).parent / "data" / "processed"
PROJECTS_PATH = DATA_PATH / "projects.json"
OBJECTS_PATH = DATA_PATH / "building_objects.json"
RENDER_IMAGES_BASE = Path("~/Desktop/建筑数据库").expanduser()


# ============================================================
# 数据加载
# ============================================================

@st.cache_data
def load_projects():
    """加载项目数据"""
    if PROJECTS_PATH.exists():
        with open(PROJECTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@st.cache_data
def load_building_objects():
    """加载建筑对象"""
    if OBJECTS_PATH.exists():
        with open(OBJECTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@st.cache_data
def load_image_base64(image_path: str, max_width: int = 600) -> str:
    """加载图片并转为 base64"""
    try:
        path = Path(image_path)
        if not path.exists():
            return None
        img = Image.open(path)
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


# ============================================================
# 3D 场景生成
# ============================================================

def create_3d_scene_from_real_data(objects: List[Dict], selected_id: str = None, project_filter: str = None):
    """从真实数据创建 3D 场景"""
    fig = go.Figure()
    
    # 类别颜色
    category_colors = {
        "structure": {"base": "#C4B5A0", "hover": "#FF5722"},
        "furniture": {"base": "#8D6E63", "hover": "#FF5722"},
        "appliance": {"base": "#78909C", "hover": "#FF5722"},
        "soft": {"base": "#A1887F", "hover": "#FF5722"},
        "utility": {"base": "#FFB74D", "hover": "#FF5722"}
    }
    
    for obj in objects:
        # 过滤项目
        if project_filter and project_filter != "全部":
            if not obj.get("name", "").startswith(project_filter):
                continue
        
        # 获取尺寸
        dims = obj.get("dimensions", {})
        w = dims.get("width", 1)
        h = dims.get("height", 1)
        d = dims.get("depth", 1)
        
        # 位置
        pos = obj.get("position", [0, 0, 0])
        x, y, z = pos[0], pos[1], pos[2]
        
        # 判断是否选中
        is_selected = obj.get("id") == selected_id
        
        cat = obj.get("category", "structure")
        colors = category_colors.get(cat, category_colors["structure"])
        color = colors["hover"] if is_selected else obj.get("color", colors["base"])
        opacity = 1.0 if is_selected else 0.75
        
        # 创建 3D 方块
        fig.add_trace(go.Mesh3d(
            x=[x-w/2, x-w/2, x+w/2, x+w/2, x-w/2, x-w/2, x+w/2, x+w/2],
            y=[y-h/2, y+h/2, y+h/2, y-h/2, y-h/2, y+h/2, y+h/2, y-h/2],
            z=[z-d/2, z-d/2, z-d/2, z-d/2, z+d/2, z+d/2, z+d/2, z+d/2],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 6, 2, 2, 0],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 3, 1, 1],
            k=[0, 7, 2, 3, 6, 7, 1, 4, 4, 5, 5, 3],
            color=color,
            opacity=opacity,
            name=obj.get("name", "未命名"),
            customdata=[obj.get("id")] * 8,
            hovertemplate=f"<b>{obj.get('name', '未命名')}</b><br>类型: {obj.get('type', '-')}<br>类别: {obj.get('category', '-')}<extra></extra>"
        ))
    
    # 设置场景
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (m)", gridcolor="#E0E0E0"),
            yaxis=dict(title="Y 高度 (m)", gridcolor="#E0E0E0"),
            zaxis=dict(title="Z (m)", gridcolor="#E0E0E0"),
            aspectmode="data",
            camera=dict(eye=dict(x=2.5, y=2.0, z=2.5))
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=550,
        showlegend=False
    )
    
    return fig


# ============================================================
# 项目面板
# ============================================================

def display_project_selector(projects: List[Dict]):
    """显示项目选择器"""
    st.markdown("### 📁 项目列表")
    
    project_names = ["全部项目"] + [p.get("name", "未命名") for p in projects]
    selected = st.selectbox("选择项目", project_names, label_visibility="collapsed")
    
    return selected


def display_render_gallery(project: Dict):
    """显示效果图画廊"""
    st.markdown("#### 🖼️ 效果图预览")
    
    render_images = project.get("render_images", [])
    if not render_images:
        st.info("该项目暂无效果图")
        return
    
    # 显示前 6 张
    cols = st.columns(min(3, len(render_images)))
    for i, img_path in enumerate(render_images[:6]):
        b64 = load_image_base64(img_path)
        if b64:
            with cols[i % 3]:
                st.markdown(
                    f'<img src="data:image/jpeg;base64,{b64}" style="width:100%; border-radius:8px; margin-bottom:8px;">',
                    unsafe_allow_html=True
                )
    
    # 显示更多按钮
    if len(render_images) > 6:
        with st.expander(f"查看全部 {len(render_images)} 张效果图"):
            cols = st.columns(4)
            for i, img_path in enumerate(render_images):
                b64 = load_image_base64(img_path)
                if b64:
                    with cols[i % 4]:
                        st.markdown(
                            f'<img src="data:image/jpeg;base64,{b64}" style="width:100%; border-radius:8px; margin-bottom:8px;">',
                            unsafe_allow_html=True
                        )


# ============================================================
# 物理属性面板
# ============================================================

def display_physics_panel(obj: Dict):
    """显示物理属性面板"""
    
    st.markdown(f"### 📦 {obj.get('name', '未命名')}")
    
    # 基本信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("类型", obj.get("type", "-"))
    with col2:
        st.metric("类别", obj.get("category", "-"))
    with col3:
        st.metric("ID", obj.get("id", "-")[:12])
    
    # 尺寸信息
    dims = obj.get("dimensions", {})
    if dims:
        st.markdown("---")
        st.markdown("#### 📐 几何属性")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("宽度", f"{dims.get('width', 0):.3f} m")
        with col2:
            st.metric("高度", f"{dims.get('height', 0):.3f} m")
        with col3:
            st.metric("深度", f"{dims.get('depth', 0):.3f} m")
        
        # 计算体积和质量（如果有密度）
        volume = dims.get("width", 0) * dims.get("height", 0) * dims.get("depth", 0)
        st.metric("体积", f"{volume:.4f} m³")
    
    # 物理属性
    physics = obj.get("physics", {})
    if physics:
        st.markdown("---")
        st.markdown("#### ⚛️ 物理属性")
        
        physics_items = []
        if physics.get("mass"):
            physics_items.append(("质量", f"{physics['mass']:.1f} kg"))
        if physics.get("material"):
            physics_items.append(("材质", physics["material"]))
        if physics.get("stiffness"):
            physics_items.append(("刚度", f"{physics['stiffness']:.0f} MPa"))
        if physics.get("friction") is not None:
            physics_items.append(("摩擦系数", f"{physics['friction']:.2f}"))
        if physics.get("isStructural") is not None:
            physics_items.append(("承重结构", "✅ 是" if physics["isStructural"] else "❌ 否"))
        
        for label, value in physics_items:
            st.markdown(f"**{label}:** {value}")
    
    # 机器人交互
    interaction = obj.get("robot_interaction", {})
    if interaction:
        st.markdown("---")
        st.markdown("#### 🤖 机器人交互")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**可抓取:** {'✅' if interaction.get('graspable') else '❌'}")
        with col2:
            st.markdown(f"**可移动:** {'✅' if interaction.get('movable') else '❌'}")
        with col3:
            st.markdown(f"**可开启:** {'✅' if interaction.get('openable') else '❌'}")
        
        if interaction.get("pathObstacle") is not None:
            st.markdown(f"**路径障碍:** {'⚠️ 是' if interaction['pathObstacle'] else '✅ 否'}")
    
    # 物理常识说明
    st.markdown("---")
    st.markdown("""
    <div style="background: rgba(76,175,80,0.1); border-left: 3px solid #4CAF50; padding: 12px; border-radius: 0 8px 8px 0;">
        <strong style="color: #4CAF50;">💡 工程级精度</strong>
        <p style="color: #666; margin-top: 4px;">
        此数据直接从 CAD 施工图提取，精度达到毫米级。
        机器人可直接使用，无需通过视觉学习估算。
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 统计面板
# ============================================================

def display_stats_panel(projects: List[Dict], objects: List[Dict]):
    """显示统计面板"""
    
    st.markdown("### 📊 数据统计")
    
    # 项目统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("项目数", len(projects))
    with col2:
        total_cads = sum(len(p.get("cad_files", [])) for p in projects)
        st.metric("CAD 文件", total_cads)
    with col3:
        total_renders = sum(len(p.get("render_images", [])) for p in projects)
        st.metric("效果图", total_renders)
    with col4:
        st.metric("建筑对象", len(objects))
    
    st.markdown("---")
    
    # 物理属性覆盖率
    st.markdown("#### ⚛️ 物理属性覆盖率")
    
    has_mass = sum(1 for o in objects if o.get("physics", {}).get("mass"))
    has_material = sum(1 for o in objects if o.get("physics", {}).get("material"))
    has_stiffness = sum(1 for o in objects if o.get("physics", {}).get("stiffness"))
    has_friction = sum(1 for o in objects if o.get("physics", {}).get("friction") is not None)
    
    total = len(objects)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pct = has_mass / total * 100 if total > 0 else 0
        st.metric("质量数据", f"{has_mass}/{total}", f"{pct:.0f}%")
    with col2:
        pct = has_material / total * 100 if total > 0 else 0
        st.metric("材质信息", f"{has_material}/{total}", f"{pct:.0f}%")
    with col3:
        pct = has_stiffness / total * 100 if total > 0 else 0
        st.metric("刚度数据", f"{has_stiffness}/{total}", f"{pct:.0f}%")
    with col4:
        pct = has_friction / total * 100 if total > 0 else 0
        st.metric("摩擦系数", f"{has_friction}/{total}", f"{pct:.0f}%")
    
    # 类别分布
    st.markdown("---")
    st.markdown("#### 📦 类别分布")
    
    categories = {}
    for obj in objects:
        cat = obj.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    df = pd.DataFrame([
        {"类别": k, "数量": v} for k, v in categories.items()
    ])
    
    fig = px.bar(df, x="类别", y="数量", color="类别")
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 主界面
# ============================================================

def main():
    # 页面配置
    st.set_page_config(
        page_title="建筑物理 AI - 真实数据 Demo",
        page_icon="🏗️",
        layout="wide"
    )
    
    # 标题
    st.title("🏗️ 建筑物理 AI 世界模型")
    st.markdown("**真实 CAD 数据驱动** | 工程级几何精度 | Physical AI")
    
    # 加载数据
    projects = load_projects()
    objects = load_building_objects()
    
    if not projects:
        st.error("❌ 未找到数据，请先运行 `python scripts/import_data.py`")
        st.stop()
    
    # 侧边栏
    with st.sidebar:
        st.header("📁 项目选择")
        
        # 项目列表
        project_names = ["全部项目"] + [p.get("name", "未命名") for p in projects]
        selected_project_name = st.selectbox("选择项目", project_names)
        
        # 找到选中项目
        selected_project = None
        if selected_project_name != "全部项目":
            for p in projects:
                if p.get("name") == selected_project_name:
                    selected_project = p
                    break
        
        st.markdown("---")
        
        # 对象选择
        st.header("🔍 建筑对象")
        
        if selected_project_name == "全部项目":
            obj_names = ["请选择..."] + [o.get("name", "未命名") for o in objects[:30]]
        else:
            filtered_objs = [o for o in objects if o.get("name", "").startswith(selected_project_name)]
            obj_names = ["请选择..."] + [o.get("name", "未命名") for o in filtered_objs]
        
        selected_obj_name = st.selectbox("选择对象", obj_names)
        
        # 找到选中对象
        selected_obj = None
        if selected_obj_name != "请选择...":
            for o in objects:
                if o.get("name") == selected_obj_name:
                    selected_obj = o
                    break
    
    # 主内容
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 3D 场景", "🖼️ 效果图", "📋 施工图信息", "📊 统计"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 渲染 3D 场景
            selected_id = selected_obj.get("id") if selected_obj else None
            fig = create_3d_scene_from_real_data(objects, selected_id, selected_project_name)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if selected_obj:
                display_physics_panel(selected_obj)
            else:
                st.info("👈 从左侧选择建筑对象查看物理属性")
    
    with tab2:
        if selected_project:
            display_render_gallery(selected_project)
        else:
            st.info("👈 请先选择一个项目")
    
    with tab3:
        if selected_project:
            st.markdown(f"### 📋 {selected_project.get('name', '未命名')} - 施工图信息")
            
            for i, parsed in enumerate(selected_project.get("parsed_data", [])):
                with st.expander(f"📄 {parsed.get('filename', f'文件{i+1}')}", expanded=(i==0)):
                    # 解析信息
                    walls = parsed.get("walls", [])
                    rooms = parsed.get("rooms", [])
                    doors_windows = parsed.get("doors_windows", [])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("墙体数据", len(walls))
                    with col2:
                        st.metric("房间标注", len(rooms))
                    with col3:
                        st.metric("门窗", len(doors_windows))
                    
                    # 原始文本预览
                    if parsed.get("raw_text"):
                        st.markdown("**提取文本预览:**")
                        st.code(parsed["raw_text"][:500] + "...")
        else:
            st.info("👈 请先选择一个项目")
    
    with tab4:
        display_stats_panel(projects, objects)
    
    # 底部
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888;">
        <strong>建筑物理 AI 世界模型</strong> | 
        真实 CAD 数据 | 工程级精度 | 
        Physical AI 时代建筑场景基础设施
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
