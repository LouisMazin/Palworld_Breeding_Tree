import MainInterface,math
from os import path, remove, mkdir, listdir,environ,rmdir,_exit
environ["PATH"] += path.abspath(".\\Graphviz\\bin")+";"
if __name__ == "__main__":
    if not path.exists("Icons"):
        _exit(1)
    elif not path.exists("Graphviz"):
        _exit(1)
    elif not path.exists("data.csv"):
        _exit(1)
    elif not path.exists("options.json") :
        _exit(1)
    elif(path.exists("Temp")):
        for file in listdir("Temp"):
            remove("Temp/"+file)
    else:
        mkdir("Temp")
    MainInterface.execute()
    if(path.exists("Temp")):
        for file in listdir("Temp"):
            remove("Temp/"+file)
        rmdir("Temp")