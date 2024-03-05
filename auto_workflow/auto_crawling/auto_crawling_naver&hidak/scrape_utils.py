import json
import os
from datetime import datetime
import pandas as pd


def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def read_from_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def append_to_csv(data, file_path):
    df = pd.DataFrame([data])
    if not os.path.isfile(file_path):
        df.to_csv(file_path, mode="w", index=False, encoding="utf-8-sig")
    else:
        df.to_csv(file_path, mode="a", index=False, encoding="utf-8-sig", header=False)


def is_today(date_str):
    date_format = "%Y.%m.%d."
    today = datetime.now().strftime(date_format)
    return date_str == today


def save_all_data_to_one_json(data):
    # 저장 경로 설정
    folder_path = "./csv_folder/today_naver_QnA"
    os.makedirs(folder_path, exist_ok=True)

    # 파일 이름 설정: id_날짜.json
    today_date = datetime.now().strftime("%Y%m%d")
    filename = f"{folder_path}/id_{today_date}.json"

    # 이전 데이터 로드
    old_data = read_from_json(filename) if os.path.exists(filename) else []

    # 새로운 데이터 추가
    old_data.extend(data)

    # 데이터 저장
    save_to_json(old_data, filename)
