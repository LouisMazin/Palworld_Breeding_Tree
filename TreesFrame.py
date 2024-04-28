from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import Graph,ImageCrop,Variables
from os import path,environ
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"

class Build(QFrame):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(objectName="TreesFrameLayout")
        self.setLayout(self.layout)
        self.positions = Variables.positions
        # for i in reversed(range(self.layout.count())):
        #     self.layout.itemAt(i).widget().setParent(None)
        for i in range(len(self.positions)):
            palFrame =TreeFrame()
            self.layout.addWidget(palFrame,self.positions[i][1],self.positions[i][0])
#Class for each frame
class TreeFrame(QFrame):
    def __init__(self):
        super().__init__(objectName="TreesFrame")
        
        self.windowswidth, self.windowsheight = self.getResolution()[0],self.getResolution()[1]
        self.treeSize = int((self.windowsheight/Variables.rows)*0.70)
        self.headerHeight = int((self.windowsheight-(self.treeSize*Variables.rows))/(4*Variables.rows))
        self.buttonHeight = int(self.treeSize/3)
        self.buttonWidth = int((self.windowsheight*0.08)/Variables.rows)
        self.fontSize = str(int(self.buttonWidth*0.40))
                
        self.palist=Variables.palList.copy()
        self.palist.sort()
        self.palGraph=Graph.getPalsGraph(Graph.getCsvContent(Variables.csvPath))
        
        self.parentChoice = QComboBox()
        self.parentChoice.setEditable(True)
        self.parentChoice.addItem(Variables.texts[1])
        self.parentChoice.addItems(self.palist)
        self.parentChoice.setCurrentIndex(0)
        self.parentChoice.currentIndexChanged.connect(self.update)
        self.parentChoice.setFixedHeight(self.headerHeight)        
        self.parentChoice.setStyleSheet("""*{padding-left: 3% ; font-size: """+self.fontSize+"""px;}""")
        
        self.text = QLabel()
        self.text.setText(Variables.texts[5])
        self.text.setFixedHeight(self.headerHeight)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setStyleSheet("""*{font-size: """+self.fontSize+"""px;}""")
        
        self.childChoice = QComboBox()
        self.childChoice.addItem(Variables.texts[2])
        self.childChoice.setEditable(True)
        self.childChoice.addItems(self.palist)
        self.childChoice.setCurrentIndex(0)
        self.childChoice.currentIndexChanged.connect(self.update)
        self.childChoice.setFixedHeight(self.headerHeight)
        self.childChoice.setStyleSheet("""*{padding-left: 3% ; font-size: """+self.fontSize+"""px;}""")
        
        if(Variables.darkMode):
            self.nonePath="Icons/DarkNone.png"
        else:
            self.nonePath="Icons/LightNone.png"
        self.tree = QLabel()
        self.tree.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.suivSlow = QPushButton(">")
        self.suivSlow.clicked.connect(lambda : self.goNext(1))
        self.suivSlow.setEnabled(False)
        self.suivMid = QPushButton(">>")
        self.suivMid.clicked.connect(lambda : self.goNext(10))
        self.suivMid.setEnabled(False)
        self.suivFast = QPushButton(">>>")
        self.suivFast.clicked.connect(lambda : self.goNext(100))
        self.suivFast.setEnabled(False)
        
        self.suiv= QGridLayout()
        self.suiv.addWidget(self.suivSlow,0,0)
        self.suiv.addWidget(self.suivMid,1,0)
        self.suiv.addWidget(self.suivFast,2,0)
        
        self.prevSlow = QPushButton("<")
        self.prevSlow.clicked.connect(lambda : self.goPrev(1))
        self.prevSlow.setEnabled(False)
        self.prevMid = QPushButton("<<")
        self.prevMid.clicked.connect(lambda : self.goPrev(10))
        self.prevMid.setEnabled(False)
        self.prevFast = QPushButton("<<<")
        self.prevFast.clicked.connect(lambda : self.goPrev(100))
        self.prevFast.setEnabled(False)
            
        self.prev = QGridLayout()
        self.prev.addWidget(self.prevSlow,0,0)
        self.prev.addWidget(self.prevMid,1,0)
        self.prev.addWidget(self.prevFast,2,0)
        
        for button in [self.prevSlow,self.prevMid,self.prevFast,self.suivSlow,self.suivMid,self.suivFast]:
            button.setFixedWidth(self.buttonWidth)
            button.setFixedHeight(self.buttonHeight)
            button.setStyleSheet("""*{padding: 0px;font-size:"""+str(int(self.buttonWidth/3))+"""px} QPushButton{color : """+Variables.Colors["primaryColor"]+"""} QPushButton::disabled{color : """+Variables.Colors["secondaryLightColor"]+"""}""")
        self.comboboxes = QGridLayout()
        self.comboboxes.addWidget(self.parentChoice,0,0)
        self.comboboxes.addWidget(self.text,0,1)
        self.comboboxes.addWidget(self.childChoice,0,2)      
        self.comboboxes.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.comboboxes.setGeometry(QRect(0,0,300,self.headerHeight))
        self.setStyleSheet("""QLabel,QComboBox{font-size: """+self.fontSize+"""px;color: """+Variables.Colors["secondaryTextColor"]+"""; } QComboBox:focus{color : """+Variables.Colors["primaryColor"]+"""}""")
        
        self.trees_buttons = QGridLayout()
        self.trees_buttons.addLayout(self.prev,0,0)
        self.trees_buttons.addWidget(self.tree,0,1)
        self.trees_buttons.addLayout(self.suiv,0,2)
        self.layout = QGridLayout()
        self.layout.addLayout(self.comboboxes,0,0)
        self.layout.addLayout(self.trees_buttons,1,0)
        
        self.setLayout(self.layout)
        
        self.update()
    def update(self):
        self.which=0
        self.father=self.parentChoice.currentText()
        self.child=self.childChoice.currentText()
        if(self.father==Variables.texts[1]):
            key = lambda x: Variables.palList.index(x[-1])
        elif(self.child==Variables.texts[2]):
            key = lambda x: Variables.palList.index(x[0])
        else:
            key = lambda x: [Variables.palList.index(i) for i in x]
        self.res=sorted(Graph.getShortestWays(self.father,self.child,self.palGraph), key=key)
        self.res = [self.res[i] for i in range(len(self.res)) if i == 0 or self.res[i] != self.res[i-1]]
        self.maximum=len(self.res)-1
        if self.maximum>0:
            self.prevSlow.setEnabled(True)
            self.prevMid.setEnabled(True)
            self.prevFast.setEnabled(True)
            self.suivSlow.setEnabled(True)
            self.suivMid.setEnabled(True)
            self.suivFast.setEnabled(True)
        else:
            self.prevSlow.setEnabled(False)
            self.prevMid.setEnabled(False)
            self.prevFast.setEnabled(False)
            self.suivSlow.setEnabled(False)
            self.suivMid.setEnabled(False)
            self.suivFast.setEnabled(False)
            if self.maximum==-1:
                self.tree.setPixmap(QPixmap(ImageCrop.ResizeTree(self.nonePath,self.treeSize)))
                return
        self.load()
    def load(self):
        self.tree.setPixmap(QPixmap(Graph.getShortestGraphs(self.res[self.which],self.treeSize)))
    def goNext(self,value):
        self.which+=value
        while(self.which>self.maximum):
            self.which=0+self.which-self.maximum
        self.load()
    def goPrev(self,value):
        self.which-=value
        while(self.which<0):
            self.which=self.maximum+self.which
        self.load()
    def getResolution(self):
        buffer = [Variables.minSize[0]+(Variables.maxSize[0] - Variables.minSize[0])*(Variables.resolution/100),Variables.minSize[1]+(Variables.maxSize[1] - Variables.minSize[1])*(Variables.resolution/100)]
        return [int(buffer[0]/Variables.dpi),int(buffer[1]/Variables.dpi)-30]