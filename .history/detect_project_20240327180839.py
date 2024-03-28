from ultralytics import YOLO
import math

# Load a model
# model = YOLO('/root/autodl-tmp/yolov8/ultralytics/models/v8/yolov8m-IAT.yaml') # build a new model from scratch
model = YOLO('yolov8m.pt')  # load a pretrained model (recommended for training)
# model = YOLO('/root/autodl-tmp/yolov8/ultralytics/models/v8/yolov8m-enhance.yaml').load('/root/autodl-tmp/yolov8/yolov8m.pt')
# Use the model
source="best.jpg"
detections = model.predict(source=source, save=True)  # train the model
# print(detections)
# print('yes')

output = [True, True, True, True, True, False]

preset_boxes = [[10, 10, 100, 100],  # 预置框1，左上角坐标 (10, 10)，右下角坐标 (100, 100)
    [150, 50, 250, 150],  # 预置框2，左上角坐标 (150, 50)，右下角坐标 (250, 150)
    [300, 200, 400, 300],  # 预置框3，左上角坐标 (300, 200)，右下角坐标 (400, 300)
    [50, 300, 150, 400],  # 预置框4，左上角坐标 (50, 300)，右下角坐标 (150, 400)
    [200, 100, 300, 200],  # 预置框5，左上角坐标 (200, 100)，右下角坐标 (300, 200)
    [350, 50, 450, 150]  # 预置框6，左上角坐标 (350, 50)，右下角坐标 (450, 150)
]

# 定义匹配阈值
threshold = 300  # 这个阈值需要根据具体情况进行调整
# print(detections[0].boxes)
print(len(detections))

for i, preset_box in enumerate(preset_boxes):
    
    # 计算预置框的中心点坐标
    preset_center_x = (preset_box[0] + preset_box[2]) / 2
    preset_center_y = (preset_box[1] + preset_box[3]) / 2

    for detection_box in detections[0].boxes:
        
        # 计算检测结果框的中心点坐标
        detection_box = detection_box.boxes
        detection_box = detection_box.squeeze()
        detection_center_x = (detection_box[0] + detection_box[2]) / 2
        detection_center_y = (detection_box[1] + detection_box[3]) / 2

        # 计算中心点之间的距离
        distance = math.sqrt((detection_center_x - preset_center_x) ** 2 + (detection_center_y - preset_center_y) ** 2)

        # 如果距离小于阈值，则认为是匹配的框
        if distance < threshold:
            output[i] = not output[i]

# 输出匹配结果数组
print(output)
