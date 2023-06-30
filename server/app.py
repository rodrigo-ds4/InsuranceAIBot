from flask import Flask
from flask_socketio import SocketIO, send
from answer import ask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blah' 
socketio = SocketIO(app, cors_allowed_origins='*')

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    answer = ask(message)
<<<<<<< HEAD
    send(message, broadcast=True)
=======
>>>>>>> 3c19aad8ca4515ed09b4ff126685875252d26351
    send(answer, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)