# 学习路线图

## 第一阶段：JavaScript 基础（1-2周）

### 学习目标
- 掌握 JavaScript 核心语法
- 理解异步编程（Promise, async/await）
- 熟悉 ES6+ 新特性

### 学习资源
- [JavaScript.info](https://zh.javascript.info/) - 最权威的 JS 教程
- [现代 JavaScript 教程](https://es6.ruanyifeng.com/) - ES6 入门

### 实践任务
```javascript
// 任务1：理解变量和函数
function calculateWallMass(density, volume) {
  return density * volume;
}

// 任务2：理解对象和数组
const wall = {
  width: 5,
  height: 3,
  depth: 0.24,
  material: '混凝土',
  getVolume() {
    return this.width * this.height * this.depth;
  }
};

// 任务3：理解异步编程
async function loadBuildingData() {
  const response = await fetch('/api/building');
  const data = await response.json();
  return data;
}
```

---

## 第二阶段：React 基础（1-2周）

### 学习目标
- 理解组件化开发思想
- 掌握 React Hooks（useState, useEffect）
- 学会状态管理

### 学习资源
- [React 官方教程](https://react.dev/learn) - 官方最新教程
- [React 入门](https://www.bilibili.com/video/BV1ZB4y1Z7po) - 视频教程

### 核心概念
```jsx
// 组件
function Wall({ width, height, onClick }) {
  return (
    <mesh onClick={onClick}>
      <boxGeometry args={[width, height, 0.24]} />
      <meshStandardMaterial color="#D2B48C" />
    </mesh>
  );
}

// 状态管理
function App() {
  const [objects, setObjects] = useState([]);
  
  useEffect(() => {
    loadBuildingData().then(setObjects);
  }, []);
  
  return <Scene objects={objects} />;
}
```

---

## 第三阶段：Three.js 3D 渲染（2-3周）

### 学习目标
- 理解 3D 渲染基础概念
- 掌握 Three.js 核心 API
- 学会 @react-three/fiber 集成

### 学习资源
- [Three.js 官方文档](https://threejs.org/docs/)
- [React Three Fiber 教程](https://docs.pmnd.rs/react-three-fiber/getting-started/introduction)
- [Three.js Journey](https://threejs-journey.com/) - 最佳付费课程

### 核心概念
```jsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'

function App() {
  return (
    <Canvas>
      {/* 相机控制 */}
      <OrbitControls />
      
      {/* 光照 */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 10]} />
      
      {/* 3D 对象 */}
      <mesh position={[0, 1.5, -3]}>
        <boxGeometry args={[8, 3, 0.24]} />
        <meshStandardMaterial color="#D2B48C" />
      </mesh>
    </Canvas>
  )
}
```

---

## 第四阶段：Python 后端（1-2周）

### 学习目标
- 掌握 Python 基础语法
- 学会 FastAPI 构建 REST API
- 理解 PDF 解析（PyMuPDF）

### 学习资源
- [Python 教程](https://www.runoob.com/python3/python3-tutorial.html)
- [FastAPI 中文文档](https://fastapi.tiangolo.com/zh/)

### 实践任务
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Wall(BaseModel):
    width: float
    height: float
    material: str

@app.post("/api/wall")
async def create_wall(wall: Wall):
    volume = wall.width * wall.height * 0.24
    mass = volume * 2400  # 混凝土密度
    return {"volume": volume, "mass": mass}
```

---

## 推荐学习顺序

```
Week 1-2: JavaScript 基础
    ↓
Week 3-4: React 基础
    ↓
Week 5-7: Three.js + React Three Fiber
    ↓
Week 8-9: Python + FastAPI
    ↓
Week 10+: 项目实战
```

---

## 学习建议

1. **边学边做**：每学一个概念，立即在项目里实践
2. **小步快跑**：先做最小可用版本，再逐步完善
3. **遇到问题**：学会用 Google + ChatGPT 搜索解决方案
4. **记录笔记**：把学到的知识点写在 `docs/` 目录

---

**下一步**：从 JavaScript 基础开始，或直接跳到项目实战边做边学
