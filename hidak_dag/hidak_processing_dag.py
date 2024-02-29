from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import json
import re

def remove_greeting(text):
    return re.sub(r'하이닥.*?입니다\.', '', text)

def remove_special_chars(text):
    return text.replace('\\xa0', '')

def preprocess_json(data_list):
    preprocessed_data = []
    for data in data_list:
        if not data['Date']:  # Date가 비어있는 경우
            preprocessed_data = data
            return preprocessed_data
        else:
            # 전처리 적용
            data['Answers'] = ''.join(data['Answers'])  # 리스트를 문자열로 변환
            data['Answers'] = remove_greeting(data['Answers'])  # 인사말 제거
            data['Answers'] = remove_special_chars(data['Answers'])  # 특수 문자 제거
            data['Question'] = remove_special_chars(data['Question'])  # 특수 문자 제거
            
            if '삭제' not in data['Question']:  # '삭제' 키워드가 없는 경우만 추가
                preprocessed_data.append(data)

    return preprocessed_data

def preprocess_json_files(json_dir, output_dir):
    for json_file in os.listdir(json_dir):
        if json_file.endswith(".json") and yesterday_str in json_file:
            json_path = os.path.join(json_dir, json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
            preprocessed_data = preprocess_json(data_list)
        
            output_filename = os.path.splitext(json_file)[0] + "_pros.json"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as outfile:
                json.dump(preprocessed_data, outfile, default=str, ensure_ascii=False, indent=4)
            print(f"전처리된 데이터가 {output_path}에 저장되었습니다.")

yesterday = datetime.today() - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 29),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'preprocess_json_files',
    default_args=default_args,
    description='A DAG to preprocess JSON files',
    schedule_interval=timedelta(days=1),
)

json_directory = "/opt/airflow/dags/hidak_qna_"
output_directory = "/opt/airflow/dags/hidak_processing_"

preprocess_task = PythonOperator(
    task_id='preprocess_json_files',
    python_callable=preprocess_json_files,
    op_args=[json_directory, output_directory],
    dag=dag,
)

preprocess_task
