from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QSlider, QPushButton, QFrame)
from PyQt6.QtCore import Qt
from core.variables_manager import VariablesManager
from core.observer_manager import ObserverManager, notification_types

class SettingsWindow(QWidget):    
    def __init__(self):
        super().__init__()
        self.variables = VariablesManager()
        self.observer_manager = ObserverManager.get_instance()
        self.observer_manager.add_observer(self)  # S'enregistrer comme observé
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Style général
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Nombre maximum d'arbres
        self.trees_container, self.trees_layout = self.create_setting_container(self.variables.getText("max_trees"))
        self.trees_widget = self.create_tree_slider()
        self.trees_layout.addWidget(self.trees_widget)
        layout.addWidget(self.trees_container)
        
        # Sélection de la langue
        self.lang_container, self.lang_layout = self.create_setting_container(self.variables.getText("language"))
        self.lang_widget = self.create_language_selector()
        self.lang_layout.addWidget(self.lang_widget)
        layout.addWidget(self.lang_container)
        
        # Mode clair/sombre
        self.theme_container, self.theme_layout = self.create_setting_container(self.variables.getText("theme"))
        self.theme_widget = self.create_theme_switch()
        self.theme_layout.addWidget(self.theme_widget)
        layout.addWidget(self.theme_container)
        
        # Ordre des Pals        
        self.order_container, self.order_layout = self.create_setting_container(self.variables.getText("pal_order"))
        self.order_widget = self.create_order_selector()
        self.order_layout.addWidget(self.order_widget)
        layout.addWidget(self.order_container)
        
        # Ajouter un espace extensible à la fin
        layout.addStretch()

    def create_setting_container(self, label_text):
        container = QFrame()
        container.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label = QLabel(label_text)
        layout.addWidget(label)
        
        return container,layout

    def create_tree_slider(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(3)
        slider.setValue(self.variables.config.get("max_trees", 3))
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(1)
        
        # Ajouter un label pour afficher la valeur
        self.slider_value_label = QLabel(str(slider.value()))
        
        layout.addWidget(slider, stretch=1)
        layout.addWidget(self.slider_value_label)
        
        # Connecter le signal valueChanged pour mettre à jour le label
        slider.valueChanged.connect(self.on_tree_count_changed)
        return container

    def create_language_selector(self):
        combo = QComboBox()
        # Ajouter toutes les langues disponibles
        for lang_code, lang_data in self.variables.language_manager.available_languages.items():
            combo.addItem(lang_data["name"], lang_code)
            
        # Sélectionner la langue actuelle
        current_index = combo.findData(self.variables.config["language"])
        combo.setCurrentIndex(current_index)
        combo.currentIndexChanged.connect(self.on_language_changed)  # Changé ici
        
        return combo

    def create_theme_switch(self):
        button = QPushButton()
        button.setCheckable(True)
        button.setChecked(self.variables.config["darkMode"])
        button.setText(self.variables.getText("dark_mode" if button.isChecked() else "light_mode"))
        button.clicked.connect(self.on_theme_changed)
        return button

    def create_order_selector(self):
        combo = QComboBox()
        combo.addItems([
            self.variables.getText("alphabetical"),
            self.variables.getText("paldex")
        ])
        combo.setCurrentIndex(0 if self.variables.config["order"] == "Alphabetical" else 1)
        combo.currentIndexChanged.connect(self.on_order_changed)
        return combo

    def on_tree_count_changed(self, value):
        self.slider_value_label.setText(str(value))
        self.variables.config["max_trees"] = value
        self.variables.save_config()
        
        self.observer_manager.notify_observers(notification_types.MAX_TREES)

    def on_language_changed(self, index):
        try:
            old_lang = self.variables.config["language"]
            lang_code = self.lang_widget.itemData(index)
            if old_lang != lang_code:
                self.variables.config["language"] = lang_code
                self.variables.save_config()
                self.observer_manager.notify_observers(notification_types.LANGUAGE)
        except Exception as e:
            print(f"Erreur lors du changement de langue: {e}")
    
    def on_theme_changed(self):
        try:
            is_dark = self.theme_widget.isChecked()
            self.variables.config["darkMode"] = is_dark
            self.theme_widget.setText(self.variables.getText("dark_mode" if self.theme_widget.isChecked() else "light_mode"))

            
            # Sauvegarder et mettre à jour
            self.observer_manager.notify_observers(notification_types.THEME)
            
        except Exception as e:
            print(f"Erreur lors du changement de thème: {e}")

    def on_order_changed(self):
        try:
            index = self.order_widget.currentIndex()
            new_order = "Alphabetical" if index == 0 else "GameOrder"
            if self.variables.config["order"] != new_order:
                self.variables.config["order"] = new_order
                self.variables.save_config()
                self.observer_manager.notify_observers(notification_types.ORDER)
        except Exception as e:
            print(f"Erreur lors du changement d'ordre: {e}")
            
    def notify(self, notification_type=notification_types.ALL):
        if notification_type == notification_types.LANGUAGE or notification_type == notification_types.ALL:
            self.update_texts()
            
    def update_texts(self):
        """Met à jour tous les textes de l'interface"""
        containers = [
            (self.trees_container, "max_trees"),
            (self.lang_container, "language"),
            (self.theme_container, "theme"),
            (self.order_container, "pal_order")
        ]
        for container, text_key in containers:
            container.layout().itemAt(0).widget().setText(
                self.variables.getText(text_key)
            )
        
        # Mettre à jour aussi les textes des widgets de configuration
        order_combo = self.order_container.layout().itemAt(1).widget()
        order_combo.clear()
        order_combo.addItems([
            self.variables.getText("alphabetical"),
            self.variables.getText("paldex")
        ])
        
        self.theme_widget.setText(self.variables.getText("dark_mode" if self.theme_widget.isChecked() else "light_mode"))