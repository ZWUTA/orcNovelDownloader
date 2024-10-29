import re
import time
import cv2
import os
import shutil
from cnocr import CnOcr
import config
import subprocess

def get_one_cap(cap_road):
    os.system('adb shell screencap -p > ' + cap_road)
    with open(cap_road, 'rb') as f:
        data = f.read()
    return data.replace(b'\r\n', b'\n')



def fast_get_one_cap() -> bytes:
    # 直接获取截图的二进制数据
    result = subprocess.check_output(['adb', 'shell', 'screencap', '-p'])
    # 替换截图中的换行符
    return result.replace(b'\r\n', b'\n')


def getCap()->None:
    cap = get_one_cap(config.CapImgPath)
    with open(config.CapImgPath, 'wb') as f:
        f.write(cap)

def saveRawCap(outpath:str)->None:
    if os.path.exists(config.OutputImgFullDir):
        pass
    else:
        os.mkdir(config.OutputImgFullDir)
    cap = get_one_cap(config.CapImgPath)
    with open(outpath, 'wb') as f:
        f.write(cap)

def fastSaveRawCap(outpath: str) -> bytes:
    # 创建输出目录（如果不存在）
    os.makedirs(config.OutputImgFullDir, exist_ok=True)
    cap = fast_get_one_cap()
    with open(outpath, 'wb') as f:
        f.write(cap)
    return cap  # 返回截图的二进制流

def cutImg()->None:
    img = cv2.imread(config.CapImgPath)
    if(config.flag_raw):
        cropped = img
        cv2.imwrite(config.CroppedImgPath, cropped)
    else:
        #print(img.shape)
        cropped = img[config.ImgCutPos[0]:config.ImgCutPos[1], config.ImgCutPos[2]:config.ImgCutPos[3]]  # 裁剪坐标为[y0:y1, x0:x1]
        cv2.imwrite(config.CroppedImgPath, cropped)

def nextScreen()->None:
    if config.VolumeKeyPagingEnabled:
        os.system("adb shell input keyevent 25")
    else:
        os.system('adb shell input swipe 540 1300 540 500 100')



def titleValidator(line:dict)->bool:
    threshold = config.TitleThresholdHigh
    # 行高大于阈值即为标题
    pattern = config.TitleRegularExpression
    # 使用正则表达式匹配
    hight = line["position"][3][1] - line["position"][0][1]
    if(hight >= threshold and config.Enable_TitleHigh):
        return True
    elif(re.match(pattern, line["text"], flags=0) != None and config.Enable_TitleRegularExpression):
        return True
    else:
        return False

def headerValidator(line:dict)->bool:
    threshold = config.HeaderThresholdIndentation
    # 缩进大于阈值即为段首
    indentation = line["position"][0][0]
    if(indentation >= threshold and config.Enable_HeaderIndentation):
        return True
    else:
        return False

def linesToMd(lines:list)->str:
    threshold = config.LinefeedThresholdDeltaHigh
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
            if(abs(pos_y_previous_sentence - pos_y_now_sentence) >= threshold and config.Enable_LinefeedThresholdDeltaHigh):
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
    img_fp = config.CroppedImgPath
    out = ocr_obj.ocr(img_fp)

    temp_out = list()
    last_line = {"text":out[0]["text"],"score":out[0]["score"],"position":out[0]["position"].tolist()}
    end_in_head_threshold = 30 * config.ZoomLevel
    head_addr = None
    index = 0
    for i in out:
        temp_line = {"text":i["text"],"score":i["score"],"position":i["position"].tolist(),"head":True,"end":True}
        if((abs(temp_line["position"][0][1] - last_line["position"][0][1]) <= end_in_head_threshold) and (index != 0)):
            #last_line["text"] = last_line["text"] + temp_line["text"]
            if(head_addr != None):
                temp_out[index - 1]["end"] = False
                temp_line["head"] = False
                pass
            else:
                head_addr = index - 1
                temp_out[head_addr]["end"] = False
                temp_line["head"] = False
                pass
        else:
            head_addr = None
        last_line = temp_line
        temp_out.append(temp_line)
        #neo_out.append(last_line)
        #print(last_line["text"])
        index += 1
    line_cache = temp_out[0]
    neo_out = list()
    for i in temp_out:
        if(i["head"] == True):
            if(i["end"] == True):
                #* Head True  End True
                neo_out.append(i)
            else:
                #* Head True  End False
                line_cache = i
        else:
            if(i["end"] == True):
                #* Head False  End True
                line_cache["text"] = line_cache["text"] + i["text"]
                line_cache["position"][1] = i["position"][1]
                line_cache["position"][2] = i["position"][2]
                neo_out.append(line_cache)
            else:
                #* Head False  End False
                line_cache["text"] = line_cache["text"] + i["text"]
                line_cache["position"][1] = i["position"][1]
                line_cache["position"][2] = i["position"][2]

    markdown_text = linesToMd(neo_out)

    #print(markdown_text)
    return markdown_text

ocr = CnOcr(
    rec_model_name = config.RecModel,
    det_model_name = config.DetModel,
    context = config.OcrProcessorsType
)

def imgOutput(outpath:str)->None:
    if os.path.exists(config.OutputImgFullDir):
        pass
    else:
        os.mkdir(config.OutputImgFullDir)
    shutil.copy(config.CroppedImgPath, outpath)




file_path = config.MarkdownPath


if(__name__ == "__main__"):
    file_obj = open(file_path, mode='a', encoding='utf-8')
    while True:
        getCap()
        cutImg()
        md = img2MD(ocr)
        print(md)
        file_obj.write(md)
        nextScreen()
        time.sleep(config.NextPageWaitTime)