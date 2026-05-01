"""
L3: 反馈循环 — 数据飞轮的核心
每一次交互都是学习机会。
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os


@dataclass
class Feedback:
    """反馈条目"""
    id: str = ""
    prompt_id: str = ""
    task_type: str = ""
    context_hash: str = ""        # 上下文的哈希（去重）
    input_summary: str = ""       # 输入摘要
    output_summary: str = ""       # 输出摘要
    success: bool = False
    rating: Optional[int] = None  # 1-5
    error: Optional[str] = None
    latency_ms: float = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.id:
            import hashlib
            self.id = hashlib.md5(f"{self.prompt_id}{self.timestamp}".encode()).hexdigest()[:12]
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class FeedbackLoop:
    """
    反馈循环引擎

    设计哲学：
    - 飞轮不是"收集数据"，而是"让数据自己生长"
    - 好的反馈 → 强化（Amplify）
    - 坏的反馈 → 适应（Adapt）
    - 差评反馈 → 隔离（Isolate）
    """

    def __init__(self, storage_path: str = "data/harness/feedback.json"):
        self.storage_path = storage_path
        self.feedbacks: List[Feedback] = []
        self.rules: List[Dict] = []

        # 自动触发规则（3条核心规则）
        self._init_rules()
        self._load()

    def _init_rules(self):
        self.rules = [
            {
                "name": "强化成功",
                "condition": lambda f: f.success and f.rating and f.rating >= 4,
                "action": "evolve_prompt",
                "priority": 1,
            },
            {
                "name": "标记失败",
                "condition": lambda f: not f.success,
                "action": "flag_for_review",
                "priority": 2,
            },
            {
                "name": "隔离差评",
                "condition": lambda f: f.rating and f.rating <= 2,
                "action": "isolate_prompt",
                "priority": 3,
            },
            {
                "name": "持续优化",
                "condition": lambda f: f.success and f.rating and 3 <= f.rating < 4,
                "action": "tune_prompt",
                "priority": 4,
            },
        ]

    def record(
        self,
        prompt_id: str,
        task_type: str,
        context: Any,         # Context 对象
        output: Dict,
        success: bool,
        rating: Optional[int] = None,
        error: Optional[str] = None,
        latency_ms: float = 0,
    ) -> Dict:
        """记录反馈并自动触发规则"""

        # 创建反馈条目
        import hashlib
        ctx_hash = hashlib.md5(str(context.__dict__ if hasattr(context, '__dict__') else context).encode()).hexdigest()[:16]

        fb = Feedback(
            prompt_id=prompt_id,
            task_type=task_type,
            context_hash=ctx_hash,
            input_summary=f"{getattr(context, 'room_category', 'unknown')}场景",
            output_summary=str(output)[:100],
            success=success,
            rating=rating,
            error=error,
            latency_ms=latency_ms,
        )

        self.feedbacks.append(fb)

        # 触发规则
        actions_taken = []
        for rule in sorted(self.rules, key=lambda r: r["priority"]):
            if rule["condition"](fb):
                action = self._execute_action(rule["action"], fb)
                actions_taken.append({"rule": rule["name"], "action": action})

        self._save()

        return {
            "feedback_id": fb.id,
            "success": fb.success,
            "actions": actions_taken,
        }

    def _execute_action(self, action: str, fb: Feedback) -> str:
        """执行反馈动作"""
        if action == "evolve_prompt":
            return f"[UP] 强化 Prompt {fb.prompt_id} (评分: {fb.rating})"

        elif action == "flag_for_review":
            # 写告警日志
            alert = {
                "feedback_id": fb.id,
                "prompt_id": fb.prompt_id,
                "task_type": fb.task_type,
                "error": fb.error,
                "timestamp": fb.timestamp,
            }
            self._write_alert(alert)
            return f"[WARN] 标记 Prompt {fb.prompt_id} 待审查"

        elif action == "isolate_prompt":
            return f"[BLOCK] 隔离 Prompt {fb.prompt_id} (差评: {fb.rating})"

        elif action == "tune_prompt":
            return f"[TUNE] 轻微调优 Prompt {fb.prompt_id}"

        return f"未知动作: {action}"

    def _write_alert(self, alert: Dict):
        """写告警到文件"""
        alert_path = self.storage_path.replace("feedback.json", "alerts.jsonl")
        os.makedirs(os.path.dirname(alert_path), exist_ok=True)
        with open(alert_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(alert, ensure_ascii=False) + "\n")

    def get_stats(self) -> Dict:
        """获取飞轮统计"""
        if not self.feedbacks:
            return {
                "total": 0,
                "success_rate": 0.0,
                "avg_rating": 0.0,
                "evolution_count": 0,
            }

        total = len(self.feedbacks)
        success = sum(1 for f in self.feedbacks if f.success)
        ratings = [f.rating for f in self.feedbacks if f.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0

        # 按任务类型统计
        by_type = {}
        for fb in self.feedbacks:
            if fb.task_type not in by_type:
                by_type[fb.task_type] = {"total": 0, "success": 0, "errors": 0}
            by_type[fb.task_type]["total"] += 1
            if fb.success:
                by_type[fb.task_type]["success"] += 1
            else:
                by_type[fb.task_type]["errors"] += 1

        # 飞轮转速（最近1小时的反馈数）
        from datetime import timedelta
        recent = sum(
            1 for f in self.feedbacks
            if datetime.fromisoformat(f.timestamp) > datetime.now() - timedelta(hours=1)
        )

        return {
            "total": total,
            "success_rate": round(success / total, 3),
            "avg_rating": round(avg_rating, 2),
            "flywheel_speed": recent,  # 飞轮转速（最近1小时）
            "by_type": by_type,
            "last_update": self.feedbacks[-1].timestamp if self.feedbacks else None,
        }

    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """获取最近告警"""
        try:
            alert_path = self.storage_path.replace("feedback.json", "alerts.jsonl")
            if not os.path.exists(alert_path):
                return []
            with open(alert_path, encoding="utf-8") as f:
                lines = f.readlines()
            return [json.loads(line) for line in lines[-limit:]]
        except:
            return []

    def _load(self):
        if not os.path.exists(self.storage_path):
            return
        try:
            data = json.load(open(self.storage_path, encoding="utf-8"))
            self.feedbacks = [Feedback(**f) for f in data.get("feedbacks", [])]
        except Exception as e:
            print(f"[FeedbackLoop] 加载失败: {e}")

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        json.dump({
            "feedbacks": [asdict(f) for f in self.feedbacks[-2000:]],  # 保留最近2000条
            "updated_at": datetime.now().isoformat(),
        }, open(self.storage_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
