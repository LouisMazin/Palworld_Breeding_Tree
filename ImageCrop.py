from PIL import Image
from os import path,environ
import Variables
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"

class ImageCrop():
    def __init__(self):
        self.Variables=Variables.Variables.getInstances()
    #function to assemble icons in a single image
    def AssemblePalsIcons(self,palListe):
        path="./Temp/"+"_".join(palListe)+".png"
        images = [Image.open("./Icons/"+x+".png") for x in palListe]
        widths, heights = zip(*(i.size for i in images))
        totalWidth = sum(widths)
        maxHeight = max(heights)
        newImage = Image.new('RGBA', (totalWidth, maxHeight))
        # create an image of 200px by 1px with the colors Variables.Colors["primaryColor"]
        separator = Image.new('RGBA', (2,200), self.Variables.Colors["primaryColor"])
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
    def ResizeTree(self,path,side):
        image = Image.open(path)
        image = image.resize((side,side))
        path=path.replace("Icons","Temp")
        image.save(path)
        return path