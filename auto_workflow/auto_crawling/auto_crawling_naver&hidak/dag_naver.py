<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
=======

>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import sys
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv
import re
import json
import requests
import os


<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
sys.path.append(
    "/home/ubuntu/airflow_work/dags/script"
)  # Add the path to your scripts here

# Importing utility functions from scrape_utils.py
from scrape_utils import *
=======

sys.path.append('/home/ubuntu/airflow_work/dags/script') # Add the path to your scripts here

# Importing utility functions from scrape_utils.py
from scrape_utils import save_to_json, read_from_json, append_to_csv, is_today, save_all_data_to_one_json
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py

# Importing main functions from other scripts
from scrape_doctor_profiles import scrape_doctor_profiles
from scrape_info import scrape_info
from scrape_details import scrape_details
from processing import *
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
from pytz import timezone

local_timezone = timezone(
    "Asia/Seoul"
) 

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": local_timezone.localize(datetime(2024, 3, 5, 23, 45)),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "naver_scraping_dag",
    default_args=default_args,
    description="A simple DAG to scrape naver data",
    schedule_interval=timedelta(days=1),
)


def scrape_info_with_xcom(**kwargs):
    ti = kwargs["ti"]
    doctor_profiles = ti.xcom_pull(task_ids="scrape_doctor_profiles")
=======

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 4),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'naver_scraping_dag',
    default_args=default_args,
    description='A simple DAG to scrape naver data',
    schedule_interval=timedelta(days=1),
)

def scrape_info_with_xcom(**kwargs):
    ti = kwargs['ti']
    doctor_profiles = ti.xcom_pull(task_ids='scrape_doctor_profiles')
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py

    all_info = []
    for profile in doctor_profiles:
        info = scrape_info(profile)
        all_info.extend(info)  # 리스트 확장을 사용하여 단일 리스트로 병합
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py

    return all_info


def scrape_details_for_all_docs(**kwargs):
    ti = kwargs["ti"]
    info_list = (
        ti.xcom_pull(task_ids="scrape_info") or []
    )  # XCom에서 값을 가져오고, None이면 빈 리스트를 사용
=======
    
    return all_info

def scrape_details_for_all_docs(**kwargs):
    ti = kwargs['ti']
    info_list = ti.xcom_pull(task_ids='scrape_info') or []  # XCom에서 값을 가져오고, None이면 빈 리스트를 사용
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py

    all_details = []
    for info in info_list:
        if info is None:
            # None 값을 DB에 삽입하려면 여기서 적절한 처리를 해야 함
            continue
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
        doc_details = scrape_details(
            info.get("doc_id"), info.get("doctors"), info.get("hospitals")
        )  # info가 None이 아니면 'doc_id' 사용
        all_details.append(doc_details)

    return all_details


# spacing = Spacing()
def preprocess_csv_file(**kwargs):
    today = datetime.today()
    today_str = today.strftime("%Y-%m-%d")
    csv_file_path = (
        f"./csv_folder/today_naver_QnA/details_{today_str}_QNA.csv"  # CSV 파일의 경로
    )

    # CSV 파일 읽기
    df = pd.read_csv(csv_file_path)

    df_cleaned = df.dropna()

    processed_data = [preprocess_data(row) for index, row in df_cleaned.iterrows()]

=======
        doc_details = scrape_details(info.get('doc_id'))  # info가 None이 아니면 'doc_id' 사용
        all_details.append(doc_details)
    
    return all_details






spacing = Spacing()
def preprocess_csv_file(**kwargs):
    today = datetime.today()
    today_str = today.strftime('%Y-%m-%d')
    csv_file_path = f'./csv_folder/today_naver_QnA/details_{today_str}_QNA.csv'  # CSV 파일의 경로

    # CSV 파일 읽기
    df = pd.read_csv(csv_file_path)
    
    df_cleaned = df.dropna()

    processed_data = [preprocess_data(row) for index, row in df_cleaned.iterrows()]
    
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
    # 결과를 DataFrame으로 변환
    preprocessed_df = pd.DataFrame(processed_data)

    # 전처리된 데이터를 새로운 CSV 파일로 저장
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
    preprocessed_csv_file_path = (
        f"./csv_folder/today_naver_QnA/details_{today_str}_QNA_pros.csv"
    )
=======
    preprocessed_csv_file_path = f'./csv_folder/today_naver_QnA/details_{today_str}_QNA_pros.csv'
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
    preprocessed_df.to_csv(preprocessed_csv_file_path, index=False)

    return preprocessed_csv_file_path


<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
def insert_data_to_postgres(**kwargs):
    ti = kwargs["ti"]
    preprocessed_csv_file_path = ti.xcom_pull(task_ids="preprocess_csv")
    today = datetime.today()
    today_str = today.strftime("%Y-%m-%d")

=======


def insert_data_to_postgres(**kwargs):
    ti = kwargs['ti']
    preprocessed_csv_file_path = ti.xcom_pull(task_ids='preprocess_csv')
    
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
    # # PostgreSQL 연결 설정
    # user = 'your_username'
    # password = 'your_password'
    # host = 'localhost'  # 또는 데이터베이스 호스트 주소
    # port = '5432'  # 또는 데이터베이스 포트 번호
    # dbname = 'your_database_name'
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py

    # engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}')

    # PostgreSQL 연결 설정
    # 로컬에서 실행할 경우 아래 ip로 설정
    # engine = create_engine('postgresql+psycopg2://encore:hadoop@54.180.156.162:5432/qna')

    # ec2 인스턴스에서 실행할땐 아래 ip로 설정
    engine = create_engine("postgresql+psycopg2://encore:hadoop@172.31.13.180:5432/qna")

=======
    
    # engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}')


    # PostgreSQL 연결 설정
    # 로컬에서 실행할 경우 아래 ip로 설정
    # engine = create_engine('postgresql+psycopg2://encore:hadoop@54.180.156.162:5432/qna')
    
    # ec2 인스턴스에서 실행할땐 아래 ip로 설정
    engine = create_engine('postgresql+psycopg2://encore:hadoop@172.31.13.180:5432/qna')
    
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
    # 전처리된 데이터를 DataFrame으로 읽기
    df = pd.read_csv(preprocessed_csv_file_path)

    # DataFrame을 PostgreSQL 테이블에 삽입
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
    df.to_sql("processed_data_naver", engine, if_exists="append", index=False)
=======
    df.to_sql('processed_data_naver', engine, if_exists='append', index=False)
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
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


# Defining tasks
scrape_doctor_profiles_task = PythonOperator(
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
    task_id="scrape_doctor_profiles",
    python_callable=scrape_doctor_profiles,
    op_kwargs={"max_pages": 50, "start_page": 1},
=======
    task_id='scrape_doctor_profiles',
    python_callable=scrape_doctor_profiles,
    op_kwargs={'max_pages': 50, 'start_page': 1},
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
    do_xcom_push=True,  # 결과를 XCom에 저장
    dag=dag,
)

scrape_info_task = PythonOperator(
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
    task_id="scrape_info",
=======
    task_id='scrape_info',
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
    python_callable=scrape_info_with_xcom,  # XCom을 사용하는 새로운 함수
    dag=dag,
)

scrape_details_task = PythonOperator(
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
    task_id="scrape_details",
=======
    task_id='scrape_details',
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
    python_callable=scrape_details_for_all_docs,  # 새로운 반복 실행 함수
    dag=dag,
)

preprocess_csv_task = PythonOperator(
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
    task_id="preprocess_csv",
=======
    task_id='preprocess_csv',
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
    python_callable=preprocess_csv_file,
    dag=dag,
)

insert_to_postgres_task = PythonOperator(
<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
    task_id="insert_to_postgres",
=======
    task_id='insert_to_postgres',
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
    python_callable=insert_data_to_postgres,
    dag=dag,
)


<<<<<<< HEAD:auto_workflow/auto_crawling/auto_crawling_naver_qna/dag_naver.py
# Setting up dependencies
(
    scrape_doctor_profiles_task
    >> scrape_info_task
    >> scrape_details_task
    >> preprocess_csv_task
    >> insert_to_postgres_task
)
=======

# Setting up dependencies
scrape_doctor_profiles_task >> scrape_info_task >> scrape_details_task >> preprocess_csv_task >> insert_to_postgres_task
>>>>>>> 565910d98a006dd76968ceaf443d0c117f4e4650:auto_workflow/auto_crawling/auto_crawling_naver&hidak/dag_naver.py
