from flask import Blueprint
from flask_socketio import send
from app import socketio

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return '¡Bienvenido al chatbot!'

@main_routes.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('message')
def handle_message(message):
    response = 'Respuesta del chatbot'
    emit('response', response)