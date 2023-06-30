import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
file_path = "policy_text.txt"  # set the p
file_content = ""

with open(file_path, "r") as file:
    file_content = file.read()

def ask(question):
    rol = '''Eres un chatbot encargado de brindar información sobre polizas de seguros. 
    Tus respuestas deben relacionarse con información relacionada con polizas de seguros. 
    
    Debes responder de forma respetuosa y precisa. 
    
    No debes responder preguntas sobre temas que no tengan que ver con las pólizas.
    Si el usuario te pregunta temas que no tengan relación con las polizas de seguro debes pedir disculpas y pedir que pregunte solo 
    por temas relacionados a polizas de seguros.
    
    Tu nombre es Nicolle. Presta atención a la información de las polizas: '''
    prompt = rol + " " + file_content + "pregunta: " + question

    response = openai.Completion.create(
        engine="text-davinci-003",  # Set the GPT engine such as "davinci" or "text-davinci-003"
        prompt=prompt,
        max_tokens=50,  # Max number of tokens in the answer
        n=1,  # Number of answers
        stop=".",  # Optional: set the last word of the conversation.
    )

    completions = response['choices']

    generated_text= ""
    for completion in completions:
        generated_text = completion['text']
        print(generated_text)

    return generated_text