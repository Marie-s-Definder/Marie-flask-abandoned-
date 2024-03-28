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
    savingurl = url+'ppp'
    returndata = {"url":savingurl}
    for item in data:
        if item['item'] == 'buttom':
            pass
        elif item['item'] == 'light':
            pass
        elif item['item'] == 'meter':
            meterDet
            pass
        elif item['item'] == 'iot':
            pass
        else:
            return "Wrong Type"
    return f'Hello, {url}!'

def slide(image,xl,yl,xb,yb):
    return image[xl:xb,yl:yb]


if __name__ == '__main__':
    app.run(debug=True)
