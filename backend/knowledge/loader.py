"""
ルール読み込み機能
"""
import os
import json
from typing import List

from core import Rule


# データファイルのパス
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RULES_FILE = os.path.join(DATA_DIR, "rules.json")


class RuleLoadError(Exception):
    """ルールファイル読み込みエラー"""
    pass


def load_rules_from_json() -> List[Rule]:
    """JSONファイルからルールを読み込む

    Raises:
        RuleLoadError: ルールファイルが存在しない、または読み込みに失敗した場合
    """
    if not os.path.exists(RULES_FILE):
        raise RuleLoadError(f"ルールファイルが見つかりません: {RULES_FILE}")

    with open(RULES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rules = []
    for idx, r in enumerate(data.get("rules", [])):
        if "conditions" not in r or "action" not in r:
            raise RuleLoadError(f"ルール {idx+1} に必須フィールドがありません")

        rule = Rule(
            conditions=r["conditions"],
            action=r["action"],
            is_or_rule=r.get("is_or_rule", False),
            is_goal_action=r.get("is_goal_action", False)
        )
        rules.append(rule)

    if not rules:
        raise RuleLoadError("ルールファイルにルールが定義されていません")

    return rules


def save_rules_to_json(rules_data: dict) -> None:
    """ルールをJSONファイルに保存

    Raises:
        RuleLoadError: 保存に失敗した場合
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(rules_data, f, ensure_ascii=False, indent=2)
