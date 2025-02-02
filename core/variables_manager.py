import json
from core.language_manager import LanguageManager
from core.observer_manager import ObserverManager, notification_types
from os import environ, path, mkdir, listdir, unlink, remove, rename, system
import sys
import requests
from PyQt6.QtWidgets import QFileDialog
import platform

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)

environ["PATH"] += resource_path("Graphviz\\bin")+";"

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
            "windowSize": {"width": 300, "height": 350},
            "language": "fr",
            "order": "Alphabetical",
            "max_trees": 3,
            "locked": []  # Ajouter le paramètre par défaut pour "combos"
        }
        self.load_config()
        self.version = "3.0.0"
        self.language_manager = LanguageManager()
        if(self.config.keys() != self.defaults.keys()):
            self.config = self.defaults.copy()
        self.picklePath = self._get_pickle_path()
        self.configPath = self._get_config_path()
        self.cachePath = self._get_cache_path()
        self.iconsPath = self._get_icons_path()
        self.rootPath = resource_path("")
        self.language_manager.load_language(self.config["language"])
        self.observer_manager = ObserverManager.get_instance()
        self.observer_manager.add_observer(self)
        self.palList = list(self.getPalList())
        self.pal_dict = {pal: self.language_manager.get_pal_name(pal) for pal in self.palList}
        self.pal_dict_reversed = {v: k for k, v in self.pal_dict.items()}
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
        self.Colors = self.darkColors if self.config["darkMode"] else self.lightColors
        self.sheet = self._generate_stylesheet(self.Colors)
        self.observers = []
        self.unlocked = []  # Ajouter une liste pour les couples déverrouillés

    def _generate_stylesheet(self, Colors):
        return f"""
        QComboBox {{
            border: 2px solid {Colors["secondaryLightColor"]};
            border-radius: 5px;
            color: {Colors["secondaryTextColor"]};
        }}
        QPushButton {{
            padding: 2px;
            color: {Colors["primaryColor"]};
        }}
        QPushButton:disabled {{
            color: {Colors["secondaryLightColor"]};
        }}
        QLabel {{
            color: {Colors["secondaryTextColor"]};
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
        with open(resource_path("pals.json"), encoding="utf-8") as pals:
            pals = json.load(pals)
        return pals.keys()

    def getPal(self, key: str):
        return self.pal_dict.get(key, key)

    def getPalByTranslation(self, translation: str):
        return self.pal_dict_reversed.get(translation, translation)

    def getOrderedPalList(self):
        if self.config["order"] == "Alphabetical":
            return sorted(self.palList, key=lambda x: self.getPal(x))
        else:
            return self.palList

    def updatePalDicts(self):
        self.pal_dict = {pal: self.language_manager.get_pal_name(pal) for pal in self.palList}
        self.pal_dict_reversed = {v: k for k, v in self.pal_dict.items()}

    def notify(self, notification_type=notification_types.ALL):
        if notification_type in {notification_types.THEME, notification_types.ALL}:
            self.Colors = self.darkColors if self.config["darkMode"] else self.lightColors
            self.sheet = self._generate_stylesheet(self.Colors)
        elif notification_type in {notification_types.LANGUAGE, notification_types.ALL}:
            self.language_manager.load_language(self.config["language"])
            self.updatePalDicts()
        self.save_config()

    def load_config(self):
        try:
            with open(self._get_config_path(), 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = self.defaults.copy()

    def save_config(self):
        with open(self._get_config_path(), 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str):
        return self.config.get(key, self.defaults.get(key))

    def set(self, key: str, value):
        self.config[key] = value
        self.save_config()

    def getText(self, key: str):
        return self.language_manager.get_text(key)

    def _get_config_base_dir(self):
        system = platform.system()
        if system == 'Windows':
            return path.join(path.expanduser("~"), "AppData", "Local", "PBT")
        else:
            return path.join(path.expanduser("~"), ".config", "PBT")

    def _get_config_path(self):
        config_dir = self._get_config_base_dir()
        if not path.exists(config_dir):
            mkdir(config_dir)
        return path.join(config_dir, "config.json")

    def _get_cache_path(self):
        cache_dir = path.join(self._get_config_base_dir(), "cache")
        if not path.exists(cache_dir):
            mkdir(cache_dir)
        return cache_dir

    def _get_pickle_path(self):
        return path.join(self._get_config_base_dir(), "pals."+self.version+".pickle")
        
    def _get_icons_path(self):
        return resource_path("Icons")
    
    def _get_languages_path(self):
        return resource_path("languages")
    
    def _empty_cache(self):
        for file in listdir(self.cachePath):
            file_path = path.join(self.cachePath, file)
            try:
                if path.isfile(file_path):
                    unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    def checkUpdate(self):
        try:
            response = requests.get("https://api.github.com/repos/LouisMazin/Palworld_Breeding_Tree/releases/latest",timeout=15)
            if response.status_code == 200:
                latest_version = response.json()['tag_name']
                return latest_version > self.version
            else:
                return False
        except:
            return False
    def updateApp(self):
        try:
            # Demander à l'utilisateur où placer la mise à jour
            update_path, _ = QFileDialog.getSaveFileName(None, self.getText("select_unzip_folder"), self.get_repo_dl_name(), "Executable (*.exe)" if platform.system() == 'Windows' else "Executable (*)")
            if not update_path:
                print("Mise à jour annulée par l'utilisateur.")
                return
            
            # Télécharger la mise à jour
            response = requests.get(self.get_repo_dl_link(), stream=True)
            with open("update_temp", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Déplacer la mise à jour vers le chemin spécifié
            remove(update_path) if path.exists(update_path) else None
            rename("update_temp", update_path)
            
            # Lancer l'app téléchargée
            system(update_path)
            sys.exit(0)
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour: {e}")

    def get_repo_dl_link(self):
        url = "https://api.github.com/repos/LouisMazin/Palworld_Breeding_Tree/releases/latest"
        response = requests.get(url)
        data = response.json()
        if platform.system() == 'Windows':
            return data["assets"][0]["browser_download_url"]
        else:
            return data["assets"][1]["browser_download_url"]

    def get_repo_dl_name(self):
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
        self.save_config()
        
    def removeLockedCombo(self, combo):
        self.config["locked"].remove(combo)
        self.unlocked.append(combo)  # Ajouter le couple à la liste des couples déverrouillés
        self.save_config()

    def is_unlocked(self, combo):
        return combo in self.unlocked

    def set_window_size(self, width, height):
        self.config["windowSize"]["width"] = width
        self.config["windowSize"]["height"] = height
        self.save_config()

    def get_window_size(self):
        return self.config["windowSize"]