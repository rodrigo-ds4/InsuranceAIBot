from flask import Flask
from flask_socketio import SocketIO, send
import answer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blah' 
socketio = SocketIO(app, cors_allowed_origins='*')

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send(message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)