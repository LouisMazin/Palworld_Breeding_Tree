from PyQt6.QtWidgets import QLabel,QComboBox,QPushButton,QFrame,QGridLayout,QButtonGroup
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt,QRect
import Graph,ImageCrop,Variables
from os import path,environ
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"

#Class for the main frame
class MainFrame(QFrame):
    def __init__(self):
        #Inherit from QFrame
        super().__init__()
        
        #Get the Variables object
        self.Variables=Variables.Variables.getInstances()
        
        self.positions = self.Variables.positions
        
        self.layout = QGridLayout(objectName="TreesFrameLayout")
        self.setLayout(self.layout)
        
        #Add the frames to the layout
        for i in range(len(self.positions)):
            palFrame =TreeFrame()
            self.layout.addWidget(palFrame,self.positions[i][1],self.positions[i][0])
            
#Class for each frame
class TreeFrame(QFrame):
    def __init__(self):
        #Inherit from QFrame
        super().__init__(objectName="TreesFrame")
        
        #Get the Variables, Graph and ImageCrop objects
        self.Variables=Variables.Variables.getInstances()
        self.ImageCrop = ImageCrop.ImageCrop()
        self.Graph = Graph.Graph()
        
        #Get the variables used for the frame
        self.windowswidth, self.windowsheight = self.getResolution()[0],self.getResolution()[1]
        self.treeSize = int((self.windowsheight/self.Variables.rows)*0.70)
        self.headerHeight = int((self.windowsheight-(self.treeSize*self.Variables.rows))/(4*self.Variables.rows))
        self.buttonHeight = int(self.treeSize/3)
        self.buttonWidth = int((self.windowsheight*0.08)/self.Variables.rows)
        self.fontSize = str(int(self.buttonWidth*0.40))
        self.palist=self.Variables.palList.copy()
        self.palist.sort()
        self.palGraph=self.Graph.getPalsGraph(self.Graph.getCsvContent(self.Variables.csvPath))
        self.nonePath = ["Icons/LightNone.png","Icons/DarkNone.png"][self.Variables.darkMode]
        self.Buttons = []
        
        #ComboBox for the parents
        self.parentChoice = QComboBox()
        self.parentChoice.setEditable(True)
        self.parentChoice.addItem(self.Variables.texts[1])
        self.parentChoice.addItems(self.palist)
        self.parentChoice.setCurrentIndex(0)
        self.parentChoice.currentIndexChanged.connect(self.update)
        self.parentChoice.setFixedHeight(self.headerHeight)        
        self.parentChoice.setStyleSheet("""*{padding-left: 3% ; font-size: """+self.fontSize+"""px;}""")
        
        #Label for the text between the comboboxes
        self.text = QLabel()
        self.text.setText(self.Variables.texts[5])
        self.text.setFixedHeight(self.headerHeight)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setStyleSheet("""*{font-size: """+self.fontSize+"""px;}""")
        
        #ComboBox for the childrens
        self.childChoice = QComboBox()
        self.childChoice.addItem(self.Variables.texts[2])
        self.childChoice.setEditable(True)
        self.childChoice.addItems(self.palist)
        self.childChoice.setCurrentIndex(0)
        self.childChoice.currentIndexChanged.connect(self.update)
        self.childChoice.setFixedHeight(self.headerHeight)
        self.childChoice.setStyleSheet("""*{padding-left: 3% ; font-size: """+self.fontSize+"""px;}""")
        
        #Label for the tree
        self.tree = QLabel()
        self.tree.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        #Buttons for the trees navigation : next
        self.suiv= QGridLayout()
        for i in range(3):
            self.Buttons.append(QPushButton(">"*(i+1),self))
            self.Buttons[i].clicked.connect(lambda i=i: self.goNext(10**i))
            self.Buttons[i].setEnabled(False)
            self.Buttons[i].setFixedWidth(self.buttonWidth)
            self.Buttons[i].setFixedHeight(self.buttonHeight)
            self.Buttons[i].setStyleSheet("""*{padding: 0px;font-size:"""+str(int(self.buttonWidth/3))+"""px} QPushButton{color : """+self.Variables.Colors["primaryColor"]+"""} QPushButton::disabled{color : """+self.Variables.Colors["secondaryLightColor"]+"""}""")
            self.suiv.addWidget(self.Buttons[i],i,0)
        
        #Buttons for the trees navigation : previous
        self.prev= QGridLayout()
        for i in range(3):
            self.Buttons.append(QPushButton("<"*(i+1),self))
            self.Buttons[i+3].clicked.connect(lambda i=i: self.goPrev(10**i))
            self.Buttons[i+3].setEnabled(False)
            self.Buttons[i+3].setFixedWidth(self.buttonWidth)
            self.Buttons[i+3].setFixedHeight(self.buttonHeight)
            self.Buttons[i+3].setStyleSheet("""*{padding: 0px;font-size:"""+str(int(self.buttonWidth/3))+"""px} QPushButton{color : """+self.Variables.Colors["primaryColor"]+"""} QPushButton::disabled{color : """+self.Variables.Colors["secondaryLightColor"]+"""}""")
            self.prev.addWidget(self.Buttons[i+3],i,0)
        
        #Layout for the header of the frame
        self.comboboxes = QGridLayout()
        self.comboboxes.addWidget(self.parentChoice,0,0)
        self.comboboxes.addWidget(self.text,0,1)
        self.comboboxes.addWidget(self.childChoice,0,2)      
        self.comboboxes.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.comboboxes.setGeometry(QRect(0,0,300,self.headerHeight))
        
        #Layout for the buttons and the tree of the frame
        self.trees_buttons = QGridLayout()
        self.trees_buttons.addLayout(self.prev,0,0)
        self.trees_buttons.addWidget(self.tree,0,1)
        self.trees_buttons.addLayout(self.suiv,0,2)
        
        #Main layout
        self.layout = QGridLayout()
        self.layout.addLayout(self.comboboxes,0,0)
        self.layout.addLayout(self.trees_buttons,1,0)
        
        #Set the layout and the stylesheet
        self.setLayout(self.layout)
        self.setStyleSheet("""QLabel,QComboBox{font-size: """+self.fontSize+"""px;color: """+self.Variables.Colors["secondaryTextColor"]+"""; } QComboBox:focus{color : """+self.Variables.Colors["primaryColor"]+"""}""")
        
        self.update()
        
    #Function to update the frame
    def update(self):
        self.which=0
        self.father=self.parentChoice.currentText()
        self.child=self.childChoice.currentText()
        if(self.father==self.Variables.texts[1]):
            key = lambda x: self.Variables.palList.index(x[-1])
        elif(self.child==self.Variables.texts[2]):
            key = lambda x: self.Variables.palList.index(x[0])
        else:
            key = lambda x: [self.Variables.palList.index(i) for i in x]
        self.res=sorted(self.Graph.getShortestWays(self.father,self.child,self.palGraph), key=key)
        self.res = [self.res[i] for i in range(len(self.res)) if i == 0 or self.res[i] != self.res[i-1]]
        self.maximum=len(self.res)-1
        if self.maximum>0:
            for button in self.Buttons:
                button.setEnabled(True)
        else:
            for button in self.Buttons:
                button.setEnabled(False)
            if self.maximum==-1:
                self.tree.setPixmap(QPixmap(self.ImageCrop.ResizeTree(self.nonePath,self.treeSize)))
                return
        self.load()
        
    #Function to load the tree
    def load(self):
        self.tree.setPixmap(QPixmap(self.Graph.getShortestGraphs(self.res[self.which],self.treeSize)))
        
    #Function to go to the next tree
    def goNext(self,value):
        self.which+=value
        while(self.which>self.maximum):
            self.which=0+self.which-self.maximum
        self.load()
        
    #Function to go to the previous tree
    def goPrev(self,value):
        self.which-=value
        while(self.which<0):
            self.which=self.maximum+self.which
        self.load()
    
    #Function to get the resolution
    def getResolution(self):
        buffer = [self.Variables.minSize[0]+(self.Variables.maxSize[0] - self.Variables.minSize[0])*(self.Variables.resolution/100),self.Variables.minSize[1]+(self.Variables.maxSize[1] - self.Variables.minSize[1])*(self.Variables.resolution/100)]
        return [int(buffer[0]/self.Variables.dpi),int(buffer[1]/self.Variables.dpi)-30]