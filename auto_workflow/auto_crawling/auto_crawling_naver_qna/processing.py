import pandas as pd
import os
import re

# 문액을 위해 '?' , '.' , 숫자 표현은 남기고 전처리 하도록 했음.

def preprocess_data(data):
    
    cleaned_title = re.sub(r'[^가-힣0-9.?\s]', '', data['title'])
    cleaned_question = re.sub(r'[^가-힣0-9.?\s]', '', data['question'])
    cleaned_answer = re.sub(r'[^가-힣0-9.?\s]', '', data['answer'])

    # "안녕하세요. 대한의사협회·네이버 지식iN 상담의사 윤민수 입니다."와 같은 문장을 제거.
    cleaned_answer = re.sub(r'^안녕하세요\..*입니다\.$', '', cleaned_answer)

    # 공백이 2개 이상이면 한번으로 줄임.
    cleaned_title = re.sub(r'\s+', ' ', cleaned_title)
    cleaned_question = re.sub(r'\s+', ' ', cleaned_question)
    cleaned_answer = re.sub(r'\s+', ' ', cleaned_answer)

    # 전처리된 데이터를 딕셔너리로 반환.
    preprocessed_data = {
        'doc_id': data['doc_id'],
        'title': cleaned_title.upper(),
        'question': cleaned_question,
        'answer': cleaned_answer.lower(),
    }
    return preprocessed_data

def preprocess_dataframe(df):
    # 결측치가 있는 행을 제거합니다.
    df = df.dropna()
    
    # 전처리 함수를 각 행에 적용합니다.
    df = df.apply(preprocess_data, axis=1)
    
    # None 값을 가진 행을 제거합니다.
    df = df.dropna()
    
    return df

# df = pd.DataFrame(data)

# preprocessed_df = preprocess_dataframe(df)
# print(preprocessed_df)