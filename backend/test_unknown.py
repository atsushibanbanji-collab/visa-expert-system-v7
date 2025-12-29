# -*- coding: utf-8 -*-
"""Unknown answer test"""
import requests

BASE_URL = 'http://localhost:8000'

def test_unknown_flow():
    session_id = 'test_unknown_1'

    resp = requests.post(f'{BASE_URL}/api/consultation/start', json={'session_id': session_id})
    data = resp.json()

    question_count = 0
    max_questions = 30

    while not data.get('is_complete') and question_count < max_questions:
        question = data.get('current_question')
        if not question:
            print(f'[STOPPED] question is null (count={question_count})')
            print(f'is_complete: {data.get("is_complete")}')
            break

        question_count += 1
        print(f'Q{question_count}: {question}')

        resp = requests.post(f'{BASE_URL}/api/consultation/answer', json={
            'session_id': session_id,
            'answer': 'unknown'
        })
        data = resp.json()

    if data.get('is_complete'):
        print('')
        print(f'[COMPLETED] Done ({question_count} questions)')
        result = data.get('diagnosis_result', {})
        print(f'Applicable: {result.get("applicable_visas", [])}')
        print(f'Conditional: {result.get("conditional_visas", [])}')
    else:
        print('')
        print('[NOT COMPLETED] Stopped early')

if __name__ == '__main__':
    test_unknown_flow()
