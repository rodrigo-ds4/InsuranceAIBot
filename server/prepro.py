import pandas as pd
import pickle
import re

def eliminar_palabras(texto):
    palabras_a_eliminar = ['de', 'en', 'la', "La", "los", "Los", "Las", "las", "el", "El"]
    patron = r'\b(?:{})\b'.format('|'.join(palabras_a_eliminar))
    texto_sin_palabras = re.sub(patron, '', texto, flags=re.IGNORECASE)
    return texto_sin_palabras


# Open pickle file and load it into a variable
df = pickle.load(open('df.pickle', 'rb'))

# Show the resulting variable
print(df)

# Crear una lista para almacenar el contenido formateado
formatted_content = []

# Iterar sobre cada fila del DataFrame
for _, row in df.iterrows():
    policy_name = row['Policy_Name']
    article_name = row['Article_Name']
    article_content = row['Text']

    # Formatear el contenido
    formatted_text = f"Policy Name: {policy_name}\nArticle Name: {article_name}\n{article_content}\n"

    # Agregar el contenido formateado a la lista
    formatted_content.append(formatted_text)

# Unir todos los elementos de la lista en un solo string
text_data = ''.join(formatted_content)

text_data=eliminar_palabras(text_data)
# Guardar el texto en un archivo de texto
with open('policy_text.txt', 'w') as file:
    file.write(text_data)
