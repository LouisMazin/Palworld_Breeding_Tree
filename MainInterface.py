from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QRect
from qt_material import apply_stylesheet
import TreesFrame, SettingsInterface, Variables
from os import path, environ
import sys
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)
environ["PATH"] += resource_path("Graphviz\\bin")+";"
##This file contains the main interface

#Window class
class Interface(QMainWindow):
    def __init__(self,app):
        
        #Inherit from QMainWindow
        super().__init__()
        
        #Create the Variables object : the QApplication and the Variables object
        self.app=app
        self.Variables=Variables.Variables(app)
        self.Variables.update(app)
        self.dpi = self.Variables.dpi
        self.texts = self.Variables.texts
        self.screenSize = self.Variables.screenSize
        #Create the tab widget and add the two tabs
        self.onglets = QTabWidget()
        self.onglets.addTab(TreesFrame.MainFrame(), self.texts[4])
        self.onglets.addTab(SettingsInterface.SettingsInterface(), self.texts[3])
        
        #Get the resolution of the window
        self.windowsWidth, self.windowsHeight = self.getResolution()[0],self.getResolution()[1]
        
        #Create the location of the window
        self.windowX=int(((self.screenSize[0]/self.dpi-self.windowsWidth)/2))
        self.windowY=int(((self.screenSize[1]/self.dpi-self.windowsHeight)/2))+15
        
        #Apply the base stylesheet
        apply_stylesheet(self, theme=['light_lightgreen.xml','dark_amber.xml'][self.Variables.darkMode])
        
        #Set the window properties
        self.setGeometry(QRect(self.windowX,self.windowY,self.windowsHeight,self.windowsWidth))
        self.setFixedSize(self.windowsWidth,self.windowsHeight)
        self.setWindowTitle(self.texts[0])
        self.setWindowIcon(QIcon(resource_path("Icons/icon.png")))
        self.setStyleSheet(self.styleSheet()+self.Variables.sheet)
        self.setCentralWidget(self.onglets)
        
    #Function to update the Interface
    def update(self):
        self.hide()
        
        #Update the Variables object
        self.Variables.update(self.app)
        
        #Update the Variables attributes
        self.texts = self.Variables.texts
        self.dpi = self.Variables.dpi
        
        #Create the tab widget and add the two tabs
        self.onglets = QTabWidget()
        self.onglets.addTab(TreesFrame.MainFrame(), self.texts[4])
        self.onglets.addTab(SettingsInterface.SettingsInterface(), self.texts[3])
        self.onglets.setCurrentIndex(1)
        
        #Get the resolution of the window
        self.windowsWidth, self.windowsHeight = self.getResolution()[0],self.getResolution()[1]
        
        #Create the location of the window ; the +15 is to avoid the top of the window
        self.windowX=int(((self.screenSize[0]/self.dpi-self.windowsWidth)/2))
        self.windowY=int(((self.screenSize[1]/self.dpi-self.windowsHeight)/2))+15
        
        #Apply the base stylesheet
        apply_stylesheet(self, theme=['light_lightgreen.xml','dark_amber.xml'][self.Variables.darkMode])
        
        #Set the window properties
        self.setGeometry(QRect(self.windowX,self.windowY,self.windowsHeight,self.windowsWidth))
        self.setFixedSize(self.windowsWidth,self.windowsHeight)
        self.setWindowTitle(self.texts[0])
        self.setStyleSheet(self.styleSheet()+self.Variables.sheet)
        self.setCentralWidget(self.onglets)
        
        self.show()
        
    #Function to get the QApplication
    def getApp(self):
        return self.app

    #Function to get the resolution
    def getResolution(self):
        minSizeX, minSizeY = self.Variables.minSize
        width = minSizeX+(self.Variables.maxSize[0] - minSizeX)*(self.Variables.resolution/100)
        height = minSizeY+(self.Variables.maxSize[1] - minSizeY)*(self.Variables.resolution/100)
        #the +30 is to avoid the top of the window
        return [int(width/self.dpi),int(height/self.dpi)-30]
def execute():
    app = QApplication([])
    window = Interface(app)
    window.show()
    app.exec()
