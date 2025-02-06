import json, math, pickle
from networkx import DiGraph, all_shortest_paths, exception
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from os import path
from core.variables_manager import VariablesManager

class GraphManager:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(GraphManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.graph = DiGraph()
        self.variables_manager = VariablesManager()
        self.cache_path = self.variables_manager.picklePath
        
        # Charger les données de base
        with open(path.join(self.variables_manager.rootPath,"pals.json"), encoding="utf-8") as pals:
            self.pals = json.load(pals)
            
        self.palList = list(self.pals.keys())
        self.gamelist = ['Nyafia', 'Prunelia', 'Gildane', 'Anubis', 'Incineram', 'Incineram Noct', 'Mau', 'Mau Cryst', 'Rushoar', 'Lifmunk', 'Tocotoco', 'Eikthyrdeer', 'Eikthyrdeer Terra', 'Digtoise', 'Galeclaw', 'Grizzbolt', 'Teafant', 'Direhowl', 'Gorirat', 'Gorirat Terra', 'Jolthog', 'Jolthog Cryst', 'Univolt', 'Foxparks', 'Bristla', 'Lunaris', 'Pengullet', 'Dazzi', 'Gobfin', 'Gobfin Ignis', 'Lamball', 'Jormuntide', 'Jormuntide Ignis', 'Loupmoon', 'Hangyu', 'Hangyu Cryst', 'Suzaku', 'Suzaku Aqua', 'Pyrin', 'Pyrin Noct', 'Elphidran', 'Elphidran Aqua', 'Woolipop', 'Cryolinx', 'Melpaca', 'Surfent', 'Surfent Terra', 'Cawgnito', 'Azurobe', 'Cattiva', 'Depresso', 'Fenglope', 'Reptyro', 'Reptyro Cryst', 'Maraith', 'Robinquill', 'Robinquill Terra', 'Relaxaurus', 'Relaxaurus Lux', 'Kitsun', 'Leezpunk', 'Leezpunk Ignis', 'Fuack', 'Vanwyrm', 'Vanwyrm Cryst', 'Chikipi', 'Dinossom', 'Dinossom Lux', 'Sparkit', 'Frostallion', 'Frostallion Noct', 'Mammorest', 'Mammorest Cryst', 'Felbat', 'Broncherry', 'Broncherry Aqua', 'Faleris', 'Blazamut', 'Blazamut Ryu', 'Caprity', 'Reindrix', 'Shadowbeak', 'Sibelyx', 'Vixy', 'Wixen', 'Wixen ♀','Wixen ♂', 'Wixen Noct', 'Lovander', 'Hoocrates', 'Kelpsea', 'Kelpsea Ignis', 'Killamari', 'Mozzarina', 'Wumpo', 'Wumpo Botan', 'Vaelet', 'Nitewing', 'Flopie', 'Lyleen', 'Lyleen Noct', 'Elizabee', 'Beegarde', 'Tombat', 'Mossanda', 'Mossanda Lux', 'Arsox', 'Rayhound', 'Fuddler', 'Astegon', 'Verdash', 'Foxcicle', 'Jetragon', 'Daedream', 'Tanzee', 'Blazehowl', 'Blazehowl Noct', 'Kingpaca', 'Kingpaca Cryst', 'Gumoss', 'Swee', 'Sweepa', 'Katress', 'Katress ♀','Katress ♂', 'Katress Ignis', 'Ribbuny', 'Beakon', 'Warsect', 'Warsect Terra', 'Paladius', 'Nox', 'Penking', 'Chillet', 'Chillet Ignis', 'Quivern', 'Quivern Botan', 'Helzephyr', 'Helzephyr Lux', 'Ragnahawk', 'Bushi', 'Bushi Noct', 'Celaray', 'Necromus', 'Petallia', 'Grintale', 'Cinnamoth', 'Menasting', 'Menasting Terra', 'Orserk', 'Cremis', 'Dumud', 'Flambelle', 'Rooby', 'Bellanoir', 'Bellanoir Libero', 'Selyne', 'Croajiro', 'Lullu', 'Shroomer', 'Shroomer Noct', 'Kikit', 'Sootseer', 'Prixter', 'Knocklem', 'Yakumo', 'Dogen', 'Dazemu', 'Mimog', 'Xenovader', 'Xenogard', 'Xenolord ', 'Nitemary', 'Starryon', 'Silvegis', 'Smokie', 'Celesdir', 'Omascul', 'Splatterina', 'Tarantriss', 'Azurmane', 'Foxparks Cryst', 'Caprity Noct', 'Ribbuny Botan', 'Loupmoon Cryst', 'Kitsun Noct', 'Dazzi Noct', 'Cryolinx Terra', 'Fenglope Lux', 'Faleris Aqua', 'Bastigor']
        self.only_himself = [pal for pal in self.pals if self.pals[pal]["onlyHimself"]]
        self.exceptions = {pal: self.pals[pal]["exception"] for pal in self.pals if self.pals[pal]["exception"]}
        self.couplesMaked = []
        #dict of pal with exceptions, who have " m" or " f" in their exception palNames
        self.exceptionsGender = {pal: [self.pals[pal]["exception"][0].replace(" f","").replace(" m",""),self.pals[pal]["exception"][1].replace(" f","").replace(" m","")] for pal in self.pals if self.pals[pal]["exception"] and (" m" in self.pals[pal]["exception"][0] or " f" in self.pals[pal]["exception"][0])}
        self.pals_without_exceptions = [pal for pal in self.pals if pal not in self.exceptions and pal not in self.only_himself]
        self.pals_without_exceptions.sort(key=lambda x: self.pals[x]["value"])

        # Essayer de charger le graphe depuis le cache
        if self._load_cached_graph():
            self._initialized = True
            return

        # Si pas de cache, construire le graphe en parallèle
        self.buildGraph()
        self._save_graph_cache()
        self._initialized = True

    def _load_cached_graph(self) -> bool:
        """Charge le graphe depuis le cache s'il existe"""
        try:
            if path.exists(self.cache_path):
                with open(self.cache_path, 'rb') as f:
                    self.graph = pickle.load(f)
                return True
        except:
            pass
        return False

    def _save_graph_cache(self):
        """Sauvegarde le graphe dans le cache"""
        with open(self.cache_path, 'wb') as f:
            pickle.dump(self.graph, f)

    def buildGraph(self):
        """Construit le graphe en utilisant plusieurs threads"""
            
        # Attendre et fusionner les résultats
        for edge in self.getEdges():
            parent1, child, data = edge
            if self.graph.has_edge(parent1, child):
                existing_data = self.graph.get_edge_data(parent1, child)
                if isinstance(existing_data['secondParent'], list):
                    existing_data['secondParent'].extend(data['secondParent'])
                else:
                    existing_data['secondParent'] = [existing_data['secondParent']] + data['secondParent']
            else:
                self.graph.add_edge(parent1, child, **data)

    def getEdges(self):
        """Traite un sous-ensemble d'indices pour la construction du graphe"""
        edges = []
        for i in range(len(self.pals)):
            parent1 = self.palList[i]
            for j in range(len(self.pals)):
                parent2 = self.palList[j]
                if parent1 == parent2:
                    edges.append((parent1, parent2, {'secondParent': [parent2]}))
                    continue
                if (parent1, parent2) in self.couplesMaked:
                    continue
                
                self.couplesMaked.append((parent1, parent2))
                self.couplesMaked.append((parent2, parent1))
                
                genre = {}
                
                if [parent1, parent2] in self.exceptions.values() or [parent2, parent1] in self.exceptions.values():
                    child = [key for key, value in self.exceptions.items() if [parent1,parent2] == value or [parent2,parent1] == value]
                elif [parent1, parent2] in self.exceptionsGender.values() or [parent2, parent1] in self.exceptionsGender.values():
                    child = [key for key, value in self.exceptionsGender.items() if [parent1,parent2] == value or [parent2,parent1] == value]
                    genre = [{parent1 : self.exceptions[c][0].split(" ")[-1], parent2 : self.exceptions[c][1].split(" ")[-1]} for c in child]
                    childWithoutGenre = self.findChild(parent1, parent2)
                    if len(childWithoutGenre) > 1:
                        for c in childWithoutGenre:
                            edges.append((parent1, c, {'secondParent': [parent2], 'genre': {}}))
                            edges.append((parent2, c, {'secondParent': [parent1], 'genre': {}}))
                    else:
                        edges.append((parent1, childWithoutGenre[0], {'secondParent': [parent2], 'genre': {}}))
                        edges.append((parent2, childWithoutGenre[0], {'secondParent': [parent1], 'genre': {}}))
                else:
                    child = self.findChild(parent1, parent2)

                if len(child) > 1:
                    for c, g in zip(child, genre):
                        edges.append((parent1, c, {'secondParent': [parent2], 'genre': g}))
                        edges.append((parent2, c, {'secondParent': [parent1], 'genre': g}))
                else:
                    edges.append((parent1, child[0], {'secondParent': [parent2], 'genre': genre}))
                    edges.append((parent2, child[0], {'secondParent': [parent1], 'genre': genre}))
                    
        return edges
    
    def findChild(self, parent1,parent2):
        childValue = math.floor((self.pals[parent1]["value"] + self.pals[parent2]["value"]+1)/2)
        closest=["Chikipi"]
        for pal in self.pals_without_exceptions:
            if abs(self.pals[pal]["value"] - childValue) < abs(self.pals[closest[0]]["value"] - childValue):
                closest = [pal]
            elif abs(self.pals[pal]["value"] - childValue) == abs(self.pals[closest[0]]["value"] - childValue):
                closest.append(pal)
        if(len(closest) > 1):
            return [min(closest,key=lambda x: self.gamelist.index(x))]
        else:
            return [closest[0]]

    def getShortestWays(self, parent : str, child : str):
        if(child == ""):
            ways=[]
            for enfant in self.get_children(parent):
                ways += [[parent,enfant]]
            return ways
        #if the child is selected but not the parent
        elif(parent == ""):
            #get all parents of the child
            ways=[]
            for parent in self.pals:
                if (child in self.get_children(parent) and child not in self.exceptionsGender and (len(self.getSecondParents(parent,child)[0]) >1 or [self.getSecondParents(parent,child)[0][0],child] not in ways)) or (child in self.get_children(parent) and child in self.exceptionsGender and [self.getSecondParents(parent,child)[0][0].replace(" f","").replace(" m",""),child] not in ways):
                    ways += [[parent,child]]
            return ways
        #if the parent and the child are selected
        elif(child in self.get_children(parent)):
            return [[parent,child]]
        else:
            try :
                return list(all_shortest_paths(self.graph,parent,child))
            except exception.NetworkXNoPath:
                return []
    
    def get_graph(self):
        return self.graph

    def get_children(self, parent):
        return list(self.graph.successors(parent))

    def get_parents(self, pal_name):
        # Récupérer toutes les combinaisons et les normaliser
        combinations = self.get_parents_combinations(pal_name)
        # Créer un dictionnaire pour regrouper les partenaires
        parent_groups = {}
        
        for p1, p2 in combinations:
            # Ajouter p1 comme parent principal
            if p1 not in parent_groups:
                parent_groups[p1] = set()
            parent_groups[p1].add(p2)
            
            # Ajouter p2 comme parent principal
            if p2 not in parent_groups:
                parent_groups[p2] = set()
            parent_groups[p2].add(p1)

        # Convertir en liste de tuples (parent, [partenaires])
        return [(parent, list(partners)) for parent, partners in parent_groups.items()]

    def get_parents_combinations(self, pal_name):
        combinations = set()
        for parent in sorted(self.graph.predecessors(pal_name), key=lambda x: x.lower()):
            second_parents = self.graph.edges.get((parent, pal_name), {}).get("secondParent", [])
            # Convertir en liste si ce n'est pas déjà une liste
            if not isinstance(second_parents, list):
                second_parents = [second_parents]
            for second_parent in second_parents:
                pair = tuple(sorted([parent, second_parent]))
                combinations.add(pair)
        return sorted(list(combinations))

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