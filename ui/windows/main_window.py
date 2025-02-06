from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QMessageBox, QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from core.variables_manager import VariablesManager
from qt_material import apply_stylesheet
from .tree_window import TreeWindow
from .settings_window import SettingsWindow
from core.observer_manager import ObserverManager, notification_types
from os import path
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.variables_manager = VariablesManager()
        
        self.observer_manager = ObserverManager.get_instance()
        self.observer_manager.add_observer(self)
        
        # Configurer la fenêtre avant de créer les widgets
        self.dpi = self.app.primaryScreen().devicePixelRatio()
        self.variables_manager.dpi = self.dpi
        size = self.app.primaryScreen().size()
        self.variables_manager.min_screen_size = min(size.height(),size.width())
        config_width = int(self.variables_manager.config["windowSize"]["width"]/self.dpi)
        config_height = int(self.variables_manager.config["windowSize"]["height"]/self.dpi)
        
        # Définir la taille une seule fois
        largeur = (self.variables_manager.min_screen_size/3)
        self.setMinimumSize(int(largeur),int(largeur*1.085))
        self.resize(config_width, config_height)
        # Appliquer le style après le resize
        theme = ['light_lightgreen.xml','dark_amber.xml'][self.variables_manager.config["darkMode"]]
        apply_stylesheet(self, theme=theme)
        self.setStyleSheet(self.styleSheet() + self.variables_manager.sheet)
        
        self.setWindowTitle("Palworld Breeding Tree")
        self.setWindowIcon(QIcon(resource_path("Icons/icon.png")))
        # Créer les widgets
        self.setup_ui()
        
        # Vérifier les mises à jour au démarrage
        self.check_for_updates()
        
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.setInterval(250)  # Augmenter le délai du timer
        self.resize_timer.timeout.connect(self.finish_resize)
    
    def setup_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Créer les fenêtres
        self.tree_window = TreeWindow()
        self.settings_window = SettingsWindow()
        
        # Ajouter les onglets
        self.tabs.addTab(self.tree_window, self.variables_manager.getText("breeding_tab"))
        self.tabs.addTab(self.settings_window, self.variables_manager.getText("settings_tab"))
        
        # Forcer le premier resize
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def showEvent(self, event):
        super().showEvent(event)
        self.tree_window.do_resize()  # Appeler handle_resize après que la fenêtre a été affichée

    def notify(self, notification_type=notification_types.ALL):
        if notification_type == notification_types.THEME or notification_type == notification_types.ALL:
            theme = ['light_lightgreen.xml','dark_amber.xml'][self.variables_manager.config["darkMode"]]
            apply_stylesheet(self, theme=theme)
            self.setStyleSheet(self.styleSheet() + self.variables_manager.sheet)
        elif notification_type == notification_types.LANGUAGE or notification_type == notification_types.ALL:
            self.setWindowTitle(self.variables_manager.getText("app_title"))
            self.tabs.setTabText(0, self.variables_manager.getText("breeding_tab"))
            self.tabs.setTabText(1, self.variables_manager.getText("settings_tab"))
            self.tabs.setTabText(2, self.variables_manager.getText("locked_tab"))

    def on_tab_changed(self, index):
        """Appelé lorsque l'onglet est changé"""
        if index == 0:  # Si l'onglet TreeWindow est sélectionné
            self.tree_window.do_resize()

    def closeEvent(self, event):
        self.variables_manager._empty_cache()
        event.accept()
    
    def check_for_updates(self):
        if self.variables_manager.checkUpdate():
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.variables_manager.getText("available_update"))
            msg_box.setText(self.variables_manager.getText("update_message"))
            yes_button = msg_box.addButton(self.variables_manager.getText("yes"), QMessageBox.ButtonRole.YesRole)
            no_button = msg_box.addButton(self.variables_manager.getText("no"), QMessageBox.ButtonRole.NoRole)
            msg_box.setDefaultButton(no_button)
            msg_box.exec()
            
            if msg_box.clickedButton() == yes_button:
                self.variables_manager.updateApp()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Forcer le traitement des événements
        self.app.processEvents()
        width = int(self.size().width() * self.dpi)
        height = int(self.size().height() * self.dpi)
        self.variables_manager.set_window_size(width, height)
        self.resize_timer.setInterval(300)  # Allonger le délai
        self.resize_timer.start()

    def finish_resize(self):
        # Notifier les fenêtres pour qu’elles se redimensionnent enfin
        self.observer_manager.notify_observers(notification_types.MAX_TREES)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow(app)
    window.show()
    app.exec()
