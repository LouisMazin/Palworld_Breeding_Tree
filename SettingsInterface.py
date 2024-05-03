from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import Variables,requests
from os import path,environ
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"

class Build(QFrame):
    def __init__(self):
        super().__init__()
        self.Variables=Variables.Variables.getInstances()
        self.windowswidth, self.windowsheight = self.getResolution("int")[0],self.getResolution("int")[1]
        self.fontSize = str(int(self.windowsheight*0.16/self.Variables.rows*0.40))
        self.setStyleSheet("""*{font-size: """+self.fontSize+"""px;}""")
        self.boxesHeight = int(self.fontSize)*2
        
        self.textUpdate = QLabel()
        self.textUpdate.setOpenExternalLinks(True)
        if(updateChecker(self.Variables.version)):
            self.textUpdate.setText('<a style="color : '+self.Variables.Colors["primaryColor"]+'" href=\"https://github.com/LouisMazin/Palworld_Breeding_Tree/releases/latest\">'+self.Variables.texts[6]+'</a>')
        else:
            self.textUpdate.setText(self.Variables.texts[7])
        self.textUpdate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.checkDarkmode = QCheckBox(self.Variables.texts[8])
        self.checkDarkmode.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        if(self.Variables.darkMode):
            self.checkDarkmode.setChecked(True)
            
        self.darkmode = QHBoxLayout()
        self.darkmode.addWidget(self.checkDarkmode)
        self.darkmode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textLanguage = QLabel(self.Variables.texts[9])
        self.textLanguage.setAlignment(Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignRight)
        self.language = QComboBox()
        self.language.addItems(["Français","English"])
        self.language.setCurrentIndex(self.Variables.language=="en")
        self.language.setFixedHeight(self.boxesHeight)
        self.languageLayout = QHBoxLayout()
        self.languageLayout.addWidget(self.textLanguage)
        self.languageLayout.addWidget(self.language)    
        self.languageLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.sliderResolution = QSlider()
        self.sliderResolution.setOrientation(Qt.Orientation.Horizontal)
        self.sliderResolution.setRange(0,80)
        self.sliderResolution.setValue(self.Variables.resolution)
        self.sliderResolution.valueChanged.connect(lambda : self.valueResolution.setText(("x").join(self.Variables.getResolution(self.sliderPosition.value(),self.sliderResolution.value()))))
        self.textResolution = QLabel(self.Variables.texts[11])
        self.valueResolution = QLabel(("x").join(self.getResolution("str")))
        self.resolution = QHBoxLayout()
        self.resolution.addWidget(self.textResolution)
        self.resolution.addWidget(self.sliderResolution)
        self.resolution.addWidget(self.valueResolution)
        
        self.sliderPosition = QSlider()
        self.sliderPosition.setOrientation(Qt.Orientation.Horizontal)
        self.sliderPosition.setRange(0,4)
        self.sliderPosition.setSliderPosition(self.Variables.position)
        self.sliderPosition.valueChanged.connect(self.changePosition)
        self.textPosition = QLabel(self.Variables.texts[10])
        self.valuePosition = QLabel(str([1,2,3,4,6][self.sliderPosition.value()]))
        self.position = QHBoxLayout()
        self.position.addWidget(self.textPosition)
        self.position.addWidget(self.sliderPosition)
        self.position.addWidget(self.valuePosition)
        
        self.applyButton = QPushButton(self.Variables.texts[12])
        self.applyButton.clicked.connect(self.apply)
        self.applyButton.setFixedHeight(self.boxesHeight)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setStyleSheet(self.styleSheet()+"""QCheckBox::indicator{width: """+str(self.boxesHeight)+"""px;height: """+str(self.boxesHeight)+"""px;}""")
        self.layout.addWidget(self.textUpdate,0,0,alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.darkmode,1,0,alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.languageLayout,2,0,alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.position,3,0,alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.resolution,4,0,alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.applyButton,5,0,alignment=Qt.AlignmentFlag.AlignCenter)
    def changePosition(self):
        self.valuePosition.setText(str([1,2,3,4,6][self.sliderPosition.value()]))
        self.valueResolution.setText(("x").join(self.Variables.getResolution(self.sliderPosition.value(),self.sliderResolution.value())))
    def apply(self):
        self.Variables.darkMode = self.checkDarkmode.isChecked()
        self.Variables.position = self.sliderPosition.value()
        self.Variables.resolution = self.sliderResolution.value()
        if(self.language.currentIndex()==0):
            self.Variables.language="fr"
        else:
            self.Variables.language="en"
        self.Variables.saveOptions()
        self.Variables.actualiser(self.parent().parent().parent().getApp())
        self.parent().parent().parent().update()
        self.destroy()
    def getResolution(self,format="int"):
        buffer = [self.Variables.minSize[0]+(self.Variables.maxSize[0] - self.Variables.minSize[0])*(self.Variables.resolution/100),self.Variables.minSize[1]+(self.Variables.maxSize[1] - self.Variables.minSize[1])*(self.Variables.resolution/100)]
        resolution =  [int(buffer[0]),int(buffer[1])]
        if format=="int":
            return [int(buffer[0]/self.Variables.dpi),int(buffer[1]/self.Variables.dpi)-30]
        else:
            return [str(resolution[0]),str(resolution[1])]
def updateChecker(target_version):
    response = requests.get("https://api.github.com/repos/LouisMazin/Palworld_Breeding_Tree/releases/latest")
    
    if response.status_code == 200:
        latest_version = response.json()['tag_name']
        return latest_version > target_version
    else:
        return False
        
        