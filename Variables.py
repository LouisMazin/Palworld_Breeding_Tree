from pyautogui import size
from csv import reader as read
##This file contains variables used in the program

def getPalList():
    liste=[]
    with open("data.csv", 'r',encoding='utf-8') as f:
        reader = read(f,delimiter=',')
        for row in reader:
            liste.append(row[0])
    return liste
csvPath="data.csv"
palList=getPalList()
arbreSide=int(int(size().width//3)*0.7)
buttonWidth=int(int(size().width//3)*0.15)
thickness=int(int(size().height/1.089808274)//2)-arbreSide
frameWidth, frameHeight = arbreSide+2*buttonWidth, arbreSide+thickness
width, height= 3*frameWidth, 2*frameHeight
positions=[(0,0),(frameWidth,0),(2*frameWidth,0),(0,frameHeight),(frameWidth,frameHeight),(2*frameWidth,frameHeight)]
