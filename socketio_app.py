from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, send, emit

app = Flask(__name__)
socketio = SocketIO(app)


@socketio.on('connect', namespace='/emotion')
def on_connect():
    join_room('emotion_group')
    send('Connected to the emotion channel.', room='emotion_group')


@socketio.on('disconnect', namespace='/emotion')
def on_disconnect():
    leave_room('emotion_group')
    print('Client disconnected from emotion channel')


@socketio.on('message', namespace='/emotion')
def handle_message(message):
    # This function can be expanded based on what you expect to receive
    print('Received message: ', message)


@socketio.on('emotion_message', namespace='/emotion')
def handle_emotion_message(json):
    emit('emotion_response', json, room='emotion_group')


if __name__ == '__main__':
    socketio.run(app, debug=True)
