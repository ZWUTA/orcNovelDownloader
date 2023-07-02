from cnocr import CnOcr



def titleValidator(line:dict)->bool:
    threshold = 60*4
    # 行高大于阈值即为标题
    hight = line["position"][3][1] - line["position"][0][1]
    if(hight >= threshold):
        return True
    else:
        return False

def headerValidator(line:dict)->bool:
    threshold = 100*4
    # 缩进大于阈值即为段首
    indentation = line["position"][0][0]
    if(indentation >= threshold):
        return True
    else:
        return False

def linesToMd(lines:list)->str:
    threshold = 10*4
    # y 坐标差大于阈值视为两行
    pos_y_previous_sentence:float = lines[0]["position"][0][1]
    text:str = ""
    for i in lines:
        pos_y_now_sentence = i["position"][0][1]
        if(titleValidator(i)):
            text += f"\n### {i['text']}\n"
        elif(headerValidator(i)):
            if(abs(pos_y_previous_sentence - pos_y_now_sentence) >= threshold):
                text += f"\n    {i['text']}"
            else:
                text += f"  {i['text']}"
        else:
            text += f"{i['text']}"
        pos_y_previous_sentence = pos_y_now_sentence
    return text



img_fp = 'C:/Users/qwe17/OneDrive/桌面/inari_178__waifu2x_4x_3n_png.png'
ocr = CnOcr(
    rec_model_name = 'densenet_lite_136-gru',
    det_model_name = 'db_resnet34',
    context = 'cpu',  # ['cpu', 'gpu', 'cuda']
    )
out = ocr.ocr(img_fp)
neo_out = list()
for i in out:
    temp_line = {"text":i["text"],"score":i["score"],"position":i["position"].tolist()}
    neo_out.append(temp_line)

markdown_text = linesToMd(neo_out)

print(markdown_text)