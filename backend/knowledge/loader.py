"""
ルール読み込み機能
"""
import os
import json
from typing import List

from core import Rule, RuleType
from core.constants import DEFAULT_GOAL_ACTIONS

# データファイルのパス
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RULES_FILE = os.path.join(DATA_DIR, "rules.json")


def load_rules_from_json() -> List[Rule]:
    """JSONファイルからルールを読み込む"""
    if not os.path.exists(RULES_FILE):
        return _get_fallback_rules()

    try:
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        rules = []
        for r in data.get("rules", []):
            rule = Rule(
                conditions=r["conditions"],
                action=r["action"],
                rule_type=RuleType(r.get("rule_type", "i")),
                is_or_rule=r.get("is_or_rule", False),
                visa_type=r.get("visa_type", "")
            )
            rules.append(rule)
        return rules
    except Exception as e:
        print(f"Warning: Failed to load rules from JSON: {e}")
        return _get_fallback_rules()


def load_goal_actions_from_json() -> List[str]:
    """JSONファイルからゴールアクションを読み込む"""
    if not os.path.exists(RULES_FILE):
        return DEFAULT_GOAL_ACTIONS.copy()

    try:
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("goal_actions", DEFAULT_GOAL_ACTIONS.copy())
    except Exception:
        return DEFAULT_GOAL_ACTIONS.copy()


def save_rules_to_json(rules_data: dict) -> bool:
    """ルールをJSONファイルに保存"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(rules_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving rules: {e}")
        return False


def _get_fallback_rules() -> List[Rule]:
    """フォールバック用の最小限ルール"""
    # JSONファイルが読めない場合のエラー防止用
    # 本番運用では rules.json が必須
    return []
