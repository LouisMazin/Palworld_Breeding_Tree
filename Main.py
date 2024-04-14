import Interface,os
    
if __name__ == "__main__":
    if(os.path.exists("Icons")!=True):
        print("Icons folder not found")
    if(os.path.exists("Temp")):
        [os.remove("Temp/"+file) for file in os.listdir("Temp")]
    else:
        os.mkdir("Temp")
    if not os.path.exists("Trees"):
        os.mkdir("Trees")
    Interface.execute()