import MainInterface
from os import path, remove, mkdir, listdir,environ,rmdir
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
    MainInterface.execute()
    if(path.exists("Temp")):
        [remove("Temp/"+file) for file in listdir("Temp")]
    rmdir("Temp")