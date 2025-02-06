from graphviz import Digraph
from core.variables_manager import VariablesManager
from core.graph_manager import GraphManager
from PIL import Image
from os import path

class TreeManager:
    def __init__(self):
        self.variablesManager = VariablesManager()
        self.graphManager = GraphManager()
        self.iconsPath = self.variablesManager.iconsPath
        self.cachePath = self.variablesManager.cachePath
        self.imagesCache = {}

    def getNoneImage(self):
        return path.join(
            self.iconsPath,
            "DarkNone.png" if self.variablesManager.getConfig("darkMode") else "LightNone.png"
        )

    def AssemblePalsIcons(self, parentsList):
        # Créer une clé de cache unique pour cette combinaison
        cacheKey = "_".join(sorted(parentsList))
        if cacheKey in self.imagesCache:
            return self.imagesCache[cacheKey]

        destPath = path.join(self.cachePath,cacheKey+".png")
        images = []
        
        # Charger toutes les images en une fois
        for x in parentsList:
            imagePath = self.getGenderImage(x) if (" f" in x or " m" in x) else path.join(self.iconsPath,x+".png")
            images.append(Image.open(imagePath))

        # Limiter le nombre de parents secondaires à 4 par ligne
        rows = [images[i:i + 4] for i in range(0, len(images), 4)]
        # Calculer les dimensions une seule fois
        totalWidth = max(sum(im.size[0] for im in row) + (len(row) - 1) * 2 for row in rows)  # 2 pixels pour le séparateur
        totalHeight = sum(max(im.size[1] for im in row) for row in rows) + (len(rows) - 1) * 2  # 2 pixels pour le séparateur

        # Créer l'image finale et les séparateurs
        newImage = Image.new('RGBA', (totalWidth, totalHeight))
        separator = Image.new('RGBA', (2, 100), self.variablesManager.getColor("primaryColor"))
        horizontalSeparator = Image.new('RGBA', (totalWidth, 2), self.variablesManager.getColor("primaryColor"))

        # Assembler les images en ajoutant les nouvelles lignes en haut
        yOffset = totalHeight
        for row in reversed(rows):
            yOffset -= max(rowImage.size[1] for rowImage in row)
            xOffset = 0
            for idx, image in enumerate(row):
                newImage.paste(image, (xOffset, yOffset))
                xOffset += image.size[0]
                if idx < len(row) - 1 or len(row) < len(rows[0]):
                    newImage.paste(separator, (xOffset, yOffset))
                    xOffset += 2
            yOffset -= 2
            if row != rows[0]:
                newImage.paste(horizontalSeparator, (0, yOffset))

        newImage.save(destPath)
        self.imagesCache[cacheKey] = destPath
        return destPath

    def getGenderImage(self, pal):
        if pal in self.imagesCache:
            return self.imagesCache[pal]

        destPath = path.join(self.cachePath,pal + ".png")
        basePal = pal.replace(" f", "").replace(" m", "")
        gender = pal.split(" ")[1]
        palImage = Image.open(path.join(self.iconsPath,basePal + ".png"))
        genderImage = Image.open(path.join(self.iconsPath,gender + ".png")).reduce(10)
        
        newImage = Image.new('RGBA', palImage.size)
        newImage.paste(palImage, (0, 0))
        newImage.paste(genderImage, (0, 0), genderImage)
        newImage.save(destPath, "PNG")
        
        self.imagesCache[pal] = destPath
        return destPath

    def getShortestGraphs(self, way: list, size: str):
        if len(way) < 2:
            return self.getNoneImage()

        graph = Digraph(
            node_attr={
                'shape': 'box',
                'label': '',
                "style": 'filled',
                "fillcolor": 'transparent',
                "color": self.variablesManager.getColor("primaryColor")
            },
            edge_attr={'color': self.variablesManager.getColor("primaryColor")},
            graph_attr={
                "bgcolor": 'transparent',
                "ratio": '1',
                "size": f"{size/96},{size/96}!"
            }
        )
        # Préparer toutes les images nécessaires en une seule fois
        nodesToCreate = {}
        for i, (parent, child) in enumerate(zip(way, way[1:])):
            parentsList, gender = self.graphManager.getSecondParents(parent, child)
            
            # Parent principal
            parentId = f"{parent}0{i}"
            if gender is not None:
                parentWithGender = f"{parent} {gender}"
                nodesToCreate[parentId] = self.getGenderImage(parentWithGender)
            else:
                nodesToCreate[parentId] = path.join(self.iconsPath,parent+".png")

            # Second parent
            parent1Id = f"{parent}1{i}"
            if len(parentsList) > 1:
                nodesToCreate[parent1Id] = self.AssemblePalsIcons(parentsList)
            else:
                pal = parentsList[0]
                if " f" in pal or " m" in pal:
                    nodesToCreate[parent1Id] = self.getGenderImage(pal)
                else:
                    nodesToCreate[parent1Id] = path.join(self.iconsPath,pal+".png")

            # Enfant
            childId = f"{child}0{i+1}"
            nodesToCreate[childId] = path.join(self.iconsPath,child+".png")

        # Créer tous les nœuds
        for nodeId, imagePath in nodesToCreate.items():
            graph.node(nodeId, image=imagePath)

        # Créer toutes les arêtes
        for i, (parent, child) in enumerate(zip(way, way[1:])):
            parent0Id = f"{parent}0{i}"
            parent1Id = f"{parent}1{i}"
            childId = f"{child}0{i+1}"
            graph.edge(parent1Id, childId)
            graph.edge(parent0Id, childId)

        outputPath = path.join(self.cachePath,"tree")
        graph.render(outputPath, format='png', cleanup=True, engine='dot', directory="./")
        return outputPath+".png"