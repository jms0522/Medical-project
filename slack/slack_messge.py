import json
import requests
import sys
from dotenv import load_dotenv
import os


load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL_MEDICAL")

def send_msg(msg):
    url = SLACK_WEBHOOK_URL
    slack_data = {"text": "Medical project message :\n" + msg}
    response = requests.post(url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
    
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

send_msg("데이터 전처리 작업이 완료 되었습니다.")

