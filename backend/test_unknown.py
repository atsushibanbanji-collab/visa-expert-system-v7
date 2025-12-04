"""わからないを多用した場合のテスト"""
import requests

BASE_URL = "http://localhost:8001"

def test_unknown_flow():
    session_id = "test_unknown_1"

    # 診断開始
    resp = requests.post(f"{BASE_URL}/api/consultation/start", json={"session_id": session_id})
    data = resp.json()

    question_count = 0
    max_questions = 30  # 無限ループ防止

    while not data.get("is_complete") and question_count < max_questions:
        question = data.get("current_question")
        if not question:
            print(f"[STOPPED] 質問がnullになりました (question_count={question_count})")
            print(f"is_complete: {data.get('is_complete')}")
            break

        question_count += 1
        print(f"Q{question_count}: {question}")

        # 全て「わからない」で回答
        resp = requests.post(f"{BASE_URL}/api/consultation/answer", json={
            "session_id": session_id,
            "answer": "unknown"
        })
        data = resp.json()

    if data.get("is_complete"):
        print(f"\n[COMPLETED] 診断完了 ({question_count}問)")
        result = data.get("diagnosis_result", {})
        print(f"適用可能: {result.get('applicable_visas', [])}")
        print(f"条件付き: {result.get('conditional_visas', [])}")
    else:
        print(f"\n[NOT COMPLETED] 途中で停止")

if __name__ == "__main__":
    test_unknown_flow()
