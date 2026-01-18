"""
ルール評価ロジック
"""
from typing import Dict, List, Optional

from core import Rule, FactStatus, RuleStatus
from .working_memory import WorkingMemory, RuleState


class RuleEvaluator:
    """ルール評価クラス"""

    def __init__(
        self,
        working_memory: WorkingMemory,
        rule_states: Dict[str, RuleState],
        derived_conditions: set,
        rules: List[Rule]
    ):
        self.working_memory = working_memory
        self.rule_states = rule_states
        self.derived_conditions = derived_conditions
        self.rules = rules

    def get_effective_value(self, condition: str) -> Optional[FactStatus]:
        """条件の実効値を取得

        導出可能条件の場合、hypothesesのTRUEはfindingsのUNKNOWNより優先する。
        """
        finding_val = self.working_memory.findings.get(condition)
        hypo_val = self.working_memory.hypotheses.get(condition)

        if condition in self.derived_conditions:
            if hypo_val == FactStatus.TRUE:
                return FactStatus.TRUE
            if hypo_val == FactStatus.FALSE:
                return FactStatus.FALSE

        if finding_val is not None:
            return finding_val
        if hypo_val is not None:
            return hypo_val
        return None

    def get_deriving_rules(self, condition: str) -> List[Rule]:
        """条件を導出するルールを取得"""
        return [r for r in self.rules if r.action == condition]

    def evaluate_all_rules(self):
        """全ルールを評価してステータスを更新"""
        for rule_id, state in self.rule_states.items():
            self._evaluate_single_rule(state)

    def _evaluate_single_rule(self, state: RuleState):
        """単一ルールを評価"""
        rule = state.rule

        all_true = True
        any_true = False
        any_false = False
        has_unknown = False

        for cond in rule.conditions:
            val = self.get_effective_value(cond)
            state.checked_conditions[cond] = val if val else FactStatus.PENDING

            if val == FactStatus.TRUE:
                any_true = True
            elif val == FactStatus.FALSE:
                any_false = True
                all_true = False
            elif val == FactStatus.UNKNOWN:
                has_unknown = True
                all_true = False
            else:
                all_true = False

        if rule.is_or_rule:
            self._evaluate_or_rule(state, any_true)
        else:
            self._evaluate_and_rule(state, all_true, any_false, has_unknown)

    def _evaluate_or_rule(self, state: RuleState, any_true: bool):
        """ORルールを評価"""
        if any_true:
            state.status = RuleStatus.FIRED
            return

        all_resolved_negative = True
        has_any_unknown = False

        for cond in state.rule.conditions:
            val = state.checked_conditions.get(cond)
            if val == FactStatus.TRUE:
                all_resolved_negative = False
                break
            elif val == FactStatus.UNKNOWN:
                has_any_unknown = True
                if cond in self.derived_conditions:
                    deriving_rules = self.get_deriving_rules(cond)
                    for dr in deriving_rules:
                        if not RuleStatus.is_resolved(self.rule_states[dr.id].status):
                            all_resolved_negative = False
                            break
                    if not all_resolved_negative:
                        break
            elif val is None or val == FactStatus.PENDING:
                all_resolved_negative = False
                break

        if all_resolved_negative:
            state.status = RuleStatus.UNCERTAIN if has_any_unknown else RuleStatus.BLOCKED

    def _evaluate_and_rule(self, state: RuleState, all_true: bool, any_false: bool, has_unknown: bool):
        """ANDルールを評価"""
        if all_true:
            state.status = RuleStatus.FIRED
        elif any_false:
            state.status = RuleStatus.BLOCKED
        elif has_unknown:
            all_answered = all(
                self.get_effective_value(cond) not in (None, FactStatus.PENDING)
                for cond in state.rule.conditions
            )
            if all_answered:
                state.status = RuleStatus.UNCERTAIN
