from longchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
import openai
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.indexes import VectorstoreIndexCreator

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

# load document
loader = PyPDFLoader("/raw-datasets/POL120190177.pdf")
documents = loader.load()
#split the documents into chunks
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=20)
texts = text_splitter.split_documents(documents)
# select wich embeddings we want to use
embeddings = OpenAIEmbeddings()
# create the vectorstore to use as the index
db = Chroma.from_documents(texts, embeddings)
# expose this index in a retriever interface
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":2})
# create a chain to answer questions
qa = ConversationalRetrievalChain.from_llm(OpenAI(), retriever)
chat_history = []
query = "Como se llama la poliza?"
result = qa({"question":query, "chat_history": chat_history})
chat_history