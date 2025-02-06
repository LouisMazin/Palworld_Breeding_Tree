import json, sys
from os import path, listdir

def resourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = path.abspath(".")
    return path.join(basePath, relativePath)

class LanguageManager:
    def __init__(self):
        self.availableLanguages = {}
        self.texts = {}
        self.pals = {}
        self.languagesPath = resourcePath("languages")
        self.loadLanguages()
    def loadLanguages(self):
        """Charge toutes les langues disponibles depuis le dossier languages"""
        for langFile in listdir(self.languagesPath):
            with open(path.join(self.languagesPath,langFile), 'r', encoding='utf-8') as file:
                langData = json.load(file)
                langCode = langFile.replace(".json", "")
                self.availableLanguages[langCode] = langData

    def loadLanguage(self, language):
        """Charge une langue spécifique"""
        if language in self.availableLanguages:
            self.texts = self.availableLanguages[language]["texts"]
            self.pals = self.availableLanguages[language]["pals"]

    def getText(self, key):
        """Récupère un texte dans la langue actuelle"""
        return self.texts.get(key, key)

    def getPalName(self, pal):
        """Récupère le nom traduit d'un Pal"""
        return self.pals.get(pal, pal)

    def getLanguages(self):
        """Renvoie une liste de langues disponibles"""
        return self.availableLanguages.items()