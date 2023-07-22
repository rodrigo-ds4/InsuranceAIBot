from dotenv import load_dotenv
import openai
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.indexes import VectorstoreIndexCreator
from langchain.memory import ChatMessageHistory

load_dotenv()
history = ChatMessageHistory()

openai.api_key = os.environ['OPENAI_API_KEY']

def ask(question, code, last_q="hola", last_a="hola"):
    embedding = OpenAIEmbeddings()
    print("code: " + code)
    print(last_a)
    #history_text = "Historial de chat: \n"
    #for chat in chat_history:
    #    history_text += "pregunta: " + chat["question"] + "\n"
        #history_text += "respuesta: " + chat["answer"] + "\n"

    loader = PyPDFLoader("raw-dataset/" + code + ".pdf")

    index = VectorstoreIndexCreator(
        #text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0),
        #embedding = embedding
    ).from_loaders([loader])
    history.add_user_message(question)
    question = "Mi nombre es Nicolle, bot asistente de seguros. Historial: Pregunta anterior del usuario fue: " + last_q + ". Respuesta: " + last_a +". Pregunta:" + question
    print(question)
    answer = index.query(question)
    history.add_ai_message(answer)

    return answer