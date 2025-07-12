from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!syahdan'
socketio = SocketIO(app)

models = {
    "face_detector": cv2.CascadeClassifier("haarcascade_frontalface_default.xml"),
    "cat_detector": cv2.CascadeClassifier("haarcascade_frontalcatface_extended.xml")
}

def base64_to_image(base64_string):
    img_data = base64_string.split(',')[1]
    img_bytes = base64.b64decode(img_data)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return image

def image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    base64_string = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_string}"

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('process_frame')
def handle_process_frame(data):
    base64_image = data['image']
    model_name = data['model']

    if model_name not in models:
        placeholder_img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(placeholder_img, "Still in development", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        processed_image_b64 = image_to_base64(placeholder_img)
    else:
        frame = base64_to_image(base64_image)
        (h_orig, w_orig) = frame.shape[:2]
        w_new = 320
        ratio = w_new / float(w_orig)
        h_new = int(h_orig * ratio)

        small_frame = cv2.resize(frame, (w_new, h_new), interpolation=cv2.INTER_AREA)
        gray_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

        classifier = models[model_name]
        objects = classifier.detectMultiScale(gray_small_frame, scaleFactor=1.2, minNeighbors=6, minSize=(30, 30))

        for (x, y, w, h) in objects:
            x_orig = int(x / ratio)
            y_orig = int(y / ratio)
            w_orig = int(w / ratio)
            h_orig = int(h / ratio)
            cv2.rectangle(frame, (x_orig, y_orig), (x_orig + w_orig, y_orig + h_orig), (30, 235, 216), 2)

        processed_image_b64 = image_to_base64(frame)

    emit('processed_frame', {'image': processed_image_b64})

if __name__ == '__main__':
    socketio.run(app, debug=True)
