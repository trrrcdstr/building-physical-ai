# -*- coding: utf-8 -*-
"""
physics_agent.py — Physics Agent
=================================
通过 HTTP /v1/chat/completions 向远程 Gateway 发送建筑物理数据

功能：
  1. 从推理服务器（localhost:5000）获取场景数据
  2. 调用 SpatialEncoder / RelationTransformer 推理
  3. 将结果格式化后发送到远程 Gateway
  4. 支持单次发送 / 持续监控模式

用法：
  python physics_agent.py --once          # 发送一次
  python physics_agent.py --watch         # 持续监控（每60秒）
  python physics_agent.py --query "厨房"  # 查询特定场景
"""

import argparse
import json
import time
import requests
from datetime import datetime
from typing import Optional

# ── 配置 ──────────────────────────────────────────────────────────────────────
LOCAL_INFERENCE = "http://localhost:5000"
REMOTE_GATEWAY  = "http://192.168.3.11:28789"
REMOTE_TOKEN    = "fe00bf4dd7a9e505f00403c6377556bd013d5d34ec863ae6"
AGENT_MODEL     = "modelroute"

HEADERS = {
    "Authorization": f"Bearer {REMOTE_TOKEN}",
    "Content-Type": "application/json",
}

# ── 本地推理 API ───────────────────────────────────────────────────────────────

def get_local_health() -> dict:
    """检查本地推理服务器状态"""
    try:
        r = requests.get(f"{LOCAL_INFERENCE}/api/health", timeout=5)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_scene_graph() -> dict:
    """获取场景图谱（151个门/窗节点）"""
    try:
        r = requests.get(f"{LOCAL_INFERENCE}/api/scene", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def predict_relation(node_i: dict, node_j: dict) -> dict:
    """预测两个节点的空间关系"""
    try:
        r = requests.post(
            f"{LOCAL_INFERENCE}/api/relation",
            json={"node_i": node_i, "node_j": node_j},
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def predict_relation_batch(pairs: list) -> dict:
    """批量预测空间关系"""
    try:
        r = requests.post(
            f"{LOCAL_INFERENCE}/api/relation_batch",
            json={"pairs": pairs},
            timeout=30
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ── 远程 Gateway 发送 ──────────────────────────────────────────────────────────

def send_to_gateway(message: str, system_prompt: Optional[str] = None) -> dict:
    """
    通过 /v1/chat/completions 向远程 Gateway 发送消息
    
    Args:
        message: 要发送的消息内容
        system_prompt: 可选的系统提示
    
    Returns:
        Gateway 的响应
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": message})

    payload = {
        "model": AGENT_MODEL,
        "messages": messages,
        "max_tokens": 500,
    }

    try:
        r = requests.post(
            f"{REMOTE_GATEWAY}/v1/chat/completions",
            headers=HEADERS,
            json=payload,
            timeout=60
        )
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        return {"ok": True, "content": content, "raw": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── 数据格式化 ─────────────────────────────────────────────────────────────────

def format_scene_report(scene: dict, health: dict) -> str:
    """将场景数据格式化为可读报告"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    nodes = scene.get("nodes", [])
    num_nodes = scene.get("num_nodes", 0)
    num_edges = scene.get("num_edges", 0)
    edge_labels = scene.get("labels", [])
    
    # 统计节点类型
    node_types = scene.get("node_types", [])
    type_count = {}
    for t in node_types:
        type_count[t] = type_count.get(t, 0) + 1
    
    # 统计关系类型
    same_room = sum(1 for l in edge_labels if l == 1)
    diff_room = sum(1 for l in edge_labels if l == 0)
    
    # 模型状态
    models = health.get("models", {})
    spatial_ok = health.get("spatial_encoder", False)
    physics_ok = health.get("physics_mlp", False)
    
    report = f"""[Physics Agent 场景报告] {ts}

📊 场景统计
  节点总数: {num_nodes}
  关系边数: {num_edges}
  同房间关系: {same_room}
  跨房间关系: {diff_room}

🏗️ 节点类型分布
{chr(10).join(f'  {k}: {v}' for k, v in type_count.items())}

🤖 模型状态
  SpatialEncoder (Val Acc=98.1%): {'✅ 已加载' if spatial_ok else '❌ 未加载'}
  PhysicsMLP: {'✅ 已加载' if physics_ok else '❌ 未加载'}
  检查点: {models.get('SpatialEncoder', 'N/A')}

🔗 推理服务器: {LOCAL_INFERENCE}
"""
    return report


def format_relation_summary(pairs_result: dict, sample_size: int = 5) -> str:
    """格式化关系预测结果摘要"""
    results = pairs_result.get("results", [])
    if not results:
        return "无关系预测结果"
    
    same_room_count = sum(1 for r in results if r.get("same_room"))
    avg_dist = sum(r.get("distance", 0) for r in results) / max(len(results), 1)
    
    # 取前几个样本
    samples = results[:sample_size]
    sample_lines = []
    for r in samples:
        i = r.get("i", "?")
        j = r.get("j", "?")
        sr = "同房间" if r.get("same_room") else "不同房间"
        dist = r.get("distance", 0)
        conf = r.get("confidence", 0)
        sample_lines.append(f"  节点{i}↔{j}: {sr}, 距离={dist:.1f}m, 置信度={conf:.2f}")
    
    return f"""关系预测摘要（共{len(results)}对）:
  同房间: {same_room_count} / {len(results)}
  平均距离: {avg_dist:.1f}m
  
样本预测:
{chr(10).join(sample_lines)}"""


# ── 主要任务 ───────────────────────────────────────────────────────────────────

def run_once(query: Optional[str] = None):
    """执行一次完整的数据采集和发送"""
    print("=" * 60)
    print(f"Physics Agent 启动 [{datetime.now().strftime('%H:%M:%S')}]")
    print("=" * 60)
    
    # 1. 检查本地推理服务器
    print("\n[1/4] 检查本地推理服务器...")
    health = get_local_health()
    if "error" in health:
        print(f"  ❌ 推理服务器不可用: {health['error']}")
        print("  请先启动: python inference_server.py")
        return False
    print(f"  ✅ 推理服务器正常 (节点数: {health.get('scene_nodes', 0)})")
    
    # 2. 获取场景数据
    print("\n[2/4] 获取场景图谱...")
    scene = get_scene_graph()
    if "error" in scene:
        print(f"  ❌ 获取场景失败: {scene['error']}")
        return False
    num_nodes = scene.get("num_nodes", 0)
    print(f"  ✅ 获取到 {num_nodes} 个节点")
    
    # 3. 格式化报告
    print("\n[3/4] 生成场景报告...")
    report = format_scene_report(scene, health)
    
    if query:
        # 如果有查询，附加查询信息
        report += f"\n🔍 用户查询: {query}\n"
        # 可以在这里加入针对查询的推理逻辑
    
    print(report)
    
    # 4. 发送到远程 Gateway
    print("\n[4/4] 发送到远程 Gateway...")
    system_prompt = (
        "你是建筑物理AI助手。接收来自本地推理服务器的场景数据报告，"
        "简洁地确认收到并给出关键洞察（1-2句话）。"
    )
    
    result = send_to_gateway(report, system_prompt)
    
    if result["ok"]:
        print(f"  ✅ 发送成功!")
        print(f"  Gateway 响应: {result['content']}")
        return True
    else:
        print(f"  ❌ 发送失败: {result['error']}")
        return False


def run_watch(interval: int = 60):
    """持续监控模式，每隔 interval 秒发送一次"""
    print(f"Physics Agent 持续监控模式 (间隔: {interval}s)")
    print("按 Ctrl+C 停止\n")
    
    count = 0
    while True:
        count += 1
        print(f"\n{'='*60}")
        print(f"第 {count} 次检查")
        run_once()
        print(f"\n等待 {interval} 秒...")
        time.sleep(interval)


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Physics Agent - 建筑物理AI数据发送器")
    parser.add_argument("--once",  action="store_true", help="发送一次后退出")
    parser.add_argument("--watch", action="store_true", help="持续监控模式")
    parser.add_argument("--query", type=str, default=None, help="附加查询内容")
    parser.add_argument("--interval", type=int, default=60, help="监控间隔（秒）")
    parser.add_argument("--test-gateway", action="store_true", help="仅测试 Gateway 连接")
    
    args = parser.parse_args()
    
    if args.test_gateway:
        print("测试远程 Gateway 连接...")
        result = send_to_gateway("ping")
        if result["ok"]:
            print(f"✅ Gateway 连接正常: {result['content']}")
        else:
            print(f"❌ Gateway 连接失败: {result['error']}")
    elif args.watch:
        run_watch(args.interval)
    else:
        # 默认 --once
        run_once(args.query)
