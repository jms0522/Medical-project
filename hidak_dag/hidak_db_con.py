import json
from datetime import datetime
import pymysql

try:
    con = pymysql.connect(host='3.36.39.116', user='encore', password='dpszhdk!@#',  db='encore', charset='utf8')
    cur = con.cursor()
except Exception as e:
    print(e)

json_file_path = "/Users/sseungpp/dev/hidak_dag/qna_protest/순환기내과_2024-02-28_QNA_pros.json"

with open(json_file_path, "r", encoding="utf-8") as json_file:
    data_list = json.load(json_file)

for data in data_list:
    q_date = datetime.strptime(data["Date"], "%Y-%m-%d").date()
    title = data["Title"]
    question = data["Question"]
    doctors = ', '.join(eval(data["Doctors"]))
    hospitals = ', '.join(eval(data["Hospitals"]))
    answers = data["Answers"]
    
    sql = "INSERT INTO hidak_sseungpp0227 (q_date, title, question, doctors, hospitals, answers) VALUES(%s, %s, %s, %s, %s, %s)"
    try:
        cur.execute(sql, (q_date, title, question, doctors, hospitals, answers))
    except Exception as e:
        print(e)

con.commit()
