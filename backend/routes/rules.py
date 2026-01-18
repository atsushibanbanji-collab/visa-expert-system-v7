"""
ルール管理関連のAPIエンドポイント
"""
import csv
import io
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse

from knowledge import (
    get_all_rules, RULES, save_rules, reload_rules
)
from schemas import RuleRequest, DeleteRequest, ReorderRequest, ImportApplyRequest
from services.validation import check_rules_integrity
from services.rule_helpers import (
    rules_to_dict_list, build_rules_data, request_to_dict
)

# CSV列定義
CSV_COLUMNS = ["No", "action", "condition1", "condition2", "condition3", "condition4",
               "operator", "is_goal"]
MAX_CONDITIONS = 4

router = APIRouter(prefix="/api", tags=["rules"])


@router.get("/rules")
async def get_rules():
    """ルール一覧を取得（rules.json順）"""
    reload_rules()
    rules = get_all_rules()
    return {"rules": rules_to_dict_list(rules)}


@router.get("/validation/check")
async def validate_rules():
    """ルールの整合性チェック"""
    reload_rules()
    issues = check_rules_integrity()
    return {"status": "ok", "message": "問題ありません"} if not issues else {"status": "issues_found", "issues": issues}


@router.post("/rules")
async def create_rule(rule: RuleRequest):
    """新しいルールを作成

    insert_after: 挿入位置（0=先頭、N=N番目の後、None=末尾）
    """
    reload_rules()
    rules_data = build_rules_data(RULES)
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

    save_rules(rules_data)
    return {"status": "created", "action": rule.action, "position": insert_index}


@router.put("/rules")
async def update_rule(rule: RuleRequest):
    """既存ルールを更新（indexで対象を特定）"""
    reload_rules()

    if rule.index is None:
        raise HTTPException(status_code=400, detail="index is required for update")

    if rule.index < 0 or rule.index >= len(RULES):
        raise HTTPException(status_code=404, detail="Rule not found at specified index")

    # インデックス位置のルールだけを更新
    rules_data = build_rules_data(RULES)
    rules_data["rules"][rule.index] = request_to_dict(rule)

    save_rules(rules_data)
    return {"status": "updated", "action": rule.action, "index": rule.index}


@router.post("/rules/delete")
async def delete_rule(request: DeleteRequest):
    """ルールを削除（indexで特定）"""
    reload_rules()

    if request.index < 0 or request.index >= len(RULES):
        raise HTTPException(status_code=404, detail="Rule not found at specified index")

    # インデックス位置のルールだけを削除
    rules_data = build_rules_data(RULES)
    deleted_action = rules_data["rules"][request.index]["action"]
    del rules_data["rules"][request.index]

    save_rules(rules_data)
    return {"status": "deleted", "index": request.index, "action": deleted_action}


@router.post("/rules/reorder")
async def reorder_rules(request: ReorderRequest):
    """ルールの順序を変更"""
    reload_rules()
    rules_map = {r.action: r for r in RULES}

    reordered = []
    for action in request.actions:
        if action in rules_map:
            reordered.append(rules_map.pop(action))
    reordered.extend(rules_map.values())

    save_rules(build_rules_data(reordered))
    return {"status": "reordered", "count": len(reordered)}


@router.post("/rules/reload")
async def reload_all_rules():
    """ルールをJSONファイルから再読み込み"""
    reload_rules()
    return {"status": "reloaded", "count": len(RULES)}


@router.get("/rules/export")
async def export_rules_csv():
    """ルールをCSV形式でエクスポート"""
    reload_rules()
    rules = get_all_rules()

    # UTF-8 BOM付きCSVを生成
    output = io.StringIO()
    output.write('\ufeff')  # BOM for Excel

    writer = csv.writer(output)
    writer.writerow(CSV_COLUMNS)

    for idx, rule in enumerate(rules):
        row = [idx + 1, rule.action]

        # 条件を最大4つまで展開
        conditions = list(rule.conditions) + [""] * MAX_CONDITIONS
        row.extend(conditions[:MAX_CONDITIONS])

        row.append("OR" if rule.is_or_rule else "AND")
        row.append("TRUE" if rule.is_goal_action else "FALSE")

        writer.writerow(row)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=rules.csv"}
    )


@router.post("/rules/import")
async def import_rules_csv(file: UploadFile = File(...)):
    """CSVファイルからルールをインポート"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="CSVファイルを選択してください")

    content = await file.read()

    # BOM対応でデコード
    try:
        text = content.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = content.decode('cp932')  # Shift-JIS fallback

    reader = csv.DictReader(io.StringIO(text))

    new_rules = []
    errors = []

    for row_num, row in enumerate(reader, start=2):
        try:
            # 条件を収集（空でないもの）
            conditions = []
            for i in range(1, MAX_CONDITIONS + 1):
                cond = row.get(f"condition{i}", "").strip()
                if cond:
                    conditions.append(cond)

            if not conditions:
                errors.append(f"行{row_num}: 条件が1つも指定されていません")
                continue

            action = row.get("action", "").strip()
            if not action:
                errors.append(f"行{row_num}: actionが空です")
                continue

            operator = row.get("operator", "AND").strip().upper()
            is_goal = row.get("is_goal", "FALSE").strip().upper() == "TRUE"

            new_rules.append({
                "conditions": conditions,
                "action": action,
                "is_or_rule": operator == "OR",
                "is_goal_action": is_goal
            })

        except Exception as e:
            errors.append(f"行{row_num}: {str(e)}")

    if errors:
        return {"status": "error", "errors": errors, "parsed_count": len(new_rules)}

    # プレビューモード（実際には保存しない）
    return {
        "status": "preview",
        "rules_count": len(new_rules),
        "rules": new_rules
    }


@router.post("/rules/import/apply")
async def apply_imported_rules(request: ImportApplyRequest):
    """インポートしたルールを適用"""
    rules_data = {"rules": request.rules}
    save_rules(rules_data)
    return {"status": "applied", "count": len(request.rules)}
