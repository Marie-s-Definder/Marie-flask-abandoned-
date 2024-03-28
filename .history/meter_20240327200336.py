from random import sample
import cv2
import numpy as np
import random
import math
import datetime
# pname, ptype = 0, 0

class Meter():
    def __init__(self):
        self.Pic = None
        self.cc = None
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


    def cut_pic(self):
        """
        :param pyrMeanShiftFiltering(input, 10, 100) 均值滤波
        :param 霍夫概率圆检测
        :param mask操作提取圆
        :return: 半径，圆心位置

        """
        
        # 均值漂移滤波
        dst = cv2.pyrMeanShiftFiltering(self.Pic, 10, 100)
        # 转换成灰度图
        cimage = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        # 霍夫圆检测
        circles = cv2.HoughCircles(cimage, cv2.HOUGH_GRADIENT, 1, 80, param1=100, param2=20, minRadius=80, maxRadius=0)
        circles = np.uint16(np.around(circles))  # 把类型换成整数
        r_1 = circles[0, 0, 2]
        c_x = circles[0, 0, 0]
        c_y = circles[0, 0, 1]
        # print(input.shape[:2])
        circle = np.ones(self.Pic.shape, dtype="uint8")
        circle = circle * 255
        # 画一个圆
        cv2.circle(circle, (c_x, c_y), int(r_1), 0, -1)
        # 按位或，在原始图片中圈出一个圆
        self.cc = cv2.bitwise_or(self.Pic, circle)
        cv2.imwrite(self.pname + '_resize' + self.ptype, self.cc)
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
        original_image = self.cc
        self.cc = cv2.imread(self.pname + '_resize' + self.ptype)
        saved_image = self.cc
        # print(self.cc == img)
        # 高斯滤波
        self.cc = cv2.GaussianBlur(self.cc, (3, 3), 0)


        if original_image.shape == saved_image.shape:
            difference = cv2.subtract(original_image, saved_image)
            b, g, r = cv2.split(difference)
            print(cv2.countNonZero(b))

            # 如果所有通道的差异都为零，则图像相同
            if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                print("图像没有变化")
            else:
                print("图像有变化")
        else:
            print("图像尺寸不同")

        num_channels = saved_image.shape[2]

        # # 检查通道顺序
        # if num_channels == 3:
        #     channel_order = "BGR"  # OpenCV默认的通道顺序是BGR
        # elif num_channels == 4:
        #     channel_order = "BGRA"  # 有时候会有alpha通道，即RGBA
        # else:
        #     channel_order = "Unknown"

        # print("图像通道顺序:", channel_order)
        

        # 转换为灰度图
        gray = cv2.cvtColor(self.cc, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('kk.jpg',self.cc)
        
        binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
        # 闭运算
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=1)
        circle = np.zeros(binary.shape, dtype="uint8")
        cv2.circle(circle, (c_x, c_y), int(r_1 * 0.8), 255, -1)
        mask = cv2.bitwise_and(binary, circle)
        # contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 100, minLineLength=int(r_1 / 3), maxLineGap=2)
        nmask = np.zeros(binary.shape, np.uint8)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(nmask, (x1, y1), (x2, y2), 100, 1, cv2.LINE_AA)
        nmask = cv2.erode(nmask, kernel, iterations=1)
        cnts, _ = cv2.findContours(nmask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        areass = [cv2.contourArea(x) for x in cnts]
        i = areass.index(max(areass))
        cnt = cnts[i]
        output = cv2.fitLine(cnt, 2, 0, 0.001, 0.001)
        k = output[1] / output[0]
        k = round(k[0], 2)
        b = output[3] - k * output[2]
        b = round(b[0], 2)
        y1 = int(k * x1 + b)
        y2 = int(k * x2 + b)
        cv2.line(self.cc, (x1, y1), (x2, y2), (0, 23, 255), 1, cv2.LINE_AA)
        
        return x1, x2, y1, y2

    def countpoint(self, pointlist,path):
        img = cv2.imread(path, 0)
        h, w = img.shape
        pic_list = np.zeros((h, w))
        for point in pointlist:
            x, y = point
            if x < w and y < h:
                pic_list[y][x] += 1
        cc = np.where(pic_list == np.max(pic_list))
        y, x = cc
        # 这里直接选取点集中频率最高的第一个，可以优化的
        cc = (x[0], y[0])
        cv2.circle(img, cc, 2, (32, 3, 240), 3)
        cv2.imwrite(self.pname + '_center_point' + self.ptype, img)
        return cc

    def angle_with_horizontal(self, line):
        x1, y1, x2, y2 = line
        angle_rad = np.arctan2(y1 - y2, x1 - x2)
        angle_deg = np.degrees(angle_rad)
        return angle_deg


    def decter(self, path, outpath):
        # global pname, ptype
        self.pname, self.ptype = path.split('.')
        self.ptype = '.' + self.ptype
        self.pname = outpath+'/'+self.pname.split('/')[-1]
        start = datetime.datetime.now()
        # 霍夫圆的圆心位置和半径
        self.Pic = cv2.imread(path)
        ninfo = self.cut_pic()  # 2.截取表盘
        x1, x2, y1, y2 = self.linecontours(ninfo)  # 提取刻度线、指针
        OZ = [x1, x2, y1, y2]
        angle1 = self.angle_with_horizontal(OZ)
        print("与水平线的夹角：", angle1)
        end = datetime.datetime.now()
        print(end - start)
        if angle1 > 0 and angle1 < 77:
            return "自动"
        if angle1 > 77 and angle1 < 112:
            return "停"
        if angle1 > 112:
            return "手动"
if __name__=="__main__":
    # 输入文件夹
    inputpath='meter.jpg'
    # 输出文件夹
    outputpath='output'

    pic = Meter()

    status = pic.decter(inputpath, outputpath)
    print("检测结果：", status)


