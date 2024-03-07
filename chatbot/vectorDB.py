import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import (SentenceTransformerEmbeddings,)
from langchain_community.vectorstores import Chroma
import pandas as pd
from neo4j import GraphDatabase
from langchain_community.vectorstores import Chroma
from typing import List, Union


#그래프 데이터베이스에서 값 추출하기
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

class Neo4jService:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # 데이터베이스 연결 종료
        self.driver.close()

    def fetch_disease_count(self):
        # Disease 노드의 총 개수를 확인하는 쿼리
        query = 'MATCH (d:Disease) RETURN count(d) AS total'
        with self.driver.session() as session:
            result = session.run(query).single()
            return result['total']
    
    def fetch_total_node_count(self):
        query = 'MATCH (n) RETURN count(n) AS totalNodes'
        with self.driver.session() as session:
            result = session.run(query).single()
            return result['totalNodes']
    
    def fetch_medicine_count(self):
        # Medicine 노드의 총 개수를 확인하는 쿼리
        query = 'MATCH (m:Medicine) RETURN count(m) AS total'
        with self.driver.session() as session:
            result = session.run(query).single()
            return result['total']
        

    def fetch_all_disease_data(self):
        # 모든 Disease 노드와 관련 정보를 가져오는 쿼리
        query = """
                MATCH (d:Disease)
                OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
                OPTIONAL MATCH (d)-[:HAS_CAUSE]->(c:Cause)
                OPTIONAL MATCH (d)-[:HAS_TREATMENT]->(t:Treatment)
                OPTIONAL MATCH (d)-[:HAS_MEDICINE]->(m:Medicine)
                RETURN d.name AS 병명,
                    collect(DISTINCT s.name) AS 증상,
                    collect(DISTINCT c.name) AS 원인,
                    collect(DISTINCT t.name) AS 치료방법,
                    collect(DISTINCT m.name) AS 의약품,
                    collect(DISTINCT {의약품명: m.name, 업체명: m.company, 복용방법: m.dosage, 주의사항: m.precautions, 이상반응: m.side_effects, 보관방법: m.storage}) AS 의약품상세정보
        """
        
        with self.driver.session() as session:
            results = session.run(query)
            return results.data()

neo4j_service = Neo4jService(uri="bolt://localhost:7687", user="neo4j", password="hadoop123")

# Disease 노드의 총 개수를 확인
total_diseases = neo4j_service.fetch_disease_count()
print(f"Disease nodes count: {total_diseases}")

# 모든 node의 총 개수를 확인하기!
total_nodes = neo4j_service.fetch_total_node_count()
print(f"모든 노드의 총 개수: {total_nodes}")

# 모든 Disease 데이터를 가져옴
data = neo4j_service.fetch_all_disease_data()
print(f"Retrieved data count: {len(data)}")  # 가져온 데이터의 개수 출력

total_medicines = neo4j_service.fetch_medicine_count()
print(f"Medicine nodes count: {total_medicines}")

# Neo4j 서비스 종료
neo4j_service.close()


#데이터에서 문서 생성
# def create_docs(data):
#     docs = []
#     for item in data:
#         disease_text = f"{item['Disease']} {' '.join(item['Symptoms'])} {' '.join(item['Causes'])} {' '.join(item['Treatments'])}"
#         medicine_texts = []
#         for medicine in item['Medicines']:
#             medicine_text = f"Medicine Name: {medicine['name']}, Company: {medicine['company']}, Dosage: {medicine['dosage']}, Efficacy: {medicine['efficacy']}, Precautions: {medicine['precautions']}, Side Effects: {medicine['sideEffects']}, Storage: {medicine['storage']}"
#             medicine_texts.append(medicine_text)
#         full_text = f"{disease_text} {' '.join(medicine_texts)}"
#         docs.append(full_text)
#     return docs

def create_docs(data):
    docs = []
    for item in data:
        # 'Disease' 대신 '병명' 키를 사용
        disease_text = f"{item['병명']} {' '.join(item.get('증상', []))} {' '.join(item.get('원인', []))} {' '.join(item.get('치료방법', []))}"
        medicine_texts = []
        # 의약품 정보가 리스트의 딕셔너리 형태로 저장되어 있는 경우
        for medicine in item.get('의약품상세정보', []):
            medicine_text = f"Medicine Name: {medicine.get('의약품명', '')}, Company: {medicine.get('업체명', '')}, Dosage: {medicine.get('복용방법', '')}, Efficacy: {medicine.get('효능', '')}, Precautions: {medicine.get('주의사항', '')}, Side Effects: {medicine.get('이상반응', '')}, Storage: {medicine.get('보관방법', '')}"
            medicine_texts.append(medicine_text)
        full_text = f"{disease_text} {' '.join(medicine_texts)}"
        docs.append(full_text)
    return docs



docs = create_docs(data)

# 생성된 문서의 수 확인
print(f"Total documents created: {len(docs)}")

model = SentenceTransformer('all-MiniLM-L6-v2')
vectors = model.encode(docs, show_progress_bar=True)

client = chromadb.PersistentClient(path="/Users/baeminseog/Medical-project/chatbot/chroma_db")
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# db = Chroma.from_documents(docs, embedding_function, persist_directory="./chroma_db")

collection_name = "my_collection"
collection = client.get_or_create_collection(name=collection_name)

documents = [doc for doc in docs]  # 문서 내용 리스트
embeddings = [vector.tolist() for vector in vectors]  # 벡터 리스트 (numpy 배열을 리스트로 변환)
ids = [str(i) for i in range(len(docs))]  # 각 문서에 대한 유니크한 ID 리스트

# Chroma 컬렉션에 문서, 벡터, 메타데이터 추가
collection.add(documents=documents, embeddings=embeddings, ids=ids)