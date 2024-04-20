import os
import cv2


def process_all_videos(video_path, output_folder):
    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open video {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % int(fps) == 0:  # Process one frame per second
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if faces is not None:
                # Save only the frames that have faces
                frame_filename = f"frame_{frame_count}.jpg"
                frame_path = os.path.join(output_folder, frame_filename)
                cv2.imwrite(frame_path, frame)

        frame_count += 1

    cap.release()
    print(f"Finished processing video: {video_path}")
