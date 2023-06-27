from flask import Flask, render_template
from flask_socketio import SocketIO, emit

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'

    from .routes import main_routes
    app.register_blueprint(main_routes)

    socketio.init_app(app)
    return app