from flask import Flask, request
from detect_project import yolov8m
from bottomReal import Bottom
from meter_single import Meter

import cv2
BottomDet = Bottom()
meterDet  = Meter()
app = Flask(__name__)

@app.route('/Recognition', methods=['POST'])
def Recognition():
    data = request.json
    url = data.get('url')
    data = data.get('data')
    try:
        pic = cv2.imread(url)
    except:
        return "Wrong Url"

    for item in data:
        print(data[0])
    return f'Hello, {url}!'

def slide(image,xl,yl,xb,yb):
    return image[xl:xb, yl:yb]


if __name__ == '__main__':
    app.run(debug=True)
