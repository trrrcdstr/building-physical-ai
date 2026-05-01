"""
建筑物理 AI - 融资路演幻灯片
============================
Slide 1: 封面
Slide 2: 市场痛点
Slide 3: 项目定位
Slide 4: 解决方案
Slide 5: 技术架构
Slide 6: 世界模型核心能力
Slide 7: AI Agent 核心能力
Slide 8: OpenClaw 执行中枢
Slide 9: 核心技术壁垒
Slide 10: 应用场景
Slide 11: 商业模式
Slide 12: 竞争优势
Slide 13: 发展规划
"""
import streamlit as st
from pathlib import Path

# 页面配置
st.set_page_config(page_title="融资路演 | 建筑物理 AI", page_icon="🏗️", layout="wide")

# 幻灯片样式
st.markdown("""
<style>
.slide {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 20px;
    padding: 60px;
    margin: 20px 0;
    min-height: 600px;
}
.slide-title {
    color: white;
    font-size: 42px;
    margin-bottom: 30px;
}
.slide-subtitle {
    color: #888;
    font-size: 20px;
}
.slide-content {
    color: #ddd;
    font-size: 18px;
    line-height: 1.8;
}
.highlight {
    color: #4CAF50;
    font-weight: bold;
}
.section-title {
    background: rgba(76,175,80,0.2);
    border-left: 4px solid #4CAF50;
    padding: 15px 20px;
    border-radius: 8px;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Slide 1: 封面
# ============================================================
st.markdown("""
<div class="slide" style="text-align: center; display: flex; flex-direction: column; justify-content: center;">
    <h1 style="color: white; font-size: 56px; margin-bottom: 20px;">
        🏗️ 建筑物理 AI 操作系统
    </h1>
    <p style="color: #4CAF50; font-size: 24px; margin-bottom: 40px;">
        基于世界模型 + AI Agent + OpenClaw 的工程智能平台
    </p>
    <hr style="border-color: #333; margin: 40px 0;">
    <p style="color: #888; font-size: 18px;">
        Physical AI 时代建筑场景基础设施
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 2: 市场痛点
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">😰 市场痛点</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 40px;">
        <div class="section-title">
            <h3 style="color: #FF5722;">❌ 建筑/工程缺乏统一物理常识模型</h3>
            <p class="slide-content">每个系统都独立运行，无法共享空间和物理认知</p>
        </div>
        
        <div class="section-title">
            <h3 style="color: #FF5722;">❌ 数字孪生只"看"不能"推演"</h3>
            <p class="slide-content">停留在可视化层面，无法进行物理仿真和预测</p>
        </div>
        
        <div class="section-title">
            <h3 style="color: #FF5722;">❌ 机器人/设备无法理解建筑空间逻辑</h3>
            <p class="slide-content">缺乏空间规则和物理常识，落地困难</p>
        </div>
        
        <div class="section-title">
            <h3 style="color: #FF5722;">❌ 施工仿真成本高、周期长、不可泛化</h3>
            <p class="slide-content">传统方法依赖大量人工标注，难以规模化</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 3: 项目定位
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">🎯 项目定位</h2>
    
    <div style="text-align: center; margin: 60px 0;">
        <h1 style="color: #4CAF50; font-size: 48px; margin-bottom: 30px;">
            建筑领域 Physical AI 基础设施提供商
        </h1>
        
        <div style="background: rgba(255,255,255,0.05); border-radius: 20px; padding: 40px; max-width: 800px; margin: 0 auto;">
            <p class="slide-content" style="font-size: 22px;">
                <span class="highlight">不做硬件</span>，专注<span class="highlight">世界模型</span>与<span class="highlight">AI 执行系统</span>，
            </p>
            <p class="slide-content" style="font-size: 22px;">
                为<span class="highlight">建筑</span>、<span class="highlight">施工</span>、<span class="highlight">机器人</span>提供物理常识大脑。
            </p>
        </div>
    </div>
    
    <div style="display: flex; justify-content: space-around; margin-top: 50px;">
        <div style="text-align: center;">
            <h2 style="color: #2196F3;">🌐</h2>
            <p style="color: white;">世界模型</p>
        </div>
        <div style="text-align: center;">
            <h2 style="color: #FF9800;">🤖</h2>
            <p style="color: white;">AI Agent</p>
        </div>
        <div style="text-align: center;">
            <h2 style="color: #9C27B0;">⚡</h2>
            <p style="color: white;">执行引擎</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 4: 解决方案
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">💡 解决方案：三大核心能力</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 30px; margin-top: 50px;">
        <div style="background: rgba(255,87,34,0.2); border: 2px solid #FF5722; 
                    border-radius: 20px; padding: 40px; text-align: center;">
            <h1 style="font-size: 72px; margin: 0;">🌐</h1>
            <h3 style="color: #FF5722; margin: 20px 0;">1. 建筑空间世界模型</h3>
            <p class="slide-content">从 CAD 施工图构建工程级精度的物理世界模型</p>
        </div>
        
        <div style="background: rgba(33,150,243,0.2); border: 2px solid #2196F3; 
                    border-radius: 20px; padding: 40px; text-align: center;">
            <h1 style="font-size: 72px; margin: 0;">🤖</h1>
            <h3 style="color: #2196F3; margin: 20px 0;">2. 任务智能体 AI Agent</h3>
            <p class="slide-content">理解任务、规划路径、执行控制的智能决策大脑</p>
        </div>
        
        <div style="background: rgba(156,39,176,0.2); border: 2px solid #9C27B0; 
                    border-radius: 20px; padding: 40px; text-align: center;">
            <h1 style="font-size: 72px; margin: 0;">⚡</h1>
            <h3 style="color: #9C27B0; margin: 20px 0;">3. 标准化执行引擎 OpenClaw</h3>
            <p class="slide-content">统一的任务调度与执行闭环系统</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 5: 技术架构
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">🔧 技术架构（纯软件）</h2>
    
    <div style="margin: 40px 0;">
        <!-- 应用层 -->
        <div style="background: rgba(76,175,80,0.2); border: 2px solid #4CAF50; 
                    border-radius: 15px; padding: 25px; text-align: center; margin-bottom: 20px;">
            <h3 style="color: #4CAF50; margin: 0;">🎯 应用层：建筑数字孪生 | 施工仿真 | 机器人调度</h3>
        </div>
        <div style="text-align: center; color: #4CAF50; font-size: 24px;">↓</div>
        
        <!-- 超级智能体 -->
        <div style="background: rgba(156,39,176,0.2); border: 2px solid #9C27B0; 
                    border-radius: 15px; padding: 25px; text-align: center; margin-bottom: 20px;">
            <h3 style="color: #9C27B0; margin: 0;">🧠 超级智能体：建筑物理 AI 操作系统</h3>
        </div>
        <div style="text-align: center; color: #9C27B0; font-size: 24px;">↓</div>
        
        <!-- 具身智能 -->
        <div style="background: rgba(33,150,243,0.2); border: 2px solid #2196F3; 
                    border-radius: 15px; padding: 25px; text-align: center; margin-bottom: 20px;">
            <h3 style="color: #2196F3; margin: 0;">🤖 具身智能：AI Agent + OpenClaw 执行引擎</h3>
        </div>
        <div style="text-align: center; color: #2196F3; font-size: 24px;">↓</div>
        
        <!-- 世界模型 -->
        <div style="background: rgba(255,87,34,0.2); border: 2px solid #FF5722; 
                    border-radius: 15px; padding: 25px; text-align: center; margin-bottom: 20px;">
            <h3 style="color: #FF5722; margin: 0;">🌐 世界模型：建筑物理世界模型</h3>
        </div>
        <div style="text-align: center; color: #FF9800; font-size: 24px;">↓</div>
        
        <!-- 数据层 -->
        <div style="background: rgba(255,152,0,0.2); border: 2px solid #FF9800; 
                    border-radius: 15px; padding: 25px; text-align: center;">
            <h3 style="color: #FF9800; margin: 0;">📥 数据层：CAD施工图 | 效果图 | 物理属性 | 环境交互 | 场景扩展</h3>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 6: 世界模型核心能力
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">🌐 世界模型核心能力</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 50px;">
        <div style="background: rgba(255,87,34,0.1); border-radius: 15px; padding: 30px;">
            <h3 style="color: #FF5722;">🏗️ 建筑 3D 空间理解</h3>
            <p class="slide-content">从 CAD 施工图提取毫米级精度的空间结构</p>
        </div>
        
        <div style="background: rgba(255,87,34,0.1); border-radius: 15px; padding: 30px;">
            <h3 style="color: #FF5722;">⚛️ 物理规则学习</h3>
            <p class="slide-content">注入刚度、摩擦、承重等真实物理属性</p>
        </div>
        
        <div style="background: rgba(255,87,34,0.1); border-radius: 15px; padding: 30px;">
            <h3 style="color: #FF5722;">🔮 动态预测与仿真</h3>
            <p class="slide-content">时序推演，预测物体运动轨迹</p>
        </div>
        
        <div style="background: rgba(255,87,34,0.1); border-radius: 15px; padding: 30px;">
            <h3 style="color: #FF5722;">⏱️ 时空一致性重建</h3>
            <p class="slide-content">4D 世界模型，时间维度连续一致</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 7: AI Agent
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">🤖 AI Agent —— 智能决策大脑</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 50px;">
        <div class="section-title">
            <h3 style="color: #2196F3;">📋 任务自动拆解</h3>
            <p class="slide-content">将复杂任务分解为可执行的原子动作序列</p>
        </div>
        
        <div class="section-title">
            <h3 style="color: #2196F3;">🔗 因果推理</h3>
            <p class="slide-content">理解动作与结果的因果关系，避免错误决策</p>
        </div>
        
        <div class="section-title">
            <h3 style="color: #2196F3;">🧪 反事实模拟</h3>
            <p class="slide-content">在执行前模拟多种方案，选择最优路径</p>
        </div>
        
        <div class="section-title">
            <h3 style="color: #2196F3;">🗺️ 自主规划路径</h3>
            <p class="slide-content">结合空间约束和物理规则生成安全路径</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 8: OpenClaw
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">⚡ OpenClaw —— 物理 AI 执行中枢</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 20px; margin-top: 50px;">
        <div style="background: rgba(156,39,176,0.1); border-radius: 15px; padding: 30px; text-align: center;">
            <h1 style="font-size: 48px; margin: 0;">🔄</h1>
            <h4 style="color: #9C27B0; margin: 15px 0;">任务流调度</h4>
            <p class="slide-content" style="font-size: 14px;">多任务并发编排</p>
        </div>
        
        <div style="background: rgba(156,39,176,0.1); border-radius: 15px; padding: 30px; text-align: center;">
            <h1 style="font-size: 48px; margin: 0;">🔌</h1>
            <h4 style="color: #9C27B0; margin: 15px 0;">硬件/系统对接</h4>
            <p class="slide-content" style="font-size: 14px;">标准化接口集成</p>
        </div>
        
        <div style="background: rgba(156,39,176,0.1); border-radius: 15px; padding: 30px; text-align: center;">
            <h1 style="font-size: 48px; margin: 0;">📊</h1>
            <h4 style="color: #9C27B0; margin: 15px 0;">状态监控</h4>
            <p class="slide-content" style="font-size: 14px;">实时反馈闭环</p>
        </div>
        
        <div style="background: rgba(156,39,176,0.1); border-radius: 15px; padding: 30px; text-align: center;">
            <h1 style="font-size: 48px; margin: 0;">🎮</h1>
            <h4 style="color: #9C27B0; margin: 15px 0;">仿真执行闭环</h1>
            <p class="slide-content" style="font-size: 14px;">虚实无缝迁移</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 9: 核心技术壁垒
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">🛡️ 核心技术壁垒</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 50px;">
        <div style="background: linear-gradient(135deg, #4CAF50, #2E7D32); 
                    border-radius: 20px; padding: 40px;">
            <h3 style="color: white; margin-top: 0;">🏗️ 建筑专业知识 + AI 深度融合</h3>
            <p class="slide-content">30年建筑行业经验与前沿 AI 技术的完美结合</p>
        </div>
        
        <div style="background: linear-gradient(135deg, #2196F3, #1565C0); 
                    border-radius: 20px; padding: 40px;">
            <h3 style="color: white; margin-top: 0;">🌐 世界模型 + Agent + 执行引擎三位一体</h3>
            <p class="slide-content">端到端全栈解决方案，无缝衔接</p>
        </div>
        
        <div style="background: linear-gradient(135deg, #9C27B0, #7B1FA2); 
                    border-radius: 20px; padding: 40px;">
            <h3 style="color: white; margin-top: 0;">🛠️ 工程场景落地经验</h3>
            <p class="slide-content">丰富的真实项目交付经验</p>
        </div>
        
        <div style="background: linear-gradient(135deg, #FF9800, #F57C00); 
                    border-radius: 20px; padding: 40px;">
            <h3 style="color: white; margin-top: 0;">⚡ 不依赖硬件，可快速规模化</h3>
            <p class="slide-content">纯软件方案，轻资产扩张</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 10: 应用场景
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">🎯 应用场景</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 50px;">
        <div class="section-title" style="border-color: #4CAF50;">
            <h3 style="color: #4CAF50;">🏗️ 建筑数字孪生智能推演</h3>
            <p class="slide-content">从"可视化"升级为"可推演"，提前预测问题</p>
        </div>
        
        <div class="section-title" style="border-color: #2196F3;">
            <h3 style="color: #2196F3;">⚠️ 施工安全模拟与风险预判</h3>
            <p class="slide-content">AI 驱动的安全分析，降低事故风险</p>
        </div>
        
        <div class="section-title" style="border-color: #9C27B0;">
            <h3 style="color: #9C27B0;">🔍 工程巡检 AI 任务系统</h3>
            <p class="slide-content">自动化巡检，实时问题识别与上报</p>
        </div>
        
        <div class="section-title" style="border-color: #FF9800;">
            <h3 style="color: #FF9800;">🏠 装修/装配方案自动生成</h3>
            <p class="slide-content">AI 辅助设计，自动生成最优方案</p>
        </div>
        
        <div class="section-title" style="border-color: #FF5722; grid-column: span 2;">
            <h3 style="color: #FF5722;">🤖 机器人任务调度（对接第三方硬件）</h3>
            <p class="slide-content">统一的任务调度平台，兼容多种机器人品牌</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 11: 商业模式
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">💰 商业模式</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 25px; margin-top: 50px;">
        <div style="background: rgba(76,175,80,0.1); border: 2px solid #4CAF50; 
                    border-radius: 20px; padding: 35px; text-align: center;">
            <h1 style="font-size: 48px; margin: 0;">🔌</h1>
            <h3 style="color: #4CAF50; margin: 20px 0;">ToB 授权</h3>
            <p class="slide-content" style="font-size: 15px;">企业级 API</p>
            <p class="slide-content" style="font-size: 15px;">私有化部署</p>
        </div>
        
        <div style="background: rgba(33,150,243,0.1); border: 2px solid #2196F3; 
                    border-radius: 20px; padding: 35px; text-align: center;">
            <h1 style="font-size: 48px; margin: 0;">📋</h1>
            <h3 style="color: #2196F3; margin: 20px 0;">项目制</h3>
            <p class="slide-content" style="font-size: 15px;">建筑/工程</p>
            <p class="slide-content" style="font-size: 15px;">定制化方案</p>
        </div>
        
        <div style="background: rgba(156,39,176,0.1); border: 2px solid #9C27B0; 
                    border-radius: 20px; padding: 35px; text-align: center;">
            <h1 style="font-size: 48px; margin: 0;">☁️</h1>
            <h3 style="color: #9C27B0; margin: 20px 0;">平台服务费</h3>
            <p class="slide-content" style="font-size: 15px;">SaaS 模式</p>
            <p class="slide-content" style="font-size: 15px;">仿真与任务调度</p>
        </div>
        
        <div style="background: rgba(255,152,0,0.1); border: 2px solid #FF9800; 
                    border-radius: 20px; padding: 35px; text-align: center;">
            <h1 style="font-size: 48px; margin: 0;">📦</h1>
            <h3 style="color: #FF9800; margin: 20px 0;">行业解决方案</h3>
            <p class="slide-content" style="font-size: 15px;">垂直行业</p>
            <p class="slide-content" style="font-size: 15px;">打包服务</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 12: 竞争优势
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">⭐ 竞争优势</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 50px;">
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); 
                    border-radius: 20px; padding: 40px; border: 2px solid #4CAF50;">
            <h3 style="color: #4CAF50; margin-top: 0;">🏗️ 建筑 + AI 双基因团队</h3>
            <p class="slide-content">懂建筑、懂 AI、懂落地</p>
        </div>
        
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); 
                    border-radius: 20px; padding: 40px; border: 2px solid #2196F3;">
            <h3 style="color: #2196F3; margin-top: 0;">🌐 世界模型 + Agent + 执行引擎全栈</h3>
            <p class="slide-content">端到端自主可控</p>
        </div>
        
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); 
                    border-radius: 20px; padding: 40px; border: 2px solid #9C27B0;">
            <h3 style="color: #9C27B0; margin-top: 0;">⚡ 不做硬件，轻量化扩张</h3>
            <p class="slide-content">软件定义，快速复制</p>
        </div>
        
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); 
                    border-radius: 20px; padding: 40px; border: 2px solid #FF9800;">
            <h3 style="color: #FF9800; margin-top: 0;">🛠️ 工程落地能力强</h3>
            <p class="slide-content">真实项目交付验证</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# Slide 13: 发展规划
# ============================================================
st.markdown("""
<div class="slide">
    <h2 class="slide-title">🚀 发展规划</h2>
    
    <div style="display: flex; justify-content: space-around; margin-top: 60px;">
        <div style="text-align: center; flex: 1;">
            <div style="background: #FF5722; border-radius: 50%; width: 100px; height: 100px; 
                        display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                <span style="font-size: 36px; color: white;">🚀</span>
            </div>
            <h3 style="color: #FF5722; margin: 20px 0;">短期</h3>
            <div style="background: rgba(255,87,34,0.1); border-radius: 15px; padding: 25px; margin-top: 15px;">
                <p class="slide-content">模型打磨</p>
                <p class="slide-content">标杆客户落地</p>
            </div>
        </div>
        
        <div style="text-align: center; flex: 1;">
            <div style="background: #2196F3; border-radius: 50%; width: 100px; height: 100px; 
                        display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                <span style="font-size: 36px; color: white;">⚡</span>
            </div>
            <h3 style="color: #2196F3; margin: 20px 0;">中期</h3>
            <div style="background: rgba(33,150,243,0.1); border-radius: 15px; padding: 25px; margin-top: 15px;">
                <p class="slide-content">行业标准化接口</p>
                <p class="slide-content">生态合作伙伴</p>
            </div>
        </div>
        
        <div style="text-align: center; flex: 1;">
            <div style="background: #4CAF50; border-radius: 50%; width: 100px; height: 100px; 
                        display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                <span style="font-size: 36px; color: white;">🌟</span>
            </div>
            <h3 style="color: #4CAF50; margin: 20px 0;">长期</h3>
            <div style="background: rgba(76,175,80,0.1); border-radius: 15px; padding: 25px; margin-top: 15px;">
                <p class="slide-content">建筑物理 AI</p>
                <p class="slide-content">基础设施平台</p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 底部
st.markdown("""
<div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #1a1a2e, #16213e); 
            border-radius: 20px; margin-top: 30px;">
    <h2 style="color: white; margin-bottom: 15px;">Physical AI 时代建筑场景基础设施</h2>
    <p style="color: #888; font-size: 18px; margin-bottom: 20px;">
        不是"看懂世界"，而是从工程源头"定义世界"
    </p>
    <p style="color: #4CAF50; font-size: 24px;">
        <strong>让机器人理解建筑空间的物理常识</strong>
    </p>
</div>
""", unsafe_allow_html=True)
