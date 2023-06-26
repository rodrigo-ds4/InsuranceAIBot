from haystack import Document, Finder
from haystack.indexing.cleaning import clean_wiki_text
from haystack.indexing.io import write_documents_to_db
from pickle import pickle 

# Open pickle file and load it into a variable
loaded_df = pickle.load(open('df.pickle', 'rb'))

# Show the resulting variable
print(loaded_df)
# Cargar el texto del PDF en un documento
with open("ruta/al/pdf.txt", "r") as file:
    text = file.read()
    doc = Document(content=text, meta={"name": "MiPDF"})

# Limpieza y escritura de documentos en la base de datos
cleaned_doc = clean_wiki_text(doc)
write_documents_to_db(cleaned_doc, "ruta/a/la/base/de/datos")