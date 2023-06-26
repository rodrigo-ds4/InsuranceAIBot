from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(message):
    # Aquí puedes procesar el mensaje y obtener la respuesta del modelo de Haystack
    # Luego, puedes enviar la respuesta de vuelta al cliente utilizando `emit()`
    emit('response', 'Respuesta del chatbot')