import requests
import io
from PIL import Image
import json

# /capture API에 요청을 보냅니다.
response = requests.get('http://localhost:8000/capture')

# 반환된 응답의 내용을 확인합니다.
if response.status_code == 200:
    # 응답으로부터 이미지 데이터를 추출합니다.
    image_data = b''
    json_data = b''
    content_type = b''
    boundary = b''
    for line in response.iter_lines():
        if line.startswith(b'Content-Type: '):
            content_type = line.split(b'Content-Type: ')[1].strip()
        elif line.startswith(b'--'):
            boundary = line.strip()
        elif boundary in line:
            continue
        elif line == boundary:
            continue
        elif content_type == b'image/jpeg':
            image_data += line + b'\n'
        elif content_type == b'application/json':
            json_data += line + b'\n'

    # 이미지 데이터를 파일로 저장합니다.
    with open('captured_image.jpg', 'wb') as image_file:
        image_file.write(image_data)

    # JSON 데이터를 파싱하여 확인합니다.
    if json_data:
        json_data = json.loads(json_data.decode('utf-8'))
        print("Captured JSON data:")
        print(json_data)
else:
    print("Error:", response.status_code)

