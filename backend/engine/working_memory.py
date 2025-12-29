"""
作業記憶 - 診断中の状態管理
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from core import Rule, FactStatus, RuleStatus


@dataclass
class WorkingMemory:
    """作業記憶クラス

    Smalltalk資料のWorkingMemoryクラスに相当。
    診断における問題の状況（作業記憶）を扱う。
    - findings: 所見（利用者の回答）
    - hypotheses: 仮説（ルールにより導出された事実）
    """
    findings: Dict[str, FactStatus] = field(default_factory=dict)
    hypotheses: Dict[str, FactStatus] = field(default_factory=dict)
    answer_history: List[Tuple[str, FactStatus]] = field(default_factory=list)

    def get_value(self, condition: str) -> Optional[FactStatus]:
        """作業記憶から指定された要素の値を取り出して返す"""
        if condition in self.findings:
            return self.findings[condition]
        if condition in self.hypotheses:
            return self.hypotheses[condition]
        return None

    def put_finding(self, condition: str, value: FactStatus):
        """利用者の回答を作業記憶に追加"""
        self.findings[condition] = value
        self.answer_history.append((condition, value))

    def put_hypothesis(self, condition: str, value: FactStatus):
        """導出された仮説を作業記憶に追加"""
        self.hypotheses[condition] = value

    def clear_after(self, condition: str):
        """指定した条件以降の回答と依存する仮説をクリア"""
        idx = -1
        for i, (cond, _) in enumerate(self.answer_history):
            if cond == condition:
                idx = i
                break

        if idx >= 0:
            to_remove = [c for c, _ in self.answer_history[idx:]]
            self.answer_history = self.answer_history[:idx]
            for cond in to_remove:
                if cond in self.findings:
                    del self.findings[cond]
            self.hypotheses.clear()


@dataclass
class RuleState:
    """ルールの評価状態"""
    rule: Rule
    status: RuleStatus = RuleStatus.PENDING
    checked_conditions: Dict[str, FactStatus] = field(default_factory=dict)
