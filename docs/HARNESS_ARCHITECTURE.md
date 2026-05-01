# Building Physical AI - Harness 架构设计

## 核心概念：嵌套演进关系

```
┌─────────────────────────────────────────────────────────────┐
│                      HARNESS（完整系统）                      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                 CONTEXT（信息层）                      │ │
│  │  ┌─────────────────────────────────────────────────┐   │ │
│  │  │           PROMPT（最小单元）                     │   │ │
│  │  │  • 任务指令                                     │   │ │
│  │  │  • 用户意图                                     │   │ │
│  │  │  • 约束条件                                     │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  │                                                         │ │
│  │  + 记忆（Memory）                                       │ │
│  │  + 知识（Knowledge）                                    │ │
│  │  + 工具输出（Tool Output）                              │ │
│  │  + 环境状态（Environment State）                        │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  + 运行时（Runtime）                                        │
│  + 护栏（Guardrails）                                       │
│  + 反馈（Feedback Loop）                                     │
│  + 工具（Tools）                                             │
│  + 存储（Storage）                                          │
│  + 并发管理（Concurrency）                                  │
│  + 监控（Monitoring）                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 第一层：从记事本到管理制度

**问题**：原始状态，无组织，无记录，无追溯

**解决方案**：建立基础结构

```yaml
Layer_1_基础结构:
  Prompt管理:
    - 版本控制：git 追踪每个 prompt 版本
    - 模板库：标准化 prompt 模板
    - 标签系统：任务类型、复杂度、优先级
    
  记忆系统:
    - 短期记忆：session 内 context
    - 长期记忆：MEMORY.md + knowledge base
    - 结构化存储：按日期、项目、任务类型
    
  日志系统:
    - 决策日志：记录每个关键决策
    - 错误日志：记录失败和修复
    - 性能日志：token 使用、响应时间
```

**关键设计**：

```python
class PromptRegistry:
    """Prompt 注册表 - 终结无政府状态的第一步"""
    
    def __init__(self):
        self.registry = {}  # prompt_id -> metadata
        self.version_control = GitBackend()
    
    def register(self, prompt_id: str, template: str, tags: list):
        """注册 prompt 模板"""
        version = self.version_control.commit(template)
        self.registry[prompt_id] = {
            "template": template,
            "version": version,
            "tags": tags,
            "created_at": datetime.now(),
            "usage_count": 0
        }
    
    def get(self, prompt_id: str, variables: dict) -> str:
        """获取渲染后的 prompt"""
        entry = self.registry[prompt_id]
        entry["usage_count"] += 1
        return entry["template"].format(**variables)


class MemorySystem:
    """记忆系统 - 从记事本到结构化存储"""
    
    def __init__(self, workspace: Path):
        self.short_term = {}  # session_id -> context
        self.long_term = MemoryMD(workspace)
        self.knowledge_base = VectorStore(workspace / "knowledge")
    
    def remember(self, session_id: str, key: str, value: Any):
        """存储记忆"""
        if session_id not in self.short_term:
            self.short_term[session_id] = {}
        self.short_term[session_id][key] = value
    
    def recall(self, session_id: str, query: str) -> Any:
        """检索记忆"""
        # 优先短期记忆
        if session_id in self.short_term:
            for k, v in self.short_term[session_id].items():
                if query in k or query in str(v):
                    return v
        
        # 然后长期记忆
        return self.long_term.search(query)
    
    def consolidate(self, session_id: str):
        """短期记忆固化为长期记忆"""
        if session_id in self.short_term:
            for key, value in self.short_term[session_id].items():
                self.long_term.write(key, value)
            del self.short_term[session_id]
```

---

## 第二层：终结无政府状态，走向并发与效率

**问题**：单线程、串行执行、资源浪费

**解决方案**：并发管理与任务调度

```yaml
Layer_2_并发管理:
  任务队列:
    - 优先级队列：紧急任务优先
    - 依赖管理：任务间依赖关系
    - 资源分配：token 预算、模型选择
    
  并发控制:
    - 信号量：控制并发数量
    - 协程池：异步执行
    - 锁机制：防止竞争条件
    
  错误处理:
    - 重试机制：指数退避
    - 降级策略：失败后备方案
    - 熔断器：防止级联失败
```

**关键设计**：

```python
class TaskScheduler:
    """任务调度器 - 并发管理的核心"""
    
    def __init__(self, max_concurrent: int = 5):
        self.queue = asyncio.PriorityQueue()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.dependencies = DependencyGraph()
        self.resource_manager = ResourceManager()
    
    async def submit(self, task: Task, priority: int = 0):
        """提交任务"""
        await self.queue.put((priority, task))
    
    async def run(self):
        """运行调度器"""
        while True:
            priority, task = await self.queue.get()
            
            # 检查依赖是否满足
            if not self.dependencies.is_ready(task):
                await self.queue.put((priority - 1, task))  # 降低优先级重新排队
                continue
            
            # 检查资源是否充足
            if not self.resource_manager.available(task):
                await self.queue.put((priority, task))
                continue
            
            # 并发执行
            asyncio.create_task(self._execute(task))
    
    async def _execute(self, task: Task):
        """执行单个任务"""
        async with self.semaphore:
            try:
                self.resource_manager.allocate(task)
                result = await task.execute()
                self.dependencies.mark_completed(task)
                return result
            except Exception as e:
                await self._handle_error(task, e)
            finally:
                self.resource_manager.release(task)


class SubagentOrchestrator:
    """子代理编排器 - 终结无政府状态"""
    
    def __init__(self):
        self.agents = {}  # agent_id -> agent
        self.sessions = {}  # session_id -> state
        self.lock = asyncio.Lock()
    
    async def spawn(self, task: str, agent_id: str = None) -> str:
        """生成子代理"""
        agent = self.agents.get(agent_id) or self._select_agent(task)
        
        session_id = generate_uuid()
        
        async with self.lock:
            self.sessions[session_id] = {
                "agent": agent,
                "task": task,
                "status": "running",
                "started_at": datetime.now()
            }
        
        # 异步执行
        asyncio.create_task(self._run_agent(session_id, agent, task))
        
        return session_id
    
    async def _run_agent(self, session_id: str, agent: Agent, task: str):
        """运行子代理"""
        try:
            result = await agent.run(task)
            
            async with self.lock:
                self.sessions[session_id]["result"] = result
                self.sessions[session_id]["status"] = "completed"
                
        except Exception as e:
            async with self.lock:
                self.sessions[session_id]["error"] = str(e)
                self.sessions[session_id]["status"] = "failed"
```

---

## 第三层：戳破盲目自信

**问题**：过度信任模型输出、无护栏、无验证

**解决方案**：护栏系统与反馈循环

```yaml
Layer_3_护栏系统:
  输入验证:
    - 意图识别：确保理解正确
    - 权限检查：确保有权限执行
    - 资源限制：防止资源滥用
    
  输出验证:
    - 格式校验：确保输出格式正确
    - 内容审核：敏感内容过滤
    - 安全检查：防止注入攻击
    
  执行护栏:
    - 预检查：执行前检查条件
    - 监控：执行中实时监控
    - 后检查：执行后验证结果
    
  反馈循环:
    - 用户反馈：收集用户评分
    - 自动评估：模型自我评估
    - 持续改进：根据反馈优化
```

**关键设计**：

```python
class GuardrailsSystem:
    """护栏系统 - 戳破盲目自信"""
    
    def __init__(self):
        self.input_validators = []
        self.output_validators = []
        self.execution_guards = []
        self.feedback_collector = FeedbackCollector()
    
    def validate_input(self, prompt: str, context: dict) -> bool:
        """输入验证"""
        for validator in self.input_validators:
            result = validator.validate(prompt, context)
            if not result.passed:
                raise ValidationError(result.message)
        return True
    
    def validate_output(self, output: str, context: dict) -> bool:
        """输出验证"""
        for validator in self.output_validators:
            result = validator.validate(output, context)
            if not result.passed:
                # 尝试修复
                output = validator.repair(output)
                if not output:
                    raise ValidationError(result.message)
        return output
    
    async def execute_with_guard(self, action: Callable, *args, **kwargs):
        """执行护栏包裹的操作"""
        # 预检查
        for guard in self.execution_guards:
            guard.before_execute(*args, **kwargs)
        
        try:
            # 执行
            result = await action(*args, **kwargs)
            
            # 后检查
            for guard in self.execution_guards:
                result = guard.after_execute(result)
            
            return result
            
        except Exception as e:
            for guard in self.execution_guards:
                guard.on_error(e)
            raise


class FeedbackLoop:
    """反馈循环 - 持续改进"""
    
    def __init__(self):
        self.collector = FeedbackCollector()
        self.analyzer = FeedbackAnalyzer()
        self.optimizer = PromptOptimizer()
    
    async def collect(self, session_id: str, feedback_type: str, value: Any):
        """收集反馈"""
        await self.collector.add(session_id, feedback_type, value)
    
    async def analyze(self):
        """分析反馈"""
        insights = await self.analyzer.analyze(self.collector.get_recent())
        return insights
    
    async def optimize(self):
        """优化 prompt"""
        insights = await self.analyze()
        for insight in insights:
            if insight.confidence > 0.8:
                await self.optimizer.apply(insight)


class ConfidenceScorer:
    """置信度评估 - 戳破盲目自信"""
    
    def __init__(self, model):
        self.model = model
        self.threshold = 0.7
    
    async def score(self, output: str, context: dict) -> float:
        """评估输出置信度"""
        # 自我评估
        prompt = f"""
        请评估以下输出的置信度（0-1）：
        
        输出：{output}
        
        上下文：{json.dumps(context, ensure_ascii=False)}
        
        考虑因素：
        1. 信息完整性
        2. 逻辑一致性
        3. 与上下文的关联度
        4. 潜在错误风险
        
        只返回一个 0-1 之间的数字。
        """
        
        response = await self.model.generate(prompt)
        confidence = float(response.strip())
        
        if confidence < self.threshold:
            # 低置信度，触发人工确认
            raise LowConfidenceError(f"置信度过低: {confidence}")
        
        return confidence
```

---

## 第四层：做加法后做减法

**问题**：过度复杂、冗余、难以维护

**解决方案**：优化与简化

```yaml
Layer_4_优化迭代:
  加法阶段（构建）:
    - 添加所有必要组件
    - 完整的功能覆盖
    - 充分的护栏和验证
    
  减法阶段（精简）:
    - 删除冗余组件
    - 合并相似功能
    - 简化调用链
    - 移除过度防护
    
  持续优化:
    - 监控性能指标
    - 识别瓶颈
    - 重构热点
    - 保持最小必要复杂度
```

**关键设计**：

```python
class HarnessProfiler:
    """性能分析器 - 找到做减法的目标"""
    
    def __init__(self):
        self.metrics = {}
        self.call_graph = CallGraph()
    
    def profile(self, func):
        """性能装饰器"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            
            # 记录调用
            call_id = self.call_graph.record_call(func.__name__, args)
            
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start
                
                # 记录指标
                self.metrics[func.__name__] = {
                    "avg_time": self._update_avg(func.__name__, elapsed),
                    "call_count": self._get_count(func.__name__) + 1,
                    "success_rate": self._update_success_rate(func.__name__, True)
                }
                
                return result
            except Exception as e:
                elapsed = time.time() - start
                self.metrics[func.__name__]["success_rate"] = \
                    self._update_success_rate(func.__name__, False)
                raise
    
    def identify_bottlenecks(self) -> List[str]:
        """识别瓶颈 - 做减法的目标"""
        bottlenecks = []
        for func_name, metrics in self.metrics.items():
            if metrics["avg_time"] > 1.0:  # 超过 1 秒
                bottlenecks.append(func_name)
            if metrics["success_rate"] < 0.9:  # 成功率低于 90%
                bottlenecks.append(func_name)
        return bottlenecks


class HarnessOptimizer:
    """优化器 - 做加法后做减法"""
    
    def __init__(self, harness: Harness):
        self.harness = harness
        self.profiler = HarnessProfiler()
        self.config = harness.config
    
    async def optimize(self):
        """自动优化"""
        # 阶段 1：分析当前状态
        bottlenecks = self.profiler.identify_bottlenecks()
        
        # 阶段 2：识别可移除组件
        removable = self._find_redundant_components()
        
        # 阶段 3：执行减法
        for component in removable:
            if self._safe_to_remove(component):
                self.harness.remove(component)
        
        # 阶段 4：验证优化效果
        await self._validate_optimization()
    
    def _find_redundant_components(self) -> List[str]:
        """找到冗余组件"""
        redundant = []
        
        # 检查未使用的工具
        for tool in self.harness.tools:
            if tool.usage_count == 0:
                redundant.append(f"tool:{tool.name}")
        
        # 检查重复的护栏
        for i, guard in enumerate(self.harness.guardrails):
            if self._has_similar_guard(guard, self.harness.guardrails[:i]):
                redundant.append(f"guard:{i}")
        
        return redundant
    
    def _safe_to_remove(self, component: str) -> bool:
        """安全移除检查"""
        # 运行测试套件
        # 确保不会破坏核心功能
        return self.harness.test_suite.can_remove(component)
```

---

## 完整 Harness 架构

```python
class Harness:
    """
    完整 Harness 架构
    
    四层设计：
    1. 基础结构：Prompt + Memory + Log
    2. 并发管理：Scheduler + Orchestrator + Resource
    3. 护栏系统：Guardrails + Feedback + Confidence
    4. 优化迭代：Profiler + Optimizer + Simplifier
    """
    
    def __init__(self, config: HarnessConfig):
        # Layer 1: 基础结构
        self.prompt_registry = PromptRegistry()
        self.memory = MemorySystem(config.workspace)
        self.logger = Logger(config.log_path)
        
        # Layer 2: 并发管理
        self.scheduler = TaskScheduler(config.max_concurrent)
        self.orchestrator = SubagentOrchestrator()
        self.resource_manager = ResourceManager()
        
        # Layer 3: 护栏系统
        self.guardrails = GuardrailsSystem()
        self.feedback = FeedbackLoop()
        self.confidence_scorer = ConfidenceScorer(config.model)
        
        # Layer 4: 优化迭代
        self.profiler = HarnessProfiler()
        self.optimizer = HarnessOptimizer(self)
        
        # Runtime
        self.model = config.model
        self.tools = ToolRegistry()
        self.storage = StorageBackend(config.storage_path)
        
        # 监控
        self.monitor = Monitor(self)
    
    async def run(self, prompt: str, context: dict = None) -> str:
        """执行 prompt"""
        # 1. 输入验证
        self.guardrails.validate_input(prompt, context)
        
        # 2. 增强 context
        enhanced_context = self._enhance_context(prompt, context)
        
        # 3. 生成响应
        response = await self.model.generate(
            prompt=prompt,
            context=enhanced_context,
            tools=self.tools,
            memory=self.memory
        )
        
        # 4. 输出验证
        validated_output = self.guardrails.validate_output(response, context)
        
        # 5. 置信度评估
        confidence = await self.confidence_scorer.score(validated_output, context)
        
        # 6. 记录日志
        self.logger.log(prompt, validated_output, confidence)
        
        # 7. 收集反馈（异步）
        asyncio.create_task(self._collect_feedback(prompt, validated_output))
        
        return validated_output
    
    async def spawn_subagent(self, task: str, agent_id: str = None) -> str:
        """生成子代理"""
        return await self.orchestrator.spawn(task, agent_id)
    
    async def optimize(self):
        """触发优化"""
        await self.optimizer.optimize()
```

---

## 数据飞轮与 Harness 的关系

```
┌─────────────────────────────────────────────────────────────┐
│                    HARNESS 架构                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            CAD 数据 → 模型训练 → 仿真验证              │  │
│  │                    ↓                                  │  │
│  │              真机部署 → 数据收集                       │  │
│  │                    ↓                                  │  │
│  │              自动矫正 → 模型优化                       │  │
│  │                    ↓                                  │  │
│  │            ←←← 飞轮加速 ←←←                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Harness 是飞轮的"轴承"，确保：                              │
│  • 数据流动有序（第一层）                                    │
│  • 并发处理高效（第二层）                                    │
│  • 输出质量可靠（第三层）                                    │
│  • 系统持续优化（第四层）                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 实施路线图

| 阶段 | 时间 | 目标 | 产出 |
|------|------|------|------|
| Phase 1 | 1周 | 建立基础结构 | Prompt注册表 + Memory系统 |
| Phase 2 | 2周 | 并发管理 | Scheduler + Orchestrator |
| Phase 3 | 1周 | 护栏系统 | Guardrails + Feedback |
| Phase 4 | 持续 | 优化迭代 | Profiler + Optimizer |

---

---

_更新时间：2026-04-09_

## 皮·骨·肉三层架构（Physical AI 执行框架）

### 皮：感知层（Perception Layer）
- **组件**：VRViewer、RenderingGallery、NeuralInferencePanel
- **数据源**：444条VR全景 + 1053张渲染图 + 151节点场景图
- **输入**：多模态建筑数据（图像/几何/语义）
- **输出**：结构化场景描述（场景图谱+空间关系）

### 骨：分析层（Reasoning Layer）
- **组件**：PhysicsPanel、AgentCommandPanel、SceneColumn
- **核心**：物理常识推理（材质/质量/摩擦/碰撞）
- **任务规划**：将用户指令分解为可执行步骤
- **安全约束**：Harness层（承重墙/管道/电气安全）

### 肉：执行层（Execution Layer）
- **组件**：Agent API（5002）、VLA Server（5004）
- **硬件**：越疆CR协作臂 + DexHand 021灵巧手
- **执行**：钻孔/搬运/清洁/巡检四类任务
- **反馈**：数据飞轮（执行结果→模型更新）
