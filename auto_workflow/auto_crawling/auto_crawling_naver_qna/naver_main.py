from scrape_doctor_profiles import scrape_doctor_profiles
from scrape_info import scrape_info
from scrape_details import scrape_details
from utils import save_to_json, read_from_json, is_today
from dotenv import load_dotenv
import os
import json
import requests
from datetime import datetime

load_dotenv()
today_str = datetime.now().strftime("%Y%m%d")
base_dir = "/Users/jangminsoo/Desktop/dev/pro/Medical-project/csv_folder/today_naver_QnA"

# all_doctor_profiles 추출
max_pages = 50
doctor_profiles = scrape_doctor_profiles(max_pages)  

# doctor_profiles 저장할 파일 이름에 오늘 날짜 포함하여 전체 경로 설정 
filename = os.path.join(base_dir, f"doctor_profiles_{today_str}.json")
save_to_json(doctor_profiles, filename)
doctor_profiles = read_from_json(filename)

start_index = 0
for profile in doctor_profiles[start_index:]:
    doctor_id = profile['doctor_id']
    total_answers = profile['total_answers']
    index = profile['index']
    # 수정된 scrape_info 함수를 호출하여 오늘 작성한 질문 ID만 필터링
    info = scrape_info(profile) 
    # 각 질문 ID에 대해 상세 정보 스크래핑
    for item in info:
        if is_today(item['date']):
            scrape_details(item['doc_id'])

print("모든 데이터 수집 완료.")

# 슬랙 알람 코드
webhook_url = os.getenv('SLACK_WEBHOOK_URL_MEDICAL')
if webhook_url:
    message = {"text": "네이버 데이터 저장 완료 !"}
    response = requests.post(webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})
    print(response.status_code, response.text)
else:
    print("SLACK_WEBHOOK_URL_MEDICAL 환경 변수가 설정되지 않았습니다.")
