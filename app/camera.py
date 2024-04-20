import os
import cv2
import numpy as np
from keras.models import load_model
from asgiref.sync import async_to_sync
from flask import request, jsonify, Response, current_app as app
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)


class Camera(object):
    def __init__(self):
        self.video = None  # Will be initialized on start_recording
        self.emotion_model = load_model(os.path.join(os.path.dirname(__file__), 'emotion_detection_model_v3.0.h5'))
        self.emotion_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}
        self.is_recording = False  # Flag to manage the recording state
        self.emotion_counts = {}  # Dictionary to store emotion counts

    def start_recording(self):
        if self.video is not None:
            # Release existing video capture object
            self.video.release()

        # Initialize video capture object
        self.video = cv2.VideoCapture(0)
        self.is_recording = True
        self.emotion_counts = {}  # Reset emotion counts when starting recording

    def stop_recording(self):
        self.is_recording = False
        if self.video is not None:
            # Release the video capture object
            self.video.release()
            self.video = None

        return self.emotion_counts  # Return emotion counts upon stopping recording

    def get_frame_with_box(self):
        if not self.is_recording:
            return None  # Do not process frames when not recording

        success, frame = self.video.read()
        if not success:
            return None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi = gray[y:y+h, x:x+w]
            crop = np.expand_dims(np.expand_dims(cv2.resize(roi, (48,48)), -1), 0)
            emotion_predict = self.emotion_model.predict(crop)
            maxIndex = int(np.argmax(emotion_predict))
            detected_emotion = self.emotion_dict[maxIndex]

            # Increment emotion count
            self.emotion_counts[detected_emotion] = self.emotion_counts.get(detected_emotion, 0) + 1

            # Send real-time emotion data to clients
            self.send_emotion_update(detected_emotion, np.max(emotion_predict))

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    @socketio.on('emotion_update')
    def send_emotion_update(self, emotion, data):
        emotion = data.get('emotion')
        index = data.get('index')
        if emotion is not None and index is not None:
            index = float(index) * 100
            emit('emotion_message', {'emotion': emotion, 'index': index}, broadcast=True)
        else:
            return jsonify({'error': 'Invalid data'})


if __name__ == '__main__':
    socketio.run(app)
