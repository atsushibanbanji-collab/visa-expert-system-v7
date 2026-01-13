"""
定数定義
"""
import json
from pathlib import Path


def _load_visa_type_order() -> dict:
    """visa_types.json から順序マップを動的に生成"""
    visa_types_file = Path(__file__).parent.parent / "knowledge" / "visa_types.json"
    try:
        with open(visa_types_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {v["code"]: v.get("order", 99) for v in data.get("visa_types", [])}
    except (FileNotFoundError, json.JSONDecodeError):
        # フォールバック
        return {"E": 0, "L": 1, "H-1B": 2, "B": 3, "J-1": 4}


# ビザタイプの表示・質問順序（起動時に読み込み）
VISA_TYPE_ORDER = _load_visa_type_order()


# ゴールアクション（最終結論）のデフォルト値
DEFAULT_GOAL_ACTIONS = [
    "Eビザでの申請ができます",
    "Blanket Lビザでの申請ができます",
    "Lビザ（Individual）での申請ができます",
    "Bビザの申請ができます",
    "契約書に基づくBビザの申請ができます",
    "B-1 in lieu of H-1Bビザの申請ができます",
    "B-1 in lieu of H3ビザの申請ができます",
    "H-1Bビザでの申請ができます",
    "J-1ビザの申請ができます",
]
