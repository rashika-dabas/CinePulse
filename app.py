from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)


@socketio.on('connect', namespace='/emotion')
def test_connect():
    print('Client connected')


@socketio.on('disconnect', namespace='/emotion')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)
