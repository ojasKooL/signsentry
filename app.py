from flask import Flask, Response, render_template, request, jsonify, send_file, after_this_request, send_from_directory
import cv2
import math
import os
import numpy as np
from ultralytics import YOLO
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="static", template_folder="templates")

MODEL_PATH = 'C:/JS/signsentry/server/models/best.pt'  # Adjust path if needed

# Ensure uploads folder is inside the project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Gets the directory of app.py
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Create the uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = YOLO(MODEL_PATH)

classNames = [
    "Road narrows on right", "50 mph speed limit", "Attention Please-", "Beware of children", 
    "CYCLE ROUTE AHEAD WARNING", "Dangerous Left Curve Ahead", "Dangerous Right Curve Ahead", 
    "End of all speed and passing limits", "Give Way", "Go Straight or Turn Right", 
    "Go straight or turn left", "Keep-Left", "Keep-Right", "Left Zig Zag Traffic", 
    "No Entry", "No Over Taking", "Overtaking by trucks is prohibited", "Pedestrian Crossing", 
    "Round-About", "Slippery Road Ahead", "Speed Limit 20 KMPh", "Speed Limit 30 KMPh", 
    "Stop Sign", "Straight Ahead Only", "Traffic signal", "Truck traffic is prohibited", 
    "Turn left ahead", "Turn right ahead", "Uneven Road"
]

def generate_frames():
    cap = cv2.VideoCapture(0)  # Use webcam

    while True:
        success, img = cap.read()
        if not success:
            break  # Stop if frame isn't captured

        results = model(img, stream=True)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])

                # Draw bounding box and text
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                label = f"{classNames[cls]} ({confidence:.2f})"
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                            0.6, (255, 0, 0), 2)

        _, buffer = cv2.imencode('.jpg', img)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/detection_methods')
def detection_methods():
    return render_template("detection.html")

@app.route('/webcam_detection')
def webcam_detection():
    return render_template("webcam.html")

@app.route('/image_detection')
def image_detection():
    return render_template("image.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Load the image
    img = cv2.imread(filepath)
    if img is None:
        return jsonify({'error': 'Failed to load image'})

    # Perform YOLO object detection
    results = model(img, stream=True)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])

            # Draw bounding box and text
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            label = f"{classNames[cls]} ({confidence:.2f})"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.6, (255, 0, 0), 2)

    # Save the processed image
    processed_filepath = os.path.join(UPLOAD_FOLDER, f"processed_{filename}")
    cv2.imwrite(processed_filepath, img)

    return send_file(processed_filepath, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

