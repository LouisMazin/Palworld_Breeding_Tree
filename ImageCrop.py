from PIL import Image
from os import path,environ
import Variables
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
        
#function to assemble icons in a single image
def AssemblePalsIcons(palListe):
    variables = Variables.Variables.getInstances()
    path=resource_path("Temp\\"+"_".join(palListe)+".png")
    images = [Image.open(resource_path("Icons\\"+x+".png")) for x in palListe]
    widths, heights = zip(*(i.size for i in images))
    totalWidth = sum(widths)
    maxHeight = max(heights)
    newImage = Image.new('RGBA', (totalWidth, maxHeight))
    separator = Image.new('RGBA', (2,200), variables.Colors["primaryColor"])
    x_offset = 0
    for im in images:
        newImage.paste(im, (x_offset,0))
        x_offset += im.size[0]
        if images.index(im)<len(images)-1:
            newImage.paste(separator, (x_offset,0))
            x_offset += separator.size[0]
    newImage.save(path)
    return path

#function to resize the tree image
def ResizeTree(path, side):
    image = Image.open(resource_path(path))
    image = image.resize((side, side))
    new_path = resource_path(path.replace("Icons", "Temp"))  # if the needed tree is None.png
    image.save(new_path)
    return new_path