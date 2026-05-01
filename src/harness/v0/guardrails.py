"""
L3: Guardrails — 安全边界
不做过度设计，只定义最关键的3条红线
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    """Guardrail 检查结果"""
    passed: bool
    violations: List[str]
    warning: Optional[str] = None


class Guardrails:
    """
    安全边界系统

    设计哲学：
    - 不追求"全面"，只守住最关键的边界
    - 3条红线 + 1条警告线 = 足够
    """

    # 红线1：数据不外泄
    FORBIDDEN_PATTERNS = [
        "password", "secret", "api_key", "token",
        "private_key", "credential", "auth",
    ]

    # 红线2：不执行危险动作
    DANGEROUS_ACTIONS = [
        "delete", "drop", "truncate", "rm -rf",
        "format", "shutdown", "reboot",
    ]

    # 红线3：不输出有害内容
    HARMFUL_CONTENT = [
        "hack", "exploit", "virus", "malware",
        "phishing", "attack",
    ]

    def __init__(self):
        self.violation_history: List[Dict] = []
        self.stats = {
            "total_checks": 0,
            "violations": 0,
            "warnings": 0,
        }

    def check(self, context: Any, output: Dict) -> GuardrailResult:
        """
        检查输出是否安全

        三层检查：
        1. 内容检查（有害内容）
        2. 行动检查（危险动作）
        3. 数据检查（信息泄露）
        """
        self.stats["total_checks"] += 1
        violations = []
        warnings = []

        output_str = str(output).lower()

        # 1. 有害内容检查
        for pattern in self.HARMFUL_CONTENT:
            if pattern in output_str:
                violations.append(f"有害内容: {pattern}")

        # 2. 危险行动检查
        for action in self.DANGEROUS_ACTIONS:
            if action in output_str:
                violations.append(f"危险动作: {action}")

        # 3. 数据泄露检查
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in output_str:
                violations.append(f"潜在数据泄露: {pattern}")

        # 警告检查（不阻断）
        if "error" in output_str or "fail" in output_str:
            warnings.append("输出包含错误标识，需人工确认")

        passed = len(violations) == 0

        if not passed:
            self.stats["violations"] += 1
            self._record_violation(context, violations)
        elif warnings:
            self.stats["warnings"] += 1

        return GuardrailResult(
            passed=passed,
            violations=violations,
            warning=warnings[0] if warnings else None,
        )

    def check_context(self, context: Any) -> GuardrailResult:
        """检查输入上下文"""
        violations = []

        # 检查敏感数据
        ctx_str = str(context.__dict__ if hasattr(context, '__dict__') else context).lower()
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in ctx_str:
                violations.append(f"敏感数据: {pattern}")

        return GuardrailResult(
            passed=len(violations) == 0,
            violations=violations,
        )

    def _record_violation(self, context: Any, violations: List[str]):
        """记录违规历史"""
        from datetime import datetime
        self.violation_history.append({
            "timestamp": datetime.now().isoformat(),
            "violations": violations,
            "context_type": type(context).__name__,
        })
        # 只保留最近100条
        if len(self.violation_history) > 100:
            self.violation_history = self.violation_history[-100:]

    def fallback(self, context: Any) -> Dict:
        """
        违规时的后备响应
        不返回错误，而是返回安全替代
        """
        return {
            "status": "blocked",
            "message": "输出被安全边界拦截",
            "recommendation": "请人工审查",
        }

    def get_stats(self) -> Dict:
        return {
            **self.stats,
            "recent_violations": self.violation_history[-5:],
        }
