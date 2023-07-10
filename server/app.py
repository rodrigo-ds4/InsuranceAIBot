from flask import Flask
from flask_socketio import SocketIO, send
from answer import ask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'prueba' 
socketio = SocketIO(app, cors_allowed_origins='*')
code = ""
last_question = ""
last_answer = ""

@socketio.on('message')
def handle_message(message):
    global last_answer
    global last_question
    print('received message: ' + message)
    answer = ask(message, code, last_question, last_answer)
    last_answer = answer
    last_question = message
    send(answer, broadcast=True)

@socketio.on('action')
def handle_message(action):
    print('action: ' + action)
    if action[:3] == "POL":
        global code
        global last_question
        global last_answer
        code = action
        last_question = "hola"
        last_answer = "hola"
        send("Conversemos sobra la póliza " + action[3:] + ", qué te gustaría saber?", broadcast=True)
    elif action[:3] == "NEW":
        send("Generemos una nueva poliza. Indicame que requerimientos tienes? ", broadcast=True)
    elif action[:3] == "FND":
        send("Voy a buscar polizas en Google, indicame que tipo de poliza buscas.", broadcast=True)
    else:
        print("action " + action + " is not available.")
        send("error", broadcast=True)
    #answer = ask(message)

if __name__ == '__main__':
    # Get the server port
    port = 5000  # Default port

    # Print server information
    print(f"Server running on http://localhost:{port}/")

    socketio.run(app, host='0.0.0.0', port=port)
