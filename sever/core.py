import json
import webbrowser
from flask import Flask, request, Response
from flask_cors import CORS
from ultralytics import YOLO
from waitress import serve
from PIL import Image

app = Flask(__name__)
CORS(app)  # Bật CORS cho toàn bộ ứng dụng

model = YOLO("10epoch.pt")


@app.route("/")
def root():
    with open("index.html") as file:
        return file.read()


@app.route("/detect", methods=["POST"])
def detect():
    # Kiểm tra xem có file được gửi không
    if 'image_file' not in request.files:
        return Response(json.dumps({"error": "No file part"}), status=400, mimetype='application/json')

    buf = request.files["image_file"]

    # Kiểm tra xem file có rỗng không
    if buf.filename == '':
        return Response(json.dumps({"error": "No selected file"}), status=400, mimetype='application/json')

    try:
        # Đọc và xử lý hình ảnh
        image = Image.open(buf.stream)
        boxes = detect_objects_on_image(image)
        return Response(json.dumps(boxes), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


def detect_objects_on_image(image):
    results = model.predict(image)
    result = results[0]
    output = []
    for box in result.boxes:
        x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
        class_id = box.cls[0].item()
        prob = round(box.conf[0].item(), 2)
        output.append([x1, y1, x2, y2, result.names[class_id], prob])
    return output


# Mở trình duyệt với trang chủ
# webbrowser.open('http://localhost:8080')
serve(app, host='0.0.0.0', port=8080)
