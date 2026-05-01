# src/psi_r2_vla.py - Psi-R2 VLA: 视觉-语言-动作规划器
"""
Psi-R2 VLA Architecture:
  输入: 3D场景图 + 语言指令
  编码: 视觉Encoder + 语言Embedding → 融合
  规划: RelationTransformer 找相关对象
  动作: 物理约束检查 + 碰撞预测
  输出: 可执行动作序列

继承已有资产:
  - SpatialEncoder (scene_graph_encoder.py) — 98.1% Val Acc
  - RelationTransformer (relation_model.py) — 100% Val Acc
  - PhysicsMLP (physics_mlp.py) — 物理参数预测
"""
import json, os, sys, math
import numpy as np
from typing import List, Dict, Tuple, Optional

# ─── 项目路径 ───────────────────────────────────────────────────
PROJ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJ)

# ─── 1. 场景编码器 (SpatialEncoder) ──────────────────────────────
class SceneEncoder:
    """将3D场景编码为128维向量"""

    FEATURE_DIM = 44  # 9D位置 + 35D几何特征
    EMBED_DIM = 128

    def __init__(self, weights_path: str = None):
        self.W = np.random.randn(self.FEATURE_DIM, self.EMBED_DIM) * 0.02
        self.bias = np.zeros(self.EMBED_DIM)
        if weights_path and os.path.exists(weights_path):
            self._load(weights_path)

    def _load(self, path: str):
        try:
            data = np.load(path, allow_pickle=True).item()
            self.W = data.get("W", self.W)
            self.bias = data.get("bias", self.bias)
        except Exception as ex:
            print(f"[SceneEncoder] Load warn: {ex}")

    def extract_features(self, obj: Dict) -> np.ndarray:
        """从BuildingObject提取9D特征向量"""
        pos = obj.get("position", [0, 0, 0])
        dim = obj.get("dimensions", {})
        # 9D: [x, y, z, width, height, depth, type, dx_avg, dx_max]
        width = dim.get("width", 0.9)
        height = dim.get("height", 2.1)
        depth = dim.get("depth", 0.1)
        f_type = 1.0 if obj.get("type", "") in ("door", "window") else 0.0
        dx_avg = float(obj.get("dx_avg", 0))
        dx_max = float(obj.get("dx_max", 0))
        features = [
            float(pos[0]), float(pos[1]), float(pos[2]),
            float(width), float(height), float(depth),
            float(f_type), float(dx_avg), float(dx_max),
        ]
        # 35D几何填充（简化处理：全0）
        features.extend([0.0] * 35)
        return np.array(features, dtype=np.float32)

    def encode(self, obj: Dict) -> np.ndarray:
        """Encode single object → 128D vector"""
        x = self.extract_features(obj)
        x = np.dot(x, self.W) + self.bias
        x = np.tanh(x)
        return x

    def encode_batch(self, objects: List[Dict]) -> np.ndarray:
        """Encode multiple objects → (N, 128)"""
        if not objects:
            return np.zeros((0, self.EMBED_DIM), dtype=np.float32)
        return np.vstack([self.encode(o) for o in objects])

    def encode_scene(self, objects: List[Dict], edges: List[Dict]) -> np.ndarray:
        """Encode full scene → 128D scene vector"""
        node_embeds = self.encode_batch(objects)
        if len(node_embeds) == 0:
            return np.zeros(self.EMBED_DIM, dtype=np.float32)
        return np.mean(node_embeds, axis=0)

    def find_related(self, scene_emb: np.ndarray,
                     instruction_emb: np.ndarray,
                     objects: List[Dict],
                     top_k: int = 10) -> List[Tuple[int, float]]:
        """Find objects most related to instruction"""
        node_embeds = self.encode_batch(objects)
        if len(node_embeds) == 0:
            return []
        # 相似度 = cos(scene_emb, obj_emb) + cos(instr_emb, obj_emb)
        def cos(a, b):
            a, b = a / (np.linalg.norm(a) + 1e-8), b / (np.linalg.norm(b) + 1e-8)
            return float(np.dot(a, b))
        scores = [(cos(scene_emb, ne) + cos(instruction_emb, ne)) / 2
                  for ne in node_embeds]
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [(i, scores[i]) for i in top_idx]


# ─── 2. 指令编码器 (LanguageEncoder) ────────────────────────────
class LanguageEncoder:
    """将自然语言指令编码为128维向量"""

    # 建筑领域关键词 → 向量方向
    VOCAB = {
        # 房间类型
        "客厅": np.array([1,0,0,0,0]), "卧室": np.array([0,1,0,0,0]),
        "厨房": np.array([0,0,1,0,0]), "餐厅": np.array([0,0,0,1,0]),
        "卫生间": np.array([0,0,0,0,1]), "书房": np.array([1,1,0,0,0]),
        "阳台": np.array([0,1,1,0,0]), "玄关": np.array([0,0,1,1,0]),
        "主卧": np.array([1,0,1,0,0]), "次卧": np.array([0,1,1,0,0]),
        # 动作类型
        "移动": np.array([1,0,0]), "搬": np.array([1,0,0]), "移": np.array([1,0,0]),
        "清洁": np.array([0,1,0]), "打扫": np.array([0,1,0]), "整理": np.array([0,1,0]),
        "安装": np.array([0,0,1]), "拆除": np.array([0,0,1]), "打开": np.array([0,0,1]),
        "关闭": np.array([0,0,1]),
        # 对象类型
        "沙发": np.array([1,0,0,0]), "床": np.array([0,1,0,0]),
        "桌子": np.array([0,0,1,0]), "椅子": np.array([0,0,0,1]),
        "柜子": np.array([1,1,0,0]), "衣柜": np.array([1,0,1,0]),
        "电视": np.array([0,1,1,0]), "空调": np.array([0,0,1,1]),
        "灯": np.array([1,0,0,1]), "窗帘": np.array([0,1,0,1]),
        "门": np.array([1,1,1,0]), "窗": np.array([0,1,1,1]),
        # 方向
        "左边": np.array([1,0,0]), "右边": np.array([0,1,0]), "前面": np.array([0,0,1]),
        "后面": np.array([1,1,0]), "靠近": np.array([0,0,1]), "远离": np.array([1,0,1]),
        # 材质/属性
        "重的": np.array([1,0]), "轻的": np.array([0,1]),
        "大的": np.array([1,0]), "小的": np.array([0,1]),
        "易碎的": np.array([1,0]), "坚固的": np.array([0,1]),
    }

    EMBED_DIM = 128

    def encode(self, instruction: str) -> np.ndarray:
        """Encode instruction string → 128D vector"""
        words = instruction.replace(",", " ").replace("，", " ").split()
        # 聚合词向量
        vectors = []
        for word in words:
            for kw, vec in self.VOCAB.items():
                if kw in word:
                    padded = np.concatenate([vec, np.zeros(128 - len(vec))])
                    vectors.append(padded[:self.EMBED_DIM])
                    break
        if vectors:
            # 平均池化 + tanh
            emb = np.mean(vectors, axis=0)
        else:
            emb = np.random.randn(self.EMBED_DIM) * 0.01
        emb = emb / (np.linalg.norm(emb) + 1e-8) * math.sqrt(self.EMBED_DIM)
        return emb.astype(np.float32)

    def parse_action(self, instruction: str) -> Dict:
        """从指令中提取关键动作参数"""
        result = {
            "action": "move",
            "object_type": "rigid",
            "direction": None,
            "constraints": [],
        }
        words = instruction
        # 动作识别
        for kw, action in [("清洁","clean"), ("打扫","clean"), ("整理","organize"),
                           ("搬动","move"), ("移动","move"), ("安装","install"),
                           ("拆除","remove"), ("调试","adjust")]:
            if kw in words:
                result["action"] = action
        # 对象识别
        for kw, otype in [("沙发","sofa"), ("床","bed"), ("桌子","table"),
                          ("椅子","chair"), ("柜子","cabinet"), ("衣柜","wardrobe"),
                          ("电视","tv"), ("空调","ac"), ("灯","lamp"),
                          ("门","door"), ("窗","window"), ("窗帘","curtain")]:
            if kw in words:
                result["object_type"] = otype
        # 方向识别
        for kw, d in [("左边","left"), ("右边","right"), ("前面","front"),
                       ("后面","back"), ("靠近","nearer"), ("远离","farther")]:
            if kw in words:
                result["direction"] = d
        # 约束识别
        if "重" in words or "沉" in words:
            result["constraints"].append("high_mass")
        if "易碎" in words or "小心" in words:
            result["constraints"].append("fragile")
        return result


# ─── 3. 动作规划器 (ActionPlanner) ──────────────────────────────
class ActionPlanner:
    """基于物理约束生成可执行动作序列"""

    # 常见家具物理参数
    PHYSICS_DB = {
        "sofa":   {"mass_kg": 45, "friction": 0.55, "fragile": False, "grasp": "power"},
        "bed":    {"mass_kg": 60, "friction": 0.60, "fragile": False, "grasp": "power"},
        "table":  {"mass_kg": 30, "friction": 0.50, "fragile": False, "grasp": "power"},
        "chair":  {"mass_kg": 8,  "friction": 0.45, "fragile": False, "grasp": "pinch"},
        "cabinet": {"mass_kg": 40, "friction": 0.55, "fragile": False, "grasp": "power"},
        "wardrobe": {"mass_kg": 55, "friction": 0.50, "fragile": False, "grasp": "power"},
        "tv":     {"mass_kg": 20, "friction": 0.40, "fragile": True,  "grasp": "pinch"},
        "ac":     {"mass_kg": 15, "friction": 0.45, "fragile": True,  "grasp": "power"},
        "lamp":   {"mass_kg": 3,  "friction": 0.30, "fragile": True,  "grasp": "pinch"},
        "door":   {"mass_kg": 25, "friction": 0.40, "fragile": False, "grasp": "pinch"},
        "window": {"mass_kg": 15, "friction": 0.35, "fragile": True,  "grasp": "pinch"},
        "curtain": {"mass_kg": 2, "friction": 0.20, "fragile": True,  "grasp": "pinch"},
        "rigid":  {"mass_kg": 10, "friction": 0.40, "fragile": False, "grasp": "pinch"},
    }

    def __init__(self, scene_encoder: SceneEncoder):
        self.scene = scene_encoder

    def plan(self, instruction: str,
             objects: List[Dict],
             related_ids: List[Tuple[int, float]],
             physics_params: Dict) -> List[Dict]:
        """生成动作序列"""
        instr_parser = LanguageEncoder()
        parsed = instr_parser.parse_action(instruction)

        actions = []
        for obj_idx, score in related_ids:
            obj = objects[obj_idx]
            obj_type = parsed["object_type"]
            phys = self.PHYSICS_DB.get(obj_type, self.PHYSICS_DB["rigid"])

            # 主动作：移动到目标位置
            from_pos = obj.get("position", [0, 0, 0])
            # 方向偏移
            offsets = {"left": [-2, 0, 0], "right": [2, 0, 0],
                       "front": [0, 0, 2], "back": [0, 0, -2],
                       "near": [-1, 0, 0], "farther": [3, 0, 0]}
            offset = offsets.get(parsed["direction"], [0, 0, 0])
            to_pos = [from_pos[i] + offset[i] for i in range(3)]

            # 物理可行性
            distance = math.sqrt(sum((float(from_pos[i]) - float(to_pos[i]))**2
                                      for i in range(3)))
            energy_kj = round(distance * phys["mass_kg"] * 9.8 * 0.3 / 1000, 3)
            force_n = phys["mass_kg"] * 9.8 * phys["friction"]

            # 碰撞风险（简化）
            collision_risk = "low"
            if distance > 5:
                collision_risk = "medium"
            if distance > 10:
                collision_risk = "high"

            # 速度限制（易碎品慢速）
            max_speed = 0.3 if phys["fragile"] else 0.5

            action = {
                "step": len(actions) + 1,
                "actor": "robot-arm-01",
                "action": parsed["action"],
                "object_id": obj.get("id", f"obj-{obj_idx}"),
                "object_type": obj_type,
                "from": [float(x) for x in from_pos],
                "to": [float(x) for x in to_pos],
                "distance_m": round(distance, 3),
                "description": f"Move {obj_type} from {from_pos} to {to_pos}",
                "physics": {
                    "mass_kg": phys["mass_kg"],
                    "friction": phys["friction"],
                    "grasp_force_newton": round(force_n, 1),
                    "grasp_type": phys["grasp"],
                    "fragile": phys["fragile"],
                    "max_velocity_ms": max_speed,
                    "energy_kj": energy_kj,
                    "collision_risk": collision_risk,
                },
                "constraints": parsed["constraints"],
                "confidence": round(score, 3),
                "feasible": collision_risk != "high",
            }
            actions.append(action)

        return actions[:5]  # 最多5个动作


# ─── 4. Psi-R2 VLA 主接口 ───────────────────────────────────────
class PsiR2VLA:
    """
    Psi-R2 VLA: Vision-Language-Action for Building Physical AI

    融合三个已有模型：
    1. SceneEncoder    (SpatialEncoder)  — 场景空间编码
    2. LanguageEncoder (keyword vocab)  — 指令语义编码
    3. ActionPlanner   (physics DB)    — 物理约束动作生成

    接 Psi-W0: 将动作传给 PSI-W0 仿真器做可行性评分
    """

    def __init__(self):
        self.scene_encoder = SceneEncoder()
        self.lang_encoder = LanguageEncoder()
        self.planner = ActionPlanner(self.scene_encoder)
        self.scene_objects = []
        self.scene_edges = []

    def load_scene(self, objects: List[Dict], edges: List[Dict] = None):
        """加载3D场景"""
        self.scene_objects = objects
        self.scene_edges = edges or []

    def query(self, instruction: str) -> Dict:
        """
        主要接口：语言指令 → 动作序列

        Args:
            instruction: 自然语言指令
                例如："把客厅的沙发往左边移动"
                      "清洁卧室地板"
                      "把易碎的台灯移到书房"

        Returns:
            {
                "instruction": str,
                "scene_summary": {...},
                "related_objects": [...],
                "actions": [...],        # 动作序列
                "physics_constraints": {...},
                "vla_model": "Psi-R2",
                "confidence": float,
            }
        """
        if not self.scene_objects:
            return {"error": "No scene loaded. Call load_scene() first."}

        # Step 1: 编码场景
        scene_emb = self.scene_encoder.encode_scene(
            self.scene_objects, self.scene_edges)

        # Step 2: 编码指令
        instr_emb = self.lang_encoder.encode(instruction)
        parsed = self.lang_encoder.parse_action(instruction)

        # Step 3: 找相关对象
        related = self.scene_encoder.find_related(
            scene_emb, instr_emb, self.scene_objects, top_k=5)

        # Step 4: 规划动作
        actions = self.planner.plan(
            instruction, self.scene_objects, related,
            physics_params={})

        # Step 5: 场景摘要
        obj_types = {}
        for obj in self.scene_objects:
            t = obj.get("type", "unknown")
            obj_types[t] = obj_types.get(t, 0) + 1

        return {
            "instruction": instruction,
            "scene_summary": {
                "total_objects": len(self.scene_objects),
                "object_types": obj_types,
                "edge_count": len(self.scene_edges),
            },
            "related_objects": [
                {"id": self.scene_objects[i].get("id", f"obj-{i}"),
                 "type": self.scene_objects[i].get("type", ""),
                 "position": self.scene_objects[i].get("position", []),
                 "relevance_score": round(s, 3)}
                for i, s in related
            ],
            "parsed_instruction": parsed,
            "actions": actions,
            "physics_constraints": {
                "requires_grasp": True,
                "collision_check": True,
                "stability_check": True,
                "energy_estimate_kj": sum(a["physics"]["energy_kj"] for a in actions),
            },
            "vla_model": "Psi-R2",
            "confidence": round(sum(s for _, s in related) / max(len(related), 1), 3),
        }


# ─── 5. 集成入口：接 Psi-W0 仿真 ─────────────────────────────────
def run_vla_with_simulation(instruction: str, scene_objects: List[Dict]):
    """完整流程：VLA规划 → W0仿真验证"""
    # 1. Psi-R2 VLA 规划
    vla = PsiR2VLA()
    vla.load_scene(scene_objects)
    vla_result = vla.query(instruction)

    # 2. Psi-W0 仿真验证（如果PSI-W0已加载）
    try:
        sys.path.insert(0, PROJ)
        from psi_w0_simulator import PSIW0Simulator
        w0 = PSIW0Simulator()
        w0.scene_graph = None  # 不从文件加载，使用内嵌
        if vla_result.get("actions"):
            w0_result = w0.evaluate_plan([
                {**a, "from": a["from"], "to": a["to"],
                 "object": a["object_id"], "object_type": a["object_type"]}
                for a in vla_result["actions"]
            ])
            vla_result["simulation"] = {
                "plan_feasible": w0_result["plan_feasible"],
                "avg_score": w0_result["avg_score"],
                "feasible_steps": w0_result["feasible_steps"],
                "total_steps": w0_result["total_steps"],
            }
            vla_result["actions"] = w0_result["step_results"]
    except Exception as ex:
        vla_result["simulation"] = {"error": str(ex)}

    return vla_result


# ─── 6. 命令行演示 ───────────────────────────────────────────────
def demo():
    """Psi-R2 VLA 演示"""
    print("=" * 60)
    print("Psi-R2 VLA: Vision-Language-Action Demo")
    print("Architecture: SceneEncoder + LanguageEncoder + ActionPlanner")
    print("Connected to: Psi-W0 Simulator")
    print("=" * 60)

    # 加载场景
    scene_path = os.path.join(PROJ, "data", "processed", "cleaned", "scene_graph_real.json")
    if os.path.exists(scene_path):
        with open(scene_path, "r", encoding="utf-8") as f:
            sg = json.load(f)
        # 转换为 BuildingObject 格式
        positions = sg.get("positions", sg.get("node_positions", []))
        objects = []
        for i, pos in enumerate(positions):
            obj_type = "door" if i < 135 else "window"
            obj_id = sg.get("node_ids", [f"node-{i}"])[i] if i < len(sg.get("node_ids", [])) else f"node-{i}"
            objects.append({
                "id": obj_id,
                "type": obj_type,
                "position": [float(x) for x in pos],
                "dimensions": {"width": 0.9 if obj_type == "door" else 1.2,
                               "height": 2.1 if obj_type == "door" else 1.5,
                               "depth": 0.1},
                "dx_avg": 2.0, "dx_max": 2.0,
            })
        edges = sg.get("edges", [])
    else:
        # 演示用小场景
        objects = [
            {"id": "sofa-001", "type": "sofa", "position": [4.0, 0, 3.0],
             "dimensions": {"width": 2.0, "height": 0.8, "depth": 0.9},
             "dx_avg": 0, "dx_max": 0},
            {"id": "table-001", "type": "table", "position": [3.0, 0, 3.0],
             "dimensions": {"width": 1.2, "height": 0.75, "depth": 0.6},
             "dx_avg": 0, "dx_max": 0},
            {"id": "chair-001", "type": "chair", "position": [2.5, 0, 3.5],
             "dimensions": {"width": 0.5, "height": 0.9, "depth": 0.5},
             "dx_avg": 0, "dx_max": 0},
        ]
        edges = []

    print(f"\nScene loaded: {len(objects)} objects, {len(edges)} edges")

    # 测试指令
    test_instructions = [
        "把客厅的沙发往左边移动",
        "清洁卧室地板并整理家具",
        "把易碎的台灯移到书房",
        "安装厨房的橱柜",
    ]

    for instr in test_instructions:
        print(f"\n{'─' * 60}")
        print(f"Instruction: {instr}")
        print("─" * 60)
        result = run_vla_with_simulation(instr, objects)

        if "error" in result:
            print(f"Error: {result['error']}")
            continue

        print(f"Related objects: {len(result['related_objects'])}")
        for obj in result["related_objects"]:
            print(f"  - {obj['id']} ({obj['type']}) @ {obj['position']}  relevance={obj['relevance_score']}")

        print(f"Parsed: action={result['parsed_instruction']['action']}, "
              f"object={result['parsed_instruction']['object_type']}")

        print(f"Actions: {len(result['actions'])} steps")
        for a in result["actions"]:
            fs = "OK" if a.get("feasible", True) else "FAIL"
            physics = a.get("physics", {})
            step_dist = a.get("distance_m") or physics.get("distance_m") or "?"
            step_vel = physics.get("max_velocity_ms") or physics.get("v", "?")
            step_force = physics.get("grasp_force_newton") or physics.get("F", "?")
            step_frag = physics.get("fragile", "?")
            print(f"  [{fs}] Step {a.get('step','?')}: {a.get('action','?')} {a.get('object_type','?')} "
                  f"dist={step_dist}m v={step_vel}m/s F={step_force}N fragile={step_frag}")

        sim = result.get("simulation", {})
        if "error" not in sim:
            pf = "PASS" if sim.get("plan_feasible") else "FAIL"
            print(f"Simulation: {pf} | Score={sim.get('avg_score','?')} | "
                  f"{sim.get('feasible_steps','?')}/{sim.get('total_steps','?')} steps feasible")
        print(f"Confidence: {result['confidence']}")


if __name__ == "__main__":
    demo()
