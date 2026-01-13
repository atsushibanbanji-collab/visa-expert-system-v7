"""
ビザタイプストア - ビザタイプの読み書き機能
"""
import json
from pathlib import Path
from typing import List, Dict, Optional

# JSONファイルのパス
VISA_TYPES_FILE = Path(__file__).parent / "visa_types.json"


def _load_visa_types() -> List[Dict]:
    """JSONファイルからビザタイプを読み込み"""
    try:
        with open(VISA_TYPES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("visa_types", [])
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def _save_visa_types(visa_types: List[Dict]) -> bool:
    """ビザタイプをJSONファイルに保存"""
    try:
        with open(VISA_TYPES_FILE, "w", encoding="utf-8") as f:
            json.dump({"visa_types": visa_types}, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# グローバルストア（初回アクセス時にロード）
VISA_TYPES: List[Dict] = _load_visa_types()


def get_all_visa_types() -> List[Dict]:
    """全ビザタイプを取得（order順）"""
    return sorted(VISA_TYPES, key=lambda v: v.get("order", 99))


def get_visa_type_codes() -> List[str]:
    """ビザタイプコードのリストを取得（order順）"""
    return [v["code"] for v in get_all_visa_types()]


def get_visa_type_order() -> Dict[str, int]:
    """ビザタイプの順序マップを取得"""
    return {v["code"]: v.get("order", 99) for v in VISA_TYPES}


def get_visa_type_by_code(code: str) -> Optional[Dict]:
    """コードでビザタイプを取得"""
    for v in VISA_TYPES:
        if v["code"] == code:
            return v
    return None


def reload_visa_types() -> List[Dict]:
    """ビザタイプを再読み込み"""
    global VISA_TYPES
    new_types = _load_visa_types()
    VISA_TYPES.clear()
    VISA_TYPES.extend(new_types)
    return VISA_TYPES


def add_visa_type(visa_type: Dict) -> bool:
    """ビザタイプを追加"""
    # 重複チェック
    if any(v["code"] == visa_type["code"] for v in VISA_TYPES):
        return False

    # orderが指定されていなければ末尾に
    if "order" not in visa_type:
        max_order = max((v.get("order", 0) for v in VISA_TYPES), default=-1)
        visa_type["order"] = max_order + 1

    VISA_TYPES.append(visa_type)
    return _save_visa_types(VISA_TYPES)


def update_visa_type(code: str, updates: Dict) -> bool:
    """ビザタイプを更新"""
    for i, v in enumerate(VISA_TYPES):
        if v["code"] == code:
            VISA_TYPES[i] = {**v, **updates}
            return _save_visa_types(VISA_TYPES)
    return False


def delete_visa_type(code: str) -> bool:
    """ビザタイプを削除"""
    for i, v in enumerate(VISA_TYPES):
        if v["code"] == code:
            del VISA_TYPES[i]
            return _save_visa_types(VISA_TYPES)
    return False
