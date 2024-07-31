import MainInterface,sys
from os import path, remove, mkdir, listdir,environ,rmdir

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)
environ["PATH"] += resource_path("Graphviz\\bin")+";"
if __name__ == "__main__":
    temp = resource_path("Temp")
    if(path.exists(temp)):
        for file in listdir(temp):
            remove(temp+"/"+file)
    else:
        mkdir(temp)
    MainInterface.execute()
    if(path.exists(temp)):
        for file in listdir(temp):
            remove(temp+"/"+file)
        rmdir(temp)