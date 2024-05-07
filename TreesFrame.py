from PyQt6.QtWidgets import QLabel,QComboBox,QPushButton,QFrame,QGridLayout
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
        
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        #Add the frames to the layout
        for x, y in self.positions:
            palFrame = TreeFrame()
            self.layout.addWidget(palFrame, y, x)

            
#Class for each frame
class TreeFrame(QFrame):
    def __init__(self):
        #Inherit from QFrame
        super().__init__()
        
        #Get the Variables, Graph and ImageCrop objects
        self.Variables=Variables.Variables.getInstances()
        
        #Get the variables used for the frame
        self.windowswidth, self.windowsheight = self.getResolution()[0],self.getResolution()[1]
        self.treeSize = int((self.windowsheight/self.Variables.rows)*0.70)
        self.headerHeight = int((self.windowsheight-(self.treeSize*self.Variables.rows))/(4*self.Variables.rows))
        self.buttonHeight = int(self.treeSize/3)
        self.buttonWidth = int((self.windowsheight*0.08)/self.Variables.rows)
        self.fontSize = str(int(self.buttonWidth*0.40))
        self.palist=self.Variables.palList.copy()
        self.palist.sort()
        self.palGraph=Graph.getPalsGraph(self.Variables.csvContent)
        self.nonePath = ["Icons/LightNone.png","Icons/DarkNone.png"][self.Variables.darkMode]
        self.Buttons = []
        self.texts = self.Variables.texts
        self.Colors = self.Variables.Colors
        #ComboBox for the parents
        self.parentChoice = QComboBox()
        self.parentChoice.setEditable(True)
        self.parentChoice.addItem(self.texts[1])
        self.parentChoice.addItems(self.palist)
        self.parentChoice.setCurrentIndex(0)
        self.parentChoice.currentIndexChanged.connect(self.update)
        self.parentChoice.setFixedHeight(self.headerHeight)        
        self.parentChoice.setStyleSheet("""*{padding-left: 3% ; font-size: """+self.fontSize+"""px;}""")
        
        #Label for the text between the comboboxes
        self.text = QLabel()
        self.text.setText(self.texts[5])
        self.text.setFixedHeight(self.headerHeight)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setStyleSheet("""*{font-size: """+self.fontSize+"""px;}""")
        
        #ComboBox for the childrens
        self.childChoice = QComboBox()
        self.childChoice.addItem(self.texts[2])
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
            self.Buttons[i].clicked.connect(self.create_lambda(i,self.goNext))
            self.Buttons[i].setEnabled(False)
            self.Buttons[i].setFixedWidth(self.buttonWidth)
            self.Buttons[i].setFixedHeight(self.buttonHeight)
            self.Buttons[i].setStyleSheet("""*{padding: 0px;font-size:"""+str(int(self.buttonWidth/3))+"""px} QPushButton{color : """+self.Colors["primaryColor"]+"""} QPushButton::disabled{color : """+self.Colors["secondaryLightColor"]+"""}""")
            self.suiv.addWidget(self.Buttons[i],i,0)
        
        #Buttons for the trees navigation : previous
        self.prev= QGridLayout()
        for i in range(3):
            self.Buttons.append(QPushButton("<"*(i+1),self))
            self.Buttons[i+3].clicked.connect(self.create_lambda(i,self.goPrev))
            self.Buttons[i+3].setEnabled(False)
            self.Buttons[i+3].setFixedWidth(self.buttonWidth)
            self.Buttons[i+3].setFixedHeight(self.buttonHeight)
            self.Buttons[i+3].setStyleSheet("""*{padding: 0px;font-size:"""+str(int(self.buttonWidth/3))+"""px} QPushButton{color : """+self.Colors["primaryColor"]+"""} QPushButton::disabled{color : """+self.Colors["secondaryLightColor"]+"""}""")
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
        self.setStyleSheet("""QLabel,QComboBox{font-size: """+self.fontSize+"""px;color: """+self.Colors["secondaryTextColor"]+"""; } QComboBox:focus{color : """+self.Colors["primaryColor"]+"""}""")
        
        self.update()
        
    #Function to update the frame
    def update(self):
        self.which=0
        self.father=self.parentChoice.currentText()
        self.child=self.childChoice.currentText()
        if(self.father==self.texts[1]):
            key = lambda x: self.palist.index(x[-1])
        elif(self.child==self.texts[2]):
            key = lambda x: self.palist.index(x[0])
        else:
            key = lambda x: [self.palist.index(i) for i in x]
        self.res=sorted(Graph.getShortestWays(self.father,self.child,self.palGraph), key=key)
        self.res = [self.res[i] for i in range(len(self.res)) if i == 0 or self.res[i] != self.res[i-1]]
        self.maximum=len(self.res)-1
        if self.maximum>0:
            for button in self.Buttons:
                button.setEnabled(True)
        else:
            for button in self.Buttons:
                button.setEnabled(False)
            if self.maximum<0:
                self.tree.setPixmap(QPixmap(ImageCrop.ResizeTree(self.nonePath,self.treeSize)))
                return
        self.load()
        
    #Function to load the tree
    def load(self):
        self.tree.setPixmap(QPixmap(Graph.getShortestGraphs(self.res[self.which],self.treeSize)))
        
    #Function to go to the next tree
    def goNext(self,value):
        if(self.maximum!=1):
            self.which+=value
            if(self.which>self.maximum):
                self.which = self.which%self.maximum-1
        else:
            self.which = int(not(bool(self.which)))
        self.load()

    #Function to go to the previous tree
    def goPrev(self,value):
        if(self.maximum!=1):
            self.which-=value
            if(self.which<0):
                self.which =(self.maximum+self.which)%self.maximum+1
        else:
            self.which = int(not(bool(self.which)))
        self.load()
    
    #Function to get the resolution
    def getResolution(self):
        minSizeX,minSizeY = self.Variables.minSize
        buffer = [minSizeX+(self.Variables.maxSize[0] - minSizeX)*(self.Variables.resolution/100),minSizeY+(self.Variables.maxSize[1] - minSizeY)*(self.Variables.resolution/100)]
        return [int(buffer[0]/self.Variables.dpi),int(buffer[1]/self.Variables.dpi)-30]

    #Function to create a lambda function
    def create_lambda(self,h,funct):
        return lambda: funct(10**h)