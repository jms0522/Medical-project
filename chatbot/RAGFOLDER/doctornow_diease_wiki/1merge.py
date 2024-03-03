import os
import pandas as pd

# CSV 파일을 불러와서 DataFrame으로 변환하는 함수
def load_csv_to_dataframe(file_path):
    return pd.read_csv(file_path)

# 현재 스크립트가 위치한 폴더 경로
script_directory = os.path.dirname(os.path.realpath(__file__))

# 폴더 내의 모든 CSV 파일을 불러와서 하나의 DataFrame으로 병합하는 함수
def merge_csv_files(folder_path):
    # 폴더 내의 모든 파일 목록을 가져옴
    file_names = os.listdir(folder_path)
    csv_files = [f for f in file_names if f.endswith('.csv')]

    # CSV 파일이 없는 경우 예외 처리
    if not csv_files:
        raise FileNotFoundError("폴더 내에 CSV 파일이 없습니다.")

    # 첫 번째 CSV 파일을 기준으로 DataFrame 생성
    merged_df = load_csv_to_dataframe(os.path.join(folder_path, csv_files[0]))

    # 나머지 CSV 파일을 순회하면서 병합
    for file in csv_files[1:]:
        df = load_csv_to_dataframe(os.path.join(folder_path, file))
        merged_df = pd.concat([merged_df, df], ignore_index=True)
    
    return merged_df

# 병합된 DataFrame을 CSV 파일로 저장하는 함수
def save_merged_csv(df, output_file):
    df.to_csv(output_file, index=False)

try:
    # 모든 CSV 파일을 하나로 병합
    merged_df = merge_csv_files(script_directory)

    # 병합된 DataFrame을 CSV 파일로 저장
    output_file = os.path.join(script_directory, "merge.csv")
    save_merged_csv(merged_df, output_file)
    print("CSV 파일 병합 및 저장이 완료되었습니다.")
except FileNotFoundError as e:
    print(e)
