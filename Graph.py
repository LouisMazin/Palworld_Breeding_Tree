import ImageCrop,Variables
from networkx import all_shortest_paths, exception, DiGraph
from graphviz import Digraph
from csv import reader as read
from os import path,environ
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"

class Graph():
    def __init__(self):
        self.Variables=Variables.Variables.getInstances()
        self.ImageCrop = ImageCrop.ImageCrop()
    #function to get a dict with pals and their childrens
    def getCsvContent(self,file : str):
        pals={}
        with open(file, 'r',encoding='utf-8') as f:
            reader = read(f,delimiter=',')
            for row in reader:
                pals[row[0]]=row[1:]
        return pals

    #function to get the graph of all the pals and their relations
    def getPalsGraph(self,csvContent : dict):
        G = DiGraph()
        for parent, enfants in csvContent.items():
            for enfant in enfants:
                G.add_edge(parent, enfant)
        return G

    #function to get all the parents of a child
    def findParents(self,pal : str, enfant : str):
        secondParents=[]
        childrens=self.getCsvContent(self.Variables.csvPath)[pal]
        for childrenIndex in range(len(childrens)):
            if childrens[childrenIndex]==enfant:
                secondParents.append(self.Variables.palList[childrenIndex])
        return secondParents

    #function to get the shorstests ways between a parent and a child
    def getShortestWays(self,parent : str, child : str,palGraph):
        if(parent==self.Variables.texts[1] and child==self.Variables.texts[2]):
            return []
        if(child == self.Variables.texts[2]):
            ways=[]
            for pal in self.Variables.palList:
                try:
                    ways+=list(all_shortest_paths(palGraph,parent,pal))
                except exception.NetworkXNoPath:
                    pass
            return ways
        elif(parent == self.Variables.texts[1]):
            ways=[]
            for pal in self.Variables.palList:
                try:
                    ways+=list(all_shortest_paths(palGraph,pal,child))
                except exception.NetworkXNoPath:
                    pass
            return ways
        elif(child in self.getCsvContent(self.Variables.csvPath)[parent]):
            return [[parent,child]]
        else:
            try :
                return list(all_shortest_paths(palGraph,parent,child))
            except exception.NetworkXNoPath:
                return []
    #function to get the graph of the shortest way between a parent and a child
    def getShortestGraphs(self,way : list,size : str):
        if(len(way)==0):
            return "./Icons/None.png"
        graph=Digraph(node_attr={'shape': 'box','label' : '',"style":'filled',"fillcolor":self.Variables.Colors["secondaryDarkColor"],"color":self.Variables.Colors["primaryColor"]},
                    edge_attr={'color': self.Variables.Colors["primaryColor"]},
                    graph_attr={'bgcolor': self.Variables.Colors["secondaryDarkColor"],"ratio":'1',"size":str(size/96)+","+str(size/96)+"!"})
        for i in range(len(way)-1):
            parentsList=self.findParents(way[i],way[i+1])
            parents="_".join(parentsList)
            if(len(parentsList)>1):
                path = self.ImageCrop.AssemblePalsIcons(parentsList)
            else:
                path="./Icons/"+parentsList[0]+".png"
            graph.node(str(id(way[i])),image="../Icons/"+way[i]+".png")
            graph.node(parents+str(i),image="."+path)
            graph.node(str(id(way[i+1])),image="../Icons/"+way[i+1]+".png")
            graph.edge(parents+str(i),str(id(way[i+1])))
            graph.edge(str(id(way[i])),str(id(way[i+1])))
        graph.render("./Temp/tree",format='png',cleanup=True,engine='dot',directory="./")
        return "./Temp/tree.png"