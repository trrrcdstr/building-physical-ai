# 快速启动指南

## 环境准备

### 1. 安装 Node.js（前端必需）

**Windows 下载安装：**
https://nodejs.org/zh-cn/ （选择 LTS 版本）

**验证安装：**
```powershell
node -v   # 应显示 v18.x 或更高
npm -v    # 应显示 9.x 或更高
```

### 2. 安装 Python（CAD 解析必需）

**Windows 下载安装：**
https://www.python.org/downloads/ （选择 Python 3.11+）

**⚠️ 安装时勾选 "Add Python to PATH"**

**验证安装：**
```powershell
python --version   # 应显示 Python 3.11.x
pip --version
```

---

## 启动项目

### 方式一：手动启动

#### 1. 启动前端（端口 3000）
```powershell
cd web-app
npm install
npm run dev
```
浏览器打开：http://localhost:3000

#### 2. 启动后端（端口 8000）
```powershell
cd cad-parser
pip install -r requirements.txt
python -m uvicorn api.main:app --reload --port 8000
```
API 文档：http://localhost:8000/docs

---

### 方式二：一键启动（推荐）

创建启动脚本 `start.ps1`：
```powershell
# 启动后端
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd cad-parser; python -m uvicorn api.main:app --reload --port 8000"

# 启动前端
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd web-app; npm run dev"
```

---

## 项目结构

```
building-physical-ai/
├── web-app/                 # 前端（React + Three.js）
│   ├── src/
│   │   ├── components/      # UI 组件
│   │   ├── scenes/          # 3D 场景
│   │   ├── data/            # 建筑数据
│   │   └── store/           # 状态管理
│   └── package.json
├── cad-parser/              # 后端（Python FastAPI）
│   ├── api/
│   │   └── main.py          # API 入口
│   └── requirements.txt
└── docs/                    # 文档
    ├── LEARNING_PATH.md     # 学习路线
    └── QUICKSTART.md        # 本文件
```

---

## 下一步

1. **第一周**：熟悉项目结构，学习 JavaScript 基础
2. **第二周**：理解 React 组件，修改 UI 样式
3. **第三周**：学习 Three.js，添加 3D 建筑元素
4. **第四周**：集成 CAD 解析，真实数据导入

---

## 常见问题

### Q: npm install 报错？
A: 切换国内镜像：
```powershell
npm config set registry https://registry.npmmirror.com
```

### Q: Python pip 安装慢？
A: 切换国内镜像：
```powershell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 浏览器打不开 localhost:3000？
A: 检查防火墙，或尝试 http://127.0.0.1:3000

---

## 技术支持

遇到问题随时问我，我会帮你：
- 调试代码错误
- 解释技术概念
- 优化项目架构
