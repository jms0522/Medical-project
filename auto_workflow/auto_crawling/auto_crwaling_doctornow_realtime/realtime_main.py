from dotenv import load_dotenv
from get_questionPid import fetch_questions  
from scape_contents import scrape_and_save_questions  
import os
import requests
import json


if __name__ == "__main__":
    
    url = "https://bff.doctornow.co.kr/graphql"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "Origin": "https://doctornow.co.kr",
        "Referer": "https://doctornow.co.kr/",
        "Sec-Ch-Ua": "\"Not A(Brand\";v=\"99\", \"Google Chrome\";v=\"121\", \"Chromium\";v=\"121\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

    payload = {
        "query": """
            query getNewestQuestionCardCursorPage($request: NewestQuestionCardCursorPageRequestInput!) {
                newestQuestionCardCursorPage(request: $request) {
                    elements {
                        question {
                            questionPid
                        }
                    }
                }
            }
        """,
        "variables": {
            "request": {
                "size": 100,
                "answered": False,
                "categoryId": None,
                "pivot": "a533d2707c70402f8bfe9d401cf5eb80"
            }
        }
    }
    try:
        question_pids = fetch_questions(url, headers, payload)
        # 가져온 질문 ID를 이용해 상세 정보 스크래핑 후 CSV에 저장
        scrape_and_save_questions(question_pids)
    except Exception as e:
        print(f"An error occurred: {e}")


# 슬랙 알람 코드 
load_dotenv()
webhook_url = os.getenv('SLACK_WEBHOOK_URL_MEDICAL')
if webhook_url:
    message = {"text": "닥터나우 실시간 상담 contents 데이터 CSV 파일 저장 완료 ! \n file : doctornow_realtime.csv"}
    response = requests.post(webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})
    print(response.status_code, response.text)
else:
    print("SLACK_WEBHOOK_URL_MEDICAL 환경 변수가 설정되지 않았습니다.")
