import Variables,ImageCrop
from networkx import all_shortest_paths, exception, DiGraph
from graphviz import Digraph
from csv import reader as read
from os import path,environ
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"
##This file contains function to get the list of all shortests
##ways between two pals
##
##It uses breed.csv and return a list of png paths

#function to get a dict with pals and their childrens
def getCsvContent(file : str):
    pals={}
    with open(file, 'r',encoding='utf-8') as f:
        reader = read(f,delimiter=',')
        for row in reader:
            pals[row[0]]=row[1:]
    return pals

#function to get the graph of all the pals and their relations
def getPalsGraph(csvContent : dict):
    G = DiGraph()
    for parent, enfants in csvContent.items():
        for enfant in enfants:
            G.add_edge(parent, enfant)
    return G

#function to get all the parents of a child
def findParents(pal : str, enfant : str):
    secondParents=[]
    childrens=getCsvContent(Variables.csvPath)[pal]
    for childrenIndex in range(len(childrens)):
        if childrens[childrenIndex]==enfant:
            secondParents.append(Variables.palList[childrenIndex])
    return secondParents

#function to get the shorstests ways between a parent and a child
def getShortestWays(parent : str, child : str,palGraph):
    if(parent==Variables.texts[1] and child==Variables.texts[2]):
        return []
    if(child == Variables.texts[2]):
        ways=[]
        for pal in Variables.palList:
            try:
                ways+=list(all_shortest_paths(palGraph,parent,pal))
            except exception.NetworkXNoPath:
                pass
        return ways
    elif(parent == Variables.texts[1]):
        ways=[]
        for pal in Variables.palList:
            try:
                ways+=list(all_shortest_paths(palGraph,pal,child))
            except exception.NetworkXNoPath:
                pass
        return ways
    elif(child in getCsvContent(Variables.csvPath)[parent]):
        return [[parent,child]]
    else:
        try :
            return list(all_shortest_paths(palGraph,parent,child))
        except exception.NetworkXNoPath:
            return []

#function to create the graph corresponding to a way
def getShortestGraphs(way : list,size : str):
    if(len(way)==0):
        return "./Icons/None.png"
    graph=Digraph(node_attr={'shape': 'box','label' : '',"style":'filled',"fillcolor":Variables.Colors["secondaryDarkColor"],"color":Variables.Colors["primaryColor"]},
                  edge_attr={'color': Variables.Colors["primaryColor"]},
                  graph_attr={'bgcolor': Variables.Colors["secondaryDarkColor"],"ratio":'1',"size":str(size/96)+","+str(size/96)+"!"})
    for i in range(len(way)-1):
        parentsList=findParents(way[i],way[i+1])
        parents="_".join(parentsList)
        if(len(parentsList)>1):
            path = ImageCrop.AssemblePalsIcons(parentsList)
        else:
            path="./Icons/"+parentsList[0]+".png"
        graph.node(str(id(way[i])),image="../Icons/"+way[i]+".png")
        graph.node(parents+str(i),image="."+path)
        graph.node(str(id(way[i+1])),image="../Icons/"+way[i+1]+".png")
        graph.edge(parents+str(i),str(id(way[i+1])))
        graph.edge(str(id(way[i])),str(id(way[i+1])))
    graph.render("./Temp/tree",format='png',cleanup=True,engine='dot',directory="./")
    return "./Temp/tree.png"