from PyQt6.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from core.variables_manager import VariablesManager
from core.tree_manager import TreeManager
from core.graph_manager import GraphManager
from core.observer_manager import ObserverManager, notification_types
from os import environ, path
import sys
from .popup_menu import PopupMenu

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)

environ["PATH"] += resource_path("Graphviz\\bin")+";"

class TreeFrame(QFrame):
    def __init__(self, side: int, combo=None):
        super().__init__()
        self.setFixedSize(side, side)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(1)
        
        # Initialize managers
        self.variables = VariablesManager()
        self.tree_manager = TreeManager()
        self.graph_manager = GraphManager()
        self.observer_manager = ObserverManager.get_instance()
        self.observer_manager.add_observer(self)
        self.combo = combo
        # Cache pour les icônes
        self._icon_cache = {}
        # Cache pour le dernier arbre généré
        self._last_tree = None
        self._last_path = None
        # Initialiser paths et maximum
        self.locked = False
        self.paths = []
        self.maximum = -1
        self.which = 0  # Initialiser self.which
        # Setup UI components
        self.setup_ui()
        # Initial update
        self.populate_combo_boxes()
        self.updateTree(0)
        # Initialize popup menu
        self.popup_menu = PopupMenu(self)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # Appliquer les valeurs de combo si fournies
        if self.combo:
            self.apply_combo(self.combo)
        
    def apply_couple(self, parent, child, number):
        self.applyOldChoice({"parent": parent, "child": child, "number": number})
    def apply_combo(self, combo):
        self.applyOldChoice(combo)
    def applyOldChoice(self, combo):
        for i in range(self.parent_choice.count()):
            if self.parent_choice.itemData(i) == combo["parent"]:
                self.parent_choice.setCurrentIndex(i)
                break
        for j in range(self.child_choice.count()):
            if self.child_choice.itemData(j) == combo["child"]:
                self.child_choice.setCurrentIndex(j)
                break
        self.which = combo["number"]
        self.updateTree(self.which)

    def setup_ui(self):
        # Create main vertical layout with proper spacing
        self.main_layout = QGridLayout(self)

        # Create header section
        header_widget = QWidget()
        header_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.header_layout = QHBoxLayout(header_widget)
        self.header_layout.setSpacing(5)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Calculate header height (6% of frame height)
        header_height = int(self.height() * 0.06)
        
        # Setup combo boxes with improved styling
        self.parent_choice = QComboBox()
        self.child_choice = QComboBox()
        for combo in [self.parent_choice, self.child_choice]:
            combo.setEditable(True)
            combo.setIconSize(QSize(int(header_height * 0.55), int(header_height * 0.55)))  # Taille d'icône proportionnelle
            combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            combo.currentIndexChanged.connect(lambda x : self.updateTree(0))
            # Centrer le texte verticalement et ajuster les marges
            line_edit = combo.lineEdit()
            line_edit.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            line_edit.setStyleSheet(f"""
                QLineEdit {{
                    margin: 0px;
                    padding: 0px;
                }}
            """)
            
            combo.setStyleSheet("""
                QComboBox {
                    padding: 1px;
                }
            """)
        
        # Setup text label
        self.text = QLabel(self.variables.language_manager.get_text("between"))
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Add widgets to header layout
        self.header_layout.addWidget(self.parent_choice, 2)
        self.header_layout.addWidget(self.text, 1)
        self.header_layout.addWidget(self.child_choice, 2)
        
        # Create content section
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(5)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup navigation buttons containers
        nav_left = QVBoxLayout()
        nav_right = QVBoxLayout()
        nav_left.setSpacing(5)
        nav_right.setSpacing(5)
        
        # Calculate button width (15% of frame width)
        button_width = int(self.width() * 0.15)
        
        # Setup buttons with equal width
        self.buttons = {
            "prev_1": QPushButton("-1"),
            "prev_10": QPushButton("-10"),
            "prev_100": QPushButton("-100"),
            "next_1": QPushButton("+1"),
            "next_10": QPushButton("+10"),
            "next_100": QPushButton("+100")
        }
        
        for key, button in self.buttons.items():
            button.setFixedWidth(button_width)
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            button.clicked.connect(self.create_lambda(key))
            layout = nav_right if "next" in key else nav_left
            layout.addWidget(button, 1)  # Equal stretch factor
        
        # Setup tree label
        self.tree = QLabel()
        self.tree.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Assemble the content layout
        content_layout.addLayout(nav_left, 1)
        content_layout.addWidget(self.tree, 8)  # Tree gets more space
        content_layout.addLayout(nav_right, 1)
        
        # Add everything to main layout
        self.main_layout.addWidget(header_widget, 0, 0)
        self.main_layout.addWidget(content_widget, 1, 0)
        self.main_layout.setRowStretch(0, 1)
        self.main_layout.setRowStretch(1, 8)

        self.populate_combo_boxes()
        self.apply_styles()
    
    def populate_combo_boxes(self):
        try:
            self.parent_choice.blockSignals(True)
            self.child_choice.blockSignals(True)
            
            # Sauvegarder les sélections actuelles
            current_parent_index = self.parent_choice.currentIndex() 
            current_child_index = self.child_choice.currentIndex()
            current_parent = self.parent_choice.itemData(current_parent_index) if current_parent_index > 0 else ""
            current_child = self.child_choice.itemData(current_child_index) if current_child_index > 0 else ""
            # Vider les combobox
            self.parent_choice.clear()
            self.child_choice.clear()
            
            # Ajouter les éléments par défaut
            noneImage = QIcon(self._get_none_path())
            self.parent_choice.addItem(noneImage, self.variables.getText("parent"), "")
            self.child_choice.addItem(noneImage, self.variables.getText("child"), "")
            
            self.used_list = self.variables.getOrderedPalList()
            
            # Ajouter les Pals dans l'ordre approprié
            for pal in self.used_list:
                tradPal = self.variables.getPal(pal)
                if pal not in self._icon_cache:
                    icon = QIcon(resource_path(f"Icons/{pal}.png"))
                    self._icon_cache[pal] = icon
                else:
                    icon = self._icon_cache[pal]
                self.parent_choice.addItem(icon, tradPal, pal)
                self.child_choice.addItem(icon, tradPal, pal)
                
            if self.combo:
                self.apply_combo(self.combo)
            else:
                self.apply_couple(current_parent, current_child, self.which)
                
            self.parent_choice.blockSignals(False)
            self.child_choice.blockSignals(False)
        except Exception as e:
            # Restaurer les signaux en cas d'erreur
            self.parent_choice.blockSignals(False)
            self.child_choice.blockSignals(False)
    
    def apply_styles(self):
        # Calculer les tailles
        header_height = int(self.height() * 0.1)
        font_size = int(header_height * 0.30)
        arrow_width = int(header_height * 0.37)
        button_font_size = int(self.height() * 0.03)  # Maximum de 12px
        style = f"""
            QComboBox {{
                font-size: {font_size}px;
            }}
            QComboBox::drop-down {{
                width: {arrow_width}px;
            }}
            QComboBox::down-arrow {{
                width: {arrow_width}px;
                height: {arrow_width}px;
            }}
            QComboBox QAbstractItemView {{
                font-size: {font_size}px;
            }}
            QComboBox QAbstractItemView::item {{
                height: {header_height}px;
            }}
            QPushButton {{
                font-size: {button_font_size}px;
            }}
            QLabel {{
                font-size: {font_size}px;
            }}
        """
        self.setStyleSheet(self.styleSheet()+style)
        
    def updateTree(self, which=None):
        if which is not None:
            self.which = which
        current_parent_index = self.parent_choice.currentIndex() 
        current_child_index = self.child_choice.currentIndex()
        current_parent = self.parent_choice.itemData(current_parent_index) if current_parent_index > 0 else ""
        current_child = self.child_choice.itemData(current_child_index) if current_child_index > 0 else ""
        
        if not current_parent and not current_child:
            self.paths = []
            self.maximum = -1
            self.update_buttons()
            self.tree.setPixmap(QPixmap(self._get_none_path()).scaled(self.tree.size()))
            return
        
        # Éviter les mises à jour inutiles
        if hasattr(self, '_last_current_parent') and hasattr(self, '_last_current_child'):
            if current_parent == self._last_current_parent and current_child == self._last_current_child:
                return
        
        self._last_current_parent = current_parent
        self._last_current_child = current_child
        
        # Get and filter paths
        paths = self.graph_manager.getShortestWays(current_parent, current_child)
        if self.variables.config["order"] == "Alphabetical":
            self.paths = sorted(paths, key=lambda x: sorted(x, key=lambda y: self.variables.getPal(y)))
        else:
            self.paths = sorted(paths, key=lambda x: [self.variables.palList.index(i) for i in x])
        self.paths = [self.paths[i] for i in range(len(self.paths)) if i == 0 or self.paths[i] != self.paths[i-1]]
        
        # Update buttons and load tree
        self.maximum = len(self.paths) - 1
        self.update_buttons()
        if self.maximum < 0:
            self.tree.setPixmap(QPixmap(self._get_none_path()).scaled(self.tree.size()))
        else:
            self.load()
    
    def load(self):
        # Forcer la génération d'une nouvelle image à chaque resize
        if not self.paths:
            none_image = self.tree_manager.getNoneImage()
            pixmap = QPixmap(none_image)
            self.tree.setPixmap(pixmap.scaled(self.tree.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            return
        
        current_path = self.paths[self.which]
        self._last_path = None  # Reset cache
        self._last_tree = None
        
        # Générer le nouvel arbre en tenant compte de la taille actuelle
        tree_width = self.tree.width()
        tree_image = self.tree_manager.getShortestGraphs(current_path, tree_width)
        pixmap = QPixmap(tree_image)
        self.tree.setPixmap(pixmap.scaled(self.tree.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        # Mettre en cache
        self._last_path = current_path
        self._last_tree = pixmap
    
    def go_next(self, value):
        self.which = (self.which + value) % (self.maximum+1)
        self.load()
    
    def go_prev(self, value):
        self.which = (self.which + value) % (self.maximum+1)
        self.load()
    
    def create_lambda(self, key):
        if "prev" in key:
            value = -int(key.split("_")[1])
            return lambda: self.go_prev(value)
        else:
            value = int(key.split("_")[1])
            return lambda: self.go_next(value)
    
    def update_buttons(self):
        if self.locked:
            for button in self.buttons.values():
                button.setEnabled(False)
        else:
            for key, button in self.buttons.items():
                value = int(key.split("_")[1])
                if "prev" in key:
                    button.setEnabled(self.maximum >= value)
                else:
                    button.setEnabled(self.maximum >= value)

    def resize_frame(self, width: int, height: int):
        # Éviter les redimensionnements inutiles
        """Update frame dimensions and refresh UI"""
        self.setFixedSize(width, height)
        # Recalculate button widths
        button_width = int(width * 0.10)
        for button in self.buttons.values():
            button.setFixedWidth(button_width)
        # Recalculate header width
        header_height = int(height * 0.1)
        self.parent_choice.setFixedHeight(header_height)
        self.child_choice.setFixedHeight(header_height)
        self.text.setFixedHeight(header_height)
        
        # Ajuster la taille des icônes en fonction de la nouvelle taille
        icon_size = int(header_height * 0.9)
        self.parent_choice.setIconSize(QSize(icon_size, icon_size))
        self.child_choice.setIconSize(QSize(icon_size, icon_size))

        self.tree.pixmap().scaled(QSize(width, height))
            
        self.apply_styles()  # Update font sizes

    def notify(self, notification_type=notification_types.ALL):
        if notification_type == notification_types.ORDER or notification_type == notification_types.ALL:
            self.on_order_changed()
        if notification_type == notification_types.LANGUAGE or notification_type == notification_types.ALL:
            self.on_language_changed()
        if notification_type == notification_types.THEME or notification_type == notification_types.ALL:
            self.on_theme_changed()
    
    def on_theme_changed(self):
        """Appelé quand le thème change"""
        # Recharger les icônes des premiers elements des combobox
        self.parent_choice.setItemIcon(0, QIcon(self._get_none_path()))
        self.child_choice.setItemIcon(0, QIcon(self._get_none_path()))
        self.tree_manager.image_cache.clear()  # Vider le cache pour régénérer les images avec le nouveau thème
        if self.maximum < 0:
            self.tree.setPixmap(QPixmap(self._get_none_path()).scaled(self.tree.size()))
        else:
            self.load()
        
    def on_order_changed(self):
        """Appelé quand l'ordre des Pals change"""
        self.populate_combo_boxes()
        self.updateTree(self.which)
        
    def on_language_changed(self):
        """Appelé quand la langue change"""
        self.text.setText(self.variables.language_manager.get_text("between"))
        self.populate_combo_boxes()
        self.popup_menu = PopupMenu(self)

    def show_context_menu(self, position):
        self.popup_menu.exec(self.tree.mapToGlobal(position))
        
    def setLocked(self, locked):
        self.locked = locked
        self.parent_choice.setEnabled(not locked)
        self.child_choice.setEnabled(not locked)
        self.update_buttons()

    def _get_none_path(self):
        return resource_path("Icons/DarkNone.png" if self.variables.config["darkMode"] else "Icons/LightNone.png")