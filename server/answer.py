""" from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper, ServiceContext
from langchain import OpenAI
import sys
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")

def construct_index(directory_path):
    # set maximum input size
    max_input_size = 500
    # set number of output tokens
    num_outputs = 100
    # set maximum chunk overlap
    max_chunk_overlap = 20
    # set chunk size limit
    chunk_size_limit = 600 

    # define prompt helper
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

    # define LLM
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-davinci-003", max_tokens=num_outputs))

    documents = SimpleDirectoryReader(directory_path).load_data()

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)

    index.save_to_disk('index.json')

    return index

def ask(question):
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    while True: 
        
        response = index.query(question)
        print(response.response)



construct_index("policy_text.txt") """


import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

def ask(question):
    rol = '''Eres un chatbot encargado de brindar información sobre polizas de seguros. 
    Tus respuestas deben relacionarse con información relacionada con polizas de seguros. 
    
    Debes saludar al principio de la conversacion y responder de forma respetuosa y precisa. 
    
    No debes responder preguntas sobre temas que no tengan que ver con las polizas.
    Si el usuario te pregunta temas que no tengan relación con las polizas de seguro debes pedir disculpas y pedir que pregunte solo 
    por temas relacionados a polizas de seguros.
    
    Tu nombre es CHATBOT.'''
    prompt = rol + " " + question

    response = openai.Completion.create(
        engine="text-davinci-003",  # Elige el motor de GPT (p. ej., "davinci" o "text-davinci-003")
        prompt=prompt,
        max_tokens=40,  # Número máximo de tokens para la respuesta generada
        n=1,  # Número de respuestas a generar
        stop=None,  # Opcional: texto para detener la respuesta generada
    )

    completions = response['choices']

    generated_text= ""
    for completion in completions:
        generated_text = completion['text']
        print(generated_text)
    
    return generated_text