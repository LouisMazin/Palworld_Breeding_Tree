from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from core.variables_manager import VariablesManager
from qt_material import apply_stylesheet
from .tree_window import TreeWindow
from .settings_window import SettingsWindow
from core.observer_manager import ObserverManager, NotificationTypes
from os import path
import sys

def resourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = path.abspath(".")
    return path.join(basePath, relativePath)

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.variablesManager = VariablesManager()
        
        self.observerManager = ObserverManager.getInstance()
        self.observerManager.addObserver(self)
        
        # Configurer la fenêtre avant de créer les widgets
        self.dpi = self.app.primaryScreen().devicePixelRatio()
        self.variablesManager.dpi = self.dpi
        size = self.app.primaryScreen().size()
        self.variablesManager.minScreenSize = min(size.height(),size.width())
        configWidth = int(self.variablesManager.getConfig("windowSize")["width"]/self.dpi)
        configHeight = int(self.variablesManager.getConfig("windowSize")["height"]/self.dpi)
        
        # Définir la taille une seule fois
        largeur = (self.variablesManager.minScreenSize/2.1)
        self.setMinimumSize(int(largeur),int(largeur*1.085))
        self.resize(configWidth, configHeight)
        # Appliquer le style après le resize
        theme = ['light_lightgreen.xml','dark_amber.xml'][self.variablesManager.config["darkMode"]]
        apply_stylesheet(self, theme=theme)
        self.setStyleSheet(self.styleSheet() + self.variablesManager.sheet)
        
        self.setWindowTitle("Palworld Breeding Tree")
        self.setWindowIcon(QIcon(resourcePath("Icons/icon.png")))
        # Créer les widgets
        self.setupUi()
        
        # Vérifier les mises à jour au démarrage
        self.checkForUpdates()
        
        self.resizeTimer = QTimer()
        self.resizeTimer.setSingleShot(True)
        self.resizeTimer.setInterval(250)  # Augmenter le délai du timer
        self.resizeTimer.timeout.connect(lambda : self.variablesManager.setConfig("maxTrees",self.variablesManager.getConfig("maxTrees")))
    
    def setupUi(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Créer les fenêtres
        self.treeWindow = TreeWindow()
        self.settingsWindow = SettingsWindow()
        
        # Ajouter les onglets
        self.tabs.addTab(self.treeWindow, self.variablesManager.getText("breeding_tab"))
        self.tabs.addTab(self.settingsWindow, self.variablesManager.getText("settings_tab"))
        
        # Forcer le premier resize
        self.tabs.currentChanged.connect(self.onTabChanged)

    def showEvent(self, event):
        super().showEvent(event)
        self.treeWindow.doResize()  # Appeler handle_resize après que la fenêtre a été affichée

    def notify(self, notification_type=NotificationTypes.ALL):
        if notification_type == NotificationTypes.THEME or notification_type == NotificationTypes.ALL:
            theme = ['light_lightgreen.xml','dark_amber.xml'][self.variablesManager.config["darkMode"]]
            apply_stylesheet(self, theme=theme)
            self.setStyleSheet(self.styleSheet() + self.variablesManager.sheet)
        elif notification_type == NotificationTypes.LANGUAGE or notification_type == NotificationTypes.ALL:
            self.setWindowTitle(self.variablesManager.getText("app_title"))
            self.tabs.setTabText(0, self.variablesManager.getText("breeding_tab"))
            self.tabs.setTabText(1, self.variablesManager.getText("settings_tab"))

    def onTabChanged(self, index):
        """Appelé lorsque l'onglet est changé"""
        if index == 0:  # Si l'onglet TreeWindow est sélectionné
            self.treeWindow.doResize()

    def closeEvent(self, event):
        self.variablesManager.emptyCache()
        event.accept()
    
    def checkForUpdates(self):
        if self.variablesManager.checkUpdate():
            messageBox = QMessageBox(self)
            messageBox.setWindowTitle(self.variablesManager.getText("available_update"))
            messageBox.setText(self.variablesManager.getText("update_message"))
            yesButton = messageBox.addButton(self.variablesManager.getText("yes"), QMessageBox.ButtonRole.YesRole)
            noButton = messageBox.addButton(self.variablesManager.getText("no"), QMessageBox.ButtonRole.NoRole)
            messageBox.setDefaultButton(noButton)
            messageBox.exec()
            
            if messageBox.clickedButton() == yesButton:
                self.variablesManager.updateApp()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Forcer le traitement des événements
        self.app.processEvents()
        width = int(self.size().width() * self.dpi)
        height = int(self.size().height() * self.dpi)
        self.variablesManager.setWindowSize(width, height)
        self.resizeTimer.setInterval(300)  # Allonger le délai
        self.resizeTimer.start()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow(app)
    window.show()
    app.exec()
