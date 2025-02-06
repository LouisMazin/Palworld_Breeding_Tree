from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QSlider, QPushButton, QFrame)
from PyQt6.QtCore import Qt
from core.variables_manager import VariablesManager
from core.observer_manager import ObserverManager, NotificationTypes

class SettingsWindow(QWidget):    
    def __init__(self):
        super().__init__()
        self.variablesManager = VariablesManager()
        self.observerManager = ObserverManager.getInstance()
        self.observerManager.addObserver(self)  # S'enregistrer comme observé
        self.dpi = self.variablesManager.dpi
        self.setupUi()

    def setupUi(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Style général
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Nombre maximum d'arbres
        self.treesContainer, self.treesLayout = self.createSettingContainer(self.variablesManager.getText("max_trees"))
        self.treesWidget = self.createTreeSlider()
        self.treesLayout.addWidget(self.treesWidget)
        layout.addWidget(self.treesContainer)
        
        # Sélection de la langue
        self.langContainer, self.langLayout = self.createSettingContainer(self.variablesManager.getText("language"))
        self.langWidget = self.createLanguageSelector()
        self.langLayout.addWidget(self.langWidget)
        layout.addWidget(self.langContainer)
        
        # Mode clair/sombre
        self.themeContainer, self.themeLayout = self.createSettingContainer(self.variablesManager.getText("theme"))
        self.themeWidget = self.createThemeSwitch()
        self.themeLayout.addWidget(self.themeWidget)
        layout.addWidget(self.themeContainer)
        
        # Ordre des Pals        
        self.orderContainer, self.orderLayout = self.createSettingContainer(self.variablesManager.getText("pal_order"))
        self.orderWidget = self.createOrderSelector()
        self.orderLayout.addWidget(self.orderWidget)
        layout.addWidget(self.orderContainer)
        
        # Ajouter un espace extensible à la fin
        layout.addStretch()

    def createSettingContainer(self, labelText):
        container = QFrame()
        container.setFrameStyle(QFrame.Shape.StyledPanel)
        container.setMinimumWidth(int(self.variablesManager.minScreenSize/3.5))  # Définir une largeur minimale pour chaque conteneur
        container.setMaximumWidth(int(self.variablesManager.minScreenSize))  # Définir une largeur maximale pour chaque conteneur
        layout = QHBoxLayout(container)
        layout.setContentsMargins(30, 10, 10, 10)
        
        label = QLabel(labelText)
        layout.addWidget(label)
        
        return container,layout

    def createTreeSlider(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(3)
        slider.setValue(self.variablesManager.getConfig("maxTrees"))
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(1)
        
        # Ajouter un label pour afficher la valeur
        self.sliderValueLabel = QLabel(str(slider.value()))
        
        layout.addWidget(slider, stretch=1)
        layout.addWidget(self.sliderValueLabel)
        
        # Connecter le signal valueChanged pour mettre à jour le label
        slider.valueChanged.connect(self.onTreeCountChanged)
        return container

    def createLanguageSelector(self):
        combo = QComboBox()
        # Ajouter toutes les langues disponibles
        for langCode, langData in self.variablesManager.languageManager.getLanguages():
            combo.addItem(langData["name"], langCode)
            
        # Sélectionner la langue actuelle
        currentIndex = combo.findData(self.variablesManager.getConfig("language"))
        combo.setCurrentIndex(currentIndex)
        combo.currentIndexChanged.connect(self.onLanguageChanged)
        
        return combo

    def createThemeSwitch(self):
        button = QPushButton()
        button.setCheckable(True)
        button.setChecked(self.variablesManager.getConfig("darkMode"))
        button.setText(self.variablesManager.getText("dark_mode" if button.isChecked() else "light_mode"))
        button.clicked.connect(self.onThemeChanged)
        return button

    def createOrderSelector(self):
        combo = QComboBox()
        combo.addItems([
            self.variablesManager.getText("alphabetical"),
            self.variablesManager.getText("paldex")
        ])
        combo.setCurrentIndex(0 if self.variablesManager.getConfig("order") == "Alphabetical" else 1)
        combo.currentIndexChanged.connect(self.onOrderChanged)
        return combo

    def onTreeCountChanged(self, value):
        self.sliderValueLabel.setText(str(value))
        self.variablesManager.setConfig("maxTrees",value)

    def onLanguageChanged(self, index):
        try:
            oldLang = self.variablesManager.getConfig("language")
            langCode = self.langWidget.itemData(index)
            if oldLang != langCode:
                self.variablesManager.setConfig("language",langCode)
        except Exception as e:
            print(f"Erreur lors du changement de langue: {e}")
    
    def onThemeChanged(self):
        try:
            is_dark = self.themeWidget.isChecked()
            self.variablesManager.setConfig("darkMode",is_dark)
            self.themeWidget.setText(self.variablesManager.getText("dark_mode" if self.themeWidget.isChecked() else "light_mode"))            
        except Exception as e:
            print(f"Erreur lors du changement de thème: {e}")

    def onOrderChanged(self):
        try:
            index = self.orderWidget.currentIndex()
            new_order = "Alphabetical" if index == 0 else "GameOrder"
            if self.variablesManager.config["order"] != new_order:
                self.variablesManager.setConfig("order", new_order)
        except Exception as e:
            print(f"Erreur lors du changement d'ordre: {e}")
            
    def notify(self, notification_type=NotificationTypes.ALL):
        if notification_type == NotificationTypes.LANGUAGE or notification_type == NotificationTypes.ALL:
            self.updateTexts()
            
    def updateTexts(self):
        """Met à jour tous les textes de l'interface"""
        containers = [
            (self.treesContainer, "max_trees"),
            (self.langContainer, "language"),
            (self.themeContainer, "theme"),
            (self.orderContainer, "pal_order")
        ]
        for container, textKey in containers:
            container.layout().itemAt(0).widget().setText(
                self.variablesManager.getText(textKey)
            )
        
        # Mettre à jour aussi les textes des widgets de configuration
        order_combo = self.orderContainer.layout().itemAt(1).widget()
        order_combo.clear()
        order_combo.addItems([
            self.variablesManager.getText("alphabetical"),
            self.variablesManager.getText("paldex")
        ])
        
        self.themeWidget.setText(self.variablesManager.getText("dark_mode" if self.themeWidget.isChecked() else "light_mode"))