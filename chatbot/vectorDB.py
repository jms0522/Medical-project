import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import (SentenceTransformerEmbeddings,)
from langchain_community.vectorstores import Chroma
import pickle

# Load documents from a CSV file
loader = CSVLoader("./merged.csv", encoding='utf-8')
documents = loader.load()

# Split texts
text_splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=20)
docs = text_splitter.split_documents(documents)

with open('list.pkl', 'wb') as file:
    pickle.dump(docs, file)

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="/Users/baeminseog/chatbot")

# create the open-source embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# save to disk
db2 = Chroma.from_documents(docs, embedding_function, persist_directory="./chroma_db")

# Create a collection with the defined embedding function
collection_name = "my_collection"
collection = client.get_or_create_collection(name=collection_name, embedding_function=embedding_function)





