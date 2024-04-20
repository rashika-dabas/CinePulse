import os
import uuid
from flask import request, jsonify, Response, current_app as app
from flask import send_from_directory
from keras.models import load_model
from pymongo import MongoClient
from .video_processing import process_all_videos
from .emotion_detection import process_images_and_predict
from .camera import Camera

# Establish a connection to MongoDB
client = MongoClient('mongodb+srv://roandimaculangan:pass1234@emopulse-prod-cluster01.wejk1x3.mongodb.net/')
db = client['emopulse_db']
videos_collection = db.videos

# mongo = PyMongo()
camera = Camera()


def init_routes(app):

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    @app.route('/api/getMovieReviewPredictions', methods=['POST'], strict_slashes=False)
    def get_movie_review_predictions():
        video_directory = os.path.join(app.root_path, 'videos', 'movies')
        segmented_images_base_directory = os.path.join(app.root_path, 'videos', 'segmented_images')
        model_path = os.path.join(app.root_path, 'emotion_detection_model_v3.0.h5')
        user_id = str(uuid.uuid4())
        model = load_model(model_path)
        file_count = 0
        all_movie_predictions = {}
        total_emotions = {emotion: 0 for emotion in ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']}

        while True:
            file_key = f'file{file_count}'
            video_file = request.files.get(file_key)
            if not video_file:
                if file_count == 0:
                    return jsonify({'error': 'No files received'}), 400
                break

            movie_name = f'movie_{file_count:02d}'
            save_path = os.path.join(video_directory, f'{movie_name}.mp4')
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            video_file.save(save_path)

            segmented_images_directory = os.path.join(segmented_images_base_directory, f'segmented_images_{file_count:02d}')
            process_all_videos(save_path, segmented_images_directory)
            predictions = process_images_and_predict(user_id, segmented_images_base_directory, model)
            all_movie_predictions[movie_name] = predictions

            for emotion, count in predictions.items():
                total_emotions[emotion] += count

            file_count += 1
            os.remove(save_path)  # Cleanup after processing

        
        db.videos.insert_one({
            'user_id': user_id,
            'movies': all_movie_predictions,
            'total_emotions': total_emotions
        })

        return jsonify({
            'user_id': user_id,
            'total_emotions': total_emotions,
            'predictions': all_movie_predictions
        })

    @app.route('/api/startRecording', methods=['GET'], strict_slashes=False)
    def start_recording():
        camera.start_recording()
        return jsonify({'status': 'recording started'})

    @app.route('/api/stopRecording/', methods=['GET'], strict_slashes=False)
    def stop_recording():
        counts = camera.stop_recording()
        return jsonify({'emotion_counts': counts})

    @app.route('/api/getCameraSnapshot', methods=['GET'], strict_slashes=False)
    def get_camera_snapshot():
        try:
            print("HERE")
            frame = camera.get_frame_with_box()
            if frame:
                return Response(frame, mimetype='image/jpeg')
            return jsonify('No frame available'), 404
        except Exception as e:
            print("Error:", e)
            return jsonify('Error accessing camera'), 500
