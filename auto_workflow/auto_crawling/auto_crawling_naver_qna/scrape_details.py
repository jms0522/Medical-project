import requests
from bs4 import BeautifulSoup
from scrape_utils import append_to_csv
import json
from dotenv import load_dotenv
import os
from datetime import datetime


def scrape_details(doc_id, doctors, hospitals):
    base_url = "https://kin.naver.com/qna/detail.naver?d1id=7&dirId=70201&docId={}"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "Cache-Control": "max-age=0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Upgrade-Insecure-Requests": "1",
    }
    today = datetime.today()
    today_str = today.strftime("%Y-%m-%d")
    try:
        url = base_url.format(doc_id)
        response = requests.get(url, headers=headers)
        # print(response.text) 디버깅 용
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        data = {
            "date": today_str,
            "title": (
                soup.select_one(".title").text.strip()
                if soup.select_one(".title")
                else "N/A"
            ),
            "question": (
                soup.select_one(".c-heading__content").text.strip()
                if soup.select_one(".c-heading__content")
                else "N/A"
            ),
            "answer": (
                soup.select_one(".se-main-container").text.strip()
                if soup.select_one(".se-main-container")
                else "N/A"
            ),
            "doctors": doctors,
            "hospitals": hospitals,
            "doc_id": doc_id,
        }

        # print("Extracted Data:", data) 디버깅 용

        csv_file_name = f"details_{today_str}_QNA.csv"  # 예시 파일 이름
        csv_file_path = os.path.join("./csv_folder/today_naver_QnA", csv_file_name)

        append_to_csv(data, csv_file_path)

    except Exception as e:
        print(f"Error scraping doc_id {doc_id}: {e}")


# test_doc_id = '465191789'  # 실제 존재하는 doc_id로 교체해야 합니다.
# scrape_details(test_doc_id)
