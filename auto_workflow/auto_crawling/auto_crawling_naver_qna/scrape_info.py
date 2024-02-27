import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils import is_today, save_all_data_to_one_json
import re
import os
from datetime import datetime

def scrape_info(profile):
    doctor_id = profile['doctor_id']
    base_url = 'https://kin.naver.com/userinfo/expert/answerList.naver?u={user_id}&page={page}'
    all_info = []

    page = 1
    found_today = False

    while True:
        url = base_url.format(user_id=doctor_id, page=page)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        tr_tags = soup.select('tbody#au_board_list tr')
        if not tr_tags:
            break  # 게시물이 없으면 종료
        
        for tr in tr_tags:
            a_tag = tr.find('a', href=True)
            href = a_tag['href'] if a_tag else ''
            doc_id_match = re.search(r'docId=(\d+)', href)
            if doc_id_match:
                doc_id = doc_id_match.group(1)
                date_td = tr.find('td', class_='t_num tc')
                if date_td:
                    date_text = date_td.text.strip()
                    if is_today(date_text):
                        found_today = True
                        all_info.append({'doctor_id': doctor_id, 'doc_id': doc_id, 'date': date_text})
                    else:
                        if found_today:
                            # 오늘 날짜의 게시물을 이미 찾았고, 이제는 오늘 날짜가 아닌 게시물을 찾았으므로 종료합니다.
                            break

        if not found_today or found_today:
            # 이 페이지에서 오늘 날짜의 게시물을 찾지 못했거나 이미 찾은 경우
            break

        page += 1

    # 저장 로직
    folder_path = '/Users/jangminsoo/Desktop/dev/pro/Medical-project/csv_folder/today_naver_QnA'
    os.makedirs(folder_path, exist_ok=True) 
    filename = os.path.join(folder_path, f'today_naver_QnA_{profile["doctor_id"]}_{datetime.now().strftime("%Y%m%d")}.json')
    save_all_data_to_one_json(all_info)

    return all_info
