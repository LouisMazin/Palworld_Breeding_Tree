import json
from core.language_manager import LanguageManager
from core.observer_manager import ObserverManager, NotificationTypes
from os import environ, path, mkdir, listdir, unlink, remove, rename, system
import sys
import requests
from PyQt6.QtWidgets import QFileDialog
import platform

def resourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = path.abspath(".")
    return path.join(basePath, relativePath)

environ["PATH"] += resourcePath("Graphviz\\bin")+";"

class VariablesManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VariablesManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Charger la config et version avant la langue et l'observer
        self._updating = False
        self.defaults = {
            "darkMode": True,
            "windowSize": {"width": 10, "height": 10},
            "language": "en",
            "order": "Paldex",
            "maxTrees": 3,
            "locked": []  # Ajouter le paramètre par défaut pour "combos"
        }
        self.version = "3.0.2"
        self.languageManager = LanguageManager()
        self.configPath = self.getConfigPath()
        self.picklePath = self.getPicklePath()
        self.cachePath = self.getCachePath()
        self.iconsPath = self.getIconsPath()
        self.rootPath = resourcePath("")
        self.loadConfig()
        if(self.config.keys() != self.defaults.keys()):
            self.config = self.defaults.copy()
        self.languageManager.loadLanguage(self.config["language"])
        self.observerManager = ObserverManager.getInstance()
        self.observerManager.addObserver(self)
        self.palList = list(self.getPalList())
        self.palDict = {pal: self.languageManager.getPalName(pal) for pal in self.palList}
        self.palDictReversed = {v: k for k, v in self.palDict.items()}
        self.darkColors = {
            'primaryColor': '#ffd740', 'primaryLightColor': '#ffff74', 'secondaryColor': '#232629',
            'secondaryLightColor': '#4f5b62', 'secondaryDarkColor': '#31363b', 'primaryTextColor': '#000000',
            'secondaryTextColor': '#ffffff'
        }
        self.lightColors = {
            'primaryColor': '#64dd17', 'primaryLightColor': '#9cff57', 'secondaryColor': '#f5f5f5',
            'secondaryLightColor': '#ffffff', 'secondaryDarkColor': '#e6e6e6', 'primaryTextColor': '#3c3c3c',
            'secondaryTextColor': '#555555'
        }
        self.colors = self.darkColors if self.config["darkMode"] else self.lightColors
        self.sheet = self.generateStylesheet(self.colors)
        self.observers = []
        self.unlocked = []  # Ajouter une liste pour les couples déverrouillés

    def generateStylesheet(self, colors):
        return f"""
        QComboBox {{
            border: 2px solid {colors["secondaryLightColor"]};
            border-radius: 5px;
            color: {colors["secondaryTextColor"]};
        }}
        QPushButton {{
            padding: 2px;
            color: {colors["primaryColor"]};
        }}
        QPushButton:disabled {{
            color: {colors["secondaryLightColor"]};
        }}
        QLabel {{
            color: {colors["secondaryTextColor"]};
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            padding: 0px;
            margin: 0px;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 0px;
            margin: 0px;
        }}
        """

    def getPalList(self):
        with open(resourcePath("pals.json"), encoding="utf-8") as pals:
            pals = json.load(pals)
        return pals.keys()

    def getPal(self, key: str):
        return self.palDict.get(key, key)

    def getPalByTranslation(self, translation: str):
        return self.palDictReversed.get(translation, translation)

    def getOrderedPalList(self):
        if self.config["order"] == "Alphabetical":
            return sorted(self.palList, key=lambda x: self.getPal(x))
        else:
            return self.palList

    def updatePalDicts(self):
        self.palDict = {pal: self.languageManager.getPalName(pal) for pal in self.palList}
        self.palDictReversed = {v: k for k, v in self.palDict.items()}

    def notify(self, notification_type=NotificationTypes.ALL):
        if notification_type in {NotificationTypes.THEME, NotificationTypes.ALL}:
            self.colors = self.darkColors if self.config["darkMode"] else self.lightColors
            self.sheet = self.generateStylesheet(self.colors)
        elif notification_type in {NotificationTypes.LANGUAGE, NotificationTypes.ALL}:
            self.languageManager.loadLanguage(self.config["language"])
            self.updatePalDicts()
        self.saveConfig()

    def loadConfig(self):
        try:
            with open(self.configPath, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = self.defaults.copy()

    def saveConfig(self):
        with open(self.configPath, 'w') as f:
            json.dump(self.config, f, indent=4)

    def getConfig(self, key: str):
        return self.config.get(key, self.defaults.get(key))

    def setConfig(self, key: str, value):
        self.config[key] = value
        self.saveConfig()
        match key:
            case "darkMode":
                self.observerManager.notifyObservers(NotificationTypes.THEME)
            case "language":
                self.observerManager.notifyObservers(NotificationTypes.LANGUAGE)
            case "order":
                self.observerManager.notifyObservers(NotificationTypes.ORDER)
            case "maxTrees":
                self.observerManager.notifyObservers(NotificationTypes.MAXTREES)
    def getColor(self, key: str):
        return self.colors.get(key)
    
    def getText(self, key: str):
        return self.languageManager.getText(key)

    def getConfigBaseDir(self):
        system = platform.system()
        if system == 'Windows':
            return path.join(path.expanduser("~"), "AppData", "Local", "PBT")
        else:
            return path.join(path.expanduser("~"), ".config", "PBT")

    def getConfigPath(self):
        configDir = self.getConfigBaseDir()
        if not path.exists(configDir):
            mkdir(configDir)
        return path.join(configDir, "config.json")

    def getCachePath(self):
        cacheDir = path.join(self.getConfigBaseDir(), "cache")
        if not path.exists(cacheDir):
            mkdir(cacheDir)
        return cacheDir

    def getPicklePath(self):
        return path.join(self.getConfigBaseDir(), "pals."+self.version+".pickle")
        
    def getIconsPath(self):
        return resourcePath("Icons")
    
    def getLanguagesPath(self):
        return resourcePath("languages")
    
    def emptyCache(self):
        for file in listdir(self.cachePath):
            filePath = path.join(self.cachePath, file)
            try:
                if path.isfile(filePath):
                    unlink(filePath)
            except Exception as e:
                print(f"Error deleting {filePath}: {e}")

    def checkUpdate(self):
        try:
            response = requests.get("https://api.github.com/repos/LouisMazin/Palworld_Breeding_Tree/releases/latest",timeout=15)
            if response.status_code == 200:
                latestVersion = response.json()['tag_name']
                return latestVersion > self.version
            else:
                return False
        except:
            return False
    def updateApp(self):
        try:
            # Demander à l'utilisateur où placer la mise à jour
            updatePath, _ = QFileDialog.getSaveFileName(None, self.getText("select_unzip_folder"), self.getRepoDownloadName(), "Executable (*.exe)" if platform.system() == 'Windows' else "Executable (*)")
            if not updatePath:
                print("Mise à jour annulée par l'utilisateur.")
                return
            
            # Télécharger la mise à jour
            response = requests.get(self.getRepoDownloadLink(), stream=True)
            with open("updateTemp", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Déplacer la mise à jour vers le chemin spécifié
            remove(updatePath) if path.exists(updatePath) else None
            rename("updateTemp", updatePath)
            
            # Lancer l'app téléchargée
            system(updatePath)
            sys.exit(0)
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour: {e}")

    def getRepoDownloadLink(self):
        url = "https://api.github.com/repos/LouisMazin/Palworld_Breeding_Tree/releases/latest"
        response = requests.get(url)
        data = response.json()
        if platform.system() == 'Windows':
            return data["assets"][0]["browser_download_url"]
        else:
            return data["assets"][1]["browser_download_url"]

    def getRepoDownloadName(self):
        url = "https://api.github.com/repos/LouisMazin/Palworld_Breeding_Tree/releases/latest"
        response = requests.get(url)
        data = response.json()
        if platform.system() == 'Windows':
            return data["assets"][0]["name"]
        else:
            return data["assets"][1]["name"]

    def addLockedCombo(self, combo):
        self.config["locked"].append(combo)
        if combo in self.unlocked:
            self.unlocked.remove(combo)  # Retirer le couple de la liste des couples déverrouillés
        self.saveConfig()
        
    def removeLockedCombo(self, combo):
        self.config["locked"].remove(combo)
        self.unlocked.append(combo)  # Ajouter le couple à la liste des couples déverrouillés
        self.saveConfig()

    def isUnlocked(self, combo):
        return combo in self.unlocked

    def setWindowSize(self, width, height):
        self.config["windowSize"]["width"] = width
        self.config["windowSize"]["height"] = height
        self.saveConfig()

    def getWindowSize(self):
        return self.config["windowSize"]
