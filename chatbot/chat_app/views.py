# langchain
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate

# chatbot
import os
import pickle
from .models import ChatBot, UserInteractionLog
import json
import markdown

# django
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.safestring import mark_safe
from .tasks import save_log
import logging

logger_interaction = logging.getLogger('drrc')
logger_error = logging.getLogger('error')

client = chromadb.PersistentClient(path="C://Users//Playdata//Desktop//final//Medical-project//chatbot")
collection_name = "my_collection"

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# db2 = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
# retriever = db2.as_retriever(search_type="mmr")

with open('list.pkl', 'rb') as file:
    docs = pickle.load(file)

chroma_vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
chroma_retriever = chroma_vectorstore.as_retriever(search_kwargs={"k": 5})

bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 5

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, chroma_retriever], weights=[0.8, 0.2]
)

# prompt = hub.pull("rlm/rag-prompt")

template = '''
질문은 사용자가 겪고 있는 증상에 대한 질문입니다. 다음과 같이 답변해주세요:
- 예측 가능한 증상
- 해결 방법
- 약 추천
이 3가지를 의사님의 의견을 바탕으로 답변해주세요.
질문 : {question}
'''
prompt = ChatPromptTemplate.from_template(template)

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

def format_docs(docs):
    # 검색한 문서 결과를 하나의 문단으로 합쳐줍니다.
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": ensemble_retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# @login_required
def ask_question(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            username = request.user.username
        else:
            username = None
        text = request.POST.get("text").strip()
        
        if not text:
            return JsonResponse({"error": "Empty question."}, status=400)
        try:
            # LangChain을 사용하여 답변 생성
            response_data = rag_chain.invoke(text)  # formatted_docs를 검색 컨텍스트로 사용
            ChatBot.objects.create(username=username, question=text, answer=response_data, created_at=timezone.now())
            
            return JsonResponse({"data": response_data}, status=200)
        except Exception as e:
            logger_error.error(f'Error during question handling: {str(e)}')
            return JsonResponse({"error": str(e)}, status=500)

def chat(request):
    # 사용자가 로그인한 경우와 로그인하지 않은   경우를 구분하여 처리
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = None  # 로그인하지 않은 경우, user를 None으로 설정
    chats = ChatBot.objects.filter(username=username)
    return render(request, "chat_bot.html", {"chats": chats})

@login_required
def get_user_chats(request):
    username = request.user.username 
    chats = ChatBot.objects.filter(username=username).order_by('created_at')
    # 마크다운을 HTML로 변환하여 리스트에 추가
    chat_data = []
    for chat in chats:
        chat_data.append({
            'username': chat.username,
            'question': mark_safe(markdown.markdown(chat.question)),
            'answer': mark_safe(markdown.markdown(chat.answer)),
            'created_at': chat.created_at,
        })
    return JsonResponse({'chats': chat_data})


@csrf_exempt
def log_interaction(request):
    if request.method == 'POST': # 로그 데이터를 JSON 형식으로 파싱
        data = json.loads(request.body) # 요청에서 사용자 인증 정보를 확인
        # 로그인한 사용자의 경우 사용자 ID를 사용, 그렇지 않은 경우 None
        username = request.user.username if request.user.is_authenticated else None
        url = data.get('url') or 'localhost'
        log_data = {
            "username": username,
            "event_type": data.get('eventType'),
            "element_id": data.get('elementId'),
            "element_class": data.get('elementClass'),
            "element_type": data.get('elementType'),
            "element_name": data.get('elementName'),
            "url": url,
            "timestamp": timezone.now().isoformat()  # isoformat을 사용하여 직렬화
        }       
        save_log.delay(log_data)
        
        logger_interaction.info(f"User interaction by {username}: {data}") # 사용자 아이디를 로그 메시지에 포함(로깅)

        return JsonResponse({"status": "success"}, status=200)
    return JsonResponse({"error": "Invalid request"}, status=400)

