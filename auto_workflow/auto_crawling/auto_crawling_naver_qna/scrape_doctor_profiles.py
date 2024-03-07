import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from dotenv import load_dotenv
import json
import os


def scrape_doctor_profiles(max_pages, start_page=1):

    folder_path = "./csv_folder/today_naver_QnA"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"폴더 '{folder_path}'가 생성되었습니다.")
    else:
        print(f"폴더 '{folder_path}'가 이미 존재합니다.")
    base_url = "https://kin.naver.com/people/expert/index.naver?type=DOCTOR&page={}"
    doctor_info = []

    for page in tqdm(range(start_page, max_pages + 1)):
        url = base_url.format(page)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        for index, item in enumerate(soup.select(".pro_list li"), start=1):
            doctor_link_tag = item.find("h5").find("a")
            if doctor_link_tag:
                doctor_name = doctor_link_tag.text.strip()
                doctor_id = doctor_link_tag["href"].split("u=")[1]
                specialty_tag = item.find("h6")
                hospitals = (
                    specialty_tag.text.split(" ")[0].strip()
                    if specialty_tag
                    else "정보 없음"
                )
                affiliation_tag = item.find("th", string="소속기관")
                affiliation = (
                    affiliation_tag.find_next("td").text.strip()
                    if affiliation_tag
                    else "정보 없음"
                )
                answer_count_tag = item.find("th", string="총 답변")
                answer_count = (
                    int(answer_count_tag.find_next("td").text.strip().replace(",", ""))
                    if answer_count_tag
                    else 0
                )

                doctor_info.append(
                    {
                        "index": index,
                        "doctor_id": doctor_id,
                        "doctor_name": doctor_name,
                        "hospitals": hospitals,
                        "total_answers": answer_count,
                        "affiliation": affiliation,
                    }
                )

    print(type(doctor_info))
    return doctor_info


if __name__ == "__main__":
    load_dotenv()
    max_pages = 50
    doctor_profiles = scrape_doctor_profiles(max_pages)

    # 스크랩핑 완료 후 슬랙 알람 전송
webhook_url = os.getenv("SLACK_WEBHOOK_URL_MEDICAL")
if webhook_url:
    message = {"text": "네이버 의사 id 수집 완료 (현재 max_page : 50 설정)!"}
    response = requests.post(
        webhook_url,
        data=json.dumps(message),
        headers={"Content-Type": "application/json"},
    )
    print(response.status_code, response.text)
else:
    print("SLACK_WEBHOOK_URL_MEDICAL 환경 변수가 설정되지 않았습니다.")
