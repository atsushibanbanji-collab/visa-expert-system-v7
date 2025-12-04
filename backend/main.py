"""
ビザ選定エキスパートシステム - FastAPI メインアプリケーション
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json

from inference_engine import InferenceEngine
from knowledge_base import get_all_rules, get_goal_rules, VISA_RULES

app = FastAPI(
    title="ビザ選定エキスパートシステム",
    description="オブジェクト指向設計によるビザ選定支援システム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# セッション管理（実運用ではRedisなどを使用）
sessions: Dict[str, InferenceEngine] = {}


class StartRequest(BaseModel):
    session_id: str


class AnswerRequest(BaseModel):
    session_id: str
    answer: str  # "yes", "no", "unknown"


class GoBackRequest(BaseModel):
    session_id: str
    steps: int = 1


@app.get("/")
async def root():
    return {"message": "ビザ選定エキスパートシステム API", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/consultation/start")
async def start_consultation(request: StartRequest):
    """診断を開始"""
    engine = InferenceEngine()
    first_question = engine.start_consultation()

    sessions[request.session_id] = engine

    return {
        "session_id": request.session_id,
        "current_question": first_question,
        "related_visa_types": engine.get_related_visa_types(first_question) if first_question else [],
        "rules_status": engine._get_rules_display_info(),
        "is_complete": first_question is None
    }


@app.post("/api/consultation/answer")
async def answer_question(request: AnswerRequest):
    """質問に回答"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    engine = sessions[request.session_id]

    if not engine.current_question:
        raise HTTPException(status_code=400, detail="No current question")

    result = engine.answer_question(engine.current_question, request.answer)

    response = {
        "session_id": request.session_id,
        "current_question": result["next_question"],
        "related_visa_types": engine.get_related_visa_types(result["next_question"]) if result["next_question"] else [],
        "rules_status": result["rules_status"],
        "derived_facts": result["derived_facts"],
        "is_complete": result["is_complete"]
    }

    if result["is_complete"]:
        response["diagnosis_result"] = result.get("diagnosis_result")

    return response


@app.post("/api/consultation/back")
async def go_back(request: GoBackRequest):
    """前の質問に戻る"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    engine = sessions[request.session_id]
    result = engine.go_back(request.steps)

    return {
        "session_id": request.session_id,
        "current_question": result["current_question"],
        "related_visa_types": engine.get_related_visa_types(result["current_question"]) if result["current_question"] else [],
        "answered_questions": result["answered_questions"],
        "rules_status": result["rules_status"]
    }


@app.post("/api/consultation/restart")
async def restart_consultation(request: StartRequest):
    """最初からやり直し"""
    engine = InferenceEngine()
    first_question = engine.start_consultation()

    sessions[request.session_id] = engine

    return {
        "session_id": request.session_id,
        "current_question": first_question,
        "related_visa_types": engine.get_related_visa_types(first_question) if first_question else [],
        "rules_status": engine._get_rules_display_info(),
        "is_complete": first_question is None
    }


@app.get("/api/consultation/state/{session_id}")
async def get_state(session_id: str):
    """現在の状態を取得"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    engine = sessions[session_id]
    state = engine.get_current_state()

    return {
        "session_id": session_id,
        **state,
        "related_visa_types": engine.get_related_visa_types(state["current_question"]) if state["current_question"] else []
    }


# ========== 管理機能 ==========

@app.get("/api/rules")
async def get_rules(visa_type: Optional[str] = None):
    """ルール一覧を取得"""
    rules = get_all_rules()

    if visa_type:
        rules = [r for r in rules if r.visa_type == visa_type]

    return {
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "conditions": r.conditions,
                "action": r.action,
                "is_or_rule": r.is_or_rule,
                "visa_type": r.visa_type,
                "rule_type": r.rule_type.value
            }
            for r in rules
        ]
    }


@app.get("/api/rules/{rule_id}")
async def get_rule(rule_id: str):
    """特定のルールを取得"""
    for rule in VISA_RULES:
        if rule.id == rule_id:
            return {
                "id": rule.id,
                "name": rule.name,
                "conditions": rule.conditions,
                "action": rule.action,
                "is_or_rule": rule.is_or_rule,
                "visa_type": rule.visa_type,
                "rule_type": rule.rule_type.value
            }

    raise HTTPException(status_code=404, detail="Rule not found")


@app.get("/api/visa-types")
async def get_visa_types():
    """利用可能なビザタイプを取得"""
    return {
        "visa_types": [
            {"code": "E", "name": "Eビザ（投資家・貿易）", "description": "投資家や貿易業者向けのビザ"},
            {"code": "L", "name": "Lビザ（企業内転勤）", "description": "グループ企業間の転勤者向けビザ"},
            {"code": "B", "name": "Bビザ（商用）", "description": "短期商用目的のビザ"},
            {"code": "H-1B", "name": "H-1Bビザ（専門職）", "description": "専門的職業従事者向けビザ"},
            {"code": "J-1", "name": "J-1ビザ（研修）", "description": "研修・交流目的のビザ"},
        ]
    }


@app.get("/api/validation/check")
async def validate_rules(visa_type: Optional[str] = None):
    """ルールの整合性チェック"""
    rules = get_all_rules()
    if visa_type:
        rules = [r for r in rules if r.visa_type == visa_type]

    issues = []
    all_actions = {r.action for r in VISA_RULES}
    all_conditions = set()
    for r in VISA_RULES:
        all_conditions.update(r.conditions)

    # 到達不能なルールをチェック
    for rule in rules:
        for cond in rule.conditions:
            if cond in all_actions:
                # この条件は他のルールの結論
                producing_rules = [r for r in VISA_RULES if r.action == cond]
                if not producing_rules:
                    issues.append({
                        "type": "unreachable",
                        "rule_id": rule.id,
                        "message": f"条件「{cond}」を導出するルールがありません"
                    })

    # 循環参照をチェック
    def check_cycle(rule_id: str, visited: set, path: list):
        if rule_id in visited:
            return path + [rule_id]
        visited.add(rule_id)
        path.append(rule_id)

        rule = next((r for r in VISA_RULES if r.id == rule_id), None)
        if rule:
            for cond in rule.conditions:
                if cond in all_actions:
                    dep_rules = [r for r in VISA_RULES if r.action == cond]
                    for dep_rule in dep_rules:
                        cycle = check_cycle(dep_rule.id, visited.copy(), path.copy())
                        if cycle:
                            return cycle
        return None

    for rule in rules:
        cycle = check_cycle(rule.id, set(), [])
        if cycle and len(cycle) > 1:
            issues.append({
                "type": "cycle",
                "rule_ids": cycle,
                "message": f"ルールに循環参照があります: {' -> '.join(cycle)}"
            })

    if not issues:
        return {"status": "ok", "message": "問題ありません"}

    return {"status": "issues_found", "issues": issues}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
