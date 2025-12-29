"""
ルールストア - ルールの保存・取得機能
"""
from typing import List

from core import Rule, VISA_TYPE_ORDER
from .loader import load_rules_from_json, load_goal_actions_from_json, save_rules_to_json


# グローバルルールストア（初回アクセス時にロード）
VISA_RULES: List[Rule] = load_rules_from_json()


def get_all_rules() -> List[Rule]:
    """全ルールを取得"""
    return VISA_RULES.copy()


def get_rules_by_visa_type(visa_type: str) -> List[Rule]:
    """ビザタイプでルールをフィルタ"""
    return [r for r in VISA_RULES if r.visa_type == visa_type]


def get_goal_rules() -> List[Rule]:
    """ゴールルール（最終結論を導くルール）を取得（E→L→H-1B→B→J-1順）"""
    goal_actions = load_goal_actions_from_json()
    goal_rules = [r for r in VISA_RULES if r.action in goal_actions]
    return sorted(goal_rules, key=lambda r: VISA_TYPE_ORDER.get(r.visa_type, 99))


def get_all_base_conditions() -> set:
    """全ての基本条件（他のルールの結論ではないもの）を取得"""
    all_conditions = set()
    all_actions = {r.action for r in VISA_RULES}

    for rule in VISA_RULES:
        for cond in rule.conditions:
            if cond not in all_actions:
                all_conditions.add(cond)

    return all_conditions


def get_derived_conditions() -> set:
    """導出可能な条件（他のルールの結論であるもの）を取得"""
    return {r.action for r in VISA_RULES}


def reload_rules() -> List[Rule]:
    """ルールを再読み込み（編集後に呼び出す）

    注意: リストをin-place更新することで、
    他モジュールからimportされた参照も最新データを指すようになる
    """
    global VISA_RULES
    new_rules = load_rules_from_json()
    VISA_RULES.clear()
    VISA_RULES.extend(new_rules)
    return VISA_RULES


def save_rules(rules_data: dict) -> bool:
    """ルールをJSONファイルに保存"""
    if save_rules_to_json(rules_data):
        reload_rules()
        return True
    return False
