from dotenv import load_dotenv
import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# 닥터나우의 실시간 상담 페이지에서 questionPid를 뽑아서 question_pids 리스트를 만드는 함수 정의

def fetch_questions(url, headers, payload):
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = json.loads(response.text)
        question_pids = [
            element['question']['questionPid'] for element in data['data']['newestQuestionCardCursorPage']['elements']
        ]
        return question_pids
    else:
        response.raise_for_status()

# 슬랙 알람 코드 
load_dotenv()
webhook_url = os.getenv('SLACK_WEBHOOK_URL_MEDICAL')
if webhook_url:
    message = {"text": "닥터나우 실시간 상담 quesionPid 추출 완료 !"}
    response = requests.post(webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})
    print(response.status_code, response.text)
else:
    print("SLACK_WEBHOOK_URL_MEDICAL 환경 변수가 설정되지 않았습니다.")