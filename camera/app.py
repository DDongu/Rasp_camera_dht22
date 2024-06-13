import io
import logging
import json
import time
from threading import Condition
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import adafruit_dht
import board
from flask import Flask, Response, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variables for storing DHT data
dht_json = {}

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

output = StreamingOutput()
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1280, 960)}))
picam2.start_recording(JpegEncoder(), FileOutput(output))

def check_dht():
    global dht_json
    pin = board.D7
    dhtDevice = adafruit_dht.DHT22(pin, use_pulseio=False)
    dht_data = []
    sum_temp, sum_hum = 0, 0
    err_chk = 0
    CHECK_NUM = 1

    while(len(dht_data) < CHECK_NUM):
        if err_chk > 20:
            print("Error: Something Error at DHT22!")
            break
        err_chk += 1
        try:
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            if temperature is not None or humidity is not None:
                dht_data.append([temperature, humidity])
            print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
            time.sleep(1)
        except RuntimeError as error:
            print(error.args[0])


    dht_json = {
        'temperature': temperature,
        'humidity': humidity
    }

    # Clean up resources
    dhtDevice.exit()

@app.route('/')
def index():
    return """
    <html>
    <head>
    <title>picamera2 MJPEG streaming demo</title>
    <script>
    function captureImage() {
        fetch('/capture', { method: 'GET' });
    }
    function getImage() {
        window.open('/get_image', '_blank');
    }
    </script>
    </head>
    <body>
    <h1>Picamera2 MJPEG Streaming Demo</h1>
    <img src="stream.mjpg" width="640" height="480" />
    <button onclick="captureImage()">Capture</button>
    <button onclick="getImage()">Check Image</button>
    </body>
    </html>
    """

@app.route('/stream.mjpg')
def stream_mjpg():
    picam2.start_recording(JpegEncoder(), FileOutput(output))
    def generate():
        while True:
            with output.condition:
                output.condition.wait()
                frame = output.frame
            yield (b'--FRAME\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=FRAME')

@app.route('/capture')
def capture():
    picam2.start()
    time.sleep(2)  # 이미지가 완전히 촬영되도록 충분한 시간 대기
    image_data = output.frame  # 촬영된 이미지 데이터 가져오기
    picam2.stop()
    return Response(image_data, mimetype='image/jpeg')

@app.route('/check_dht')
def check_dht_route():
    check_dht()
    return jsonify(dht_json)

@app.route('/get_image')
def get_image():
    try:
        return send_file("image/image.jpg", mimetype='image/jpeg')
    except FileNotFoundError:
        return 'Image not found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

