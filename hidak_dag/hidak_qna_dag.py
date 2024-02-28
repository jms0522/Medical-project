import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id = 'test2',
    schedule_interval="0 18 * * *",
    start_date=datetime(year=2024, month=2, day=28),
    catchup=True
)

def process_all_qna():
    today = datetime.today().strftime('%Y-%m-%d')
    for json_file in os.listdir("/opt/airflow/dags/hidak_link_"):
        if json_file.endswith(".json") and today in json_file:
            with open(os.path.join("/opt/airflow/dags/hidak_link_", json_file), 'r') as f:
                links_list = json.load(f)
            department = json_file.split("_")[1].split(".")[0]  # 파일명에서 부서명 추출, 확장자 제거
            list1 = links_list

            head = { 'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
            data = []
            for link in list1:
                url = f"https://mobile.hidoc.co.kr/healthqna/part/{link}"
                r = requests.get(url, headers=head)
                bs = BeautifulSoup(r.text, 'html.parser')
                date_data = bs.find("span", class_='date')
                date = date_data.text
                title_data = bs.select('.tit_qna')
                pattern = r'<strong class="tit_qna">\s*(.*?)\s*<div class="qna_info">'
                title_data_ = str(title_data[0])
                title = re.search(pattern, title_data_)
                if title:
                    title_ = title.group(1)
                else:
                    title_ = "매칭되는 부분이 없습니다."
                question_data = bs.find('div', class_='desc')   
                question = question_data.text.strip() 
                doctor_info = bs.find_all("strong", class_='link_doctor')
                doctor_list = []
                for x in range(len(doctor_info)):
                    doctor_list.append(doctor_info[0].text)
                doc_hospital = bs.find_all("span", class_ ='txt_clinic')
                hospital_list = []
                for x in range(len(doc_hospital)):
                    hospital_list.append(doc_hospital[0].text)
                a = bs.findAll("div", class_ = 'desc')
                answer = []
                for x in range(1,len(a)):
                    answer.append(a[x].text.strip())
                data.append({
                    'Date': date,
                    'Title': title_,
                    'Question': question,
                    'Doctors': doctor_list,
                    'Hospitals': hospital_list,
                    'Answers': answer
                })
            output_directory = "/opt/airflow/dags/hidak_qna_"
            output_file = os.path.join(output_directory, f"{department}_{today}_QNA.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"{department}의 새로운 데이터가 저장되었습니다:")

today_qna1 = PythonOperator(
    task_id = "today_qna1",
    python_callable = process_all_qna,
    dag=dag,
)

