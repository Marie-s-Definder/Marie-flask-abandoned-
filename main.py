from flask import Flask, request
from detect_project import yolov8m
from bottomReal import Bottom
from meter_single import Meter
from PIL import Image, ImageDraw, ImageFont
import numpy as np
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
    '''发送时候的url最好处理后发给flask，原路径保存'''
    base = r'F:\CODE\project\marie-definder\mariee-api\data\snapshots'
    url = base +'\\'+ data.get('url')
    # url = data.get('url')
    data = data.get('data')
    # 读取图片
    pic = None
    try:
        pic = cv2.imread(url)
    except:
        return "Wrong Url"
    # 将要保存的图片url-需要修改
    savingurl = datetime.datetime.now().strftime('%Y%m%d%H%M%S') +'-result.jpg'# 结尾必须是.jpg
    returndata = {"url":savingurl}
    rowHeight, rowWidth, _ = pic.shape

    dataList = []
    for item in data:
        dataa = {}
        dataa['id'] = item['id']
        if item['type'] == 'buttom':
            image, Width, Height = slide(pic, item['location'])
            # 获取按钮状态
            result, flag = BottomDet.decter(image)
            dataa['result'] = str(result)
            # 获取时间戳
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dataa['time'] = timestamp
            # 获取状态
            
            if flag>=int(item['lowerLimit']) and flag<=int(item['upperLimit']):
                status = 0
            else:
                status = 1
            dataa['status'] = status
            # 画图
            # location, status, text
            pic = boxdraw(pic, [int(x) for x in item['location'].split(',')], status, f"结果：{str(result)}，状态：{'正常' if status==0 else '异常'}")

        # 表识别
        elif item['type'] == 'meter':
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
            
            pic = boxdraw(pic, [int(x) for x in item['location'].split(',')], status, f"结果:{str(result)}{item['unit']},状态:{'正常' if status==0 else '异常'}")

        # 灯识别，比较特殊
        elif item['type'] == 'light':
            Id = dataa['id']
            # image, Width, Height = slide(pic, item['location'])
            image = pic
            # 获取6个结果
            one = [int(x) for x in item['preset_boxes1'].split(',')]
            two = [int(x) for x in item['preset_boxes2'].split(',')]
            three = [int(x) for x in item['preset_boxes3'].split(',')]
            four = [int(x) for x in item['preset_boxes4'].split(',')]
            five =[int(x) for x in item['preset_boxes5'].split(',')]
            six = [int(x) for x in item['preset_boxes6'].split(',')]
            thebox = [one, two, three, four, five, six]
            results, draw_boxes = yolov8m(image, preset_boxes=thebox)
            # 获取时间戳
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #
            '''
                结果需要如下：
                上界000001
                下界000001
            '''
            for index, (result, box2draw) in enumerate(zip(results, draw_boxes)):
                result = '1' if result else '0' # True为1，反之为0
                normalvalue = ''.join(item['upperLimit'])
                status = 0 if normalvalue[index]==result else 1 # True为1，反之为0

                # 加入列表
                dataList.append({'id':Id+index,\
                                 "time": timestamp,\
                                 "result": result,\
                                 "status": status})# 跟上界不一样就直接判定为错
                
                # 直接画图
                # pic = boxdraw(pic, box2draw, status, f"结果：{str(result)}，状态：{'正常' if status==0 else '异常'}")
                
                pic = boxdraw(pic, box2draw, status, f"结果:{'亮' if result=='1' else '灭'},状态:{'正常' if status==0 else '异常'}")
            
            continue

        # iot直接画图
        elif item['type'] == 'iot':
            # 先画图，然后直接下一轮
            rowHeight -= 80
            pic = paddingdraw(pic,f"{item['deviceNname']} (IOT) :{item['value']}{item['unit']}",(0,rowHeight))
            continue
        else:
            # 说明type有问题
            return f"Wrong Type with id == {item['id']}"
        # 每轮循环都需要加入列表
        dataList.append(dataa)
    # padding
    # pic = cv2.copyMakeBorder(pic, 50, 50, 0, 0, cv2.BORDER_CONSTANT, value=(150, 150, 150))
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rowHeight -= 80
    pic = paddingdraw(pic, f"拍摄时间：{str(timestamp)}",(0,rowHeight))
    cv2.imwrite(savingurl, pic)
    # 将data加入json
    returndata['data'] = dataList
    # 返回消息
    json_result = json.dumps(returndata)
    return json_result, 200, {'Content-Type': 'application/json'}

# 抠图
def slide(image,location):
    
    xl,yl,xb,yb = [int(x) for x in location.split(',')]
    # print(image)
    # print(xl,yl,xb,yb)
    return image[yl:yb,xl:xb], xb-xl, yb-yl

# 画框写字
def boxdraw(img, location, status, text):
    start_point = (location[0], location[1])  # 左上角坐标 (x, y)
    end_point = (location[2], location[3])  # 右下角坐标 (x, y)
    # 定义矩形的颜色，BGR 格式
    color = (0, 255, 0)
    textcolor = color
    # 异常为红色, 包括文本颜色
    if status == 1:
        color = (0, 0, 255)  # 蓝色，格式为 (blue, green, red)
        textcolor = (255, 0, 0)
    # 定义矩形的线条宽度
    thickness = 3
    # 在图像上绘制矩形
    # print(start_point, end_point)
    cv2.rectangle(img, start_point, end_point, color, thickness)
    # 文本左下角坐标
    nopaddingy = 100
    nopaddingx = 50
    if location[1] <= 30:
        nopaddingy = -80
        nopaddingx= -50
    org = (start_point[0] - nopaddingx, start_point[1] - nopaddingy)  
    # 定义字体和字号
    # 定义文本粗细
    # 在图像上绘制文本
    return cv2AddChineseText(img, text, org, textcolor,textSize=70)
    # return cv2.putText(img, text, org, font, font_scale, color, thickness)


def cv2AddChineseText(img, text, position, textColor=(0, 255, 0), textSize=0):
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

# 左下角写字
def paddingdraw(img,text,org):
    # color = (255, 255, 255)
    color = (0, 0, 255)
    # 在图像上绘制文本
    return cv2AddChineseText(img, text, org, color,textSize=70)


if __name__ == '__main__':
    app.run(debug=True)
