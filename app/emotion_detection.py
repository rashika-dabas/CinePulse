import os
import cv2
import shutil
import numpy as np


def save_frames_with_faces(video_path, output_folder):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}.")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % fps == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if len(faces) > 0:
                frame_filename = os.path.join(output_folder, f"frame_{frame_count // fps:04d}.jpg")
                cv2.imwrite(frame_filename, frame)
                print(f"Saved {frame_filename} with {len(faces)} faces.")

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()


def process_images_and_predict(user_id, base_dir, model):
    class_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    global_emotion_counts = {emotion: 0 for emotion in class_labels}
    print("Starting image processing...")

    for product_dir in sorted(os.listdir(base_dir)):
        product_path = os.path.join(base_dir, product_dir)
        print(f"Checking directory: {product_path}")
        if os.path.isdir(product_path):
            for image_file in sorted(os.listdir(product_path)):
                if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(product_path, image_file)
                    img = cv2.imread(img_path)
                    if img is None:
                        print(f"Failed to load image: {img_path}")
                        continue
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                    print(f"{len(faces)} faces detected in {image_file}")

                    for (x, y, w, h) in faces:
                        face_img = gray[y:y+h, x:x+w]
                        face_img = cv2.resize(face_img, (48, 48))
                        face_img = face_img.astype('float32') / 255
                        face_img = np.expand_dims(face_img, axis=0)

                        predictions = model.predict(face_img)
                        predicted_emotion = class_labels[np.argmax(predictions)]
                        global_emotion_counts[predicted_emotion] += 1
                        print(f"Detected emotion: {predicted_emotion}")

            shutil.rmtree(product_path)
            print(f"Archived processed images from {product_path}")

    print("Finished processing all images.")
    return global_emotion_counts
