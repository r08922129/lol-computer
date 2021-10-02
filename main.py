#!/usr/bin/env python
# coding: utf-8

# In[1]:

import argparse
from json import load as json_load
from ui import Ui_MainWindow
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets

class CoolDownComputer:
    
    def compute(self, skill_cd, ability_haste):
        try:
            skill_cd = float(skill_cd)
            ability_haste = float(ability_haste)

            return skill_cd * (1 - ability_haste/(ability_haste+100))
        except:
            return None
# In[ ]:


parser = argparse.ArgumentParser()
# parser.add_argument("champion", default=None, help="英雄名稱")
# parser.add_argument("skill", default=None, help="Q, W, E or R")
# parser.add_argument("skill_level", default=None, type=int, help="技能等級")
# parser.add_argument("ability_haste", default=None, type=int, help="技能急速")
# parser.add_argument("-u", "--update", action="store_true", help="update champions data")
parser.add_argument("-c", "--config", default="config.json", help="path to config")
args = parser.parse_args()

if __name__ == "__main__":

    with open(args.config) as f:
        config = json_load(f)
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    ui = Ui_MainWindow()
    computer = CoolDownComputer()
    ui.setupUi(MainWindow, computer, config["path_to_champions"])
    MainWindow.show()
    sys.exit(app.exec_())