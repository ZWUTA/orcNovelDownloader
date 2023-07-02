import os

# ! 基本设置
WindowTitle = "AndreaNeoNovelDownloader"
WindowIcon = "app/resource/images/logo.png"

# ! 裁切设置
# * 裁剪坐标为[y0:y1, x0:x1]
#ImgCutPos = [170,2360,50,1000] # 裁剪坐标为[y0:y1, x0:x1]
# ? Redmi Note12T Pro [170,2360,50,1000]
# ? Redmi Note7 Pro   [145,2200,50,1000]

ImgCutPos = [145,2200,50,1000]

# ! 识别设置
    # * 识别增强
ZoomLevel = 4
    # * 标题识别
TitleThresholdHigh = 70
Enable_TitleHigh = False
TitleRegularExpression = "^第.*章.*"
Enable_TitleRegularExpression = True
    # * 段首识别
HeaderThresholdIndentation = 100
Enable_HeaderIndentation = True
    # * 换行识别
LinefeedThresholdDeltaHigh = 10
Enable_LinefeedThresholdDeltaHigh = True

    # * 截图翻页等待时间
NextPageWaitTime = 0.5

    # * 索引设置
MaximumPage = 2147483647

# ! OCR设置
RecModel = "densenet_lite_136-gru"
DetModel = "db_resnet34"
OcrProcessorsType = "cuda"  # ['cpu', 'gpu', 'cuda']

# ! 文件路径
    # * 临时文件路径
TempPath = "R:/Temp"
CapImg = "cap.png"
CroppedImg = "cv_cut_thor.png"
CapImgPath = f"{TempPath}/{CapImg}"
CroppedImgPath = f"{TempPath}/{CroppedImg}"
    # * 输出文件路径
OutputPath = "D:/临时文件/noveldownload"
OutputImgPath = "img"
OutputImgFullDir = f"{OutputPath}/{OutputImgPath}"
MarkdownName = "out.md"
MarkdownPath = f"{OutputPath}/{MarkdownName}"
def getOutputImgPath(index:int,prefix:str):
    OutputImgName = f"{prefix}_{index}_.png"
    return f"{OutputPath}/{OutputImgPath}/{OutputImgName}"
