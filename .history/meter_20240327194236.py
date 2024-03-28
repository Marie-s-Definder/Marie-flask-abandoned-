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
        self.Pic = cv2.bitwise_or(self.Pic, circle)
        # cv2.imwrite(self.pname + '_resize' + self.ptype, bitwiseOr)
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
        img = self.Pic
        # 高斯滤波
        img = cv2.GaussianBlur(img, (3, 3), 0)
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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
        cv2.line(img, (x1, y1), (x2, y2), (0, 23, 255), 1, cv2.LINE_AA)
        return x1, x2, y1, y2

    def needle(self, path, img, r, cx, cy, x0, y0):
        oimg = self.Pic
        circle = np.zeros(img.shape, dtype="uint8")
        cv2.circle(circle, (cx, cy), int(r), 255, -1)
        mask = cv2.bitwise_and(img, circle)
        kernel = np.ones((4, 4), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 100, minLineLength=int(r / 3), maxLineGap=2)
        nmask = np.zeros(img.shape, np.uint8)
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
        # print(len(areass))
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
        print(self.pname +'_fin'+ self.ptype)
        cv2.imwrite(self.pname +'_fin'+ self.ptype,oimg)
        return x1, y1, x2, y2


    # def findpoint(self, kb,path):
    #     img = cv2.imread(path)
    #     w, h, c = img.shape
    #     point_list = []
    #     if len(kb) > 2:
    #         # print(len(kb))
    #         random.shuffle(kb)
    #         lkb = int(len(kb) / 2)
    #         kb1 = kb[0:lkb]
    #         kb2 = kb[lkb:(2 * lkb)]
    #         print('len', len(kb1), len(kb2))
    #         kb1sample = sample(kb1, int(len(kb1) / 1))
    #         kb2sample = sample(kb2, int(len(kb2) / 1))
    #     else:
    #         kb1sample = kb[0]
    #         kb2sample = kb[1]

    #     for i, wx in enumerate(kb1sample):
    #         for wy in kb2sample:
    #             k1, b1 = wx
    #             k2, b2 = wy
    #             try:
    #                 if (b2 - b1) == 0:
    #                     b2 = b2 - 0.1
    #                 if (k1 - k2) == 0:
    #                     k1 = k1 - 0.1
    #                 x = (b2 - b1) / (k1 - k2)
    #                 y = k1 * x + b1
    #                 x = int(round(x))
    #                 y = int(round(y))
    #             except:
    #                 x = (b2 - b1 - 0.01) / (k1 - k2 + 0.01)
    #                 y = k1 * x + b1
    #                 x = int(round(x))
    #                 y = int(round(y))
    #             # x,y=solve_point(k1, b1, k2, b2)
    #             if x < 0 or y < 0 or x > w or y > h:
    #                 break
    #             point_list.append([x, y])
    #             cv2.circle(img, (x, y), 2, (122, 22, 0), 2)
    #     if len(kb) > 2:
    #         cv2.imwrite(self.pname + '_pointset' + self.ptype, img)
    #     return point_list


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


