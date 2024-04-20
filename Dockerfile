FROM python:3.9-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

ADD . /cinepulse_face_detector
WORKDIR /cinepulse_face_detector
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["cinepulse.py"]
