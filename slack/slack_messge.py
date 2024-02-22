import json
import requests
import sys

def send_msg(msg):
    url = "https://hooks.slack.com/services/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"  # 웹후크 URL을 입력하세요
    message = "Medical project message :\n" + msg  # 보낼 메시지
    slack_data = {
        "username": "Medical project management bot",  # 보내는 사람 이름
        "icon_emoji": ":satellite:",
        "text": message,  # 여기서 메시지를 전송합니다
    }

    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

# 사용 예시
send_msg("python 코드로 구현한 메시지입니당,..")
