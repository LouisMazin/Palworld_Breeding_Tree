from csv import reader as read
from os import path,environ
from PyQt6.QtGui import QGuiApplication
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"
##This file contains variables used in the program
def chargerOptions():
    #import options from the options.json
    import json
    with open("options.json") as f:
        options=json.load(f)
    return options.values()
def save():
    #save options in the options.json
    import json
    with open("options.json","w") as f:
        json.dump({"darkMode": darkMode, "position" : position, "windowSize" : resolution, "language": language},f)
    return
def getPalList():
    liste=[]
    with open("data.csv", 'r',encoding='utf-8') as f:
        reader = read(f,delimiter=',')
        for row in reader:
            liste.append(row[0])
    return liste
def getStyleDimensions(position,app):
    global dpi,positions,screenSize
    #return order : dpi,rows,listeResolutions,minSize,maxSize
    dpi = app.primaryScreen().devicePixelRatio()
    screenSize= ((app.primaryScreen().size()*dpi).width(),(app.primaryScreen().size()*dpi).height())
    match position:
        case 0:
            return dpi,1,[480,480],[2440,2440]
        case 1:
            return dpi,1,[960,480],[2440,1220]
        case 2:
            return dpi,1,[1440,480],[2440,814]
        case 3:
            return dpi,2,[720,720],[2440,2440]
            
        case 4:
            return dpi,2,[1080,720],[2440,1627]
def actualiser(app):
    global darkMode,language,texts,positions,themeName,sheet,Colors,dpi,position,resolution,minSize,maxSize,rows
    darkMode,position,resolution,language=chargerOptions()
    positions = positionsList[position]
    dpi,rows,minSize,maxSize = getStyleDimensions(position,app)
    if(language=="fr"):
        texts=frenchTexts
    elif(language=="en"):
        texts=englishTexts
    themeName=["lightTheme","darkTheme"][darkMode]
    Colors=[LightColors,darkColors][darkMode]
    sheet=Sheet(Colors)
    return
version="1.5.0"
csvPath="data.csv"
frenchTexts=["Calculateur d'arbre d'accouplement","Parents","Enfants","Paramètres","Construire","pour obtenir un :","Une mise à jour est disponible","Aucune mise à jour disponible","Mode Sombre : ","Langue :","Nombre d'arbres :","Résolution :", "Appliquer"]
englishTexts=["Breeding tree calculator","Parents","Childs","Settings","Build","to get an egg of :","to get a :","No update available","Dark Mode : ","Language : ","Number of trees : ","Resolution :","Apply"]
palList=getPalList()
positionsList=[[(0,0)],[(0,0),(1,0)],[(0,0),(1,0),(2,0)],[(0,0),(1,0),(0,1),(1,1)],[(0,0),(1,0),(2,0),(0,1),(1,1),(2,1)]]
texts=frenchTexts
darkColors={'primaryColor': '#ffd740', 'primaryLightColor': '#ffff74', 'secondaryColor': '#232629', 'secondaryLightColor': '#4f5b62', 'secondaryDarkColor': '#31363b', 'primaryTextColor': '#000000', 'secondaryTextColor': '#ffffff'}
LightColors={'primaryColor': '#64dd17', 'primaryLightColor': '#9cff57', 'secondaryColor': '#f5f5f5', 'secondaryLightColor': '#ffffff', 'secondaryDarkColor': '#e6e6e6', 'primaryTextColor': '#3c3c3c', 'secondaryTextColor': '#555555'}
Sheet=lambda Colors : """
*{
    background-color: transparent;
    color: """+Colors["secondaryTextColor"]+""";
    border: none;
    padding: 0;
    margin: 0;
    line-height: 0;
    font-family: "Segoe UI", sans-serif;
}

QWidget{
    color: """+Colors["secondaryTextColor"]+""";
}

QLabel{
    color: """+Colors["secondaryTextColor"]+""";
    }
"""