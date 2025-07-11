# app.py

from flask import Flask, render_template, Response
import cv2
import numpy as np

app = Flask(__name__)

# Kita siapkan semua model yang kita punya dalam sebuah dictionary
# Ini membuat kode lebih rapi dan mudah dikelola
models = {
    "face_detector": cv2.CascadeClassifier("haarcascade_frontalface_default.xml"),
    "cat_detector": cv2.CascadeClassifier("haarcascade_frontalcatface_extended.xml")
}

# FUNGSI BARU UNTUK MEMBUAT GAMBAR PLACEHOLDER
def generate_placeholder(text_line1, text_line2):
    # Buat gambar hitam kosong dengan ukuran 640x480
    placeholder_img = np.zeros((480, 640, 3), dtype=np.uint8)

    # Atur font dan posisi teks
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Tulis teks baris pertama
    cv2.putText(placeholder_img, text_line1, (50, 220), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    # Tulis teks baris kedua
    cv2.putText(placeholder_img, text_line2, (180, 280), font, 0.8, (200, 200, 200), 1, cv2.LINE_AA)

    # Encode gambar menjadi JPEG
    ret, buffer = cv2.imencode('.jpg', placeholder_img)
    frame_bytes = buffer.tobytes()

    # Kirim gambar sebagai respons
    return (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def generate_frames(model_name):
    """
    Fungsi generator sekarang menerima 'model_name' untuk tahu
    model mana yang harus digunakan untuk deteksi.
    """
    # Inisialisasi kamera DI DALAM fungsi ini
    # Ini adalah praktik yang lebih baik
    camera = cv2.VideoCapture(0)
    
    # Memastikan model yang diminta ada
    if model_name not in models:
        print(f"Model {model_name} tidak ditemukan!")
        return

    classifier = models[model_name]

    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Menggunakan classifier yang sudah dipilih
                objects = classifier.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                
                for (x, y, w, h) in objects:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        # Bagian ini akan selalu dijalankan, bahkan saat streaming berhenti
        # Ini memastikan kamera selalu dimatikan dengan benar
        print("Melepaskan kamera...")
        camera.release()

@app.route('/')
def index():
    return render_template('index.html')

# RUTE BARU UNTUK MENAMPILKAN PLACEHOLDER
@app.route('/placeholder/<program_name>')
def placeholder(program_name):
    line1 = "This program is not available yet."
    line2 = "Stay tuned for updates!"
    return Response(generate_placeholder(line1, line2), mimetype='multipart/x-mixed-replace; boundary=frame')

# Rute video feed sekarang dinamis, menerima nama model dari URL
@app.route('/video_feed/<model_name>')
def video_feed(model_name):
    return Response(generate_frames(model_name), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)