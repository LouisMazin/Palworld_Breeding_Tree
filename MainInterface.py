from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QRect
from qt_material import apply_stylesheet
import TreesFrame, SettingsInterface, Variables
from os import path, environ
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"
##This file contains the main interface

#Window class
class Interface(QMainWindow):
    def __init__(self,app):
        super().__init__()
        self.app=app
        self.Variables=Variables.Variables(app)
        self.Variables.actualiser(app)
        self.windowswidth, self.windowsheight = self.getResolution()[0],self.getResolution()[1]
        self.onglets = QTabWidget()
        self.onglets.addTab(TreesFrame.Build(), self.Variables.texts[4])
        self.onglets.addTab(SettingsInterface.Build(), self.Variables.texts[3])
        
        
        if(self.Variables.darkMode):
            apply_stylesheet(self, theme='dark_amber.xml')
        else:
            apply_stylesheet(self, theme='light_lightgreen.xml')
            
        self.setWindowTitle(self.Variables.texts[0])
        self.setWindowIcon(QIcon("Icons/icon.png"))
        self.setStyleSheet(self.styleSheet()+self.Variables.sheet)
        self.windowX=int(((self.Variables.screenSize[0]/self.Variables.dpi-self.windowswidth)/2))
        self.windowY=int(((self.Variables.screenSize[1]/self.Variables.dpi-self.windowsheight)/2))+15
        self.setGeometry(QRect(self.windowX,self.windowY,self.windowsheight,self.windowswidth))
        self.setFixedSize(self.windowswidth,self.windowsheight)
        self.setCentralWidget(self.onglets)
    def update(self):
        self.hide()
        self.onglets = QTabWidget()
        self.onglets.addTab(TreesFrame.Build(), self.Variables.texts[4])
        self.onglets.addTab(SettingsInterface.Build(), self.Variables.texts[3])
        self.onglets.setCurrentIndex(1)
        self.setCentralWidget(self.onglets)
        if(self.Variables.darkMode):
            apply_stylesheet(self, theme='dark_amber.xml')
        else:
            apply_stylesheet(self, theme='light_lightgreen.xml')
        self.setStyleSheet(self.styleSheet()+self.Variables.sheet)
        self.windowswidth, self.windowsheight = self.getResolution()[0],self.getResolution()[1]
        self.windowX=int(((self.Variables.screenSize[0]/self.Variables.dpi-self.windowswidth)/2))
        self.windowY=int(((self.Variables.screenSize[1]/self.Variables.dpi-self.windowsheight)/2))+15
        self.setGeometry(QRect(self.windowX,self.windowY,self.windowsheight,self.windowswidth))
        self.setFixedSize(self.windowswidth,self.windowsheight)
        self.show()
    def getApp(self):
        return self.app
    def getResolution(self):
        buffer = [self.Variables.minSize[0]+(self.Variables.maxSize[0] - self.Variables.minSize[0])*(self.Variables.resolution/100),self.Variables.minSize[1]+(self.Variables.maxSize[1] - self.Variables.minSize[1])*(self.Variables.resolution/100)]
        return [int(buffer[0]/self.Variables.dpi),int(buffer[1]/self.Variables.dpi)-30]
def execute():
    app = QApplication([])
    window = Interface(app)
    window.show()
    app.exec()