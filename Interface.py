from PyQt5.QtWidgets import QStyleFactory,QFrame,QLabel,QPushButton,QComboBox,QBoxLayout,QGridLayout,QWidget,QVBoxLayout,QApplication
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtCore import Qt,QRect
import Graph,ImageCrop,Variables
from os import remove, listdir, path
##This file contains all the graphic interface of the program

#Window class
class Interface(QWidget):
    def __init__(self):
        super().__init__()
        self.positions=Variables.positions
        self.form = QGridLayout()
        self.form.setSpacing(0)
        self.form.setContentsMargins(0,0,0,0)
        self.setLayout(self.form)
        self.setWindowTitle("Breeding tree calculator")
        self.setWindowIcon(QIcon("Icons/icon.png"))
        self.setFixedSize(Variables.width,Variables.height)
        
        for i in range(6):
            palFrame = frame()
            self.form.addWidget(palFrame,self.positions[i][1],self.positions[i][0])
    def closeEvent(self, event):
        [remove("Temp/"+file) for file in listdir("Temp")]
        event.accept()
    
#Class for each frame
class frame(QFrame):
    def __init__(self):
        super().__init__()
        self.palist=Variables.palList.copy()
        self.palist.sort()
        self.which=0
        self.maximum=0
        self.ready=True
        self.x=Variables.frameWidth
        self.y=Variables.frameHeight
        self.parentChoice = QComboBox()
        self.parentChoice.setStyle(QStyleFactory.create("Cleanlooks"))
        self.parentChoice.addItem("Select a parent")
        self.parentChoice.addItems(self.palist)
        self.parentChoice.setCurrentIndex(0)
        self.parentChoice.currentIndexChanged.connect(self.update)
        
        self.text = QLabel()
        self.text.setStyle(QStyleFactory.create("Cleanlooks"))
        self.text.setText("to get an egg of :")
        
        self.childChoice = QComboBox()
        self.childChoice.setStyle(QStyleFactory.create("Cleanlooks"))
        self.childChoice.addItem("Select a child")
        self.childChoice.addItems(self.palist)
        self.childChoice.setCurrentIndex(0)
        self.childChoice.currentIndexChanged.connect(self.update)
        
        self.arbre = QLabel()
        self.arbre.setPixmap(QPixmap(ImageCrop.ResizeTree("Icons/None.png")))
        
        self.suiv = QPushButton(">")
        self.suiv.clicked.connect(lambda : self.actionButton(1))
        self.suiv.setStyle(QStyleFactory.create("Cleanlooks"))
        self.suiv.setMinimumHeight(Variables.arbreSide)
        self.suiv.setMaximumHeight(Variables.arbreSide)
        self.suiv.setMinimumWidth(Variables.buttonWidth)
        self.suiv.setMaximumWidth(Variables.buttonWidth)
        self.suiv.setEnabled(False)
        
        self.prec = QPushButton("<")
        self.prec.clicked.connect(lambda : self.actionButton(-1))
        self.prec.setStyle(QStyleFactory.create("Cleanlooks"))
        self.prec.setMinimumHeight(Variables.arbreSide)
        self.prec.setMaximumHeight(Variables.arbreSide)
        self.prec.setMinimumWidth(Variables.buttonWidth)
        self.prec.setMaximumWidth(Variables.buttonWidth)
        self.prec.setEnabled(False)
        
        self.form1 = QBoxLayout(0)
        self.form1.addWidget(self.parentChoice,alignment=Qt.AlignLeft)
        self.form1.addWidget(self.text,alignment=Qt.AlignCenter)
        self.form1.addWidget(self.childChoice,alignment=Qt.AlignRight)
        self.form1.setContentsMargins(0,0,0,0)
        self.form1.setSpacing(0)
        self.form1.setGeometry(QRect(0,0,self.x,Variables.thickness))
        
        self.form2 = QGridLayout()
        self.form2.addWidget(self.prec,0,0)
        self.form2.addWidget(self.arbre,0,1)
        self.form2.addWidget(self.suiv,0,2)
        self.form2.setContentsMargins(0,0,0,0)
        self.form2.setSpacing(0)
        
        self.form2.setGeometry(QRect(0,0,self.x,Variables.arbreSide))
        
        self.grid = QVBoxLayout()
        self.grid.addLayout(self.form1,Qt.AlignTop)
        self.grid.addLayout(self.form2,Qt.AlignTop)
        self.grid.setContentsMargins(0,0,0,0)
        self.grid.setSpacing(0)
        self.setLayout(self.grid)
        self.setGeometry(0,0,self.x,self.y)
        self.setContentsMargins(0,0,0,0)
        self.update()
    def update(self):
        if(self.ready and self.parentChoice.currentText()!="Select a parent" and self.childChoice.currentText()!="Select a child"):
            self.ready = False
            self.father=self.parentChoice.currentText()
            self.child=self.childChoice.currentText()
            self.res=sorted(Graph.getShortestWays(self.father,self.child), key=lambda x: [Variables.palList.index(i) for i in x])
            self.maximum=len(self.res)-1
            if(self.which>=self.maximum):
                self.which=self.maximum
            self.prec.setEnabled(False)
            self.suiv.setEnabled(False)
            if self.res!=[]:
                if self.maximum>0:
                    self.prec.setEnabled(True)
                    self.suiv.setEnabled(True)
                self.ready = self.load()
            else:
                self.arbre.setPixmap(QPixmap(ImageCrop.ResizeTree("Icons/None.png")))
                self.ready = True
    def load(self):
        if(path.exists("./Trees/"+self.father+"_to_"+self.child+"_n_"+str(self.which)+".png")):
            self.arbre.setPixmap(QPixmap(ImageCrop.ResizeTree("./Trees/"+self.father+"_to_"+self.child+"_n_"+str(self.which)+".png")))
        else:
            self.arbre.setPixmap(QPixmap(ImageCrop.ResizeTree(Graph.getShortestGraphs(self.res[self.which],self.which))))
        return True
    def actionButton(self,nbr):
        if(self.ready):
            self.ready = False
            self.which+=nbr
            if(self.which<0):
                self.which=self.maximum
            elif(self.which>self.maximum):
                self.which=0
            self.ready = self.load()
            
#Function to execute the GUI
def execute():
    app = QApplication([])
    window = Interface()
    window.showMaximized()
    app.exec_()
