# coding:utf-8
import sys
import os
import time
import typing
import PyQt5
from PyQt5.QtCore import QObject, Qt, QRect, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPainter, QImage, QBrush, QColor, QFont
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel


from click import Option
from qfluentwidgets import (NavigationInterface, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, setThemeColor, qrouter)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets.components import widgets
from qfluentwidgets.components.widgets.label import PixmapLabel

from qfluentwidgets.components.widgets.line_edit import TextEdit
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPainter
from app.view.simple_interface import SimpleInterface, SimpleCard
from qfluentwidgets import SwitchButton
from qfluentwidgets import LineEdit, SpinBox, DoubleSpinBox, TimeEdit, DateTimeEdit, DateEdit, TextEdit
from qfluentwidgets import ToggleButton
from qfluentwidgets import StateToolTip

import usb2md_copy
import config

class CommandWidget(QFrame):
    def __init__(self, text: str ,parent=None, context = None):
        super().__init__(parent=parent)
        self.parent = parent
        self.context = context
        
        self.context.ocr_thread.tootipTitleUpdate.connect(self.Tooltip_titleUpdate)
        self.context.ocr_thread.tooltipContentUpdate.connect(self.Tooltip_contentUpdate)
        self.context.ocr_thread.indexdisplayValUpdate.connect(self.ImgIndex_valUpdate)
        self.context.ocr_thread.taskdone.connect(self.OcrThread_taskDone)
        
        self.layout = QHBoxLayout()
        
        self.ImgOutLabel = QLabel()
        self.ImgOutLabel.setText("保存图片文件")
        self.ImgOutBottom = SwitchButton(parent=self)
        self.ImgOutBottom.setMinimumWidth(80)
        self.ImgOutBottom.setMaximumWidth(80)
        self.ImgOutBottom.checkedChanged.connect(self.ImgOutBottom_onCheckedChanged)
        
        self.OcrSwitchLabel = QLabel()
        self.OcrSwitchLabel.setText("启动OCR")
        self.OcrSwitchBottom = SwitchButton(parent=self)
        self.OcrSwitchBottom.setMinimumWidth(80)
        self.OcrSwitchBottom.setMaximumWidth(80)
        self.OcrSwitchBottom.checkedChanged.connect(self.OcrSwitch_onCheckedChanged)
        
        self.PrefixLabel = QLabel()
        self.PrefixLabel.setText("文件名前缀")
        self.PrefixInput = LineEdit(self)
        
        self.ImgIndexLabel = QLabel()
        self.ImgIndexLabel.setText("图片索引")
        self.ImgIndexDisplay = SpinBox(self)
        self.ImgIndexDisplay.setMaximum(config.MaximumPage)
        
        self.ImgTargetLabel = QLabel()
        self.ImgTargetLabel.setText("识别张数")
        self.ImgTargetInput = SpinBox(self)
        self.ImgTargetInput.setMaximum(config.MaximumPage)
        
        self.StartRunBottom = ToggleButton('运行', self)
        self.StartRunBottom.setMaximumWidth(80)
        self.StartRunBottom.setMinimumWidth(80)
        self.StartRunBottom.clicked.connect(self.StartRunBottom_onCheckedChanged)
        
        
        self.layout.addWidget(self.ImgOutLabel)
        self.layout.addWidget(self.ImgOutBottom)
        self.layout.addWidget(self.OcrSwitchLabel)
        self.layout.addWidget(self.OcrSwitchBottom)
        self.layout.addWidget(self.PrefixLabel)
        self.layout.addWidget(self.PrefixInput)
        self.layout.addWidget(self.ImgIndexLabel)
        self.layout.addWidget(self.ImgIndexDisplay)
        self.layout.addWidget(self.ImgTargetLabel)
        self.layout.addWidget(self.ImgTargetInput)
        self.layout.addWidget(self.StartRunBottom)
        
        self.setLayout(self.layout)
        self.ImgOutBottom.setChecked(False)

    def OcrSwitch_onCheckedChanged(self,isChecked:bool):
        if isChecked:
            text = "On"
            self.context.ocr_thread.OcrSwitch(True)
        else:
            text = "Off"
            self.context.ocr_thread.OcrSwitch(False)
        #text = "On " if isChecked else "Off"
        self.OcrSwitchBottom.setText(text)

    def ImgOutBottom_onCheckedChanged(self, isChecked:bool):
        if isChecked:
            text = "On"
            self.context.ocr_thread.IMGoutSwitch(True)
        else:
            text = "Off"
            self.context.ocr_thread.IMGoutSwitch(False)
        #text = "On " if isChecked else "Off"
        self.ImgOutBottom.setText(text)
        
    def StartRunBottom_onCheckedChanged(self, isChecked:bool):
        if isChecked:
            text = "运行中"
            self.stateTooltip = StateToolTip('', '', self.parent)
            self.stateTooltip.move(880, 0)
            self.stateTooltip.show()
            if(self.ImgTargetInput.value() != 0):
                self.stateTooltip.setTitle("正在下载小说")
                self.StartRunBottom.setCheckable(False)
                self.context.ocr_thread.setTarget(self.ImgTargetInput.value(), self.ImgIndexDisplay.value(), self.PrefixInput.text(),self.ImgOutBottom.isChecked())
                self.context.ocr_thread.start()
            else:
                self.stateTooltip.setTitle("参数错误")
                self.stateTooltip.setContent("页面增量不能为0")
                self.stateTooltip.setState(True)
                self.stateTooltip = None
                text = "运行"
                self.StartRunBottom.setCheckable(True)
                self.StartRunBottom.setChecked(False)

        else:
            text = "运行"
        #text = "运行中" if isChecked else "运行"
        self.StartRunBottom.setText(text)

    def downloadDone(self):
            text = "运行"
            self.stateTooltip.setTitle("小说下载完成啦 😆")
            self.stateTooltip.setContent("小说已经下载完成！")
            self.stateTooltip.setState(True)
            self.stateTooltip = None
            self.StartRunBottom.setText(text)
            self.StartRunBottom.setCheckable(True)
            self.StartRunBottom.setChecked(False)

    def Tooltip_titleUpdate(self, new_title):
        self.stateTooltip.setTitle(new_title)
    def Tooltip_contentUpdate(self, new_content):
        self.stateTooltip.setContent(new_content)
    def ImgIndex_valUpdate(self, new_val):
        self.ImgIndexDisplay.setValue(new_val)
    def OcrThread_taskDone(self):
        self.downloadDone()

class Widget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))

class PicWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(self)
        #self.label.setText("O")
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.hBoxLayout.setContentsMargins(0,0,0,0)
    
    def updatePixmap(self, pixmap):
        self.label.setPixmap(pixmap)
    setPixmap = updatePixmap


class HomeInterface(SimpleInterface):
    """ Text interface """

    def __init__(self, parent=None ,context=None):
        #t = Translator()
        super().__init__(
            title="Home Page",
            subtitle="自代码丢失后几年说是要重构 咕咕咕了几年总算是勉勉强强跑起来了（",
            parent=parent
        )
        # text edit
        self.textEdit = TextEdit(self)
        self.textEdit.setMarkdown(
            "## Steel Ball Run \n * Johnny Joestar 🦄 \n * Gyro Zeppeli 🐴 ")
        self.textEdit.setFixedHeight(650)
        self.textEditCard = SimpleCard(
            title="文本预览",
            widget=self.textEdit,
            stretch=1,
            parent=self.view
            )

        #? 原始图片
        img_path = config.CapImgPath
        self.pic_widget = PicWidget(parent)
        if(os.path.exists(img_path)):
            self.pixmap = QPixmap(img_path)
            self.pic_widget.setPixmap(self.pixmap)
        #self.pic_card.setMaximumHeight(400)
        #self.pic_card.setScaledContents(True)
        self.pic_widget.setMaximumWidth(300)
        self.pic_widget.setMaximumHeight(650)
        self.pic_widget.setMinimumHeight(650)
        self.PicViewCard = SimpleCard(
            title="原始图片",
            widget=self.pic_widget,
            stretch=1,
            parent=self.view
            )
        self.PicViewCard.vBox2Center()

        #? 裁剪后图片
        cuted_img_path = config.CroppedImgPath
        self.cuted_pic_widget = PicWidget(parent)
        if(os.path.exists(cuted_img_path)):
            self.cuted_pixmap = QPixmap(cuted_img_path)
            self.cuted_pic_widget.setPixmap(self.cuted_pixmap)
        #self.pic_card.setMaximumHeight(400)
        #self.pic_card.setScaledContents(True)
        self.cuted_pic_widget.setMaximumWidth(300)
        self.cuted_pic_widget.setMaximumHeight(650)
        self.cuted_pic_widget.setMinimumHeight(650)
        self.cuted_PicViewCard = SimpleCard(
            title="输出图片",
            widget=self.cuted_pic_widget,
            stretch=1,
            parent=self.view
            )
        self.cuted_PicViewCard.vBox2Center()

        
        self.commandCard = SimpleCard(
            title= "Command",
            widget=CommandWidget(parent,parent=self,context=context),
            stretch=1,
            parent=self.view
        )

        
        
        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.PicViewCard)
        self.hlayout.addWidget(self.cuted_PicViewCard)
        self.hlayout.addWidget(self.textEditCard)
        self.hwidget = QFrame(parent)
        self.hwidget.setLayout(self.hlayout)
        self.addWidget(self.hwidget)
        self.addWidget(self.commandCard)

class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.initOCR()
        self.setTitleBar(StandardTitleBar(self))

        # use dark theme mode
        # setTheme(Theme.DARK)

        # change the theme color
        # setThemeColor('#0078d4')

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)

        # create sub interface
        #self.home_page = Widget('Home Page', self)
        self.home_page = HomeInterface(self,context=self)
        self.settingInterface = Widget('Setting Interface', self)


        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()
        
        self.initWindow()
        #self.run()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.home_page, FIF.HOME, 'Home Page')

        self.navigationInterface.addSeparator()

        # add navigation items to scroll area
        # self.addSubInterface(self.folderInterface, FIF.FOLDER, 'Folder library', NavigationItemPosition.SCROLL)
        # for i in range(1, 21):
        #     self.navigationInterface.addItem(
        #         f'folder{i}',
        #         FIF.FOLDER,
        #         f'Folder {i}',
        #         lambda: print('Folder clicked'),
        #         position=NavigationItemPosition.SCROLL
        #     )


        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

        #!IMPORTANT: don't forget to set the default route key if you enable the return button
        # qrouter.setDefaultRouteKey(self.stackWidget, self.musicInterface.objectName())

        # set the maximum width
        # self.navigationInterface.setExpandWidth(300)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        #self.stackWidget.setCurrentIndex(0)
        self.onCurrentInterfaceChanged(0)
        # 启动时切换到首页

    def initWindow(self):
        self.resize(1200, 1000)
        self.setWindowIcon(QIcon(config.WindowIcon))
        self.setWindowTitle(config.WindowTitle)
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'app/resource/qss/{color}/simple_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())
        
        #!IMPORTANT: This line of code needs to be uncommented if the return button is enabled
        # qrouter.push(self.stackWidget, widget.objectName())
    
    def cutImgUpdate(self,img_path:typing.Optional[str] = None):
        if img_path is None:
            self.home_page.pixmap = QPixmap(config.CapImgPath)
            self.home_page.pic_widget.updatePixmap(w.home_page.pixmap)
        else:
            self.home_page.pixmap = QPixmap(img_path)
            self.home_page.pic_widget.updatePixmap(w.home_page.pixmap)
    def cutedImgUpdate(self):
        self.home_page.cuted_pixmap = QPixmap(config.CroppedImgPath)
        self.home_page.cuted_pic_widget.updatePixmap(w.home_page.cuted_pixmap)
    def mdUpdate(self,md):
        self.home_page.textEdit.setMarkdown(md)
    def initOCR(self):
        self.ocr_thread=OcrThread()
        self.ocr_thread.picUpdate.connect(self.cutImgUpdate)
        self.ocr_thread.cutedpicUpdate.connect(self.cutedImgUpdate)
        self.ocr_thread.mdUpdate.connect(self.mdUpdate)
        
        """
        self.ocr_thread.start()
        """

class OcrThread(QThread):
    picUpdate = pyqtSignal(str)
    cutedpicUpdate = pyqtSignal()
    mdUpdate = pyqtSignal(str)
    tootipTitleUpdate = pyqtSignal(str)
    tooltipContentUpdate = pyqtSignal(str)
    indexdisplayValUpdate = pyqtSignal(int)
    taskdone = pyqtSignal()
    def __init__(self) -> None:
        super(OcrThread,self).__init__()
        self.enable_ocr = False
    def setTarget(self,page_add:int,page_index:int,prefix:str,img_out_switch:bool):
        self.page_add = page_add
        self.page_index = page_index
        self.prefix = prefix
        self.img_out_switch = img_out_switch
    def IMGoutSwitch(self,satge):
        self.img_out_switch = satge
    def OcrSwitch(self,stage):
        self.enable_ocr = stage
    def run(self):
        j = 1
        for i in range(self.page_index, self.page_index+self.page_add):
            img_path = config.getOutputImgPath(i,self.prefix)
            
            self.indexdisplayValUpdate.emit(i)
            file_obj = open(usb2md_copy.file_path, mode='a', encoding='utf-8')
            if config.flag_raw:
                usb2md_copy.saveRawCap(img_path)
                self.picUpdate.emit(img_path)
                self.tooltipContentUpdate.emit(f"创建截图完成 {j}/{self.page_add}")
            else:
                # ! 截图部分
                usb2md_copy.getCap()
                self.picUpdate.emit()
                self.tooltipContentUpdate.emit(f"创建截图完成 {j}/{self.page_add}")
                
                usb2md_copy.cutImg()
                self.cutedpicUpdate.emit()
                self.tooltipContentUpdate.emit(f"裁剪截图完成 {j}/{self.page_add}")
                if self.img_out_switch:
                # ! 输出截图
                    usb2md_copy.imgOutput(img_path)
                
            # ! OCR部分
            # ! OCR部分
            if(self.enable_ocr):
                md = usb2md_copy.img2MD(usb2md_copy.ocr)
                #w.home_page.textEdit.setMarkdown(md)
                self.mdUpdate.emit(md)
                self.tooltipContentUpdate.emit(f"OCR完成 {j}/{self.page_add}")
                print(md)
                file_obj.write(md)
                file_obj.close()
            # ! 下一屏
            usb2md_copy.nextScreen()
            time.sleep(config.NextPageWaitTime)
            j += 1
            self.indexdisplayValUpdate.emit(i+1)
        self.taskdone.emit()

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()


    