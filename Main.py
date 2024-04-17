import Interface,os
    
if __name__ == "__main__":
    #check if Graphviz/bin is in the PATH
    os.environ["PATH"] += os.pathsep + os.path.abspath(os.path.join(os.path.dirname(__file__), 'Graphviz/bin'))
    if(os.path.exists("Icons")!=True):
        print("Icons folder not found")
    if(os.path.exists("Graphviz")!=True):
        print("Graphviz folder not found")
    if(os.path.exists("Temp")):
        [os.remove("Temp/"+file) for file in os.listdir("Temp")]
    else:
        os.mkdir("Temp")
    if not os.path.exists("Trees"):
        os.mkdir("Trees")
    Interface.execute()