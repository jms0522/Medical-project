import os
import pandas as pd

# 특정 컬럼만 추출하여 CSV 파일을 DataFrame으로 변환하는 함수
def load_csv_to_dataframe(file_path, columns):
    try:
        return pd.read_csv(file_path, usecols=columns)
    except ValueError:
        # 지정된 컬럼 중 일부가 없는 경우, 해당 컬럼을 누락시키지 않고 모두 null 값으로 채워서 DataFrame 생성
        df = pd.read_csv(file_path)
        missing_cols = set(columns) - set(df.columns)
        for col in missing_cols:
            df[col] = None
        return df[columns]

# 폴더 내의 모든 CSV 파일을 불러와서 하나의 DataFrame으로 병합하는 함수
def merge_csv_files(folder_path, columns):
    file_names = os.listdir(folder_path)
    csv_files = [f for f in file_names if f.endswith('.csv')]

    if not csv_files:
        raise FileNotFoundError("폴더 내에 CSV 파일이 없습니다.")

    # 지정된 컬럼만 포함하여 첫 번째 CSV 파일을 기준으로 DataFrame 생성
    merged_df = load_csv_to_dataframe(os.path.join(folder_path, csv_files[0]), columns)

    # 나머지 CSV 파일을 순회하면서 병합
    for file in csv_files[1:]:
        df = load_csv_to_dataframe(os.path.join(folder_path, file), columns)
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    return merged_df

# 병합된 DataFrame을 CSV 파일로 저장하는 함수
def save_merged_csv(df, output_file):
    df.to_csv(output_file, index=False)

script_directory = os.path.dirname(os.path.realpath(__file__))
columns = ['병명', '정의', '원인', '증상']  # 추출하려는 컬럼 목록

try:
    merged_df = merge_csv_files(script_directory, columns)
    output_file = os.path.join(script_directory, "merged.csv")
    save_merged_csv(merged_df, output_file)
    print("CSV 파일 병합 및 저장이 완료되었습니다.")
except FileNotFoundError as e:
    print(e)
