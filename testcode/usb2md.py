import time
import cv2
import os
from cnocr import CnOcr

def get_one_cap(cap_road):
    os.system('adb shell screencap -p > ' + cap_road)
    with open(cap_road, 'rb') as f:
        data = f.read()
    return data.replace(b'\r\n', b'\n')

def getCap()->None:
    cap = get_one_cap('R:/Temp/cap.png')
    with open('R:/Temp/cap.png', 'wb') as f:
        f.write(cap)

def cutImg()->None:
    img = cv2.imread("R:/Temp/cap.png")
    #print(img.shape)
    cropped = img[170:2360, 50:1000]  # 裁剪坐标为[y0:y1, x0:x1]
    cv2.imwrite("R:/Temp/cv_cut_thor.jpg", cropped)

def nextScreen()->None:
    os.system('adb shell input swipe 540 1300 540 500 100')



def titleValidator(line:dict)->bool:
    threshold = 70
    # 行高大于阈值即为标题
    hight = line["position"][3][1] - line["position"][0][1]
    if(hight >= threshold):
        return True
    else:
        return False

def headerValidator(line:dict)->bool:
    threshold = 100
    # 缩进大于阈值即为段首
    indentation = line["position"][0][0]
    if(indentation >= threshold):
        return True
    else:
        return False

def linesToMd(lines:list)->str:
    threshold = 10
    # y 坐标差大于阈值视为两行
    end_in_head_threshold = 30
    # 如果段首存在标点符号，且是此页第一行 则插入空格隔断
    pos_y_previous_sentence:float = lines[0]["position"][0][1]
    text:str = ""
    last_title = False
    for i in lines:
        pos_y_now_sentence = i["position"][0][1]
        if(titleValidator(i)):
            if not last_title:
                text += f"\n### {i['text']}"
            else:
                text += f"{i['text']}"
            last_title = True
        elif(headerValidator(i)):
            last_title = False
            if(abs(pos_y_previous_sentence - pos_y_now_sentence) >= threshold):
                text += f"\n\n{i['text']}"
            else:
                text += f"  {i['text']}"
        else:
            last_title = False
            if(i == lines[0] and i["position"][0][0] >= end_in_head_threshold):
                text += "  "
            text += f"{i['text']}"
        pos_y_previous_sentence = pos_y_now_sentence
    return text

def img2MD(ocr_obj)->str:
    img_fp = 'R:/Temp/cv_cut_thor.jpg'
    out = ocr_obj.ocr(img_fp)
    neo_out = list()
    for i in out:
        temp_line = {"text":i["text"],"score":i["score"],"position":i["position"].tolist()}
        neo_out.append(temp_line)

    markdown_text = linesToMd(neo_out)

    print(markdown_text)
    return markdown_text
ocr = CnOcr(
    rec_model_name = 'densenet_lite_136-gru',
    det_model_name = 'db_resnet34',
    context = 'cpu',  # ['cpu', 'gpu', 'cuda']
)
file_path = 'out.md'
file_obj = open(file_path, mode='a', encoding='utf-8')

while True:
    getCap()
    cutImg()
    md = img2MD(ocr)
    file_obj.write(md)
    nextScreen()
    time.sleep(1)