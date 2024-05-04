from csv import reader
from os import path,environ
from json import load,dump
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"

class Variables():
    __instance_variable = False
    def __init__(self,app):
        Variables.__instance_variable = self
        self.version="1.0.0"
        self.csvPath="data.csv"
        self.frenchTexts=["Calculateur d'arbre d'accouplement","Parents","Enfants","Paramètres","Construire","pour obtenir un :","Une mise à jour est disponible","Aucune mise à jour disponible","Mode Sombre : ","Langue :","Nombre d'arbres :","Résolution :", "Appliquer"]
        self.englishTexts=["Breeding tree calculator","Parents","Childs","Settings","Build","to get an egg of :","An update is available","No update available","Dark Mode : ","Language : ","Number of trees : ","Resolution :","Apply"]
        self.palList=self.getPalList()
        self.darkColors={'primaryColor': '#ffd740', 'primaryLightColor': '#ffff74', 'secondaryColor': '#232629', 'secondaryLightColor': '#4f5b62', 'secondaryDarkColor': '#31363b', 'primaryTextColor': '#000000', 'secondaryTextColor': '#ffffff'}
        self.LightColors={'primaryColor': '#64dd17', 'primaryLightColor': '#9cff57', 'secondaryColor': '#f5f5f5', 'secondaryLightColor': '#ffffff', 'secondaryDarkColor': '#e6e6e6', 'primaryTextColor': '#3c3c3c', 'secondaryTextColor': '#555555'}
        self.Sheet=lambda Colors : """*{background-color: transparent;color: """+Colors["secondaryTextColor"]+""";border: none;padding: 0;margin: 0;line-height: 0;font-family: "Segoe UI", sans-serif;}QWidget{color: """+Colors["secondaryTextColor"]+""";}QLabel{color: """+Colors["secondaryTextColor"]+""";}"""
        #posisitonsList like coord of the trees , number of rowq, minSize and maxSize
        self.positionsList=[[[(0,0)],1,[480,480],1],
                            [[(0,0),(1,0)],1,[960,480],2],
                            [[(0,0),(1,0),(2,0)],1,[1440,480],3],
                            [[(0,0),(1,0),(0,1),(1,1)],2,[720,720],1],
                            [[(0,0),(1,0),(2,0),(0,1),(1,1),(2,1)],2,[1080,720],1.5]
                            ]
        self.dpi = app.primaryScreen().devicePixelRatio()
        self.screenSize= ((app.primaryScreen().size()*self.dpi).width(),(app.primaryScreen().size()*self.dpi).height())
    def loadOptions(self):
        #import options from the options.json
        with open("options.json") as f:
            options=load(f)
        f.close()
        return options.values()
    def saveOptions(self):
        #save options in the options.json
        with open("options.json","w") as f:
            dump({"darkMode": self.darkMode, "position" : self.position, "windowSize" : self.resolution, "language": self.language},f)
        f.close()
    def getPalList(self):
        liste=[]
        with open("data.csv", 'r',encoding='utf-8') as f:
            read = reader(f,delimiter=',')
            for row in read:
                liste.append(row[0])
        f.close()
        return liste
    def actualiser(self,app):
        self.app=app
        self.darkMode,self.position,self.resolution,self.language=self.loadOptions()
        self.current = self.positionsList[self.position]
        self.positions,self.rows,self.minSize,self.ratio=self.current
        if(self.screenSize[0]/self.ratio<self.screenSize[1]):
            self.maxSize = [self.screenSize[0],self.screenSize[0]/self.ratio]
        else:
            self.maxSize = [self.screenSize[1]*self.ratio,self.screenSize[1]]
        if(self.language=="fr"):
            self.texts=self.frenchTexts
        elif(self.language=="en"):
            self.texts=self.englishTexts
        self.themeName=["lightTheme","darkTheme"][self.darkMode]
        self.Colors=[self.LightColors,self.darkColors][self.darkMode]
        self.sheet=self.Sheet(self.Colors)
        return
    @staticmethod
    def getInstances():
        return Variables.__instance_variable
    def getResolution(self,position,resolution):
        ratio = self.positionsList[position][3]
        if(self.screenSize[0]/ratio<self.screenSize[1]):
            maxSize = [self.screenSize[0],self.screenSize[0]/ratio]
        else:
            maxSize = [self.screenSize[1]*ratio,self.screenSize[1]]
            
        minSize = self.positionsList[int(position)][2]
        buffer = [minSize[0]+(maxSize[0] - minSize[0])*(resolution/100),minSize[1]+(maxSize[1] - minSize[1])*(resolution/100)]
        resolution =  [int(buffer[0]),int(buffer[1])]
        return [str(resolution[0]),str(resolution[1])]