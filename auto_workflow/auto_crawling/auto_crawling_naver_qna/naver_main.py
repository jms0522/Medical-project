from scrape_doctor_profiles import scrape_doctor_profiles
from scrape_info import scrape_info
from scrape_details import scrape_details
from utils import save_to_json, read_from_json, is_today
from dotenv import load_dotenv
import os
import json
import requests
from datetime import datetime


def main():
    load_dotenv()
    today_str = datetime.now().strftime("%Y%m%d")
    base_dir = "./csv_folder/today_naver_QnA"

    doctor_profiles = get_doctor_profiles()
    save_and_reload_profiles(doctor_profiles, base_dir, today_str)
    process_profiles(doctor_profiles)
    send_slack_notification()


def get_doctor_profiles(max_pages=50):
    return scrape_doctor_profiles(max_pages)


def save_and_reload_profiles(doctor_profiles, base_dir, today_str):
    filename = os.path.join(base_dir, f"doctor_profiles_{today_str}.json")
    save_to_json(doctor_profiles, filename)
    return read_from_json(filename)


def process_profiles(doctor_profiles, start_index=0):
    for profile in doctor_profiles[start_index:]:
        process_individual_profile(profile)


def process_individual_profile(profile):
    info = scrape_info(profile)
    for item in info:
        if is_today(item["date"]):
            scrape_details(item["doc_id"])


def send_slack_notification():
    webhook_url = os.getenv("SLACK_WEBHOOK_URL_MEDICAL")
    if webhook_url:
        message = {"text": "네이버 데이터 저장 완료 !"}
        response = requests.post(
            webhook_url,
            data=json.dumps(message),
            headers={"Content-Type": "application/json"},
        )
        print(response.status_code, response.text)
    else:
        print("SLACK_WEBHOOK_URL_MEDICAL 환경 변수가 설정되지 않았습니다.")


if __name__ == "__main__":
    main()
