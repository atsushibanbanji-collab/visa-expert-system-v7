"""
ルール管理関連のAPIエンドポイント
"""
from typing import Optional
from fastapi import APIRouter, HTTPException

from core import VISA_TYPE_ORDER
from knowledge import (
    get_all_rules, VISA_RULES, save_rules, reload_rules,
    get_all_visa_types, add_visa_type, update_visa_type, delete_visa_type, reload_visa_types
)
from schemas import RuleRequest, DeleteRequest, ReorderRequest, VisaTypeRequest
from services.validation import check_rules_integrity
from services.rule_helpers import (
    rules_to_dict_list, build_rules_data, request_to_dict
)

router = APIRouter(prefix="/api", tags=["rules"])


@router.get("/rules")
async def get_rules(visa_type: Optional[str] = None, sort: Optional[str] = "visa_type"):
    """ルール一覧を取得

    sort: "visa_type" (E→L→H-1B→B→J-1順), "none" (JSON保存順)
    """
    reload_rules()
    rules = get_all_rules()

    if visa_type:
        rules = [r for r in rules if r.visa_type == visa_type]
    if sort == "visa_type":
        rules = sorted(rules, key=lambda r: VISA_TYPE_ORDER.get(r.visa_type, 99))

    return {"rules": rules_to_dict_list(rules)}


@router.get("/visa-types")
async def get_visa_types():
    """利用可能なビザタイプを取得"""
    reload_visa_types()
    return {"visa_types": get_all_visa_types()}


@router.post("/visa-types")
async def create_visa_type(visa_type: VisaTypeRequest):
    """ビザタイプを追加"""
    data = visa_type.model_dump()
    if not add_visa_type(data):
        raise HTTPException(status_code=400, detail="ビザタイプの追加に失敗しました（コードが重複している可能性があります）")
    return {"status": "created", "code": visa_type.code}


@router.put("/visa-types/{code}")
async def update_visa_type_endpoint(code: str, visa_type: VisaTypeRequest):
    """ビザタイプを更新"""
    data = visa_type.model_dump()
    if not update_visa_type(code, data):
        raise HTTPException(status_code=404, detail="ビザタイプが見つかりません")
    return {"status": "updated", "code": code}


@router.delete("/visa-types/{code}")
async def delete_visa_type_endpoint(code: str):
    """ビザタイプを削除"""
    if not delete_visa_type(code):
        raise HTTPException(status_code=404, detail="ビザタイプが見つかりません")
    return {"status": "deleted", "code": code}


@router.get("/validation/check")
async def validate_rules(visa_type: Optional[str] = None):
    """ルールの整合性チェック"""
    reload_rules()
    issues = check_rules_integrity(visa_type)
    return {"status": "ok", "message": "問題ありません"} if not issues else {"status": "issues_found", "issues": issues}


@router.post("/rules")
async def create_rule(rule: RuleRequest):
    """新しいルールを作成

    insert_after: 挿入位置（0=先頭、N=N番目の後、None=末尾）
    """
    reload_rules()
    rules_data = build_rules_data(VISA_RULES)
    new_rule = request_to_dict(rule)

    # 挿入位置を決定
    if rule.insert_after is not None:
        insert_index = rule.insert_after
        if insert_index < 0:
            insert_index = 0
        elif insert_index > len(rules_data["rules"]):
            insert_index = len(rules_data["rules"])
        rules_data["rules"].insert(insert_index, new_rule)
    else:
        insert_index = len(rules_data["rules"])
        rules_data["rules"].append(new_rule)

    if not save_rules(rules_data):
        raise HTTPException(status_code=500, detail="Failed to save rule")

    return {"status": "created", "action": rule.action, "position": insert_index}


@router.put("/rules")
async def update_rule(rule: RuleRequest):
    """既存ルールを更新（indexで対象を特定）"""
    reload_rules()

    if rule.index is None:
        raise HTTPException(status_code=400, detail="index is required for update")

    if rule.index < 0 or rule.index >= len(VISA_RULES):
        raise HTTPException(status_code=404, detail="Rule not found at specified index")

    # インデックス位置のルールだけを更新
    rules_data = build_rules_data(VISA_RULES)
    rules_data["rules"][rule.index] = request_to_dict(rule)

    if not save_rules(rules_data):
        raise HTTPException(status_code=500, detail="Failed to save rule")
    return {"status": "updated", "action": rule.action, "index": rule.index}


@router.post("/rules/delete")
async def delete_rule(request: DeleteRequest):
    """ルールを削除（indexで特定）"""
    reload_rules()

    if request.index < 0 or request.index >= len(VISA_RULES):
        raise HTTPException(status_code=404, detail="Rule not found at specified index")

    # インデックス位置のルールだけを削除
    rules_data = build_rules_data(VISA_RULES)
    deleted_action = rules_data["rules"][request.index]["action"]
    del rules_data["rules"][request.index]

    if not save_rules(rules_data):
        raise HTTPException(status_code=500, detail="Failed to delete rule")
    return {"status": "deleted", "index": request.index, "action": deleted_action}


@router.post("/rules/reorder")
async def reorder_rules(request: ReorderRequest):
    """ルールの順序を変更"""
    reload_rules()
    rules_map = {r.action: r for r in VISA_RULES}

    reordered = []
    for action in request.actions:
        if action in rules_map:
            reordered.append(rules_map.pop(action))
    reordered.extend(rules_map.values())

    if not save_rules(build_rules_data(reordered)):
        raise HTTPException(status_code=500, detail="Failed to save rule order")
    return {"status": "reordered", "count": len(reordered)}


@router.post("/rules/reload")
async def reload_all_rules():
    """ルールをJSONファイルから再読み込み"""
    reload_rules()
    return {"status": "reloaded", "count": len(VISA_RULES)}
