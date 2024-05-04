import MainInterface
from os import path, remove, mkdir, listdir,environ,rmdir,_exit
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"
if __name__ == "__main__":
    if(path.exists("Icons")!=True):
        _exit(1)
    if(path.exists("Graphviz")!=True):
        _exit(1)
    if(path.exists("data.csv")!=True):
        _exit(1)
    if(path.exists("options.json")!=True):
        _exit(1)
    if(path.exists("Temp")):
        [remove("Temp/"+file) for file in listdir("Temp")]
    else:
        mkdir("Temp")
    MainInterface.execute()
    if(path.exists("Temp")):
        [remove("Temp/"+file) for file in listdir("Temp")]
    rmdir("Temp")