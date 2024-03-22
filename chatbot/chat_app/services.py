# langchain
from functools import wraps
import chromadb
from django.http import JsonResponse
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
from langchain.schema.runnable import RunnableMap
import chromadb

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging
from .models import ChatBot, SimilarAnswer

logger_interaction = logging.getLogger('drrc')
logger_error = logging.getLogger('error')

def format_docs(docs):
    # 검색한 문서 결과를 하나의 문단으로 합쳐줍니다.
    return "\n\n".join(doc.page_content for doc in docs)

# 질문 처리용 LangChain 모델 설정
def get_question_handling_chain():
    chroma_client = chromadb.HttpClient(host="43.201.236.125", port=8001)
    # 임베딩 함수 설정
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    # Chroma 인스턴스 생성
    db = Chroma(client = chroma_client, collection_name = "drrc", embedding_function=embedding_function)
    retriever = db.as_retriever()

    template = """
        ※ 안녕하세요. 질문해주신 내용에 대한 답변을 해드릴게요.
        당신은 의사이고, 환자가 말하는 증상을 듣고 합리적인 근거를 바탕으로 해결 방안을 제시하는 역할을 한다.
        또한 약에 대한 질문을 받으면, 참조 가능한 정보를 바탕으로 약의 효능, 복용 방법, 부작용 등에 대해 자세히 대답한다.
        마크다운 형식을 사용하여 응답을 구조화하고 가독성을 높인다.
        환자로부터 제공된 정보를 분석하여 다음 정보를 제공합니다:
        1. **증상에 대한 답변**일 경우:
            - 예측 가능한 증상
            - 해결 방법
            ※ 제공되는 정보는 보조적인 수단으로 활용되어야 하며, 정확한 진단 및 치료를 위해서는 반드시 전문 의료인과 상담하는 것을 권장합니다.
        2. **약에 대해 물어보면**:
            - 약 추천
            - 약에 대한 설명
            - 약에 대한 추가 정보
        대화 중에 제공된 증상 정보만으로 진단하기 어려운 경우, 추가적인 정보를 요청하는 질문을 할 수 있으며, 이를 통해 보다 정확한 진단을 내릴 수 있습니다.
        모든 응답은 참조 가능한 정보를 바탕으로 하며, 환자와의 대화는 친절하고 이해하기 쉬운 방식으로 진행됩니다.
        질문은 사용자가 겪고 있는 증상에 대한 질문이거나, 특정 약에 대한 정보를 요청하는 것입니다. 다음과 같이 답변해주세요:
        - 질문 유형에 맞는 카테고리에서 정보 제공
            - 증상에 대한 질문일 경우, 예측 가능한 증상과 해결 방법을 답변합니다.
            - 약에 대한 질문일 경우, 약 추천과 약에 대한 자세한 설명을 제공합니다.
        질문 : {question}
        ※ 약에 대한 정보를 원하시면 해당 약의 이름을 말씀해주세요. 감사합니다. -Dr.RC-
        """

    prompt = ChatPromptTemplate.from_template(template) 
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

# 유사한 답변 찾기용 LangChain 모델 설정
def get_similar_answers_chain():
    # Chroma 클라이언트 및 컬렉션 설정
    chroma_client = chromadb.HttpClient(host="43.201.236.125", port=8001)
    embedding_function = SentenceTransformerEmbeddings(model_name="jhgan/ko-sroberta-multitask")
    
    # Chroma 인스턴스 생성
    db = Chroma(client = chroma_client, collection_name = "embedding_test0318", embedding_function=embedding_function)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 8})

    template = """
        질문은 사용자가 겪고 있는 증상에 대한 질문입니다. 다음과 같이 답변해주세요:
        - {context}
        이전에 사용자들이 제출한 질문들 중에서, 당신이 입력한 질문과 가장 유사한 질문들을 찾아보았습니다. 이 질문들은 데이터베이스 내에서 관련성이 높은 것으로 평가되었습니다. 아래는 그 질문들과 그에 대한 답변입니다. 이 정보를 바탕으로, 당신의 질문에 가장 잘 맞는 답변을 찾을 수 있을 것입니다.
        1. 유사 질문 1: [첫 번째로 유사한 질문]
        답변: [해당 질문에 대한 답변]
        2. 유사 질문 2: [두 번째로 유사한 질문]
        답변: [해당 질문에 대한 답변]
        3. 유사 질문 3: [세 번째로 유사한 질문]
        답변: [해당 질문에 대한 답변]
        4. 유사 질문 4: [네 번째로 유사한 질문]
        답변: [해당 질문에 대한 답변]
        5. 유사 질문 5: [다섯 번째로 유사한 질문]
        답변: [해당 질문에 대한 답변]
        
        질문, 답변, 날짜가 모두있는 데이터만 보여주세요
        중복된 질문은 없어야 합니다. 
        질문: {question}
        """

    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

def handle_question(username, text):
    try:
        question_chain = get_question_handling_chain()  # 질문 처리용 모델 호출
        response_data = question_chain.invoke(text)
        chat_bot_instance = ChatBot.objects.create(username=username, question=text, answer=response_data, created_at=timezone.now())
        return JsonResponse({"id": chat_bot_instance.id, "data": response_data}, status=200)
    except Exception as e:
        logger_error.error(f'Error during question handling: {str(e)}')
        return JsonResponse({"error": str(e)}, status=500)

def fetch_similar_answers(question_id, username):
    try:
        original_question = get_object_or_404(ChatBot, id=question_id, username=username)
        similar_answer_instance, created = SimilarAnswer.objects.get_or_create(
            original_question=original_question,
            defaults={'similar_answer': ''}  # 유사 답변 생성 시 기본값 설정
        )
        
        if created:
            similar_chain = get_similar_answers_chain()
            similar_answer_instance.similar_answer = similar_chain.invoke(original_question.question)
            similar_answer_instance.save()

        # JsonResponse로 similar_answer_instance의 데이터를 반환합니다.
        return JsonResponse({
            "id": original_question.id,
            "originalQuestion": original_question.question,
            "similarAnswer": similar_answer_instance.similar_answer,
            "createdAt": similar_answer_instance.created_at
        }, status=200)
    except Exception as e:
        logger_error.error(f'Error during fetching similar answers: {str(e)}')
        return JsonResponse({"error": str(e)}, status=500, safe=False)
    
def login_required_ajax(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"error": "로그인이 필요합니다."}, status=403)
            else:
                return login_required(view_func)(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)
    return _wrapped_view