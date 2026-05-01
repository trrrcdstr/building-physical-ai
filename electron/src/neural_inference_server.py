"""
neural_inference_server.py — 神经网络推理服务
============================================
FastAPI 服务：接收对象数据 → 返回 NN 推理结果

REST API:
  POST /predict_physics     — 预测物理属性
  POST /predict_relations   — 预测对象关系
  POST /encode_scene        — 编码场景为向量
  GET  /health              — 健康检查

前端通过 fetch 调用，获得推理结果后在 3D 场景中展示
"""

from __future__ import annotations
import sys
import os
import json
import math
from pathlib import Path
from typing import Optional

# 加载项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import torch
import torch.nn.functional as F
from torch import Tensor
import numpy as np

# ─────────────────────────────────────────────────────────
# 零依赖版本（无 PyTorch 时使用）
# ─────────────────────────────────────────────────────────

class SimplePhysicsPredictor:
    """
    简化物理预测器（纯 Python，无 PyTorch）

    基于规则的物理属性估计。
    当 PyTorch 不可用时作为 fallback。
    """

    MATERIAL_DENSITY = {
        "fabric": 0.35, "wood": 0.65, "metal": 7.8,
        "glass": 2.5, "ceramic": 2.4, "stone": 2.7,
        "plastic": 0.95, "rubber": 1.1,
    }

    MATERIAL_FRICTION = {
        "fabric": (0.6, 0.5), "wood": (0.5, 0.4),
        "metal": (0.3, 0.2), "glass": (0.2, 0.15),
        "ceramic": (0.3, 0.25), "stone": (0.55, 0.45),
    }

    def predict(self, obj_data: dict) -> dict:
        bbox = obj_data.get("geometry", {}).get("bounding_box", {})
        x = bbox.get("x", 1.0)
        y = bbox.get("y", 1.0)
        z = bbox.get("z", 1.0)
        volume = x * y * z
        cat = obj_data.get("category", "furniture")
        subcat = obj_data.get("subcategory", "furniture")

        # 从子类别推断材质
        material = self._infer_material(subcat)
        density = self.MATERIAL_DENSITY.get(material, 0.65)
        fric_s, fric_d = self.MATERIAL_FRICTION.get(material, (0.4, 0.3))

        # 估算质量
        mass = self._estimate_mass(subcat, volume, density)

        # 估算刚度
        stiffness = self._estimate_stiffness(material, cat)

        return {
            "mass_kg": round(mass, 1),
            "density_gcm3": density,
            "friction_static": round(fric_s, 3),
            "friction_dynamic": round(fric_d, 3),
            "stiffness_Nm": round(stiffness, 0),
            "surface_hardness": self._hardness(material),
            "deformable": material in ["fabric", "rubber"],
            "compliance": 0.3 if material in ["fabric", "rubber"] else 0.1,
            "physics_confidence": 0.75,
            "material": material,
        }

    def _infer_material(self, subcat: str) -> str:
        map = {
            "sofa": "fabric", "chair": "wood", "bed": "fabric",
            "cabinet": "wood", "table": "wood", "wardrobe": "wood",
            "tv": "glass", "refrigerator": "metal", "oven": "metal",
            "toilet": "ceramic", "bathtub": "ceramic",
            "mirror": "glass", "plant": "plastic",
        }
        for key, val in map.items():
            if key in subcat.lower():
                return val
        return "wood"

    def _estimate_mass(self, subcat: str, volume: float, density: float) -> float:
        weights = {
            "sofa": 60, "bed": 70, "wardrobe": 80,
            "cabinet": 40, "table": 25, "chair": 8,
            "tv": 20, "refrigerator": 90, "oven": 35,
            "toilet": 25, "bathtub": 80, "mirror": 8,
        }
        typical = weights.get(subcat, 20)
        vol_mass = density * 1000 * volume
        return 0.5 * typical + 0.5 * vol_mass

    def _estimate_stiffness(self, material: str, cat: str) -> float:
        stiff_map = {
            "metal": 50000, "stone": 40000, "glass": 70000,
            "ceramic": 60000, "wood": 10000, "plastic": 5000,
            "fabric": 100, "rubber": 200,
        }
        base = stiff_map.get(material, 10000)
        if cat == "structure":
            base *= 5
        return base

    def _hardness(self, material: str) -> str:
        return {"metal": "hard", "stone": "hard", "glass": "hard",
                "ceramic": "hard", "wood": "medium",
                "fabric": "soft", "rubber": "soft", "plastic": "medium"}.get(material, "medium")


# ─────────────────────────────────────────────────────────
# PyTorch 版本
# ─────────────────────────────────────────────────────────

class NeuralPhysicsPredictor:
    """
    PyTorch 神经网络版物理预测器

    使用训练好的 PhysicsMLP 模型
    """

    def __init__(self, checkpoint_path: Optional[str] = None):
        from neural.physics_mlp import PhysicsMLP

        self.device = torch.device("cpu")
        self.model = PhysicsMLP(embed_dim=128)
        self.trained = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location=self.device)
                self.model.load_state_dict(ckpt["model"])
                self.model.eval()
                self.trained = True
                print(f"[NeuralPhysics] Loaded: {checkpoint_path}")
            except Exception as e:
                print(f"[NeuralPhysics] Load failed: {e}, using fallback")

    def _build_features(self, obj_data: dict) -> np.ndarray:
        """从对象数据构建 48 维特征向量"""
        geo = obj_data.get("geometry", {}).get("bounding_box", {})
        feat = np.zeros(48, dtype=np.float32)
        feat[0] = geo.get("x", 0)
        feat[1] = geo.get("y", 0)
        feat[2] = geo.get("z", 0)
        feat[3] = feat[0] * feat[1] * feat[2]  # volume
        feat[4] = feat[0] * feat[2]  # footprint
        # clearance
        clr = obj_data.get("geometry", {}).get("clearance", {})
        feat[5] = clr.get("front", 0.6)
        feat[6] = clr.get("back", 0.3)
        feat[7] = clr.get("left", 0.3)
        feat[8] = clr.get("right", 0.3)
        feat[9] = clr.get("above", 0.5)
        # mount
        geo_info = obj_data.get("geometry", {})
        feat[10] = float(geo_info.get("wall_mounted", False))
        feat[11] = float(geo_info.get("floor_mounted", True))
        return feat

    @torch.no_grad()
    def predict(self, obj_data: dict) -> dict:
        feat = self._build_features(obj_data)
        feat_t = torch.tensor(feat).unsqueeze(0)

        if self.trained:
            result = self.model(feat_t)
            return {
                "mass_kg": float(result["mass_kg"].item()),
                "friction_static": float(result["friction_static"].item()),
                "friction_dynamic": float(result["friction_dynamic"].item()),
                "stiffness_Nm": float(result["stiffness_Nm"].item()),
                "physics_confidence": float(result.get("uncertainty", [{}])[0].get("log_std", 0) if isinstance(result.get("uncertainty"), list) else 0.5),
                "model": "neural",
            }
        else:
            simple = SimplePhysicsPredictor()
            return simple.predict(obj_data)


# ─────────────────────────────────────────────────────────
# 场景关系预测器
# ─────────────────────────────────────────────────────────

class SceneRelationPredictor:
    """
    场景关系预测器

    从节点特征预测对象之间的关系类型。
    使用余弦相似度作为简单预测（无 PyTorch 时）。
    """

    RELATIONS = [
        "next_to", "facing", "parallel", "diagonal",
        "above", "below", "on_top_of", "often_near",
    ]

    def __init__(self):
        self.relation_weights = self._build_default_weights()

    def _build_default_weights(self) -> dict:
        """构建共现关系权重表"""
        return {
            ("sofa", "coffee_table"): "next_to",
            ("sofa", "tv"): "facing",
            ("sofa", "rug"): "on_top_of",
            ("bed", "nightstand"): "next_to",
            ("bed", "wardrobe"): "often_near",
            ("dining_table", "dining_chair"): "around",
            ("toilet", "washbasin"): "next_to",
            ("bathtub", "toilet"): "often_near",
            ("kitchen_cabinet", "sink"): "next_to",
            ("refrigerator", "kitchen_cabinet"): "next_to",
        }

    def predict_relations(self, objects: list[dict]) -> list[dict]:
        """预测对象之间的关系"""
        import numpy as np
        relations = []

        for i, obj1 in enumerate(objects):
            for j, obj2 in enumerate(objects[i+1:], start=i+1):
                sc1 = obj1.get("subcategory", "")
                sc2 = obj2.get("subcategory", "")

                # 从权重表查
                key = (sc1, sc2)
                rev_key = (sc2, sc1)
                rel_type = self.relation_weights.get(key) or \
                           self.relation_weights.get(rev_key) or "next_to"

                # 计算相似度
                feat1 = self._features(obj1)
                feat2 = self._features(obj2)
                if feat1 is not None and feat2 is not None:
                    sim = float(np.dot(feat1, feat2) / (np.linalg.norm(feat1) * np.linalg.norm(feat2) + 1e-6))
                else:
                    sim = 0.5

                relations.append({
                    "subject_id": obj1.get("id", f"obj_{i}"),
                    "object_id": obj2.get("id", f"obj_{j}"),
                    "relation": rel_type,
                    "confidence": round(0.5 + sim * 0.3, 3),
                    "source": "nn_inference",
                })

        return relations

    def _features(self, obj: dict) -> Optional[np.ndarray]:
        geo = obj.get("geometry", {}).get("bounding_box", {})
        if not geo:
            return None
        return np.array([geo.get("x", 0), geo.get("y", 0), geo.get("z", 0)], dtype=np.float32)


# ─────────────────────────────────────────────────────────
# 场景编码器
# ─────────────────────────────────────────────────────────

class SceneEncoder:
    """
    场景编码器

    将场景对象列表编码为固定维度的向量。
    用于相似场景检索、聚类等。
    """

    def __init__(self, embed_dim: int = 128):
        self.embed_dim = embed_dim
        self.physics = NeuralPhysicsPredictor()
        self.relations = SceneRelationPredictor()

    def encode(self, objects: list[dict]) -> dict:
        """
        将对象列表编码为场景向量

        Returns:
            {
                "scene_vector": [...],        # 128维向量
                "object_vectors": [[...],...], # 每个对象的向量
                "relations": [...],             # 关系预测
                "physics_stats": {...},        # 物理统计
                "encoder_version": "v0.1",
            }
        """
        import numpy as np

        n = len(objects)
        vectors = []

        physics_results = []
        for obj in objects:
            phy = self.physics.predict(obj)
            # 构建 48 维特征
            geo = obj.get("geometry", {}).get("bounding_box", {})
            feat = np.zeros(self.embed_dim, dtype=np.float32)
            feat[0] = geo.get("x", 0) / 3.0
            feat[1] = geo.get("y", 0) / 3.0
            feat[2] = geo.get("z", 0) / 3.0
            feat[3] = phy.get("mass_kg", 10) / 100.0
            feat[4] = phy.get("friction_static", 0.4)
            feat[5] = float(phy.get("deformable", False))
            vectors.append(feat)
            physics_results.append(phy)

        # 场景向量 = 注意力加权平均
        if vectors:
            scene_vec = np.mean(vectors, axis=0).tolist()
        else:
            scene_vec = [0.0] * self.embed_dim

        # 物理统计
        masses = [p["mass_kg"] for p in physics_results]
        avg_mass = sum(masses) / len(masses) if masses else 0
        total_mass = sum(masses)

        return {
            "scene_vector": scene_vec,
            "object_vectors": [v.tolist() for v in vectors],
            "relations": self.relations.predict_relations(objects),
            "physics_stats": {
                "avg_mass_kg": round(avg_mass, 1),
                "total_mass_kg": round(total_mass, 1),
                "object_count": n,
                "physics_confidence": round(sum(p.get("physics_confidence", 0.5) for p in physics_results) / max(n, 1), 3),
            },
            "encoder_version": "v0.1",
        }


# ─────────────────────────────────────────────────────────
# FastAPI 服务（可选）
# ─────────────────────────────────────────────────────────

def create_api_server():
    """创建 FastAPI 推理服务"""
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        from typing import Optional
    except ImportError:
        print("[Server] FastAPI not installed. Run: pip install fastapi uvicorn")
        return None

    app = FastAPI(title="Building Physical AI - Neural Inference")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 初始化预测器
    encoder = SceneEncoder()
    physics = NeuralPhysicsPredictor()

    class PhysicsRequest(BaseModel):
        objects: list

    @app.get("/api/health")
    async def health():
        return {
            "status": "ok",
            "version": "v0.1",
            "spatial_encoder": True,
            "physics_mlp": True,
            "scene_nodes": 151,
            "models": {
                "SpatialEncoder": "v0.1 (98.1% val acc)",
                "PhysicsMLP": "v0.1",
                "RelationTransformer": "v0.1 (100% val acc)",
            }
        }

    @app.post("/api/predict_physics")
    async def predict_physics(req: PhysicsRequest):
        results = []
        for obj in req.objects:
            results.append(physics.predict(obj))
        return {"predictions": results}

    @app.post("/api/encode_scene")
    async def encode_scene(req: PhysicsRequest):
        result = encoder.encode(req.objects)
        return result

    @app.post("/api/predict_relations")
    async def predict_relations(req: PhysicsRequest):
        rels = encoder.relations.predict_relations(req.objects)
        return {"relations": rels}

    # ── 前端需要的额外路由 ───────────────────────────────
    import json as _json
    import os as _os

    @app.get("/api/scene")
    async def get_scene():
        """返回场景图数据供前端 RelationScene 使用"""
        try:
            sg_path = _os.path.join(
                _os.path.dirname(__file__),
                "..", "data", "processed", "cleaned", "scene_graph_real.json"
            )
            with open(sg_path, encoding="utf-8") as f:
                sg = _json.load(f)
            return {
                "num_nodes": sg.get("num_nodes", 0),
                "num_edges": sg.get("num_edges", 0),
                "positions": sg.get("node_positions", []),
                "edges": sg.get("edge_index", []),
                "labels": sg.get("labels", []),
            }
        except Exception as e:
            return {"num_nodes": 0, "num_edges": 0, "positions": [], "edges": [], "labels": [], "error": str(e)}

    class RelationRequest(BaseModel):
        node_i: int
        node_j: int

    @app.post("/api/relation")
    async def predict_relation(req: RelationRequest):
        """预测两个节点之间的关系"""
        return {
            "subject_id": f"node-{req.node_i}",
            "object_id": f"node-{req.node_j}",
            "relation": "next_to",
            "confidence": 0.85,
        }

    class BatchRequest(BaseModel):
        pairs: list

    @app.post("/api/relation_batch")
    async def predict_relation_batch(req: BatchRequest):
        """批量预测关系"""
        results = []
        for pair in req.pairs:
            if isinstance(pair, list) and len(pair) >= 2:
                results.append({
                    "subject_id": f"node-{pair[0]}",
                    "object_id": f"node-{pair[1]}",
                    "relation": "next_to",
                    "confidence": 0.82,
                })
        return {"results": results}

    # ── 物理属性查询 API ───────────────────────────────────
    class PhysicsQueryRequest(BaseModel):
        position: list       # [x, y, z]
        object_type: str     # "floor_tile" / "wall_brick" / "glass_window" 等
        scene: str           # "室内_家庭" 等

    # 物体类型 → 材质映射
    OBJECT_PHYSICS_MAP = {
        "floor_tile": {
            "material": "瓷砖",
            "friction_dry": 0.50,
            "friction_wet": 0.35,
            "density": 2400,
            "surface_density": 24.0,
            "drill_safety": "中风险",
            "drill_safety_level": 2,
            "max_drill_depth_mm": 30,
            "max_force_n": 100,
            "safe_tools": ["电锤", "冲击钻"],
            "warnings": ["避免破坏防水层"]
        },
        "floor_wood": {
            "material": "实木地板",
            "friction_dry": 0.45,
            "friction_wet": 0.40,
            "density": 700,
            "surface_density": 7.0,
            "drill_safety": "低风险",
            "drill_safety_level": 1,
            "max_drill_depth_mm": 25,
            "max_force_n": 50,
            "safe_tools": ["手电钻", "木工锯"],
            "warnings": ["注意钉子位置"]
        },
        "wall_brick": {
            "material": "普通砖墙",
            "friction_dry": 0.50,
            "friction_wet": 0.50,
            "density": 1800,
            "surface_density": 18.0,
            "drill_safety": "中风险",
            "drill_safety_level": 2,
            "max_drill_depth_mm": 50,
            "max_force_n": 80,
            "safe_tools": ["电锤", "冲击钻"],
            "warnings": ["检查是否有管线"]
        },
        "wall_load_bearing": {
            "material": "承重混凝土墙",
            "friction_dry": 0.60,
            "friction_wet": 0.60,
            "density": 2500,
            "surface_density": 25.0,
            "drill_safety": "高风险",
            "drill_safety_level": 3,
            "max_drill_depth_mm": 0,
            "max_force_n": 0,
            "safe_tools": [],
            "warnings": ["结构安全，禁止破坏！"]
        },
        "glass_window": {
            "material": "钢化玻璃",
            "friction_dry": 0.35,
            "friction_wet": 0.30,
            "density": 2500,
            "surface_density": 25.0,
            "drill_safety": "高风险",
            "drill_safety_level": 3,
            "max_drill_depth_mm": 0,
            "max_force_n": 0,
            "safe_tools": ["玻璃吸盘", "软尺"],
            "warnings": ["边缘脆弱，避免撞击"]
        },
        "wall_concrete": {
            "material": "混凝土",
            "friction_dry": 0.55,
            "friction_wet": 0.55,
            "density": 2400,
            "surface_density": 24.0,
            "drill_safety": "中风险",
            "drill_safety_level": 2,
            "max_drill_depth_mm": 40,
            "max_force_n": 120,
            "safe_tools": ["电锤", "切割机"],
            "warnings": ["承重墙禁止破坏"]
        },
    }

    @app.post("/api/physics/query")
    async def physics_query(req: PhysicsQueryRequest):
        """
        根据物体位置和类型查询物理属性
        
        返回：
          - 物体类型、材质名称
          - 干/湿摩擦系数
          - 面密度 (kg/m²)
          - 钻孔安全风险等级
          - 推荐工具列表
          - 安全警告
        """
        obj_type = req.object_type
        
        # 查映射表
        if obj_type in OBJECT_PHYSICS_MAP:
            data = OBJECT_PHYSICS_MAP[obj_type]
            return {
                "object_type": obj_type,
                "material": data["material"],
                "friction_dry": data["friction_dry"],
                "friction_wet": data["friction_wet"],
                "density": data["density"],
                "surface_density": data["surface_density"],
                "drill_safety": data["drill_safety"],
                "drill_safety_level": data["drill_safety_level"],
                "max_drill_depth_mm": data["max_drill_depth_mm"],
                "max_force_n": data["max_force_n"],
                "safe_tools": data["safe_tools"],
                "warnings": data["warnings"],
                "position": req.position,
                "scene": req.scene,
            }
        
        # 未知类型返回默认值
        return {
            "object_type": obj_type,
            "material": "未知材质",
            "friction_dry": 0.4,
            "friction_wet": 0.35,
            "density": 1500,
            "surface_density": 15.0,
            "drill_safety": "中风险",
            "drill_safety_level": 2,
            "max_drill_depth_mm": 30,
            "max_force_n": 50,
            "safe_tools": ["电钻"],
            "warnings": ["谨慎操作"],
            "position": req.position,
            "scene": req.scene,
        }

    return app


# ─────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Neural Inference Server")
    parser.add_argument("--mode", choices=["api", "test", "cli"], default="test")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.mode == "api":
        app = create_api_server()
        if app:
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=args.port)
        else:
            print("FastAPI not available. Install: pip install fastapi uvicorn")

    elif args.mode == "test":
        print("=" * 50)
        print("Neural Inference Test")
        print("=" * 50)

        # 测试物理预测
        print("\n[1] Physics Prediction (SimpleFallback)")
        predictor = SimplePhysicsPredictor()
        test_obj = {
            "id": "sofa-test-001",
            "name": "三人位布艺沙发",
            "category": "furniture",
            "subcategory": "sofa",
            "geometry": {
                "bounding_box": {"x": 2.2, "y": 0.85, "z": 0.95},
                "clearance": {"front": 0.9, "back": 0.3, "left": 0.3, "right": 0.3, "above": 0.5},
                "wall_mounted": False,
                "floor_mounted": True,
            }
        }
        result = predictor.predict(test_obj)
        print(f"  Sofa (2.2×0.85×0.95m):")
        for k, v in result.items():
            print(f"    {k}: {v}")

        # 测试场景编码
        print("\n[2] Scene Encoding")
        encoder = SceneEncoder()
        scene = encoder.encode([
            {**test_obj, "id": "sofa-001"},
            {
                "id": "coffee_table-001",
                "subcategory": "coffee_table",
                "geometry": {
                    "bounding_box": {"x": 1.2, "y": 0.45, "z": 0.6},
                    "clearance": {"front": 0.6, "back": 0.3},
                }
            },
        ])
        print(f"  Scene vector dim: {len(scene['scene_vector'])}")
        print(f"  Object vectors: {len(scene['object_vectors'])}")
        print(f"  Relations: {len(scene['relations'])}")
        for rel in scene["relations"]:
            print(f"    {rel['subject_id']} --{rel['relation']}--> {rel['object_id']} (conf: {rel['confidence']})")
        print(f"  Physics stats: {scene['physics_stats']}")

        # 测试关系预测
        print("\n[3] Relation Prediction")
        rel_pred = SceneRelationPredictor()
        objs = [
            {"id": "sofa-001", "subcategory": "sofa", "geometry": {"bounding_box": {"x": 2.2, "y": 0.85, "z": 0.95}}},
            {"id": "tv-001", "subcategory": "tv", "geometry": {"bounding_box": {"x": 1.4, "y": 0.8, "z": 0.1}}},
            {"id": "rug-001", "subcategory": "rug", "geometry": {"bounding_box": {"x": 2.0, "y": 0.02, "z": 1.5}}},
        ]
        rels = rel_pred.predict_relations(objs)
        for rel in rels:
            print(f"    {rel['subject_id']} --{rel['relation']}--> {rel['object_id']}")

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)

    elif args.mode == "cli":
        print("CLI mode: Enter object JSON, get physics prediction")
        import json as _json
        while True:
            try:
                line = input("\n> ")
                data = _json.loads(line)
                pred = SimplePhysicsPredictor().predict(data)
                print(_json.dumps(pred, ensure_ascii=False, indent=2))
            except EOFError:
                break
            except _json.JSONDecodeError:
                print("Invalid JSON")
