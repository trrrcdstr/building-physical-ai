# 建筑物理 AI 世界模型 Demo

> **目标**：验证机器人理解物理常识，加速 Physical AI 落地，完成天使轮融资

## 项目结构

```
building-physical-ai/
├── web-app/                # Web 前端 Demo（React + Three.js）
│   ├── src/
│   │   ├── components/     # UI 组件
│   │   ├── scenes/         # 3D 场景
│   │   ├── data/           # 建筑数据
│   │   └── utils/          # 工具函数
│   └── package.json
├── cad-parser/             # CAD 解析服务（Python）
│   ├── parsers/            # PDF/DWG 解析器
│   ├── extractors/         # 物理属性提取
│   └── api/                # FastAPI 接口
├── physics-engine/         # 物理计算模块
│   ├── properties/         # 物理属性库
│   └── simulation/         # 物理仿真
├── data/                   # 建筑数据库（从桌面同步）
│   ├── raw/                # 原始文件（CAD、效果图）
│   └── processed/          # 处理后的结构化数据
└── docs/                   # 学习笔记和文档
```

## 技术栈

| 模块 | 技术 | 学习难度 |
|------|------|----------|
| 前端 | React + Three.js | ⭐⭐⭐ |
| 3D 渲染 | Three.js | ⭐⭐⭐⭐ |
| 后端 | Python FastAPI | ⭐⭐ |
| CAD 解析 | PyMuPDF + 规则引擎 | ⭐⭐⭐ |
| 移动端打包 | Capacitor | ⭐ |

## 开发路线

### Phase 1：基础框架搭建（1-2周）
- [ ] React 项目初始化
- [ ] Three.js 3D 场景基础
- [ ] 建筑数据导入和展示

### Phase 2：建筑空间可视化（2周）
- [ ] 墙体、门窗、地板建模
- [ ] 点击交互和信息面板
- [ ] 效果图贴图映射

### Phase 3：物理属性注入（2周）
- [ ] 物体物理属性定义
- [ ] 属性面板展示
- [ ] 物理常识标注

### Phase 4：机器人任务演示（2周）
- [ ] 路径规划可视化
- [ ] 任务执行动画
- [ ] 物理交互模拟

### Phase 5：移动端打包（1周）
- [ ] Capacitor 打包
- [ ] iOS/Android 测试
- [ ] 演示优化

## 学习资源

### JavaScript / React（前置）
- [JavaScript 基础](https://zh.javascript.info/)
- [React 官方教程](https://react.dev/learn)
- [Three.js 入门](https://threejs.org/docs/index.html#manual/en/introduction/Creating-a-scene)

### Python（CAD 解析）
- [Python 基础](https://www.runoob.com/python3/python3-tutorial.html)
- [PyMuPDF 文档](https://pymupdf.readthedocs.io/)
- [FastAPI 教程](https://fastapi.tiangolo.com/zh/)

---

**下一步**：从 Phase 1 开始，先搭建前端框架
