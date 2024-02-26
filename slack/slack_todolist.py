import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# .env 파일에서 환경 변수 로드
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL_TODOLIST")
ISSUE_NUMBER = "60"
REPO_OWNER = "jms0522"
REPO_NAME = "Medical-project"

def get_last_issue_comment(owner, repo, issue_number, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        # 마지막 댓글의 내용 반환
        return response.json()[-1]['body']
    return None

def send_slack_message(webhook_url, message):
    formatted_message = message.replace("- [ ]", "❗️ ").replace("- [x]", ":white_check_mark:").replace("##", "💻 ")
    formatted_message = formatted_message.replace("/#", "**")  # '/#'을 '*'로 변경하여 볼드체로 만듦
    payload = {
        "username": "TodoList Update Bot",
        "icon_emoji": ":clipboard:",
        "text": f"*오늘의 TodoList 업데이트 !!*\n\n{formatted_message}",  # 볼드체로 변경 및 줄바꿈 추가
        "mrkdwn": True  # Markdown 사용을 활성화
    }
    response = requests.post(webhook_url, json=payload)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

# 메인 함수
if __name__ == "__main__":
    last_comment = get_last_issue_comment(REPO_OWNER, REPO_NAME, ISSUE_NUMBER, GITHUB_TOKEN)
    if last_comment:
        send_slack_message(SLACK_WEBHOOK_URL, last_comment)

