
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import sys
import pandas as pd
import psycopg2
from sqlalchemy import create_engine


sys.path.append('/home/ubuntu/airflow_work/dags/script') # Add the path to your scripts here

# Importing utility functions from scrape_utils.py
from scrape_utils import save_to_json, read_from_json, append_to_csv, is_today, save_all_data_to_one_json

# Importing main functions from other scripts
from scrape_doctor_profiles import scrape_doctor_profiles
from scrape_info import scrape_info
from scrape_details import scrape_details
from processing import preprocess_dataframe

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 28),
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

    all_info = []
    for profile in doctor_profiles:
        info = scrape_info(profile)
        all_info.extend(info)  # 리스트 확장을 사용하여 단일 리스트로 병합
    
    return all_info

def scrape_details_for_all_docs(**kwargs):
    ti = kwargs['ti']
    info_list = ti.xcom_pull(task_ids='scrape_info') or []  # XCom에서 값을 가져오고, None이면 빈 리스트를 사용

    all_details = []
    for info in info_list:
        if info is None:
            # None 값을 DB에 삽입하려면 여기서 적절한 처리를 해야 함
            continue
        doc_details = scrape_details(info.get('doc_id'))  # info가 None이 아니면 'doc_id' 사용
        all_details.append(doc_details)
    
    return all_details

def preprocess_csv_file(**kwargs):
    csv_file_path = './csv_folder/today_naver_QnA/details.csv'  # CSV 파일의 경로

    # CSV 파일 읽기
    df = pd.read_csv(csv_file_path)

    # 전처리 함수 적용
    preprocessed_df = preprocess_dataframe(df)

    # 전처리된 데이터를 새로운 CSV 파일로 저장
    preprocessed_csv_file_path = './csv_folder/today_naver_QnA/preprocessed_details.csv'
    preprocessed_df.to_csv(preprocessed_csv_file_path, index=False)

    return preprocessed_csv_file_path

def insert_data_to_postgres(**kwargs):
    ti = kwargs['ti']
    preprocessed_csv_file_path = ti.xcom_pull(task_ids='preprocess_csv')
    
    # # PostgreSQL 연결 설정
    # user = 'your_username'
    # password = 'your_password'
    # host = 'localhost'  # 또는 데이터베이스 호스트 주소
    # port = '5432'  # 또는 데이터베이스 포트 번호
    # dbname = 'your_database_name'
    
    # engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}')


    # PostgreSQL 연결 설정
    engine = create_engine('postgresql+psycopg2://postgres:hadoop@172.23.189.177:5433/test')

    # 전처리된 데이터를 DataFrame으로 읽기
    df = pd.read_csv(preprocessed_csv_file_path)

    # DataFrame을 PostgreSQL 테이블에 삽입
    df.to_sql('processed_data', engine, if_exists='append', index=False)


# Defining tasks
scrape_doctor_profiles_task = PythonOperator(
    task_id='scrape_doctor_profiles',
    python_callable=scrape_doctor_profiles,
    op_kwargs={'max_pages': 10, 'start_page': 1},
    do_xcom_push=True,  # 결과를 XCom에 저장
    dag=dag,
)

scrape_info_task = PythonOperator(
    task_id='scrape_info',
    python_callable=scrape_info_with_xcom,  # XCom을 사용하는 새로운 함수
    dag=dag,
)

scrape_details_task = PythonOperator(
    task_id='scrape_details',
    python_callable=scrape_details_for_all_docs,  # 새로운 반복 실행 함수
    dag=dag,
)

preprocess_csv_task = PythonOperator(
    task_id='preprocess_csv',
    python_callable=preprocess_csv_file,
    dag=dag,
)

insert_to_postgres_task = PythonOperator(
    task_id='insert_to_postgres',
    python_callable=insert_data_to_postgres,
    dag=dag,
)



# Setting up dependencies
scrape_doctor_profiles_task >> scrape_info_task >> scrape_details_task >> preprocess_csv_task >> insert_to_postgres_task
