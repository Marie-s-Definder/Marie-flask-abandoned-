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
    pic = None
    try:
        pic = cv2.imread(url)
    except:
        return "Wrong Url"
    # 将要保存的图片url-需要修改
    savingurl = url[:-4]+'_re.jpg'# 结尾必须是.jpg
    returndata = {"url":savingurl}
    rowHeight, rowWidth, _ = pic.shape


    dataList = []
    for item in data:
        dataa = {}
        dataa['id'] = item['id']
        if item['item'] == 'buttom':
            image, Width, Height = slide(pic, item['location'])
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
            image, Width, Height = slide(pic, item['location'])
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
            Id = dataa['id']
            image, Width, Height = slide(pic, item['location'])
            # 获取6个结果
            results, draw_boxes = yolov8m(image, preset_boxes=item['preset_boxes'])# 需要框输出，明天看看
            # 获取时间戳
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            '''
                结果需要如下：
                上界000001
                下界000001
            '''
            for index, (result, box2draw) in enumerate(zip(results, draw_boxes)):
                dataList.append({'id':Id+index,\
                                 "time": timestamp,\
                                 "result": result,\
                                 "status": 0 if item['upperLimit'][index]==result else 1})# 跟上界不一样就直接判定为错
                
            # 直接画图
                
            continue

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

# 抠图
def slide(image,location):
    xl,yl,xb,yb = location
    return image[xl:xb,yl:yb], xb-xl, yb-yl

# 画框写字
def boxdraw():
    pass

# 左下角写字
def paddingdraw():
    pass


if __name__ == '__main__':
    app.run(debug=True)
