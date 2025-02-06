from graphviz import Digraph
from core.variables_manager import VariablesManager
from core.graph_manager import GraphManager
from PIL import Image
from os import path

class TreeManager:
    def __init__(self):
        self.image_cache = {}  # Cache pour stocker les images déjà générées
        self.variables = VariablesManager()
        self.graph_manager = GraphManager()
        self.iconsPath = self.variables.iconsPath
        self.cachePath = self.variables._get_cache_path()

    def getNoneImage(self):
        return path.join(
            self.iconsPath,
            "DarkNone.png" if self.variables.config["darkMode"] else "LightNone.png"
        )

    def AssemblePalsIcons(self, parentsList):
        # Créer une clé de cache unique pour cette combinaison
        cache_key = "_".join(sorted(parentsList))
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        destPath = path.join(self.cachePath,cache_key+".png")
        images = []
        
        # Charger toutes les images en une fois
        for x in parentsList:
            img_path = self.getGenderImage(x) if (" f" in x or " m" in x) else path.join(self.iconsPath,x+".png")
            images.append(Image.open(img_path))

        # Limiter le nombre de parents secondaires à 4 par ligne
        rows = [images[i:i + 4] for i in range(0, len(images), 4)]
        # Calculer les dimensions une seule fois
        total_width = max(sum(im.size[0] for im in row) + (len(row) - 1) * 2 for row in rows)  # 2 pixels pour le séparateur
        total_height = sum(max(im.size[1] for im in row) for row in rows) + (len(rows) - 1) * 2  # 2 pixels pour le séparateur

        # Créer l'image finale et les séparateurs
        new_image = Image.new('RGBA', (total_width, total_height))
        separator = Image.new('RGBA', (2, 100), self.variables.Colors["primaryColor"])
        horizontal_separator = Image.new('RGBA', (total_width, 2), self.variables.Colors["primaryColor"])

        # Assembler les images en ajoutant les nouvelles lignes en haut
        y_offset = total_height
        for row in reversed(rows):
            y_offset -= max(im.size[1] for im in row)
            x_offset = 0
            for idx, im in enumerate(row):
                new_image.paste(im, (x_offset, y_offset))
                x_offset += im.size[0]
                if idx < len(row) - 1 or len(row) < len(rows[0]):
                    new_image.paste(separator, (x_offset, y_offset))
                    x_offset += 2
            y_offset -= 2
            if row != rows[0]:
                new_image.paste(horizontal_separator, (0, y_offset))

        new_image.save(destPath)
        self.image_cache[cache_key] = destPath
        return destPath

    def getGenderImage(self, pal):
        if pal in self.image_cache:
            return self.image_cache[pal]

        destPath = path.join(self.cachePath,pal + ".png")
        base_pal = pal.replace(" f", "").replace(" m", "")
        gender = pal.split(" ")[1]
        pal_image = Image.open(path.join(self.iconsPath,base_pal + ".png"))
        gender_image = Image.open(path.join(self.iconsPath,gender + ".png")).reduce(10)
        
        new_image = Image.new('RGBA', pal_image.size)
        new_image.paste(pal_image, (0, 0))
        new_image.paste(gender_image, (0, 0), gender_image)
        new_image.save(destPath, "PNG")
        
        self.image_cache[pal] = destPath
        return destPath

    def getShortestGraphs(self, way: list, size: str):
        if len(way) < 2:
            return self.getNoneImage()

        graph = Digraph(
            node_attr={
                'shape': 'box',
                'label': '',
                "style": 'filled',
                "fillcolor": self.variables.Colors["secondaryDarkColor"],
                "color": self.variables.Colors["primaryColor"]
            },
            edge_attr={'color': self.variables.Colors["primaryColor"]},
            graph_attr={
                "bgcolor": 'transparent',
                "ratio": '1',
                "size": f"{size/96},{size/96}!"
            }
        )
        # Préparer toutes les images nécessaires en une seule fois
        nodes_to_create = {}
        for i, (parent, child) in enumerate(zip(way, way[1:])):
            parentsList, gender = self.graph_manager.getSecondParents(parent, child)
            
            # Parent principal
            parent_id = f"{parent}0{i}"
            if gender is not None:
                parent_with_gender = f"{parent} {gender}"
                nodes_to_create[parent_id] = self.getGenderImage(parent_with_gender)
            else:
                nodes_to_create[parent_id] = path.join(self.iconsPath,parent+".png")

            # Second parent
            parent1_id = f"{parent}1{i}"
            if len(parentsList) > 1:
                nodes_to_create[parent1_id] = self.AssemblePalsIcons(parentsList)
            else:
                pal = parentsList[0]
                if " f" in pal or " m" in pal:
                    nodes_to_create[parent1_id] = self.getGenderImage(pal)
                else:
                    nodes_to_create[parent1_id] = path.join(self.iconsPath,pal+".png")

            # Enfant
            child_id = f"{child}0{i+1}"
            nodes_to_create[child_id] = path.join(self.iconsPath,child+".png")

        # Créer tous les nœuds
        for node_id, image_path in nodes_to_create.items():
            graph.node(node_id, image=image_path)

        # Créer toutes les arêtes
        for i, (parent, child) in enumerate(zip(way, way[1:])):
            parent0_id = f"{parent}0{i}"
            parent1_id = f"{parent}1{i}"
            child_id = f"{child}0{i+1}"
            graph.edge(parent1_id, child_id)
            graph.edge(parent0_id, child_id)

        output_path = path.join(self.cachePath,"tree")
        graph.render(output_path, format='png', cleanup=True, engine='dot', directory="./")
        return output_path+".png"
