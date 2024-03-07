from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from get_questionPid import fetch_questions
from scape_contents import scrape_and_save_questions
import os
from dotenv import load_dotenv
from pytz import timezone
import re
import pandas as pd
import requests
import json
import psycopg2
from sqlalchemy import create_engine

local_timezone = timezone(
    "Asia/Seoul"
) 

# 환경 변수 로드
load_dotenv()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": local_timezone.localize(datetime(2024, 3, 7, 23, 35)),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "doctornow_scraping_dag",
    default_args=default_args,
    description="A DAG for scraping doctornow questions",
    schedule_interval=timedelta(hours=8),
)

def clean_text(text):
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 이메일 주소 제거
    text = re.sub(r'\S+@\S+', '', text)
    # URL 제거
    text = re.sub(r'http\S+', '', text)
    # 공백 제거
    text = re.sub(r'\s+', ' ', text)
    # 특수 문자 제거
    text = re.sub(r'[^\w\s]', '', text)
    return text

# 문장 분리 및 정규화
def split_sentences(text):
    # 문장 분리
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    # 각 문장 정규화
    sentences = [clean_text(sentence) for sentence in sentences]
    return ' '.join(sentences)

def convert_date_format(date_str):
    return date_str.replace(".", "-")

def scrape_questions():
    url = "https://bff.doctornow.co.kr/graphql"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "Origin": "https://doctornow.co.kr",
        "Referer": "https://doctornow.co.kr/",
        "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
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
                "pivot": "a533d2707c70402f8bfe9d401cf5eb80",
            }
        },
    }
    try:
        question_pids = fetch_questions(url, headers, payload)
        scrape_and_save_questions(question_pids)
        folder_name="./csv_folder/doctornow_realtime"
        current_date = datetime.now().strftime("%Y-%m-%d")
        csv_file_path = os.path.join(folder_name, f'doctornow_realtime_{current_date}.csv')
        
        df = pd.read_csv(csv_file_path)
        df['title'] = df['title'].apply(clean_text)
        df['question'] = df['question'].apply(clean_text)
        df['answer'] = df['answer'].apply(split_sentences)
        df['date'] = df['date'].apply(convert_date_format)
        
        csv_out_path = os.path.join(folder_name, f'doctornow_realtime_{current_date}_pros.csv')
        df.to_csv(csv_out_path, index=False) 
        
        
        # PostgreSQL 연결 설정
        # 로컬에서 실행할 경우 아래 ip로 설정
        # engine = create_engine('postgresql+psycopg2://encore:hadoop@54.180.156.162:5432/qna')

        # ec2 인스턴스에서 실행할땐 아래 ip로 설정
        engine = create_engine("postgresql+psycopg2://encore:hadoop@172.31.13.180:5432/qna")



        # DataFrame을 PostgreSQL 테이블에 삽입
        df.to_sql("processed_data_doctornow", engine, if_exists="append", index=False)

        
        load_dotenv()
        webhook_url = os.getenv("SLACK_WEBHOOK_URL_MEDICAL")
        if webhook_url:
            message = {
                "text": "닥터나우 실시간 상담 contents 데이터 CSV 파일 저장 완료 ! \n file : doctornow_realtime.csv"
            }
            response = requests.post(
                webhook_url,
                data=json.dumps(message),
                headers={"Content-Type": "application/json"},
            )
            print(response.status_code, response.text)
        else:
            print("SLACK_WEBHOOK_URL_MEDICAL 환경 변수가 설정되지 않았습니다.")

    except Exception as e:
        print(f"An error occurred: {e}")



scrape_task = PythonOperator(
    task_id="scrape_questions",
    python_callable=scrape_questions,
    dag=dag,
)
