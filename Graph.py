import ImageCrop,Variables
from networkx import all_shortest_paths, exception, DiGraph
from graphviz import Digraph
from os import path,environ
import sys
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)
environ["PATH"] += resource_path("Graphviz\\bin")+";"

#function to get the graph of all the pals and their relations
def getPalsGraph(csvContent : dict):
    palGraph = DiGraph()
    for parent, enfants in csvContent.items():
        palGraph.add_edges_from([(parent, enfant) for enfant in enfants])
    return palGraph

#function to get all the parent2 for a combinaison of parent1 + child
def findParents(pal : str, enfant : str):
    variables = Variables.Variables.getInstances()
    secondParents=[]
    childrens=variables.csvContent[pal]
    for childrenIndex, child in enumerate(childrens):
        if child == enfant:
            secondParents.append(variables.palList[childrenIndex])
    return secondParents

#function to get the shortest ways between a parent and a child
def getShortestWays(parent : str, child : str,palGraph : DiGraph):
    variables = Variables.Variables.getInstances()
    #if no parent or child are selected
    if(parent==variables.texts[1] and child==variables.texts[2]):
        return []
    #if the parent is selected but not the child
    elif(child == variables.texts[2]):
        #get all children of the parent
        ways=[]
        for enfant in dict.fromkeys(variables.csvContent[parent]):
            ways += [[parent,enfant]]
        return ways
    #if the child is selected but not the parent
    elif(parent == variables.texts[1]):
        #get all parents of the child
        ways=[]
        for parent in variables.palList:
            if child in variables.csvContent[parent]:
                ways += [[parent,child]]
        return ways
    #if the parent and the child are selected
    elif(child in variables.csvContent[parent]):
        return [[parent,child]]
    else:
        try :
            return list(all_shortest_paths(palGraph,parent,child))
        except exception.NetworkXNoPath:
            return []
        
#function to get the graph of the shortest way between a parent and a child
def getShortestGraphs(way: list, size: str):
    variables = Variables.Variables.getInstances()
    if len(way) < 2:
        return resource_path("Icons\\None.png")
    
    graph = Digraph(node_attr={'shape': 'box','label': '',"style": 'filled',"fillcolor": variables.Colors["secondaryDarkColor"],"color": variables.Colors["primaryColor"]},
                    edge_attr={'color': variables.Colors["primaryColor"]},
                    graph_attr={'bgcolor': variables.Colors["secondaryDarkColor"],"ratio": '1',"size": str(size/96) + "," + str(size/96) + "!"})

    for i, (parent, child) in enumerate(zip(way, way[1:])):
        parentsList = findParents(parent, child)
        if len(parentsList) > 1:
            path = ImageCrop.AssemblePalsIcons(parentsList)
        else:
            path = resource_path(f"Icons\\{parentsList[0]}.png")
        
        number = str(i)
        parent0_id = parent +"0"+ number
        child_id = child + "0" + str(i+1)
        parent1_id = parent +"1"+ number
        
        graph.node(parent0_id, image=resource_path(f"Icons\\{parent}.png"))
        graph.node(parent1_id, image=path)
        graph.node(child_id, image=resource_path(f"Icons\\{child}.png"))
        
        graph.edge(parent1_id, child_id)
        graph.edge(parent0_id, child_id)

    graph.render(resource_path("Temp\\tree"), format='png', cleanup=True, engine='dot', directory="./")
    return resource_path("Temp\\tree.png")