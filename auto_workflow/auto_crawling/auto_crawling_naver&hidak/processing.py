import pandas as pd
import os
import re
from pykospacing import Spacing




def remove_greeting2(text):
    text = re.sub(r'하이닥.*?입니다\.', '', text)
    text = re.sub(r'네이버.*?입니다\.', '', text)
    text = re.sub(r'닥톡.*?입니다\.', '', text)
    text = re.sub(r'대한의사협회.*?입니다\.', '', text)
    # text = re.sub(r'\p{Hangul}+과전문의.*?입니다\.', '', text)
    return text
def remove_greeting1(text):
    return re.sub(r'안녕하세요\.', '', text)
def remove_special_chars(text):
    return text.replace('\\xa0', '')

spacing = Spacing()
def preprocess_json(data_list):
    preprocessed_data = []
    for data in data_list:
        if not data['Date']:  # Date가 비어있는 경우
            preprocessed_data = data
            return preprocessed_data
        else:
            # 전처리 적용
            # data['title'] = spacing(data['title'])
            # data['question'] = spacing(data['question'])
            # data['answer'] = spacing(data['answer'])
            data['answer'] = ''.join(data['answer'])  # 리스트를 문자열로 변환
            data['question'] = remove_greeting1(data['question'])  # 인사말 제거
            data['answer'] = remove_greeting1(data['answer'])  # 인사말 제거
            data['answer'] = remove_greeting2(data['answer'])  # 인사말 제거
            data['answer'] = remove_special_chars(data['answer'])  # 특수 문자 제거

            data['question'] = remove_special_chars(data['question'])  # 특수 문자 제거
            if '삭제' not in data['question']:  # '삭제' 키워드가 없는 경우만 추가
                preprocessed_data.append(data)
    return preprocessed_data




# 문액을 위해 '?' , '.' , 숫자 표현은 남기고 전처리 하도록 했음.

def preprocess_data(data):
    
    cleaned_title = re.sub(r'[^가-힣0-9.?\s]', '', data['title'])
    cleaned_question = re.sub(r'[^가-힣0-9.?\s]', '', data['question'])
    cleaned_answer = re.sub(r'[^가-힣0-9.?\s]', '', data['answer'])

    # "안녕하세요. 대한의사협회·네이버 지식iN 상담의사 윤민수 입니다."와 같은 문장을 제거.
    cleaned_answer = re.sub(r'안녕하세요\..*입니다\.$', '', cleaned_answer)

    # 공백이 2개 이상이면 한번으로 줄임.
    cleaned_title = re.sub(r'\s+', ' ', cleaned_title)
    cleaned_question = re.sub(r'\s+', ' ', cleaned_question)
    cleaned_answer = re.sub(r'\s+', ' ', cleaned_answer)
    cleaned_answer = remove_greeting1(cleaned_answer)  # 인사말 제거
    cleaned_answer = remove_greeting2(cleaned_answer)  # 인사말 제거

    # 시간이 오래걸리는 것인지, airflow에서 공백을 전처리 하는 부분이 동작이 잘안되어서 주석처리
    # cleaned_title = spacing(cleaned_title)
    # cleaned_question = spacing(cleaned_question)
    # cleaned_answer = spacing(cleaned_answer)


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