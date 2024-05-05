from PyQt6.QtWidgets import QLabel,QCheckBox,QHBoxLayout,QComboBox,QSlider,QPushButton,QFrame,QGridLayout
from PyQt6.QtCore import Qt
import Variables,requests
from os import path,environ
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"

#Settings Interface class
class SettingsInterface(QFrame):
    def __init__(self):
        #Inherit from QFrame
        super().__init__()
        
        #Get the Variables object
        self.Variables=Variables.Variables.getInstances()
        
        #Get the variables used for the frame
        self.windowswidth, self.windowsheight = self.getResolution("int")[0],self.getResolution("int")[1]
        self.fontSize = str(int(self.windowsheight*0.05))
        self.boxesHeight = int(self.fontSize)*2
        self.texts = self.Variables.texts
        
        #Label for the update text
        self.textUpdate = QLabel()
        self.textUpdate.setOpenExternalLinks(True)
        if(self.updateChecker(self.Variables.version)):
            self.textUpdate.setText('<a style="color : '+self.Variables.Colors["primaryColor"]+'" href=\"https://github.com/LouisMazin/Palworld_Breeding_Tree/releases/latest\">'+self.Variables.texts[6]+'</a>')
        else:
            self.textUpdate.setText(self.texts[7])
        self.textUpdate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        #Checkbox for the darkmode
        self.checkDarkmode = QCheckBox(self.texts[8])
        self.checkDarkmode.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        if(self.Variables.darkMode):
            self.checkDarkmode.setChecked(True)
            
        self.darkmode = QHBoxLayout()
        self.darkmode.addWidget(self.checkDarkmode)
        self.darkmode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        #Combobox for the language ad his label
        self.language = QComboBox()
        self.language.addItems(["Français","English"])
        self.language.setCurrentIndex(self.Variables.language=="en")
        self.language.setFixedHeight(self.boxesHeight)
        
        self.textLanguage = QLabel(self.texts[9])
        self.textLanguage.setAlignment(Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignRight)
        
        self.languageLayout = QHBoxLayout()
        self.languageLayout.addWidget(self.textLanguage)
        self.languageLayout.addWidget(self.language)    
        self.languageLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        #Slider for the resolution and his label and value
        self.sliderResolution = QSlider()
        self.sliderResolution.setOrientation(Qt.Orientation.Horizontal)
        self.sliderResolution.setRange(0,100)
        self.sliderResolution.setValue(self.Variables.resolution)
        self.sliderResolution.valueChanged.connect(lambda : self.valueResolution.setText(("x").join(self.Variables.getResolution(self.sliderPosition.value(),self.sliderResolution.value()))))
        
        self.textResolution = QLabel(self.texts[11])
        
        self.valueResolution = QLabel(("x").join(self.getResolution("str")))
        
        self.resolution = QHBoxLayout()
        self.resolution.addWidget(self.textResolution)
        self.resolution.addWidget(self.sliderResolution)
        self.resolution.addWidget(self.valueResolution)
        
        #Slider for the position and his label and value
        self.sliderPosition = QSlider()
        self.sliderPosition.setOrientation(Qt.Orientation.Horizontal)
        self.sliderPosition.setRange(0,4)
        self.sliderPosition.setSliderPosition(self.Variables.position)
        self.sliderPosition.valueChanged.connect(self.changePosition)
        
        self.textPosition = QLabel(self.texts[10])
        
        self.valuePosition = QLabel(str([1,2,3,4,6][self.sliderPosition.value()]))
        
        self.position = QHBoxLayout()
        self.position.addWidget(self.textPosition)
        self.position.addWidget(self.sliderPosition)
        self.position.addWidget(self.valuePosition)
        
        #Button to apply the changes
        self.applyButton = QPushButton(self.texts[12])
        self.applyButton.clicked.connect(self.apply)
        self.applyButton.setFixedHeight(self.boxesHeight)
        
        #Set the main layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.textUpdate,0,0,alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.darkmode,1,0,alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.languageLayout,2,0,alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.position,3,0,alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.resolution,4,0,alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.applyButton,5,0,alignment=Qt.AlignmentFlag.AlignCenter)
        
        #Set the stylesheet
        self.setStyleSheet("""*{font-size: """+self.fontSize+"""px;} QCheckBox::indicator{width: """+str(self.boxesHeight)+"""px;height: """+str(self.boxesHeight)+"""px;}""")
    
    #Function to change the position text label and the resolution text label
    def changePosition(self):
        self.valuePosition.setText(str([1,2,3,4,6][self.sliderPosition.value()]))
        self.valueResolution.setText(("x").join(self.Variables.getResolution(self.sliderPosition.value(),self.sliderResolution.value())))
    
    #Function to apply the changes
    def apply(self):
        self.Variables.saveOptions(self.checkDarkmode.isChecked(),self.sliderPosition.value(),self.sliderResolution.value(),["fr","en"][self.language.currentIndex()])
        self.parent().parent().parent().update()
        self.destroy()
    
    #Function to get a resolution
    def getResolution(self,wanted="int"):
        minSizeX, minSizeY = self.Variables.minSize
        buffer = [minSizeX+(self.Variables.maxSize[0] - minSizeX)*(self.Variables.resolution/100),minSizeY+(self.Variables.maxSize[1] - minSizeY)*(self.Variables.resolution/100)]
        resolution =  [int(buffer[0]),int(buffer[1])]
        if wanted=="int":
            return [int(buffer[0]/self.Variables.dpi),int(buffer[1]/self.Variables.dpi)-30]
        else:
            return [str(resolution[0]),str(resolution[1])]
    
    #Function to check if there is an update
    def updateChecker(self,target_version):
        try:
            response = requests.get("https://api.github.com/repos/LouisMazin/Palworld_Breeding_Tree/releases/latest",timeout=15)
            if response.status_code == 200:
                latest_version = response.json()['tag_name']
                return latest_version > target_version
            else:
                return False
        except:
            return False
        
        