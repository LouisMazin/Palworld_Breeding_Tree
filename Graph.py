import ImageCrop,Variables
from networkx import all_shortest_paths, exception, DiGraph
from graphviz import Digraph
from csv import reader as read
from os import path,environ
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"
        
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
    palGraph = DiGraph()
    for parent, enfants in csvContent.items():
        for enfant in enfants:
            palGraph.add_edge(parent, enfant)
    return palGraph

#function to get all the parent2 for a combinaison of parent1 + child
def findParents(pal : str, enfant : str):
    variables = Variables.Variables.getInstances()
    secondParents=[]
    childrens=getCsvContent(variables.csvPath)[pal]
    for childrenIndex in range(len(childrens)):
        if childrens[childrenIndex]==enfant:
            secondParents.append(variables.palList[childrenIndex])
    return secondParents

#function to get the shortest ways between a parent and a child
def getShortestWays(parent : str, child : str,palGraph : DiGraph):
    variables = Variables.Variables.getInstances()
    #if no parent or child are selected
    if(parent==variables.texts[1] and child==variables.texts[2]):
        return []
    #if the parent is selected but not the child
    if(child == variables.texts[2]):
        ways=[]
        for pal in variables.palList:
            try:
                ways+=list(all_shortest_paths(palGraph,parent,pal))
            except exception.NetworkXNoPath:
                pass
        return ways
    #if the child is selected but not the parent
    elif(parent == variables.texts[1]):
        ways=[]
        for pal in variables.palList:
            try:
                ways+=list(all_shortest_paths(palGraph,pal,child))
            except exception.NetworkXNoPath:
                pass
        return ways
    #if the parent and the child are selected
    elif(child in getCsvContent(variables.csvPath)[parent]):
        return [[parent,child]]
    else:
        try :
            return list(all_shortest_paths(palGraph,parent,child))
        except exception.NetworkXNoPath:
            return []
        
#function to get the graph of the shortest way between a parent and a child
def getShortestGraphs(way : list,size : str):
    variables = Variables.Variables.getInstances()
    if(len(way)==0):
        return "./Icons/None.png"
    graph=Digraph(node_attr={'shape': 'box','label' : '',"style":'filled',"fillcolor":variables.Colors["secondaryDarkColor"],"color":variables.Colors["primaryColor"]},
                edge_attr={'color': variables.Colors["primaryColor"]},
                graph_attr={'bgcolor': variables.Colors["secondaryDarkColor"],"ratio":'1',"size":str(size/96)+","+str(size/96)+"!"})
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