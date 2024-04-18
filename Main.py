import Interface
from os import path, remove, mkdir, listdir,environ
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"
if __name__ == "__main__":
    if(path.exists("Icons")!=True):
        print("Icons folder not found")
    if(path.exists("Graphviz")!=True):
        print("Graphviz folder not found")
    if(path.exists("Temp")):
        [remove("Temp/"+file) for file in listdir("Temp")]
    else:
        mkdir("Temp")
    if not path.exists("Trees"):
        mkdir("Trees")
    Interface.execute()