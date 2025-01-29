import json, sys
from os import path, listdir

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)

class LanguageManager:
    def __init__(self, language="fr"):
        self.current_language = language
        self.available_languages = {}
        self.texts = {}
        self.pals = {}
        self.languagesPath = resource_path("languages")
        self.load_languages()
        self.load_language(language)
    def load_languages(self):
        """Charge toutes les langues disponibles depuis le dossier languages"""
        for lang_file in listdir(self.languagesPath):
            with open(path.join(self.languagesPath,lang_file), 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
                lang_code = lang_file.replace(".json", "")
                self.available_languages[lang_code] = lang_data

    def load_language(self, language):
        """Charge une langue spécifique"""
        if language in self.available_languages:
            self.current_language = language
            self.texts = self.available_languages[language]["texts"]
            self.pals = self.available_languages[language]["pals"]

    def get_text(self, key):
        """Récupère un texte dans la langue actuelle"""
        return self.texts.get(key, key)

    def get_pal_name(self, pal):
        """Récupère le nom traduit d'un Pal"""
        return self.pals.get(pal, pal)
