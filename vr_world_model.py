"""
建筑物理 AI - VR 世界模型展示
===============================
将效果图链接、VR漫游整合到机器人大脑
"""
import streamlit as st
import json
from pathlib import Path
import webbrowser

# 页面配置
st.set_page_config(page_title="VR 世界模型 | 建筑物理 AI", page_icon="🏗️", layout="wide")

# VR 数据
VR_LINKS = [
    {"id": "vr-001", "name": "VR漫游 1", "url": "https://vr.justeasy.cn/view/1718680457xw3007-1758796618.html", "platform": "Justeasy"},
    {"id": "vr-002", "name": "VR漫游 2", "url": "https://vr.3d66.com/vr/index_detail_7562631.asp", "platform": "3D66"},
    {"id": "vr-003", "name": "VR漫游 3", "url": "https://vr.justeasy.cn/view/1755u7gc330z71t7-1756400719.html", "platform": "Justeasy"},
    {"id": "vr-004", "name": "VR漫游 4", "url": "https://vr.3d66.com/vr/index_detail_6492015.asp", "platform": "3D66"},
    {"id": "vr-005", "name": "VR漫游 5", "url": "https://vr.3d66.com/vr/index_detail_1065244.asp", "platform": "3D66"},
    {"id": "vr-006", "name": "VR漫游 6", "url": "https://vr.justeasy.cn/view/1g73lx28bi6s7018-1758796696.html", "platform": "Justeasy"},
    {"id": "vr-007", "name": "VR漫游 7", "url": "https://vr.justeasy.cn/view/1g97301di687n244-1730343238.html", "platform": "Justeasy"},
]

# 项目数据
PROJECTS = [
    {"name": "山水庭院", "vr_count": 1, "render_count": 0, "cad_count": 1},
    {"name": "李女士", "vr_count": 0, "render_count": 13, "cad_count": 1},
    {"name": "王总", "vr_count": 0, "render_count": 10, "cad_count": 1},
    {"name": "覃总", "vr_count": 0, "render_count": 11, "cad_count": 1},
]

# 样式
st.markdown("""
<style>
.main-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 20px;
    padding: 40px;
    margin: 20px 0;
}
.vr-card {
    background: rgba(255,255,255,0.05);
    border: 2px solid #4CAF50;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
}
.vr-card:hover {
    background: rgba(76,175,80,0.1);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 主标题
# ============================================================
st.markdown("""
<div class="main-card" style="text-align: center;">
    <h1 style="color: white; font-size: 48px; margin-bottom: 15px;">
        🌐 建筑物理 AI 世界模型
    </h1>
    <p style="color: #888; font-size: 20px;">
        效果图 + VR漫游 + CAD施工图 + 物理属性 = 机器人大脑
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# 数据来源
# ============================================================
st.markdown("## 📥 世界模型数据来源")

col1, col2, col3, col4 = st.columns(4)

sources = [
    ("📄", "CAD施工图", "4 个文件", "#FF5722"),
    ("🖼️", "效果图", "34 张图片", "#2196F3"),
    ("🎥", "VR漫游", "7 个链接", "#9C27B0"),
    ("⚛️", "物理属性", "151 个对象", "#4CAF50")
]

for i, (icon, title, count, color) in enumerate(sources):
    with [col1, col2, col3, col4][i]:
        st.markdown(f"""
        <div class="main-card" style="border-top: 4px solid {color};">
            <h1 style="font-size: 48px; margin: 0;">{icon}</h1>
            <h3 style="color: {color};">{title}</h3>
            <p style="color: #888; font-size: 24px;">{count}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# VR 漫游链接
# ============================================================
st.markdown("---")
st.markdown("## 🎥 VR 漫游链接（已导入世界模型）")

st.markdown(f"**共 {len(VR_LINKS)} 个 VR 全景漫游**")

cols = st.columns(3)
for i, vr in enumerate(VR_LINKS):
    with cols[i % 3]:
        platform_color = "#9C27B0" if vr["platform"] == "Justeasy" else "#E91E63"
        st.markdown(f"""
        <div class="vr-card">
            <h3 style="color: white; margin-bottom: 10px;">{vr['name']}</h3>
            <p style="color: {platform_color}; font-size: 14px;">{vr['platform']}</p>
            <p style="color: #888; font-size: 12px; word-break: break-all;">{vr['url'][:50]}...</p>
            <a href="{vr['url']}" target="_blank">
                <button style="background: #4CAF50; color: white; border: none; 
                               padding: 10px 20px; border-radius: 8px; cursor: pointer;">
                    🚀 打开 VR
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 项目数据汇总
# ============================================================
st.markdown("---")
st.markdown("## 📁 项目数据汇总")

# 项目表格
import pandas as pd
df = pd.DataFrame(PROJECTS)
st.dataframe(df, use_container_width=True)

# ============================================================
# 世界模型构建流程
# ============================================================
st.markdown("---")
st.markdown("## 🔧 世界模型构建流程")

st.markdown("""
<div class="main-card">
    <div style="display: flex; justify-content: space-around; align-items: center; margin-top: 30px;">
        <div style="text-align: center;">
            <h2 style="color: #FF5722;">📄</h2>
            <p style="color: white;">CAD施工图</p>
            <p style="color: #888; font-size: 12px;">几何尺寸</p>
        </div>
        <div style="color: #4CAF50; font-size: 24px;">→</div>
        <div style="text-align: center;">
            <h2 style="color: #2196F3;">🖼️</h2>
            <p style="color: white;">效果图/VR</p>
            <p style="color: #888; font-size: 12px;">视觉纹理</p>
        </div>
        <div style="color: #4CAF50; font-size: 24px;">→</div>
        <div style="text-align: center;">
            <h2 style="color: #9C27B0;">⚛️</h2>
            <p style="color: white;">物理属性</p>
            <p style="color: #888; font-size: 12px;">材质/摩擦/刚度</p>
        </div>
        <div style="color: #4CAF50; font-size: 24px;">→</div>
        <div style="text-align: center;">
            <h2 style="color: #4CAF50;">🧠</h2>
            <p style="color: white;">世界模型</p>
            <p style="color: #888; font-size: 12px;">机器人大脑</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 底部
# ============================================================
st.markdown("---")
st.markdown("""
<div class="main-card" style="text-align: center;">
    <h2 style="color: white;">🤖 装入机器人大脑</h2>
    <p style="color: #888; margin-top: 15px;">
        VR全景 + CAD几何 + 物理属性 = 建筑物理AI世界模型
    </p>
    <p style="color: #4CAF50; margin-top: 20px; font-size: 18px;">
        <strong>让机器人理解建筑空间的物理常识</strong>
    </p>
</div>
""", unsafe_allow_html=True)
