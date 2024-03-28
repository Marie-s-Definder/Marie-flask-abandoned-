from flask import Flask, request
from detect_project import yolov8m
from bottomReal import Bottom
from meter_single import Meter
import datetime
import json

import cv2
BottomDet = Bottom()
meterDet  = Meter()
app = Flask(__name__)

@app.route('/Recognition', methods=['POST'])
def Recognition():
    # 从POST读取数据
    data = request.json
    url = data.get('url')
    data = data.get('data')
    # 读取图片
    try:
        pic = cv2.imread(url)
    except:
        return "Wrong Url"
    # 将要保存的图片url-需要修改
    savingurl = url+'ppp'
    returndata = {"url":savingurl}

    dataList = []
    for item in data:
        dataa = {}
        dataa['id'] = item['id']
        if item['item'] == 'buttom':
            image = slide(pic, item['location'])
            # 获取按钮状态
            result = BottomDet.decter(image)
            dataa['result'] = str(result)
            # 获取时间戳
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dataa['time'] = timestamp
            # 获取状态
            if ang>=int(item['lowerLimit']) and ang<=int(item['upperLimit']):
                status = 0
            else:
                status = 1
            dataa['status'] = status
            # 画图

        # 表识别
        elif item['item'] == 'meter':
            image = slide(pic, item['location'])
            # 获取角度
            ang = meterDet.decter(image, item['zeroPoint'])
            dataa['result'] = str(ang)
            # 获取时间戳
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dataa['time'] = timestamp
            # 获取状态
            if ang>=int(item['lowerLimit']) and ang<=int(item['upperLimit']):
                status = 0
            else:
                status = 1
            dataa['status'] = status
            # 画图

        # 灯识别，比较特殊
        elif item['item'] == 'light':
            pass

        # iot直接画图
        elif item['item'] == 'iot':
            # 先画图，然后直接下一轮

            continue
        else:
            # 说明type有问题
            return f"Wrong Type with id == {item['id']}"
        # 每轮循环都需要加入列表
        dataList.append(dataa)

    # 将data加入json
    returndata['data'] = dataList
    # 返回消息
    json_result = json.dumps(returndata)
    return json_result, 200, {'Content-Type': 'application/json'}

def slide(image,xl,yl,xb,yb):
    return image[xl:xb,yl:yb]


if __name__ == '__main__':
    app.run(debug=True)
