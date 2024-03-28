from random import sample
import cv2
import numpy as np
import random
from sympy import *
import math
import datetime

pname, ptype = 0, 0

class mential():
    def __init__(self):
        pass
        
    def get_max_point(self, cnt):
        lmost = tuple(cnt[cnt[:, :, 0].argmin()][0])
        rmost = tuple(cnt[cnt[:, :, 0].argmax()][0])
        tmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
        bmost = tuple(cnt[cnt[:, :, 1].argmax()][0])
        pmost = [lmost, rmost, tmost, bmost]
        return pmost

    def distance(self, pmost, centerpoint):
        cx, cy = centerpoint
        distantion = []
        for point in pmost:
            dx, dy = point
            distantion.append((cx - dx) ** 2 + (cy - dy) ** 2)
        index_of_max = distantion.index((max(distantion)))
        return index_of_max

    def ds_ofpoint(self, a, b):
        x1, y1 = a
        x2, y2 = b
        distances = int(sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
        return distances

    def findline(self, cp, lines):
        x, y = cp
        cntareas = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            aa = sqrt(min((x1 - x) ** 2 + (y1 - x) ** 2, (x2 - x) ** 2 + (y2 - x) ** 2))
            if (aa < 50):
                cntareas.append(line)
        print(cntareas)
        return cntareas


def angle(v1, v2):
    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]
    dx2 = v2[2] - v2[0]
    dy2 = v2[3] - v2[1]
    angle1 = math.atan2(dy1, dx1)
    angle1 = angle1 * 180 / math.pi

    print('angle1', angle1)
    angle2 = math.atan2(dy2, dx2)
    angle2 = angle2 * 180 / math.pi
    print('angle2', angle2)
    if angle1 * angle2 >= 0:
        if angle2<=0 and  angle2>=-90:
            included_angle =abs(angle1 - angle2)
        else:
            included_angle = 360-abs(angle1 - angle2)
    else:
        included_angle = abs(angle1) + abs(angle2)
        # if included_angle > 180:
        #     included_angle = 360 - included_angle
    return included_angle


def get_mode(arr):
    while 0 in arr:
        arr.remove(0)
    mode = []
    arr_appear = dict((a, arr.count(a)) for a in arr)  # 统计各个元素出现的次数
    if max(arr_appear.values()) == 1:  # 如果最大的出现为1
        arrs = np.array(arr)
        oo = np.median(arrs)
        return oo
    else:
        for k, v in arr_appear.items():  # 否则，出现次数最大的数字，就是众数
            if v == max(arr_appear.values()):
                mode.append(k)
    return mode


def remove_diff(deg):
    """
    :funtion :
    :param b:
    :param c:
    :return:
    """
    if (True):
        # new_nums = list(set(deg)) #剔除重复元素
        mean = np.mean(deg)
        var = np.var(deg)
        # print("原始数据共", len(deg), "个\n", deg)
        '''
        for i in range(len(deg)):
            print(deg[i],'→',(deg[i] - mean)/var)
            #另一个思路，先归一化，即标准正态化，再利用3σ原则剔除异常数据，反归一化即可还原数据
        '''
        # print("中位数:",np.median(deg))
        percentile = np.percentile(deg, (25, 50, 75), method='midpoint')
        # print("分位数：", percentile)
        # 以下为箱线图的五个特征值
        Q1 = percentile[0]  # 上四分位数
        Q3 = percentile[2]  # 下四分位数
        IQR = Q3 - Q1  # 四分位距
        ulim = Q3 + 2.5 * IQR  # 上限 非异常范围内的最大值
        llim = Q1 - 1.5 * IQR  # 下限 非异常范围内的最小值

        new_deg = []
        uplim = []
        for i in range(len(deg)):
            if (llim < deg[i] and deg[i] < ulim):
                new_deg.append(deg[i])
        # print("清洗后数据共", len(new_deg), "个\n", new_deg)
    new_deg = np.mean(new_deg)

    return new_deg
    # 图表表达


flag = 0
p0 = 0


# 选取零点
def markzero(path):
    img = cv2.imread(path)


    def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
        global flag, p0
        if event == cv2.EVENT_LBUTTONDOWN:
            xy = "%d,%d" % (x, y)
            p0 = [x, y]
            print(x, y)
            cv2.circle(img, (x, y), 2, (0, 0, 255), thickness=-1)
            cv2.putText(img, '*0*', (x - 30, y), 1,
                        2.0, (0, 0, 0), thickness=2)
            # cv2.imshow("image", img)

        elif event == cv2.EVENT_LBUTTONUP:  # 鼠标左键fang
            cv2.destroyWindow("image")
            print(p0)

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", on_EVENT_LBUTTONDOWN)

    cv2.imshow('image', img)
    cv2.waitKey(5000)
    return p0

def cut_pic(path):
    """
    :param pyrMeanShiftFiltering(input, 10, 100) 均值滤波
    :param 霍夫概率圆检测
    :param mask操作提取圆
    :return: 半径，圆心位置

    """
    input = cv2.imread(path)
    # 均值漂移滤波
    # dst = cv2.pyrMeanShiftFiltering(input, 10, 100)
    # 转换成灰度图
    cimage = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
    # 霍夫圆检测
    circles = cv2.HoughCircles(cimage, cv2.HOUGH_GRADIENT, 1, 80, param1=100, param2=20, minRadius=80, maxRadius=0)
    circles = np.uint16(np.around(circles))  # 把类型换成整数
    r_1 = circles[0, 0, 2]
    c_x = circles[0, 0, 0]
    c_y = circles[0, 0, 1]
    circle = np.ones(input.shape, dtype="uint8")
    circle = circle * 255
    # 画一个圆
    cv2.circle(circle, (c_x, c_y), int(r_1), 0, -1)
    # 按位或，在原始图片中圈出一个圆
    bitwiseOr = cv2.bitwise_or(input, circle)
    cv2.imwrite(pname + '_resize' + ptype, bitwiseOr)
    ninfo = [r_1, c_x, c_y]
    return ninfo


def linecontours(cp_info):
    """
    :funtion : 提取刻度线，指针
    :param a: 高斯滤波 GaussianBlur，自适应二值化adaptiveThreshold，闭运算
    :param b: 轮廓寻找 findContours，
    :return:kb,new_needleset
    """
    r_1, c_x, c_y = cp_info
    img = cv2.imread(pname + '_resize' + ptype)
    # 在输入图片上画一个实心圆
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(~gray, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -7)
    # 闭运算
    kernel = np.ones((2, 2), np.uint8)
    binary = cv2.dilate(binary, kernel, iterations=1)
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    cntset = []  # 刻度线轮廓集合
    cntareas = []  # 刻度线面积集合
    needlecnt = []  # 指针轮廓集合
    needleareas = []  # 指针面积集合
    ca = (c_x, c_y)
    incircle = [r_1 * 0.6, r_1 * 0.9]

    localtion = []  # 存放指针和中心点的距离，后面求平均之后直接用作半径
    for xx in contours:
        # 最小外接矩形
        rect = cv2.minAreaRect(xx)
        # print(rect)
        a, b, c = rect
        w, h = b
        w = int(w)
        h = int(h)
        ''' 满足条件:“长宽比例”，“面积”'''
        if h == 0 or w == 0:
            pass
        else:
            # 计算矩形中心和圆心之间的欧式距离
            dis = mential.ds_ofpoint(self=0, a=ca, b=a)

            if (incircle[0] < dis and incircle[1] > dis):
                localtion.append(dis)
                if h / w > 4 or w / h > 4:
                    cntset.append(xx)
                    cntareas.append(w * h)
            else:
                if w > r_1 / 4 or h > r_1 / 4:
                    needlecnt.append(xx)
                    needleareas.append(w * h)
    cntareas = np.array(cntareas)
    nss = remove_diff(cntareas)  # 中位数，上限区
    new_cntset = []
    # 面积
    for i, xx in enumerate(cntset):
        if (cntareas[i] <= nss * 2 and cntareas[i] >= nss * 0.65):
            new_cntset.append(xx)
    kb = []  # 拟合线集合
    for xx in new_cntset:
        rect = cv2.minAreaRect(xx)
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        cv2.polylines(img, [box], True, (0, 255, 0), 1)  # pic
        output = cv2.fitLine(xx, 2, 0, 0.001, 0.001)
        k = output[1] / output[0]
        k = round(k[0], 2)
        b = output[3] - k * output[2]
        b = round(b[0], 2)
        x1 = 1
        x2 = gray.shape[0]
        y1 = int(k * x1 + b)
        y2 = int(k * x2 + b)
        # cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
        kb.append([k, b])  # 求中心点的点集[k,b]

    ############################################################
    r = np.mean(localtion)  # 得到的半径
    mask = np.zeros(img.shape[0:2], np.uint8)
    # for cnt in needlecnt:
    #     cv2.fillConvexPoly(mask,cnt , 255)
    mask = cv2.drawContours(mask, needlecnt, -1, (255, 255, 255), -1)  # 生成掩膜
    # cv2.imshow('da', mask)

    cv2.imwrite(pname + '_scale' + ptype, img)
    cv2.imwrite(pname + '_needle' + ptype, mask)
    return kb, r, mask


def needle(path, img, r, cx, cy, x0, y0):
    oimg = cv2.imread(path)
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
    cv2.line(oimg, (x1, y1), (x0, y0), (0, 23, 255), 1, cv2.LINE_AA)
    print(pname +'_fin'+ ptype)
    cv2.imwrite(pname +'_fin'+ ptype,oimg)
    return x1, y1, x2, y2


def findpoint(kb,path):
    img = cv2.imread(path)
    w, h, c = img.shape
    point_list = []
    if len(kb) > 2:
        random.shuffle(kb)
        lkb = int(len(kb) / 2)
        kb1 = kb[0:lkb]
        kb2 = kb[lkb:(2 * lkb)]
        print('len', len(kb1), len(kb2))
        kb1sample = sample(kb1, int(len(kb1) / 1))
        kb2sample = sample(kb2, int(len(kb2) / 1))
    else:
        kb1sample = kb[0]
        kb2sample = kb[1]
    for i, wx in enumerate(kb1sample):
        for wy in kb2sample:
            k1, b1 = wx
            k2, b2 = wy
            try:
                if (b2 - b1) == 0:
                    b2 = b2 - 0.1
                if (k1 - k2) == 0:
                    k1 = k1 - 0.1
                x = (b2 - b1) / (k1 - k2)
                y = k1 * x + b1
                x = int(round(x))
                y = int(round(y))
            except:
                x = (b2 - b1 - 0.01) / (k1 - k2 + 0.01)
                y = k1 * x + b1
                x = int(round(x))
                y = int(round(y))
            if x < 0 or y < 0 or x > w or y > h:
                break
            point_list.append([x, y])
            cv2.circle(img, (x, y), 2, (122, 22, 0), 2)
    if len(kb) > 2:
        cv2.imwrite(pname + '_pointset' + ptype, img)
    return point_list


def countpoint(pointlist,path):
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
    cv2.imwrite(pname + '_center_point' + ptype, img)
    return cc


def decter(path,outpath,opoint):
    # 零点的位置坐标
    x0 = opoint[0]
    y0 = opoint[1]
    global pname, ptype
    pname, ptype = path.split('.')
    ptype = '.' + ptype
    pname = outpath+'/'+pname.split('/')[-1]
    start = datetime.datetime.now()
    # 霍夫圆的圆心位置和半径
    ninfo = cut_pic(path)  # 2.截取表盘
    kb, r, mask = linecontours(ninfo)  # 提取刻度线、指针
    # 根据刻度线的斜率和截距找到中心点的集合
    point_list = findpoint(kb, path)
    # 找到中心点坐标
    cx, cy = countpoint(point_list, path)
    # 找到指针的坐标
    da, db, dc, de = needle(path, mask, r, cx, cy, x0, y0)

    distinguish = 0.364

    OZ = [da, db, x0, y0]
    OP = [da, db, dc, de]
    ang1 = 360 - angle(OZ, OP)
    output = ang1 * distinguish
    print("AB和CD的夹角")
    print()
    # output=str(output)
    end = datetime.datetime.now()
    print(end - start)
    # cv2.waitKey(1)
    # cv2.destroyAllWindows()
    return output
if __name__=="__main__":
    # 输入文件夹
    inputpath='meter.jpg'
    # 输出文件夹
    outputpath='images'

    p0 = markzero(inputpath)
    ang1 = decter(inputpath, outputpath, p0)
    print("读数为：", ang1)