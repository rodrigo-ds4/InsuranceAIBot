from dotenv import load_dotenv
import openai
import os
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.schema import Document

from langchain.indexes import VectorstoreIndexCreator

load_dotenv()
current_directory = os.getcwd()
print("Directorio actual:", current_directory)
openai.api_key = os.environ['OPENAI_API_KEY']
print(os.environ['OPENAI_API_KEY'])

def ask(question, code):
    embedding = OpenAIEmbeddings()
    print("code: " + code)
    loader = PyPDFLoader("raw-dataset/" + code + ".pdf")

    index = VectorstoreIndexCreator(
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=20),
        embedding = OpenAIEmbeddings()
    ).from_loaders([loader])
    generated_text = index.query(question)
    return generated_text
