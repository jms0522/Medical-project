import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.python import PythonOperator

# from pykospacing import Spacing
import psycopg2
from sqlalchemy import create_engine
import pandas as pd

from pytz import timezone

local_timezone = timezone("Asia/Seoul")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": local_timezone.localize(datetime(2024, 3, 7, 23, 45)),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "hidak_scraping_dag",
    default_args=default_args,
    description="A simple DAG to scrape naver data",
    schedule_interval=timedelta(days=1),
)


def process_all_departments():

    folder_path = "./hidak/hidak_link_"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"폴더 '{folder_path}'가 생성되었습니다.")
    else:
        print(f"폴더 '{folder_path}'가 이미 존재합니다.")
    folder_path = "./hidak/hidak_qna_"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"폴더 '{folder_path}'가 생성되었습니다.")
    else:
        print(f"폴더 '{folder_path}'가 이미 존재합니다.")
    folder_path = "./hidak/hidak_processing_"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"폴더 '{folder_path}'가 생성되었습니다.")
    else:
        print(f"폴더 '{folder_path}'가 이미 존재합니다.")

    # 과 이름에 대한 코드 매핑

    head = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    # 어제 날짜 구하기
    yesterday = datetime.today() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    link_list = []

    for page in range(1, 60):
        # url = f"https://mobile.hidoc.co.kr/healthqna/part/list?code={department_code}&page={page}"
        url = f"https://mobile.hidoc.co.kr/healthqna/list?page={page}"
        r = requests.get(url, headers=head)
        bs = BeautifulSoup(r.text, "html.parser")

        data = bs.find("section", class_="contents").find_all("a")

        pattern = r'href="(view[^"]+)"'
        for tag in data:
            tag_str = str(tag)
            match = re.search(pattern, tag_str)
            if match:
                link = match.group(1)
                link_list.append(link)

    link_list = list(set(link_list))
    if link_list:
        # 새로운 파일명 생성 (오늘 날짜)
        new_file_path = f"./hidak/hidak_link_/{yesterday_str}_link.json"

        with open(new_file_path, "w", encoding="utf-8") as f:
            json.dump(link_list, f, ensure_ascii=False, indent=4)


def process_all_qna():
    yesterday = datetime.today() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    for json_file in os.listdir("./hidak/hidak_link_"):
        if json_file.endswith(".json") and yesterday_str in json_file:
            with open(os.path.join("./hidak/hidak_link_", json_file), "r") as f:
                links_list = json.load(f)

            list1 = links_list

            head = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            }
            data = []
            for link in list1:
                url = f"https://mobile.hidoc.co.kr/healthqna/part/{link}"
                r = requests.get(url, headers=head)
                bs = BeautifulSoup(r.text, "html.parser")
                date_data = bs.find("span", class_="date")
                date = date_data.text
                date = date.replace(".", "-")
                title_data = bs.select(".tit_qna")
                pattern = r'<strong class="tit_qna">\s*(.*?)\s*<div class="qna_info">'
                title_data_ = str(title_data[0])
                title = re.search(pattern, title_data_)
                if title:
                    title_ = title.group(1)
                else:
                    title_ = "매칭되는 부분이 없습니다."
                question_data = bs.find("div", class_="desc")
                question = question_data.text.strip()
                doctor_info = bs.find_all("strong", class_="link_doctor")
                doctor_list = []
                for x in range(len(doctor_info)):
                    doctor_list.append(doctor_info[x].text)
                doc_hospital = bs.find_all("span", class_="txt_clinic")
                hospital_list = []
                for x in range(len(doc_hospital)):
                    hospital_list.append(doc_hospital[x].text)
                a = bs.findAll("div", class_="desc")
                answer = []
                for x in range(1, len(a)):
                    answer.append(a[x].text.strip())
                if date == yesterday_str:
                    data.append(
                        {
                            "date": date,
                            "title": title_,
                            "question": question,
                            "answer": answer,
                            "doctors": doctor_list,
                            "hospitals": hospital_list,
                        }
                    )
            if len(data) == 0:
                data = [
                    (
                        {
                            "date": "",
                            "title": "",
                            "question": "",
                            "answer": [],
                            "doctors": [],
                            "hospitals": [],
                        }
                    )
                ]
            output_directory = "./hidak/hidak_qna_"
            output_file = os.path.join(output_directory, f"{yesterday_str}_qna.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)


# json_directory = "/Users/sseungpp/dev/hidak_dag/qnatest"
# output_directory = "/Users/sseungpp/dev/hidak_dag/qna_protest"


def remove_greeting2(text):
    return re.sub(r"하이닥.*?입니다\.", "", text)


def remove_greeting1(text):
    return re.sub(r"안녕하세요\.", "", text)


def remove_special_chars(text):
    return text.replace("\\xa0", "")


# spacing = Spacing()
def preprocess_json(data_list):
    preprocessed_data = []
    for data in data_list:
        if not data["date"]:  # Date가 비어있는 경우
            preprocessed_data = data
            return preprocessed_data
        else:
            # 전처리 적용
            # data['Title'] = spacing(data['Title'])
            # data['Question'] = spacing(data['Question'])
            data["answer"] = "".join(data["answer"])  # 리스트를 문자열로 변환
            data["question"] = remove_greeting1(data["question"])  # 인사말 제거
            data["doctors"] = data["doctors"][0]
            data["hospitals"] = data["hospitals"][0]
            data["answer"] = remove_greeting1(data["answer"])  # 인사말 제거
            data["answer"] = remove_greeting2(data["answer"])  # 인사말 제거
            data["answer"] = remove_special_chars(data["answer"])  # 특수 문자 제거
            # data['answers'] = spacing(data['Answers'])text = re.sub(r'\p{Hangul}+과전문의.*?입니다\.', '', text)
            data["question"] = remove_special_chars(data["question"])  # 특수 문자 제거
            if "삭제" not in data["question"]:  # '삭제' 키워드가 없는 경우만 추가
                preprocessed_data.append(data)
    return preprocessed_data


def preprocess_json_files():
    json_dir = "/opt/airflow/hidak/hidak_qna_"
    output_dir = "/opt/airflow/hidak/hidak_processing_"
    yesterday = datetime.today() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    print(yesterday_str)
    for json_file in os.listdir(json_dir):
        print(json_file)
        if json_file.endswith(".json") and yesterday_str in json_file:
            json_path = os.path.join(json_dir, json_file)
            with open(json_path, "r", encoding="utf-8") as f:
                data_list = json.load(f)
            preprocessed_data = preprocess_json(data_list)

            output_filename = os.path.splitext(json_file)[0] + "_pros.json"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, "w", encoding="utf-8") as outfile:
                json.dump(
                    preprocessed_data,
                    outfile,
                    default=str,
                    ensure_ascii=False,
                    indent=4,
                )
            print(f"전처리된 데이터가 {output_path}에 저장되었습니다.")


def insert_data_to_postgres(**kwargs):
    json_file_path = "/opt/airflow/hidak/hidak_processing_/"

    # # PostgreSQL 연결 설정
    # user = 'your_username'
    # password = 'your_password'
    # host = 'localhost'  # 또는 데이터베이스 호스트 주소
    # port = '5432'  # 또는 데이터베이스 포트 번호
    # dbname = 'your_database_name'

    # engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}')

    # PostgreSQL 연결 설정
    # 로컬에서 실행할 경우 아래 ip로 설정
    # engine = create_engine('postgresql+psycopg2://encore:hadoop@54.180.156.162:5432/qna')

    # ec2 인스턴스에서 실행할땐 아래 ip로 설정
    engine = create_engine("postgresql+psycopg2://encore:hadoop@172.31.13.180:5432/qna")

    for file in os.listdir(json_file_path):
        if file.endswith(".json"):
            # json 파일의 전체 경로
            file_path = os.path.join(json_file_path, file)

            # json 파일을 DataFrame으로 읽기
            df = pd.read_json(file_path)
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["title"] = df["title"].astype("str")
            df["question"] = df["question"].astype("str")
            df["doctors"] = df["doctors"].astype("str")
            df["hospitals"] = df["hospitals"].astype("str")
            df["answer"] = df["answer"].astype("str")
            # DataFrame을 PostgreSQL 테이블에 삽입
            df.to_sql("processed_data_hidak", engine, if_exists="append", index=False)
    webhook_url = os.getenv("SLACK_WEBHOOK_URL_MEDICAL")
    if webhook_url:
        message = {"text": "전처리된 QnA데이터 DB에 저장 완료!"}
        response = requests.post(
            webhook_url,
            data=json.dumps(message),
            headers={"Content-Type": "application/json"},
        )
        print(response.status_code, response.text)
    else:
        print("SLACK_WEBHOOK_URL_MEDICAL 환경 변수가 설정되지 않았습니다.")


today_link1 = PythonOperator(
    task_id="today_link1",
    python_callable=process_all_departments,
    dag=dag,
)


today_qna1 = PythonOperator(
    task_id="today_qna1",
    python_callable=process_all_qna,
    dag=dag,
)


preprocess_task = PythonOperator(
    task_id="preprocess_json_files",
    python_callable=preprocess_json_files,
    dag=dag,
)

insert_to_DB = PythonOperator(
    task_id="insert_to_DB",
    python_callable=insert_data_to_postgres,
    dag=dag,
)

today_link1 >> today_qna1 >> preprocess_task >> insert_to_DB
