"""
Planner Agent - 路径规划 Agent
每秒检查 world_state.json，读到新帧后规划路径，写入 trajectory_plan.json

Usage:
    python scripts/planner_agent.py [--poll-interval SECONDS] [--world-state PATH] [--output PATH]
"""

import json
import os
import sys
import time
import argparse
import hashlib
from pathlib import Path
from datetime import datetime

# 默认路径
DEFAULT_WORLD_STATE = "data/world_state.json"
DEFAULT_OUTPUT = "data/trajectory_plan.json"


def compute_frame_hash(frame_data):
    """计算帧数据的 hash 用于检测变化"""
    frame_str = json.dumps(frame_data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(frame_str.encode('utf-8')).hexdigest()


def load_world_state(path):
    """加载 world_state.json"""
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] 读取 world_state 失败: {e}")
        return None


def save_trajectory_plan(path, plan):
    """保存轨迹规划结果"""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    print(f"[PLAN] 已保存轨迹规划到 {path}")


def plan_trajectory(world_state):
    """
    路径规划核心逻辑
    输入: world_state (包含 robot_pose, obstacles, goal 等)
    输出: trajectory_plan (包含 waypoints, estimated_time 等)
    
    TODO: 这里先用规则引擎，后续可接入 LLM 或 Navigation Agent
    """
    robot_pose = world_state.get('robot_pose', {})
    goal = world_state.get('goal', {})
    obstacles = world_state.get('obstacles', [])
    
    # 提取坐标
    rx, ry = robot_pose.get('x', 0), robot_pose.get('y', 0)
    gx, gy = goal.get('x', 0), goal.get('y', 0)
    
    # 简单直线规划（后续替换为 A* / RRT 等算法）
    waypoints = [
        {"x": rx, "y": ry, "action": "start"},
        {"x": (rx + gx) / 2, "y": (ry + gy) / 2, "action": "move"},
        {"x": gx, "y": gy, "action": "goal"}
    ]
    
    # 计算距离
    distance = ((gx - rx) ** 2 + (gy - ry) ** 2) ** 0.5
    
    plan = {
        "timestamp": datetime.now().isoformat(),
        "frame_id": world_state.get('frame_id', 'unknown'),
        "status": "success",
        "robot_pose": robot_pose,
        "goal": goal,
        "trajectory": {
            "waypoints": waypoints,
            "total_distance": round(distance, 2),
            "estimated_time_seconds": round(distance / 0.5, 1),  # 假设 0.5 m/s
            "algorithm": "simple_linear"
        },
        "obstacles_considered": len(obstacles)
    }
    
    return plan


def main():
    parser = argparse.ArgumentParser(description="Planner Agent - 路径规划")
    parser.add_argument('--poll-interval', type=float, default=1.0, 
                        help='轮询间隔（秒）')
    parser.add_argument('--world-state', type=str, default=DEFAULT_WORLD_STATE,
                        help='world_state.json 路径')
    parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT,
                        help='trajectory_plan.json 输出路径')
    args = parser.parse_args()
    
    # 转换为绝对路径
    project_root = Path(__file__).parent.parent
    world_state_path = project_root / args.world_state
    output_path = project_root / args.output
    
    print(f"[Planner Agent] 启动")
    print(f"  轮询间隔: {args.poll_interval}s")
    print(f"  监控文件: {world_state_path}")
    print(f"  输出文件: {output_path}")
    print("-" * 50)
    
    last_frame_hash = None
    frame_count = 0
    
    try:
        while True:
            # 读取 world_state
            world_state = load_world_state(str(world_state_path))
            
            if world_state is None:
                print(f"[WAIT] 等待 world_state.json 出现...")
                time.sleep(args.poll_interval)
                continue
            
            # 计算当前帧 hash
            current_hash = compute_frame_hash(world_state)
            
            # 检测新帧
            if current_hash != last_frame_hash:
                frame_count += 1
                last_frame_hash = current_hash
                
                print(f"[FRAME #{frame_count}] 检测到新帧: frame_id={world_state.get('frame_id', 'unknown')}")
                print(f"  robot_pose: {world_state.get('robot_pose')}")
                print(f"  goal: {world_state.get('goal')}")
                
                # 执行路径规划
                plan = plan_trajectory(world_state)
                
                # 保存结果
                save_trajectory_plan(str(output_path), plan)
                print(f"  规划完成: {plan['trajectory']['total_distance']}m, "
                      f"{plan['trajectory']['estimated_time_seconds']}s")
            
            # 等待下一帧
            time.sleep(args.poll_interval)
            
    except KeyboardInterrupt:
        print(f"\n[STOP] Planner Agent 已停止，共处理 {frame_count} 帧")
        sys.exit(0)


if __name__ == "__main__":
    main()
