"""
建筑物理 AI - 核心技术可视化
============================
投资人版本：一页纸核心技术展示
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
from pathlib import Path

# 页面配置
st.set_page_config(page_title="核心技术 | 建筑物理 AI", page_icon="🏗️", layout="wide")

# 自定义样式
st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 20px;
    padding: 40px;
    margin: 20px 0;
    text-align: center;
}
.hero-section h1 {
    color: white;
    font-size: 42px;
    margin-bottom: 10px;
}
.hero-section p {
    color: #888;
    font-size: 18px;
}
.tech-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 15px;
    padding: 25px;
    text-align: center;
}
.tech-card h3 {
    color: white;
    margin-bottom: 10px;
}
.tech-card p {
    color: #aaa;
    font-size: 14px;
}
.flow-box {
    background: rgba(76,175,80,0.1);
    border: 2px solid #4CAF50;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-box {
    background: rgba(33,150,243,0.1);
    border-radius: 10px;
    padding: 15px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 主标题
# ============================================================
st.markdown("""
<div class="hero-section">
    <h1>🏗️ 建筑物理 AI 世界模型</h1>
    <p>让机器人理解建筑空间的物理常识</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# 核心技术架构
# ============================================================
st.markdown("## 🔧 核心技术架构")

# 三列：数据源 → 核心工艺 → 最终形态
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="tech-card" style="border-color: #FF5722;">
        <h3 style="color: #FF5722;">📥 数据源</h3>
        <hr style="border-color: #333;">
        <p>• 全专业施工图</p>
        <p>• 效果图/渲染图</p>
        <p>• 物理属性数据</p>
        <p>• 材质纹理库</p>
        <p>• 光影分析数据</p>
        <p>• 景观设计图</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="tech-card" style="border-color: #4CAF50;">
        <h3 style="color: #4CAF50;">⚙️ 核心工艺</h3>
        <hr style="border-color: #333;">
        <p><b>图纸</b> → <b>结构</b></p>
        <p>↓</p>
        <p><b>结构</b> → <b>视觉</b></p>
        <p>↓</p>
        <p><b>视觉</b> → <b>物理</b></p>
        <p>↓</p>
        <p><b>物理</b> → <b>交互</b></p>
        <p style="color: #4CAF50; margin-top: 15px;">一体化重建</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="tech-card" style="border-color: #2196F3;">
        <h3 style="color: #2196F3;">🎯 最终形态</h3>
        <hr style="border-color: #333;">
        <h2 style="color: white; font-size: 36px; margin: 20px 0;">
            建筑专属<br>4D 视觉世界模型
        </h2>
        <p style="color: #888;">3D空间 + 时间演化</p>
        <p style="color: #888;">+ 物理推演 + 因果逻辑</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 训练方式
# ============================================================
st.markdown("---")
st.markdown("## 🧠 训练方式")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-box">
        <h2 style="color: #FF9800; margin: 0;">RL</h2>
        <p style="color: #888; margin-top: 5px;">强化学习</p>
        <p style="color: #aaa; font-size: 12px;">Reinforcement Learning</p>
        <p style="color: #666; font-size: 11px; margin-top: 10px;">与环境交互<br>最大化奖励</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-box">
        <h2 style="color: #9C27B0; margin: 0;">DL</h2>
        <p style="color: #888; margin-top: 5px;">深度学习</p>
        <p style="color: #aaa; font-size: 12px;">Deep Learning</p>
        <p style="color: #666; font-size: 11px; margin-top: 10px;">多层次特征<br>端到端学习</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-box">
        <h2 style="color: #4CAF50; margin: 0;">CL</h2>
        <p style="color: #888; margin-top: 5px;">因果逻辑</p>
        <p style="color: #aaa; font-size: 12px;">Causal Logic</p>
        <p style="color: #666; font-size: 11px; margin-top: 10px;">物理规则注入<br>可解释推理</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="flow-box" style="margin-top: 30px;">
    <h3>🤖 三位一体训练 = RL + DL + CL</h3>
    <p style="color: #666;">强化学习驱动行为优化 | 深度学习提取特征表示 | 因果逻辑注入物理规则</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 核心壁垒
# ============================================================
st.markdown("---")
st.markdown("## 🛡️ 核心壁垒")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: rgba(76,175,80,0.1); border-left: 4px solid #4CAF50; 
                padding: 20px; border-radius: 8px; height: 180px;">
        <h3 style="color: #4CAF50; margin-top: 0;">🏗️ 建筑行业 Know-how</h3>
        <p style="color: #aaa; font-size: 14px;">
            • 30年建筑行业经验<br>
            • 专业知识积累<br>
            • 工程规范理解<br>
            • 施工工艺认知
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(33,150,243,0.1); border-left: 4px solid #2196F3; 
                padding: 20px; border-radius: 8px; height: 180px;">
        <h3 style="color: #2196F3; margin-top: 0;">🔗 多源数据融合</h3>
        <p style="color: #aaa; font-size: 14px;">
            • CAD + 效果图<br>
            • 结构 + 机电<br>
            • 材质 + 光影<br>
            • 室内 + 景观
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(255,152,0,0.1); border-left: 4px solid #FF9800; 
                padding: 20px; border-radius: 8px; height: 180px;">
        <h3 style="color: #FF9800; margin-top: 0;">⚙️ 物理规则注入</h3>
        <p style="color: #aaa; font-size: 14px;">
            • 刚度/摩擦系数<br>
            • 承重结构约束<br>
            • 电路/水管走向<br>
            • 安全边界条件
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 技术优势对比
# ============================================================
st.markdown("---")
st.markdown("## 📊 技术优势对比")

# 创建一个对比表格
fig = go.Figure()

categories = ['数据准确率', '训练效率', 'Sim2Real迁移', '物理真实性', '部署成本']

# 传统方法
fig.add_trace(go.Scatterpolargauge(
    r=[40, 30, 25, 35, 60],
    theta=categories,
    name='传统方法',
    gauge=dict(
        shape="polygon",
        bgcolor="rgba(255,0,0,0.1)",
        bordercolor="red",
        borderwidth=2
    )
))

# 我们的方法
fig.add_trace(go.Scatterpolargauge(
    r=[99, 95, 98, 99, 15],
    theta=categories,
    name='我们的方法',
    gauge=dict(
        shape="polygon",
        bgcolor="rgba(0,255,0,0.1)",
        bordercolor="#4CAF50",
        borderwidth=2
    )
))

fig.update_layout(
    title="性能雷达图",
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]
        )
    ),
    showlegend=True,
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 数据飞轮
# ============================================================
st.markdown("---")
st.markdown("## 🔄 数据飞轮（商业模式）")

# 飞轮
stages = [
    ("📄", "CAD数据", "施工图解析"),
    ("🧠", "模型训练", "RL+DL+CL"),
    ("🎮", "仿真验证", "Sim2Real"),
    ("🤖", "真机部署", "机器人运行"),
    ("📊", "数据收集", "反馈闭环"),
    ("🔧", "自动矫正", "持续优化")
]

cols = st.columns(len(stages))
for i, (icon, name, desc) in enumerate(stages):
    with cols[i]:
        st.markdown(f"""
        <div style="background: {'#4CAF50' if i == 0 else '#333'}22; 
                    border: 2px solid #4CAF50; border-radius: 12px; 
                    padding: 15px; text-align: center;">
            <h2>{icon}</h2>
            <p style="font-weight: bold; color: white; margin: 5px 0;">{name}</p>
            <p style="color: #888; font-size: 12px;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin: 20px 0; padding: 15px; 
            background: linear-gradient(90deg, transparent, #4CAF5022, transparent);">
    <h3 style="color: #4CAF50;">飞轮一旦启动，优势持续扩大</h3>
    <p style="color: #888;">更多部署 → 更多数据 → 模型更准 → 成本更低 → 更多客户</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 核心指标
# ============================================================
st.markdown("---")
st.markdown("## 📈 核心指标")

col1, col2, col3, col4 = st.columns(4)

metrics = [
    ("99%", "数据准确率", "+39%"),
    ("-80%", "训练时间", "vs 传统"),
    ("99%", "部署成功率", "+59%"),
    ("-95%", "数据成本", "无需标注")
]

cols_list = [col1, col2, col3, col4]
for i, (value, label, delta) in enumerate(metrics):
    with cols_list[i]:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4CAF50, #2E7D32); 
                    border-radius: 15px; padding: 25px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 42px;">{value}</h1>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0;">{label}</p>
            <p style="color: rgba(255,255,255,0.6); font-size: 12px;">{delta}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 底部
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 30px; background: #1a1a2e; border-radius: 15px; margin-top: 30px;">
    <h2 style="color: white; margin-bottom: 10px;">Physical AI 时代建筑场景基础设施</h2>
    <p style="color: #888;">
        从工程源头定义世界 | 让机器人理解物理常识 | 虚实零迁移损耗
    </p>
    <p style="color: #4CAF50; margin-top: 20px; font-size: 18px;">
        <strong>不是"看懂世界"，而是从工程源头"定义世界"</strong>
    </p>
</div>
""", unsafe_allow_html=True)
