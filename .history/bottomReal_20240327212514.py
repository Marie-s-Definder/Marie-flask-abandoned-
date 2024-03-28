from random import sample
import cv2
import numpy as np
import random
import math
import datetime
pname, ptype = 0, 0

class Bottom():
    def __init__(self):
        self.pic = None
        
    def angle(self, v1, v2):
        dx1 = v1[2] - v1[0]
        dy1 = v1[3] - v1[1]
        dx2 = v2[2] - v2[0]
        dy2 = v2[3] - v2[1]
        angle1 = math.atan2(dy1, dx1)
        angle1 = angle1 * 180 / math.pi

        print('angle1',angle1)
        angle2 = math.atan2(dy2, dx2)
        angle2 = angle2 * 180 / math.pi
        print('angle2',angle2)
        if angle1 * angle2 >= 0:
            if angle2<=0 and  angle2>=-90:
                included_angle =abs(angle1 - angle2)
            else:
                included_angle = 360-abs(angle1 - angle2)
        else:
            included_angle = abs(angle1) + abs(angle2)
        return included_angle


    def cut_pic(self, image):
        """
        :param pyrMeanShiftFiltering(input, 10, 100) 均值滤波
        :param 霍夫概率圆检测
        :param mask操作提取圆
        :return: 半径，圆心位置

        """
        # 均值漂移滤波
        dst = cv2.pyrMeanShiftFiltering(image, 10, 100)
        # 转换成灰度图
        cimage = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        # 霍夫圆检测
        circles = cv2.HoughCircles(cimage, cv2.HOUGH_GRADIENT, 1, 80, param1=100, param2=20, minRadius=80, maxRadius=0)
        circles = np.uint16(np.around(circles))  # 把类型换成整数
        r_1 = circles[0, 0, 2]
        c_x = circles[0, 0, 0]
        c_y = circles[0, 0, 1]
        # print(input.shape[:2])
        circle = np.ones(image.shape, dtype="uint8")
        circle = circle * 255
        # 画一个圆
        cv2.circle(circle, (c_x, c_y), int(r_1), 0, -1)
        # 按位或，在原始图片中圈出一个圆
        bitwiseOr = cv2.bitwise_or(image, circle)
        cv2.imwrite(pname + '_resize' + ptype, bitwiseOr)
        ninfo = [r_1, c_x, c_y]
        return ninfo


    def linecontours(self, cp_info):
        """
        :funtion : 提取刻度线，指针
        :param a: 高斯滤波 GaussianBlur，自适应二值化adaptiveThreshold，闭运算
        :param b: 轮廓寻找 findContours，
        :return:kb,new_needleset
        """
        r_1, c_x, c_y = cp_info
        img = cv2.imread(pname + '_resize' + ptype)
        # 高斯滤波
        img = cv2.GaussianBlur(img, (3, 3), 0)
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(~gray, 255,
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
        # 闭运算
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=1)
        circle = np.zeros(binary.shape, dtype="uint8")
        cv2.circle(circle, (c_x, c_y), int(r_1 * 0.8), 255, -1)
        mask = cv2.bitwise_and(binary, circle)
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 100, minLineLength=int(r_1 / 3), maxLineGap=2)
        nmask = np.zeros(binary.shape, np.uint8)

        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(nmask, (x1, y1), (x2, y2), 100, 1, cv2.LINE_AA)
        nmask = cv2.erode(nmask, kernel, iterations=1)
        cnts, _ = cv2.findContours(nmask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        areass = [cv2.contourArea(x) for x in cnts]
        # print(len(areass))
        i = areass.index(max(areass))
        cnt = cnts[i]
        output = cv2.fitLine(cnt, 2, 0, 0.001, 0.001)
        k = output[1] / output[0]
        k = round(k[0], 2)
        b = output[3] - k * output[2]
        b = round(b[0], 2)
        y1 = int(k * x1 + b)
        y2 = int(k * x2 + b)
        cv2.line(img, (x1, y1), (x2, y2), (0, 23, 255), 1, cv2.LINE_AA)
        return x1, x2, y1, y2

    def needle(self, path, img, r, cx, cy, x0, y0):
        oimg = cv2.imread(path)
        circle = np.zeros(img.shape, dtype="uint8")
        cv2.circle(circle, (cx, cy), int(r), 255, -1)
        mask = cv2.bitwise_and(img, circle)

        kernel = np.ones((4, 4), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)

        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 100, minLineLength=int(r / 3), maxLineGap=2)
        nmask = np.zeros(img.shape, np.uint8)
        # lines = mential.findline(self=0, cp=[x, y], lines=lines)
        # print('lens', len(lines))

        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(nmask, (x1, y1), (x2, y2), 100, 1, cv2.LINE_AA)

        x1, y1, x2, y2 = lines[0][0]
        d1 = (x1 - cx) ** 2 + (y1 - cy) ** 2
        d2 = (x2 - cx) ** 2 + (y2 - cy) ** 2
        if d1 > d2:
            axit = [x1, y1]
        else:
            axit = [x2, y2]
        nmask = cv2.erode(nmask, kernel, iterations=1)
        cnts, hier = cv2.findContours(nmask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        areass = [cv2.contourArea(x) for x in cnts]
        i = areass.index(max(areass))
        cnt = cnts[i]
        output = cv2.fitLine(cnt, 2, 0, 0.001, 0.001)
        k = output[1] / output[0]
        k = round(k[0], 2)
        b = output[3] - k * output[2]
        b = round(b[0], 2)
        x1 = cx
        x2 = axit[0]
        y1 = int(k * x1 + b)
        y2 = int(k * x2 + b)
        cv2.line(oimg, (x1, y1), (x2, y2), (0, 23, 255), 1, cv2.LINE_AA)
        cv2.line(oimg, (x1, y1), (x0,y0), (0, 23, 255), 1, cv2.LINE_AA)
        print(pname +'_fin'+ ptype)
        cv2.imwrite(pname +'_fin'+ ptype,oimg)
        return x1, y1, x2, y2
    
    def angle_with_horizontal(self, line):
        x1, y1, x2, y2 = line
        angle_rad = np.arctan2(y1 - y2, x1 - x2)
        angle_deg = np.degrees(angle_rad)
        return angle_deg


    def decter(self, path, outpath):
        global pname, ptype
        pname, ptype = path.split('.')
        ptype = '.' + ptype
        pname = outpath+'/'+pname.split('/')[-1]
        start = datetime.datetime.now()
        # 霍夫圆的圆心位置和半径
        image = cv2.imread(path)
        ninfo = self.cut_pic(image)  # 2.截取表盘
        x1, x2, y1, y2 = self.linecontours(ninfo)  # 提取刻度线、指针
        OZ = [x1, x2, y1, y2]
        angle1 = self.angle_with_horizontal(OZ)
        print("与水平线的夹角：", angle1)
        end = datetime.datetime.now()
        print(end - start)
        cv2.waitKey(1)
        if angle1 > 0 and angle1 < 77:
            return "自动"
        if angle1 > 77 and angle1 < 112:
            return "停"
        if angle1 > 112:
            return "手动"
if __name__=="__main__":
    # 输入文件夹
    inputpath='kkl.jpg'
    # 输出文件夹
    outputpath='output'
    aa = Bottom()
    status = aa.decter(inputpath, outputpath)
    print("检测结果：", status)


