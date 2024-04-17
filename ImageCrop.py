import Variables,PIL
from os import environ,path as osPath
environ["PATH"] += osPath.abspath("./Graphviz/bin")+";"
##This file contains function to manipulate images
##
##It uses the Icons directory

#function to assemble icons in a single image
def AssemblePalsIcons(palListe):
    path="./Temp/"+"_".join(palListe)+".png"
    images = [PIL.Image.open("./Icons/"+x+".png") for x in palListe]
    widths, heights = zip(*(i.size for i in images))
    totalWidth = sum(widths)
    maxHeight = max(heights)
    newImage = PIL.Image.new('RGBA', (totalWidth, maxHeight))
    separator=PIL.Image.open("./Icons/Separation.png")
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
def ResizeTree(path):
    image = PIL.Image.open(path)
    image = image.resize((Variables.arbreSide,Variables.arbreSide))
    image.save(path)
    return path