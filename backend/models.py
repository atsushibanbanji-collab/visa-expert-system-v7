"""
ビザ選定エキスパートシステム - データモデル
Smalltalk資料のオブジェクト指向設計に基づく実装
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from enum import Enum


class AnswerType(str, Enum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class ConditionStatus(str, Enum):
    UNCHECKED = "unchecked"  # グレー: 未確認
    TRUE = "true"            # 緑: Yes
    FALSE = "false"          # 赤: No
    UNKNOWN = "unknown"      # 黄色: わからない
    DERIVED = "derived"      # 紫: 他ルールから導出


class RuleStatus(str, Enum):
    PENDING = "pending"      # 未評価
    FIRED = "fired"          # 発火済み
    BLOCKED = "blocked"      # 発火不可能


class VisaType(str, Enum):
    E = "E"
    B = "B"
    L = "L"
    H1B = "H-1B"
    J1 = "J-1"


# API リクエスト/レスポンスモデル
class StartConsultationRequest(BaseModel):
    visa_type: Optional[str] = None  # None = 全ビザタイプを診断


class AnswerRequest(BaseModel):
    question_key: str
    answer: AnswerType


class GoBackRequest(BaseModel):
    steps: int = 1


class QuestionResponse(BaseModel):
    key: str
    text: str
    is_final: bool = False
    related_visa_types: List[str] = []


class RuleDisplayInfo(BaseModel):
    id: str
    name: str
    visa_type: str
    conditions: List[Dict[str, Any]]
    conclusion: str
    status: str
    is_and_rule: bool


class ConsultationStateResponse(BaseModel):
    current_question: Optional[QuestionResponse]
    answered_questions: List[Dict[str, Any]]
    rules_status: List[RuleDisplayInfo]
    derived_facts: List[str]
    is_complete: bool
    results: Optional[Dict[str, Any]] = None


class DiagnosisResult(BaseModel):
    applicable_visas: List[str]
    conditional_visas: List[Dict[str, Any]]
    unknown_conditions: List[str]
    reasoning_history: List[str]
