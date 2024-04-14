import networkx,Variables,graphviz,ImageCrop,csv

##This file contains function to get the list of all shortests
##ways between two pals
##
##It uses breed.csv and return a list of png paths

#function to get a dict with pals and their childrens
def getCsvContent(file : str):
    pals={}
    with open(file, 'r',encoding='utf-8') as f:
        reader = csv.reader(f,delimiter=',')
        for row in reader:
            pals[row[0]]=row[1:]
    return pals

#function to get the graph of all the pals and their relations
def getPalsGraph(csvContent : dict):
    G = networkx.DiGraph()
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
def getShortestWays(parent : str, child : str):
    if(parent=="Select a parent" or child=="Select a child"):
        return []
    if(child in getCsvContent(Variables.csvPath)[parent]):
        return [[parent,child]]
    else:
        try :
            return list(networkx.all_shortest_paths(getPalsGraph(getCsvContent(Variables.csvPath)),parent,child))
        except networkx.exception.NetworkXNoPath:
            return []

#function to create the graph corresponding to a way
def getShortestGraphs(way : list,nbr : int):
    if(len(way)==0):
        return "./Icons/None.png"
    graph=graphviz.Digraph()
    graph.attr(ratio='1',fixedsize='true',size='9')
    for i in range(len(way)-1):
        parentsList=findParents(way[i],way[i+1])
        parents="_".join(parentsList)
        if(len(parentsList)>1):
            path = ImageCrop.AssemblePalsIcons(parentsList)
        else:
            path="./Icons/"+parentsList[0]+".png"
        graph.node(str(id(way[i])),shape='box',image="../Icons/"+way[i]+".png",label="")
        graph.node(parents+str(i),shape='box',image="."+path,label="")
        graph.node(str(id(way[i+1])),shape='box',image="../Icons/"+way[i+1]+".png",label="")
        graph.edge(parents+str(i),str(id(way[i+1])))
        graph.edge(str(id(way[i])),str(id(way[i+1])))
    graphPath="./Trees/"+way[0]+"_to_"+way[-1]+"_n_"+str(nbr)
    graph.render(graphPath, format='png', cleanup=True, engine='dot')
    return graphPath+".png"