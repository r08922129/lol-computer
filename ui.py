# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cd_computer.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
from os import listdir
from json import load as json_load
from os.path import join as join_path
from utils import *
from scraper import *
from nltk import edit_distance
from collections import deque
from PyQt5 import QtCore, QtGui, QtWidgets

class ChampionsMap:

    def __init__(self, champions=None, support_regions=set(["en_US", "zh_TW"])):

        self.champions = champions
        self.region_to_name = {}
        self.support_regions = support_regions

    def load(self, path_to_champions):

        champion_ids = listdir(path_to_champions)
        champions = []
        for champion_id in champion_ids:
            champion = Champion(champion_id)
            champion.load(join_path(path_to_champions, champion_id))
            champions.append(champion)

        self.build_map(champions)

    def build_map(self, champions):
        self.champions = champions
        for region in self.support_regions:
            self.region_to_name[region] = {}
            for champion in champions:
                champion_name = champion.get_name()
                self.region_to_name[region][champion_name] = champion

    def get_champion(self, champion_name, region="zh_TW"):
        return self.region_to_name[region][champion_name]

    def get_champion_names(self, region="zh_TW"):
        champion_names = list(self.region_to_name[region].keys())
        return champion_names


class Champion:
    
    def __init__(self, id_=None, region="zh_TW"):
        self.id_ = id_
        self.champion_info = None
        self.spells = []

    def load(self, path, region="zh_TW"):
        self.champion_info = {}
        with open(join_path(path, f"info-{region}.json")) as f:
            self.champion_info = json_load(f)
        for spell_data in self.champion_info["data"][self.id_]["spells"]:
            self.spells.append(Spell(spell_data))

    def get_name(self):
        return self.champion_info["data"][self.id_]["name"]

    def get_id(self):
        return self.id_

    def get_spell(self, spell_index):
        return self.spells[spell_index]

class Spell:

    def __init__(self, data):
        '''
        Parameter: dict
        eg.
            "id": "ApheliosQ_ClientTooltipWrapper",
            "name": "武器技能",
            "description": "亞菲利歐根據裝備的主武器不同，會擁有 5 個不同的主動技能：<br>
                <br>月影步槍（步槍）：長距離射擊，能夠標記目標以進行一次長程的追加攻擊。<br>
                月鐮槍刃（鐮刀短銃）：快速奔跑的同時用兩把武器攻擊附近的敵人。<br>
                月殞重砲 （加農重砲）：定身所有被這把武器緩速的敵人。<br>
                熾夜月燄（火焰噴射器）：轟襲錐形範圍的敵人並用你的副武器攻擊他們。<br>
                月曲終章（環型飛刃）：部署一個會用你的副武器射擊的哨兵。<br>",
            "maxrank": 6,
            "cooldown": [9, 9, 9, 9, 9, 9],
            "cost": [60, 60, 60, 60, 60, 60]
        '''
        self.data = data

    def get_cooldown(self, level):
        return self.data["cooldown"][level-1]
    def get_max_rank(self):
        return self.data["maxrank"]

class Updater:

    def __init__(self, path_to_champions, progressBar, textBrowser):
        self.root = "https://leagueoflegends.fandom.com"
        self.progressBar = progressBar
        self.textBrowser = textBrowser
        self.path_to_champions = path_to_champions
        self.resource_scraper = DataDragonScraper(None, progressBar, textBrowser)

    def update(self, callback):
        self.textBrowser.write("Start crawling resources...")
        self.resource_scraper.get_champions_resources()
        callback()
        self.progressBar.setValue(100)
        self.textBrowser.write("Finish :)")

class TextBrowser(QtWidgets.QTextBrowser):

    def __init__(self, widget):
        super().__init__(widget)
        self.buffer = deque()
        self.max_len = 1000

    def write(self, text):
        text = str(text)
        if len(self.buffer) > self.max_len:
            self.buffer.popleft()
        self.buffer.append(text)
        self.display()
    
    def display(self):
        self.setPlainText("\n".join(self.buffer))

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, computer, path_to_champions):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(811, 497)
        # self-defined attributes
        self.path_to_champions = path_to_champions
        self.computer = computer
        self.champions_map = ChampionsMap()
        self.current_champion = None

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(20, 40, 101, 31))
        self.comboBox.setMaxVisibleItems(10)
        self.comboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLength)
        self.comboBox.setObjectName("comboBox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 10, 161, 31))
        self.label.setMaximumSize(QtCore.QSize(161, 31))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 150, 161, 31))
        self.label_2.setMaximumSize(QtCore.QSize(161, 31))
        self.label_2.setObjectName("label_2")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(20, 190, 101, 31))
        self.lineEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit.setObjectName("lineEdit")
        # text browser
        self.textBrowser = TextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(440, 100, 331, 341))
        self.textBrowser.setObjectName("textBrowser")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(680, 10, 91, 31))
        self.pushButton.setObjectName("pushButton")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 260, 341, 185))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.line = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 1)
        self.spinBox_2 = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.spinBox_2.setAlignment(QtCore.Qt.AlignCenter)
        self.spinBox_2.setMinimum(1)
        self.spinBox_2.setMaximum(5)
        self.spinBox_2.setObjectName("spinBox_2")
        self.gridLayout.addWidget(self.spinBox_2, 4, 1, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.spinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(5)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 2, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 6, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 0, 2, 1, 1)
        self.spinBox_3 = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.spinBox_3.setAlignment(QtCore.Qt.AlignCenter)
        self.spinBox_3.setMinimum(1)
        self.spinBox_3.setMaximum(5)
        self.spinBox_3.setObjectName("spinBox_3")
        self.gridLayout.addWidget(self.spinBox_3, 6, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 8, 0, 1, 1)
        self.spinBox_4 = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.spinBox_4.setAlignment(QtCore.Qt.AlignCenter)
        self.spinBox_4.setMinimum(1)
        self.spinBox_4.setMaximum(3)
        self.spinBox_4.setObjectName("spinBox_4")
        self.gridLayout.addWidget(self.spinBox_4, 8, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 0, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_11.setText("")
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 4, 2, 1, 1)
        self.line_3 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 5, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_10.setText("")
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 2, 2, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_13.setText("")
        self.label_13.setAlignment(QtCore.Qt.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 8, 2, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_12.setText("")
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 6, 2, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 3, 0, 1, 1)
        self.line_4 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout.addWidget(self.line_4, 7, 0, 1, 1)
        self.line_5 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.gridLayout.addWidget(self.line_5, 9, 0, 1, 1)
        self.line_6 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.gridLayout.addWidget(self.line_6, 1, 1, 1, 1)
        self.line_7 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_7.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.gridLayout.addWidget(self.line_7, 1, 2, 1, 1)
        self.line_8 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_8.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.gridLayout.addWidget(self.line_8, 3, 1, 1, 1)
        self.line_9 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_9.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_9.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_9.setObjectName("line_9")
        self.gridLayout.addWidget(self.line_9, 3, 2, 1, 1)
        self.line_10 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_10.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_10.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_10.setObjectName("line_10")
        self.gridLayout.addWidget(self.line_10, 5, 1, 1, 1)
        self.line_11 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_11.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_11.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_11.setObjectName("line_11")
        self.gridLayout.addWidget(self.line_11, 5, 2, 1, 1)
        self.line_12 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_12.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_12.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_12.setObjectName("line_12")
        self.gridLayout.addWidget(self.line_12, 7, 1, 1, 1)
        self.line_13 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_13.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_13.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_13.setObjectName("line_13")
        self.gridLayout.addWidget(self.line_13, 7, 2, 1, 1)
        self.line_14 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_14.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_14.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_14.setObjectName("line_14")
        self.gridLayout.addWidget(self.line_14, 9, 1, 1, 1)
        self.line_15 = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line_15.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_15.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_15.setObjectName("line_15")
        self.gridLayout.addWidget(self.line_15, 9, 2, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(280, 230, 80, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(160, 40, 130, 130))
        self.graphicsView.setObjectName("graphicsView")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(447, 60, 321, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setGeometry(QtCore.QRect(20, 160, 59, 15))
        self.label_14.setText("")
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setGeometry(QtCore.QRect(20, 80, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(20, 120, 101, 31))
        self.lineEdit_2.setObjectName("lineEdit_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 811, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.updater = Updater(path_to_champions, self.progressBar, self.textBrowser)

        # signal and slot
        self.pushButton.clicked.connect(lambda: self.updater.update(self.update_combobox_champions))
        self.pushButton_2.clicked.connect(self.compute)
        self.lineEdit_2.textChanged.connect(lambda: self.search_champion(self.lineEdit_2.text()))
        self.comboBox.currentTextChanged.connect(self.change_current_champion)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # set champions
        self.update_combobox_champions()


    def update_combobox_champions(self):
        try:
            self.champions_map.load(self.path_to_champions)
            try:
                self.comboBox.clear()
                champion_names = self.champions_map.get_champion_names(region="zh_TW")
                for champion_name in champion_names:
                    self.comboBox.addItem(champion_name)
            except Exception as e:
                print(e)
                self.textBrowser.write("Failed to update champions...")

        except Exception as e:
            print(e)
            self.textBrowser.write("Failed to load champions...")
            self.textBrowser.write("If you use the app first time, please update the data first.")


    def compute(self):
        # get current champion
        ability_haste = self.lineEdit.text()
        skill_levels = [
            self.spinBox.value(),
            self.spinBox_2.value(),
            self.spinBox_3.value(),
            self.spinBox_4.value(),
        ]
        skill_labels = [
            self.label_10,
            self.label_11,
            self.label_12,
            self.label_13
        ]

        for i, (skill_level, skill_label) in enumerate(zip(skill_levels, skill_labels)):
            spell = self.current_champion.get_spell(i)
            raw_cd = spell.get_cooldown(skill_level)
            cd = self.computer.compute(raw_cd, ability_haste)
            cd = f"{cd:.2f}" if cd is not None else "-"
            skill_label.setText(cd)

    def search_champion(self, name):
        champion_names = self.champions_map.get_champion_names(region="zh_TW")
        most_similar_name = match_champion_name(name, champion_names)
        index = self.comboBox.findText(most_similar_name)
        self.comboBox.setCurrentIndex(index)


    def change_current_champion(self):
        try:
            current_champion_name = self.comboBox.currentText()
            self.current_champion = self.champions_map.get_champion(current_champion_name, region="zh_TW")
            
            self.change_champion_image()
            self.change_champion_spell_info()
        except:
            pass
    
    def change_champion_image(self):
        try:
            champion_id = self.current_champion.get_id()
            pix = QtGui.QPixmap(join_path(self.path_to_champions, champion_id, "img.png"))
            item = QtWidgets.QGraphicsPixmapItem(pix)
            scene = QtWidgets.QGraphicsScene()
            scene.addItem(item)
            self.graphicsView.setScene(scene)
        except:
            pass

    def change_champion_spell_info(self):
        spinBoxes = [self.spinBox, self.spinBox_2, self.spinBox_3, self.spinBox_4]
        for i, spinBox in enumerate(spinBoxes):
            spell = self.current_champion.get_spell(i)
            maxrank = spell.get_max_rank()
            spinBox.setMaximum(maxrank)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "技能冷卻換算機"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">選擇英雄</span></p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">當前技能急速</span></p></body></html>"))
        self.lineEdit.setText(_translate("MainWindow", "0"))
        self.pushButton.setText(_translate("MainWindow", "更新英雄資料"))
        self.label_5.setText(_translate("MainWindow", "E"))
        self.label_3.setText(_translate("MainWindow", "W"))
        self.label_7.setText(_translate("MainWindow", "技能"))
        self.label_4.setText(_translate("MainWindow", "Q"))
        self.label_9.setText(_translate("MainWindow", "冷卻"))
        self.label_6.setText(_translate("MainWindow", "R"))
        self.label_8.setText(_translate("MainWindow", "技能等級"))
        self.pushButton_2.setText(_translate("MainWindow", "計算冷卻"))
        self.label_15.setText(_translate("MainWindow", "搜尋英雄"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
