from dotenv import load_dotenv
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import csv
import json 
import os

# get_questionPid.py에서 가져온 question_pids 리스트를 활용해서 contents의 내용을 가져오는 함수

def scrape_and_save_questions(question_pids, folder_name="/Users/jangminsoo/Desktop/dev/pro/Medical-project/csv_folder/doctornow_realtime"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # 현재 날짜를 가져와서 파일 이름에 포함
    current_date = datetime.now().strftime("%Y-%m-%d")
    csv_file_path = os.path.join(folder_name, f'doctornow_realtime_{current_date}.csv')
    
    with open(csv_file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['제목', '내용', '작성시간', '카테고리', '답변'])

        for question_pid in question_pids:
            try:
                url = f"https://doctornow.co.kr/content/qna/{question_pid}"
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                
                # 각 요소를 찾을 때 예외 처리를 추가
                title = soup.find("h1", class_="sc-e3e1167b-4 iOOxvE")
                createtime = soup.find("div", class_="sc-e3e1167b-5 jPpKkT")
                content = soup.find("p", class_="sc-a7e6ffaf-2 bzrGUI")
                category = soup.find("span", class_="sc-e3e1167b-7 hpgLSb")
                answer = soup.find("p", class_="sc-a7e6ffaf-2 sc-1044f6b8-10 bzrGUI jvjLuq")

                # 찾은 요소의 텍스트를 추출, 요소가 None이면 기본값 할당
                title_text = title.text.strip() if title else "제목 없음"
                createtime_text = createtime.text.strip().split("•")[1].strip() if createtime else "시간 정보 없음"
                content_text = content.text.strip() if content else "내용 없음"
                category_text = category.text.strip() if category else "카테고리 정보 없음"
                answer_text = answer.text.strip() if answer else "답변 없음"
                
                writer.writerow([title_text, content_text, createtime_text, category_text, answer_text])
            except Exception as e:
                print(f"Error while scraping {question_pid}: {e}")
                continue

    print("CSV 파일이 생성되었습니다.")
    
# 슬랙 알람 코드 
load_dotenv()
webhook_url = os.getenv('SLACK_WEBHOOK_URL_MEDICAL')
if webhook_url:
    message = {"text": "닥터나우 실시간 상담 contents 스크랩핑 완료 !"}
    response = requests.post(webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})
    print(response.status_code, response.text)
else:
    print("SLACK_WEBHOOK_URL_MEDICAL 환경 변수가 설정되지 않았습니다.")


