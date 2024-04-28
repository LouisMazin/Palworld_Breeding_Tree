from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import TreesFrame, SettingsInterface, Variables, qt_material
from os import path,environ
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"
##This file contains the main interface

#Window class
class Interface(QMainWindow):
    def __init__(self,app):
        super().__init__()
        self.app=app
        self.windowswidth, self.windowsheight = self.getResolution()[0],self.getResolution()[1]
        self.onglets = QTabWidget()
        self.onglets.addTab(TreesFrame.Build(), Variables.texts[4])
        self.onglets.addTab(SettingsInterface.Build(), Variables.texts[3])
        
        
        if(Variables.darkMode):
            qt_material.apply_stylesheet(self, theme='dark_amber.xml')
        else:
            qt_material.apply_stylesheet(self, theme='light_lightgreen.xml')
            
        self.setWindowTitle(Variables.texts[0])
        self.setWindowIcon(QIcon("Icons/icon.png"))
        self.setStyleSheet(self.styleSheet()+Variables.sheet)
        self.windowX=int((Variables.screenSize[0]-self.windowswidth)/2)
        self.windowY=int((Variables.screenSize[1]-self.windowsheight)/2)
        self.setGeometry(QRect(self.windowX,self.windowY,self.windowsheight,self.windowswidth))
        self.setFixedSize(self.windowswidth,self.windowsheight)
        self.setCentralWidget(self.onglets)
    def update(self):
        self.hide()
        self.onglets = QTabWidget()
        self.onglets.addTab(TreesFrame.Build(), Variables.texts[4])
        self.onglets.addTab(SettingsInterface.Build(), Variables.texts[3])
        self.onglets.setCurrentIndex(1)
        self.setCentralWidget(self.onglets)
        if(Variables.darkMode):
            qt_material.apply_stylesheet(self, theme='dark_amber.xml')
        else:
            qt_material.apply_stylesheet(self, theme='light_lightgreen.xml')
        self.setStyleSheet(self.styleSheet()+Variables.sheet)
        self.windowswidth, self.windowsheight = self.getResolution()[0],self.getResolution()[1]
        self.setGeometry(QRect(self.windowX,self.windowY,self.windowsheight,self.windowswidth))
        self.windowX=((Variables.screenSize[0]-self.windowswidth)//2)
        self.windowY=((Variables.screenSize[1]-self.windowsheight)//2)
        self.setFixedSize(self.windowswidth,self.windowsheight)
        self.show()
    def getApp(self):
        return self.app
    def getResolution(self):
        buffer = [Variables.minSize[0]+(Variables.maxSize[0] - Variables.minSize[0])*(Variables.resolution/100),Variables.minSize[1]+(Variables.maxSize[1] - Variables.minSize[1])*(Variables.resolution/100)]
        return [int(buffer[0]/Variables.dpi),int(buffer[1]/Variables.dpi)-30]
def execute():
    app = QApplication([])
    Variables.actualiser(app)
    window = Interface(app)
    #theme based on C:\Logiciels\Python\Python311\Lib\site-packages\qt_material\material.css.template
    print("C:\Logiciels\Python\Python311\Lib\site-packages\qt_material\material.css.template")
 
    window.show()
    app.exec()