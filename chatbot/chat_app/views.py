import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_community.vectorstores import Chroma
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
import os
from .models import ChatBot
import pickle

os.environ["OPENAI_API_KEY"] = "."

client = chromadb.PersistentClient(path="/Users/baeminseog/chatbot")
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

prompt = hub.pull("rlm/rag-prompt")
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

@login_required
def ask_question(request):
    if request.method == "POST":
        text = request.POST.get("text").strip()
        if not text:
            return JsonResponse({"error": "Empty question."}, status=400)

        try:
            # LangChain을 사용하여 답변 생성
            response_data = rag_chain.invoke(text)  # formatted_docs를 검색 컨텍스트로 사용
            return JsonResponse({"data": response_data}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def chat(request):
    user = request.user
    chats = ChatBot.objects.filter(user=user)
    return render(request, "chat_bot.html", {"chats": chats})
