from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import json
import pymysql

def preprocess_and_store_data():
    try:
        con = pymysql.connect(host='3.36.39.116', user='encore', password='dpszhdk!@#',  db='encore', charset='utf8')
        cur = con.cursor()
    except Exception as e:
        print("DB 연결 오류:", e)
        return

    yesterday = datetime.today() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    json_directory = "/opt/airflow/dags/hidak_processing_/"

    for json_file in os.listdir(json_directory):
        if json_file.endswith(".json") and yesterday_str in json_file:
            json_path = os.path.join(json_directory, json_file)
            with open(json_path, "r", encoding="utf-8") as json_file:
                data_list = json.load(json_file)

            for data in data_list:
                if "Date" not in data or "Title" not in data or "Question" not in data or "Doctors" not in data or "Hospitals" not in data or "Answers" not in data:
                    print(f"JSON 파일 {json_file}의 형식이 잘못되었습니다. 필수 필드가 누락되었습니다.")
                    continue

                q_date = datetime.strptime(data["Date"], "%Y-%m-%d").date()
                title = data["Title"]
                question = data["Question"]
                doctors = ', '.join(data["Doctors"])  # eval() 함수 사용하지 않음
                hospitals = ', '.join(data["Hospitals"])  # eval() 함수 사용하지 않음
                answers = data["Answers"]

                # 데이터 삽입 SQL 실행
                sql = "INSERT INTO hidak_sseungpp0227 (q_date, title, question, doctors, hospitals, answers) VALUES(%s, %s, %s, %s, %s, %s)"
                try:
                    cur.execute(sql, (q_date, title, question, doctors, hospitals, answers))
                except Exception as e:
                    print("데이터 삽입 오류:", e)

    # 변경사항을 DB에 반영
    con.commit()

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
    dag_id = 'test4',
    default_args=default_args,
    description='A DAG to preprocess JSON files and store data in the database',
    schedule_interval=timedelta(days=1),
)

db_store_task = PythonOperator(
    task_id='preprocess_and_store_data',
    python_callable=preprocess_and_store_data,
    dag=dag,
)

db_store_task