"""
L3-L4 核心世界模型层 - 整合核心
整合所有模块，对外提供统一的 world_model推理接口
"""

import json
import torch
from pathlib import Path
from typing import Optional

from .semantic_encoder import SemanticEncoder
from .physical_engine import PhysicalEngine, get_physical_engine
from .rule_library import RuleLibrary
from .scene_graph_builder import SceneGraphBuilder
from .vla_controller import VLAController


class WorldModelCore:
    """
    世界模型核心：整合 L2-L4 所有模块

    对外接口：
    - scene_graph: 构建好的场景图
    - encode_instruction(): 语义编码
    - predict_relation(): 空间关系预测
    - plan_action(): 动作规划
    - verify_physics(): 物理验证
    - check_rules(): 规则检查
    - full_inference(): 端到端推理
    """

    def __init__(self, building_objects_path: str = None):
        print("[WorldModelCore] Initializing v1 architecture...")

        # L2: 语义编码
        self.sem = SemanticEncoder()
        self.embedding_dim = self.sem.embedding_dimension

        # L3: 物理引擎
        self.physics = get_physical_engine(device="cuda" if torch.cuda.is_available() else "cpu")

        # L3: 规则库
        self.rules = RuleLibrary()

        # L4: 场景图
        self.scene_graph = SceneGraphBuilder()
        if building_objects_path and Path(building_objects_path).exists():
            self.scene_graph.build_from_building_objects(building_objects_path)
            print(f"[WorldModelCore] Scene graph loaded: {len(self.scene_graph.nodes)} nodes")

        # L4: VLA控制器
        self.vla = VLAController(
            semantic_encoder=self.sem,
            physical_engine=self.physics,
            rule_library=self.rules,
            scene_graph=self.scene_graph,
        )

        # L1: 任务库
        self.task_corpus = self.sem.task_corpus

        print("[WorldModelCore] [OK] All layers initialized")

    def full_inference(
        self,
        instruction: str,
        target_object: str = None,
        target_position: dict = None,
        return_details: bool = True,
    ) -> dict:
        """
        端到端推理：自然语言指令 -> 完整执行计划

        完整流程：
        1. 语义编码
        2. 任务理解（相似任务）
        3. 动作规划
        4. 物理验证
        5. 规则检查
        6. 风险评估
        """
        # 获取执行计划
        plan = self.vla.process_instruction(
            instruction=instruction,
            target_object=target_object,
            target_position=target_position,
        )

        # 场景上下文
        scene_info = self.scene_graph.summary() if self.scene_graph.nodes else {}

        # 物理模拟（如果指定了目标位置）
        physics_sim = {}
        if target_position:
            physics_sim = self._simulate_placement(target_object, target_position)

        result = {
            "instruction": instruction,
            "target_object": target_object,
            "scene_info": scene_info,
            "plan": plan,
            "physics_sim": physics_sim,
            "ready": plan["execution_ready"],
        }

        # 执行计划
        if return_details and plan["execution_ready"]:
            result["execution"] = self.vla.execute_plan(plan)

        return result

    def _simulate_placement(
        self,
        target_object: str,
        target_position: dict,
    ) -> dict:
        """模拟物体放置"""
        if not target_object:
            return {}
        mass = self.physics.get_mass(target_object)
        surface = {
            "x": target_position.get("x", 0),
            "z": target_position.get("z", 0),
            "width": target_position.get("surface_width", 1.5),
            "depth": target_position.get("surface_depth", 1.0),
            "material": target_position.get("material", "木材"),
        }
        obj = {
            "x": target_position.get("x", 0),
            "z": target_position.get("z", 0),
            "width": target_position.get("obj_width", 0.8),
            "depth": target_position.get("obj_depth", 0.8),
            "mass": mass,
        }
        stability = self.physics.stability_check(obj, surface)
        push_info = self.physics.can_push(mass)

        return {
            "object": target_object,
            "mass_kg": mass,
            "stability": stability,
            "push_feasibility": push_info,
        }

    def predict_relation(self, source_id: str, target_id: str) -> dict:
        """预测两个建筑对象的空间关系"""
        if source_id not in self.scene_graph.nodes:
            return {"error": f"Node {source_id} not found"}
        if target_id not in self.scene_graph.nodes:
            return {"error": f"Node {target_id} not found"}

        neighbors = self.scene_graph.get_neighbors(source_id)
        for n in neighbors:
            if n["node_id"] == target_id:
                return {
                    "source": source_id,
                    "target": target_id,
                    "relation": n["relation"],
                    "confidence": n.get("confidence", 0.5),
                }

        # 未直接连接，通过距离估算
        dist = self.scene_graph._euclidean_distance(source_id, target_id)
        if dist < 6:
            rel = "same_room"
        elif dist < 15:
            rel = "adjacent"
        else:
            rel = "far_apart"

        return {
            "source": source_id,
            "target": target_id,
            "relation": rel,
            "distance_m": round(dist, 2),
            "confidence": 0.5,
        }

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """语义搜索任务库"""
        return self.sem.find_similar_tasks(query, top_k=top_k, threshold=0.3)

    def check_scene_rule(
        self,
        rule_name: str,
        value: float,
    ) -> dict:
        """快速规则检查"""
        return self.rules.check_rule(rule_name, value)

    def get_scene_stats(self) -> dict:
        """获取场景统计"""
        return {
            "scene_graph": self.scene_graph.summary() if self.scene_graph.nodes else {},
            "embedding_dim": self.embedding_dim,
            "task_corpus_size": len(self.task_corpus),
            "architecture_rules": len(self.rules.rules),
            "furniture_clearances": len(self.rules.clearances),
            "physics_device": self.physics.device,
            "cuda_available": torch.cuda.is_available(),
        }

    def load_scene_graph(self, building_objects_path: str):
        """加载场景图"""
        self.scene_graph = SceneGraphBuilder()
        self.scene_graph.build_from_building_objects(building_objects_path)
        self.vla.set_scene_graph(self.scene_graph)
        return self.scene_graph.summary()
