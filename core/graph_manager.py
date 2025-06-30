import json, math, pickle
from networkx import DiGraph, all_shortest_paths, exception
from os import path
from core.variables_manager import VariablesManager

class GraphManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraphManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.graph = DiGraph()
        self.variablesManager = VariablesManager()
        self.cachePath = self.variablesManager.picklePath
        
        # Charger les données de base
        with open(path.join(self.variablesManager.rootPath,"pals.json"), encoding="utf-8") as pals:
            self.jsonPals = json.load(pals)
            
        self.palList = list(self.jsonPals.keys())
        self.gameList = ["Nyafia","Prunelia","Gildane","Turtacle","Turtacle Terra","Anubis","Incineram","Incineram Noct","Mau","Mau Cryst","Rushoar","Lifmunk","Tocotoco","Eikthyrdeer","Eikthyrdeer Terra","Digtoise","Galeclaw","Grizzbolt","Teafant","Direhowl","Gorirat","Gorirat Terra","Jolthog","Jolthog Cryst","Univolt","Foxparks","Bristla","Lunaris","Pengullet","Pengullet Lux","Dazzi","Gobfin","Gobfin Ignis","Lamball","Jormuntide","Jormuntide Ignis","Loupmoon","Hangyu","Hangyu Cryst","Suzaku","Suzaku Aqua","Pyrin","Pyrin Noct","Elphidran","Elphidran Aqua","Woolipop","Cryolinx","Melpaca","Surfent","Surfent Terra","Cawgnito","Azurobe","Azurobe Cryst","Cattiva","Depresso","Fenglope","Reptyro","Reptyro Cryst","Maraith","Robinquill","Robinquill Terra","Relaxaurus","Relaxaurus Lux","Kitsun","Leezpunk","Leezpunk Ignis","Fuack","Fuack Ignis","Vanwyrm","Vanwyrm Cryst","Chikipi","Dinossom","Dinossom Lux","Sparkit","Frostallion","Frostallion Noct","Mammorest","Mammorest Cryst","Felbat","Broncherry","Broncherry Aqua","Faleris","Blazamut","Blazamut Ryu","Caprity","Reindrix","Shadowbeak","Sibelyx","Vixy","Wixen","Wixen Noct","Lovander","Hoocrates","Kelpsea","Kelpsea Ignis","Killamari","Killamari Primo","Mozzarina","Wumpo","Wumpo Botan","Vaelet","Nitewing","Flopie","Lyleen","Lyleen Noct","Elizabee","Beegarde","Tombat","Mossanda","Mossanda Lux","Arsox","Rayhound","Fuddler","Astegon","Verdash","Foxcicle","Jetragon","Daedream","Tanzee","Blazehowl","Blazehowl Noct","Kingpaca","Kingpaca Cryst","Gumoss","Swee","Sweepa","Katress","Katress Ignis","Ribbuny","Beakon","Warsect","Warsect Terra","Paladius","Nox","Penking","Penking Lux","Chillet","Chillet Ignis","Quivern","Quivern Botan","Helzephyr","Helzephyr Lux","Ragnahawk","Bushi","Bushi Noct","Celaray","Celaray Lux","Necromus","Petallia","Grintale","Cinnamoth","Menasting","Menasting Terra","Orserk","Cremis","Dumud","Dumud Gild","Flambelle","Rooby","Bellanoir","Bellanoir Libero","Selyne","Croajiro","Croajiro Noct","Lullu","Shroomer","Shroomer Noct","Kikit","Sootseer","Prixter","Knocklem","Yakumo","Dogen","Dazemu","Mimog","Xenovader","Xenogard","Xenolord","Nitemary","Starryon","Silvegis","Smokie","Celesdir","Omascul","Splatterina","Tarantriss","Azurmane","Gloopie","Whalaska","Whalaska Ignis","Jelliette","Foxparks Cryst","Caprity Noct","Ribbuny Botan","Loupmoon Cryst","Kitsun Noct","Dazzi Noct","Cryolinx Terra","Fenglope Lux","Faleris Aqua","Bastigor","Ghangler","Ghangler Ignis","Icelyn","Herbil","Munchill","Finsider","Finsider Ignis","Polapup","Braloha","Palumba","Frostplume","Jellroy","Neptilius","Green Slime","Blue Slime","Red Slime","Purple Slime","Illuminant Slime","Rainbow Slime","Enchanted Sword","Cave Bat","Illuminant Bat","Eye of Cthulhu","Demon Eye"]
        self.onlyHimself = [pal for pal in self.jsonPals if self.jsonPals[pal]["onlyHimself"]]
        self.exceptions = {pal: self.jsonPals[pal]["exception"] for pal in self.jsonPals if self.jsonPals[pal]["exception"]}
        self.couplesMaked = []
        self.exceptionsGender = self.getExceptionsGender()
        self.palsWithoutExceptions = [pal for pal in self.jsonPals if pal not in self.exceptions and pal not in self.onlyHimself]
        self.palsWithoutExceptions.sort(key=lambda x: self.jsonPals[x]["value"])

        # Essayer de charger le graphe depuis le cache
        if self.loadCachedGraph():
            self._initialized = True
            return

        # Si pas de cache, construire le graphe en parallèle
        self.buildGraph()
        self.saveGraphCache()
        self._initialized = True

    def getExceptionsGender(self):
        res = {}
        for pal, exception in self.exceptions.items():
            if type(exception[0]) is list:
                val = []
                for e in exception:
                    if " m" in e[0] or " m" in e[1] or " f" in e[0] or " f" in e[1]:
                        val.append([e[0].replace(" f","").replace(" m",""), e[1].replace(" f","").replace(" m","")])
                if(val):
                    if(len(val) == 1):
                        res[pal] = val[0]
                    else:
                        res[pal] = val
            else:
                if " m" in exception[0] or " m" in exception[1] or " f" in exception[0] or " f" in exception[1]:
                    res[pal] = [exception[0].replace(" f","").replace(" m",""), exception[1].replace(" f","").replace(" m","")]
        return res

    def loadCachedGraph(self) -> bool:
        """Charge le graphe depuis le cache s'il existe"""
        try:
            if path.exists(self.cachePath):
                with open(self.cachePath, 'rb') as f:
                    self.graph = pickle.load(f)
                return True
        except:
            pass
        return False

    def saveGraphCache(self):
        """Sauvegarde le graphe dans le cache"""
        with open(self.cachePath, 'wb') as f:
            pickle.dump(self.graph, f)

    def buildGraph(self):
        """Construit le graphe en utilisant plusieurs threads"""
            
        # Attendre et fusionner les résultats
        for edge in self.getEdges():
            parent1, child, data = edge
            if self.graph.has_edge(parent1, child):
                existingData = self.graph.get_edge_data(parent1, child)
                if isinstance(existingData['secondParent'], list):
                    existingData['secondParent'].extend(data['secondParent'])
                else:
                    existingData['secondParent'] = [existingData['secondParent']] + data['secondParent']
            else:
                self.graph.add_edge(parent1, child, **data)

    def getEdges(self):
        """Traite un sous-ensemble d'indices pour la construction du graphe"""
        edges = []
        for i in range(len(self.jsonPals)):
            parent1 = self.palList[i]
            for j in range(len(self.jsonPals)):
                parent2 = self.palList[j]
                if parent1 == parent2:
                    edges.append((parent1, parent2, {'secondParent': [parent2]}))
                    continue
                if (parent1, parent2) in self.couplesMaked:
                    continue
                
                self.couplesMaked.append((parent1, parent2))
                self.couplesMaked.append((parent2, parent1))
                
                genre = {}
                
                # Helper function to check if a parent pair exists in exception values
                def check_parents_in_exceptions(exceptions_dict):
                    matching_keys = []
                    for key, value in exceptions_dict.items():
                        if isinstance(value[0], list):  # Nested list case
                            for pair in value:
                                if ([parent1, parent2] == pair or [parent2, parent1] == pair):
                                    matching_keys.append(key)
                        else:  # Simple list case
                            if ([parent1, parent2] == value or [parent2, parent1] == value):
                                matching_keys.append(key)
                    return matching_keys
                
                # Check exceptions
                exception_matches = check_parents_in_exceptions(self.exceptions)
                if exception_matches:
                    childs = exception_matches
                # Check exceptionsGender
                elif check_parents_in_exceptions(self.exceptionsGender):
                    childs = check_parents_in_exceptions(self.exceptionsGender)
                    
                    # Build genre information
                    genre_list = []
                    for c in childs:
                        exception_data = self.exceptions[c]
                        if isinstance(exception_data[0], list):  # Nested list case
                            for pair in exception_data:
                                if ([parent1, parent2] == [p.replace(" f","").replace(" m","") for p in pair] or 
                                    [parent2, parent1] == [p.replace(" f","").replace(" m","") for p in pair]):
                                    genre_list.append({parent1: pair[0].split(" ")[-1], parent2: pair[1].split(" ")[-1]})
                                    break
                        else:  # Simple list case
                            if ([parent1, parent2] == [exception_data[0].replace(" f","").replace(" m",""), exception_data[1].replace(" f","").replace(" m","")] or
                                [parent2, parent1] == [exception_data[0].replace(" f","").replace(" m",""), exception_data[1].replace(" f","").replace(" m","")]):
                                genre_list.append({parent1: exception_data[0].split(" ")[-1], parent2: exception_data[1].split(" ")[-1]})
                    
                    genre = genre_list
                    
                    childWithoutGenre = self.findChild(parent1, parent2)
                    if len(childWithoutGenre) > 1:
                        for child in childWithoutGenre:
                            edges.append((parent1, child, {'secondParent': [parent2], 'genre': {}}))
                            edges.append((parent2, child, {'secondParent': [parent1], 'genre': {}}))
                    else:
                        edges.append((parent1, childWithoutGenre[0], {'secondParent': [parent2], 'genre': {}}))
                        edges.append((parent2, childWithoutGenre[0], {'secondParent': [parent1], 'genre': {}}))
                else:
                    childs = self.findChild(parent1, parent2)

                if len(childs) > 1:
                    for child, g in zip(childs, genre):
                        edges.append((parent1, child, {'secondParent': [parent2], 'genre': g}))
                        edges.append((parent2, child, {'secondParent': [parent1], 'genre': g}))
                else:
                    edges.append((parent1, childs[0], {'secondParent': [parent2], 'genre': genre}))
                    edges.append((parent2, childs[0], {'secondParent': [parent1], 'genre': genre}))
                    
        return edges
    
    def findChild(self, parent1,parent2):
        childValue = math.floor((self.jsonPals[parent1]["value"] + self.jsonPals[parent2]["value"]+1)/2)
        closest=["Chikipi"]
        for pal in self.palsWithoutExceptions:
            if abs(self.jsonPals[pal]["value"] - childValue) < abs(self.jsonPals[closest[0]]["value"] - childValue):
                closest = [pal]
            elif abs(self.jsonPals[pal]["value"] - childValue) == abs(self.jsonPals[closest[0]]["value"] - childValue):
                closest.append(pal)
        if(len(closest) > 1):
            return [min(closest,key=lambda x: self.gameList.index(x))]
        else:
            return [closest[0]]

    def getShortestWays(self, parent : str, child : str):
        if(child == ""):
            ways=[]
            for enfant in self.getChildrens(parent):
                ways += [[parent,enfant]]
            return ways
        #if the child is selected but not the parent
        elif(parent == ""):
            #get all parents of the child
            ways=[]
            for parent in self.jsonPals:
                if (child in self.getChildrens(parent) and child not in self.exceptionsGender and (len(self.getSecondParents(parent,child)[0]) >1 or [self.getSecondParents(parent,child)[0][0],child] not in ways)) or (child in self.getChildrens(parent) and child in self.exceptionsGender and [self.getSecondParents(parent,child)[0][0].replace(" f","").replace(" m",""),child] not in ways):
                    ways += [[parent,child]]
            return ways
        #if the parent and the child are selected
        elif(child in self.getChildrens(parent)):
            return [[parent,child]]
        else:
            try :
                return list(all_shortest_paths(self.graph,parent,child))
            except exception.NetworkXNoPath:
                return []
    

    def getChildrens(self, parent):
        return list(self.graph.successors(parent))

    def getSecondParents(self, parent, child):
        # return the second parents of the child added to their genre if they have one
        secondParents = self.graph.edges.get((parent, child), {}).get("secondParent", [])
        if not isinstance(secondParents, list):
            secondParents = [secondParents]
        genre = self.graph.edges.get((parent, child), {}).get("genre", {})
        add=""
        gender = None
        if(genre):
            add = " "+genre[secondParents[0]]
            gender = genre[parent]
        return [secondParent+add for secondParent in secondParents],gender
