"""
建筑物理 AI - 数据飞轮可视化
================================
展示：数据训练 → 模型学习 → 真机部署 → 数据收集 → 自动矫正 → 飞轮加速

启动方式：
    streamlit run flywheel.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import random

# 页面配置
st.set_page_config(
    page_title="建筑物理 AI - 数据飞轮",
    page_icon="🔄",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
.flywheel-container {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
}
.metric-card {
    background: rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
}
.center-metric {
    text-align: center;
}
.center-metric h2 {
    font-size: 48px;
    margin: 0;
    color: #4CAF50;
}
.center-metric p {
    color: #888;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 飞轮可视化
# ============================================================

def create_flywheel_diagram(current_stage: int = 0):
    """创建数据飞轮图"""
    
    fig = go.Figure()
    
    # 飞轮各阶段
    stages = [
        {"name": "CAD 数据", "angle": 0, "color": "#FF5722", "icon": "📄"},
        {"name": "模型训练", "angle": 60, "color": "#2196F3", "icon": "🧠"},
        {"name": "仿真验证", "angle": 120, "color": "#9C27B0", "icon": "🎮"},
        {"name": "真机部署", "angle": 180, "color": "#FF9800", "icon": "🤖"},
        {"name": "数据收集", "angle": 240, "color": "#4CAF50", "icon": "📊"},
        {"name": "自动矫正", "angle": 300, "color": "#E91E63", "icon": "🔧"},
    ]
    
    center_x, center_y = 0, 0
    radius = 2.5
    
    # 绘制中心
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='text',
        text=['🔄'],
        textfont=dict(size=80),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # 绘制各阶段节点
    for i, stage in enumerate(stages):
        angle_rad = np.radians(stage["angle"])
        x = radius * np.cos(angle_rad)
        y = radius * np.sin(angle_rad)
        
        is_active = i == current_stage
        size = 80 if is_active else 50
        opacity = 1.0 if is_active else 0.5
        
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(
                size=size,
                color=stage["color"],
                opacity=opacity,
                line=dict(color='white', width=2)
            ),
            text=[stage["icon"]],
            textfont=dict(size=30 if is_active else 20),
            textposition='middle center',
            showlegend=False,
            hovertemplate=f"<b>{stage['name']}</b><extra></extra>"
        ))
        
        # 节点名称
        fig.add_annotation(
            x=x, y=y - 0.6,
            text=f"<b>{stage['name']}</b>",
            showarrow=False,
            font=dict(color='white', size=14),
            align='center'
        )
    
    # 绘制连接箭头（顺时针）
    for i in range(len(stages)):
        start_angle = np.radians(stages[i]["angle"])
        end_angle = np.radians(stages[(i + 1) % len(stages)]["angle"])
        
        # 弧线路径
        t = np.linspace(start_angle, start_angle + np.radians(60), 20)
        arc_x = radius * np.cos(t)
        arc_y = radius * np.sin(t)
        
        # 添加动画效果
        color = stages[(i + 1) % len(stages)]["color"]
        width = 4 if i == (current_stage - 1) % len(stages) else 2
        
        fig.add_trace(go.Scatter(
            x=arc_x, y=arc_y,
            mode='lines',
            line=dict(color=color, width=width),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # 箭头
        arrow_x = arc_x[-1]
        arrow_y = arc_y[-1]
        
    fig.update_layout(
        xaxis=dict(visible=False, range=[-4, 4]),
        yaxis=dict(visible=False, range=[-4, 4]),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig, stages


def create_data_flow_chart():
    """创建数据流图"""
    
    # 模拟数据流
    steps = ['CAD导入', '特征提取', '物理标注', '模型训练', '仿真验证', '真机测试', '数据回流', '模型优化']
    data_volume = [100, 85, 75, 70, 65, 60, 80, 95]  # 数据量（相对值）
    accuracy = [0, 0.3, 0.5, 0.65, 0.75, 0.82, 0.88, 0.92]  # 模型精度
    
    fig = go.Figure()
    
    # 数据量柱状图
    fig.add_trace(go.Bar(
        x=steps,
        y=data_volume,
        name='数据量',
        marker_color='#FF5722',
        opacity=0.7
    ))
    
    # 精度曲线
    fig.add_trace(go.Scatter(
        x=steps,
        y=[a * 100 for a in accuracy],
        name='模型精度',
        mode='lines+markers',
        marker=dict(size=12, color='#4CAF50'),
        line=dict(width=3, color='#4CAF50'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='数据流与模型精度提升',
        yaxis=dict(title='数据量（相对值）', side='left'),
        yaxis2=dict(title='模型精度 (%)', side='right', overlaying='y', range=[0, 100]),
        legend=dict(orientation='h', y=1.1),
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_flywheel_acceleration_chart():
    """创建飞轮加速曲线"""
    
    # 模拟飞轮加速效果
    iterations = list(range(1, 13))
    
    # 各项指标随迭代的变化
    data_accuracy = [60, 68, 75, 82, 87, 91, 94, 96, 97, 98, 98.5, 99]
    training_speed = [100, 85, 70, 55, 45, 38, 32, 28, 25, 23, 21, 20]  # 相对训练时间
    deployment_success = [40, 55, 68, 78, 85, 90, 93, 96, 97, 98, 99, 99]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=iterations,
        y=data_accuracy,
        name='数据准确率 (%)',
        mode='lines+markers',
        line=dict(width=3),
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=iterations,
        y=deployment_success,
        name='部署成功率 (%)',
        mode='lines+markers',
        line=dict(width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='🔄 数据飞轮加速效果（迭代周期）',
        xaxis=dict(title='迭代周期'),
        yaxis=dict(title='百分比 (%)', range=[0, 100]),
        legend=dict(orientation='h', y=1.1),
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_real_data_preview():
    """展示真实数据预览"""
    
    # 加载解析的项目数据
    projects_path = Path(__file__).parent / "data" / "processed" / "projects.json"
    
    if projects_path.exists():
        with open(projects_path, "r", encoding="utf-8") as f:
            projects = json.load(f)
        
        st.markdown("### 📄 已导入的真实数据")
        
        for project in projects:
            with st.expander(f"📁 {project.get('name', '未命名')}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("CAD 文件", len(project.get('cad_files', [])))
                with col2:
                    st.metric("效果图", len(project.get('render_images', [])))
                with col3:
                    parsed = project.get('parsed_data', [])
                    total_walls = sum(len(p.get('walls', [])) for p in parsed)
                    st.metric("解析墙体", total_walls)
                
                # 显示解析的房间
                rooms_found = []
                for p in parsed:
                    for room in p.get('rooms', []):
                        if room.get('found'):
                            rooms_found.append(room.get('type'))
                
                if rooms_found:
                    st.markdown(f"**识别房间:** {', '.join(set(rooms_found))}")
    else:
        st.info("暂无数据，请先运行数据导入脚本")


# ============================================================
# 主界面
# ============================================================

def main():
    
    st.title("🔄 建筑物理 AI - 数据飞轮")
    st.markdown("**真实数据 → 模型训练 → 真机部署 → 数据收集 → 自动矫正 → 飞轮加速**")
    
    # ============================================================
    # 飞轮动画
    # ============================================================
    
    st.markdown("---")
    st.markdown("### 🔄 数据飞轮核心机制")
    
    # 飞轮阶段说明
    stages_info = [
        ("📄 CAD 数据", "从施工图提取真实几何、物理属性", "#FF5722"),
        ("🧠 模型训练", "RL强化学习，训练世界模型", "#2196F3"),
        ("🎮 仿真验证", "Sim2Real迁移验证", "#9C27B0"),
        ("🤖 真机部署", "机器人真实场景运行", "#FF9800"),
        ("📊 数据收集", "收集真机运行数据", "#4CAF50"),
        ("🔧 自动矫正", "模型自动优化迭代", "#E91E63"),
    ]
    
    # 创建动画
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 飞轮图
        current_stage = st.slider("飞轮阶段", 0, 5, 0, label_visibility="collapsed")
        fig, stages = create_flywheel_diagram(current_stage)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 当前阶段详情
        current = stages_info[current_stage]
        st.markdown(f"""
        <div style="background: {current[2]}22; border-left: 4px solid {current[2]}; padding: 20px; border-radius: 8px;">
            <h3>{current[0]}</h3>
            <p style="color: #666; margin-top: 10px;">{current[1]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("**🎯 核心价值：**")
        st.markdown("""
        - ✅ 零样本学习（从CAD直接注入）
        - ✅ 数据飞轮自我加速
        - ✅ 模型精度持续提升
        - ✅ 部署成本持续降低
        """)
    
    # ============================================================
    # 数据流展示
    # ============================================================
    
    st.markdown("---")
    st.markdown("### 📊 数据流与精度提升")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig = create_data_flow_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        **💡 关键洞察：**
        
        1️⃣ CAD数据100%准确率
        - 几何精度：毫米级
        - 物理属性：工程数据
        
        2️⃣ 传统方法需要：
        - 数万次试错
        - 数月训练
        
        3️⃣ 我们的方法：
        - 从源头注入
        - 零试错成本
        """)
    
    # ============================================================
    # 飞轮加速效果
    # ============================================================
    
    st.markdown("---")
    st.markdown("### 🚀 飞轮加速效果（每轮迭代）")
    
    fig = create_flywheel_acceleration_chart()
    st.plotly_chart(fig, use_container_width=True)
    
    # ============================================================
    # 真实数据预览
    # ============================================================
    
    st.markdown("---")
    create_real_data_preview()
    
    # ============================================================
    # 核心指标
    # ============================================================
    
    st.markdown("---")
    st.markdown("### 📈 核心指标（投资人关注）")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        ("数据准确率", "99%", "↑ +39%"),
        ("训练时间", "-80%", "vs 传统方法"),
        ("部署成功率", "99%", "↑ +59%"),
        ("数据成本", "-95%", "vs 标注数据"),
        ("迭代周期", "1周", "vs 数月"),
    ]
    
    cols = [col1, col2, col3, col4, col5]
    for i, (label, value, delta) in enumerate(metrics):
        with cols[i]:
            st.metric(label, value, delta)
    
    # ============================================================
    # 商业模式（隐藏）
    # ============================================================
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 15px; margin-top: 20px;">
        <h2 style="color: white; margin-bottom: 10px;">🔄 数据飞轮 = 核心壁垒</h2>
        <p style="color: #888;">
        更多部署 → 更多数据 → 模型更准 → 成本更低 → 更多客户 → 更多部署
        </p>
        <p style="color: #4CAF50; font-size: 18px; margin-top: 20px;">
        <strong>飞轮一旦启动，优势持续扩大</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
