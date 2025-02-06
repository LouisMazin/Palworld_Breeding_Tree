from PyQt6.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from core.variables_manager import VariablesManager
from core.tree_manager import TreeManager
from core.graph_manager import GraphManager
from core.observer_manager import ObserverManager, NotificationTypes
from os import environ, path
import sys
from .popup_menu import PopupMenu

def resourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = path.abspath(".")
    return path.join(basePath, relativePath)

environ["PATH"] += resourcePath("Graphviz\\bin")+";"

class TreeFrame(QFrame):
    def __init__(self, side: int, combo=None):
        super().__init__()
        self.setFixedSize(side, side)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(1)
        
        # Initialize managers
        self.variablesManager = VariablesManager()
        self.treeManager = TreeManager()
        self.graphManager = GraphManager()
        self.observerManager = ObserverManager.getInstance()
        self.observerManager.addObserver(self)
        self.combo = combo
        # Cache pour les icônes
        self.iconCache = {}
        # Cache pour le dernier arbre généré
        self.lastTree = None
        self.lastePath = None
        # Initialiser paths et maximum
        self.locked = False
        self.paths = []
        self.maximum = -1
        self.which = 0  # Initialiser self.which
        # Setup UI components
        self.setupUi()
        # Initial update
        self.updateTree(0)
        # Initialize popup menu
        self.popupMenu = PopupMenu(self)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # Appliquer les valeurs de combo si fournies
        if self.combo:
            self.applyCombo(self.combo)
        
    def applyCouple(self, parent, child, number):
        self.applyOldChoice({"parent": parent, "child": child, "number": number})
    def applyCombo(self, combo):
        self.applyOldChoice(combo,True)
    def applyOldChoice(self, combo, locked=False):
        for index in range(self.parentChoice.count()):
            if self.parentChoice.itemData(index) == combo["parent"]:
                self.parentChoice.setCurrentIndex(index)
                break
        for index in range(self.childChoice.count()):
            if self.childChoice.itemData(index) == combo["child"]:
                self.childChoice.setCurrentIndex(index)
                break
        self.which = combo["number"]
        self.updateTree(self.which)
        self.setLocked(locked)
    def setupUi(self):
        # Create main vertical layout with proper spacing
        self.mainLayout = QGridLayout(self)

        # Create header section
        headerWidget = QWidget()
        headerWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.headerLayout = QHBoxLayout(headerWidget)
        self.headerLayout.setSpacing(5)
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        
        # Calculate header height (6% of frame height)
        headerHeight = int(self.height() * 0.06)
        
        # Setup combo boxes with improved styling
        self.parentChoice = QComboBox()
        self.childChoice = QComboBox()
        for combo in [self.parentChoice, self.childChoice]:
            combo.setEditable(True)
            combo.setIconSize(QSize(int(headerHeight * 0.55), int(headerHeight * 0.55)))  # Taille d'icône proportionnelle
            combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            combo.currentIndexChanged.connect(lambda x : self.updateTree(0))
            # Centrer le texte verticalement et ajuster les marges
            lineEdit = combo.lineEdit()
            lineEdit.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            lineEdit.setStyleSheet(f"""
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
        self.text = QLabel(self.variablesManager.getText("between"))
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Add widgets to header layout
        self.headerLayout.addWidget(self.parentChoice, 2)
        self.headerLayout.addWidget(self.text, 1)
        self.headerLayout.addWidget(self.childChoice, 2)
        
        # Create content section
        contentWidget = QWidget()
        contentLayout = QHBoxLayout(contentWidget)
        contentLayout.setSpacing(5)
        contentLayout.setContentsMargins(0, 0, 0, 0)
        
        # Setup navigation buttons containers
        navLeft = QVBoxLayout()
        navRight = QVBoxLayout()
        navLeft.setSpacing(5)
        navRight.setSpacing(5)
        
        # Calculate button width (15% of frame width)
        buttonWidth = int(self.width() * 0.15)
        
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
            button.setFixedWidth(buttonWidth)
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            button.clicked.connect(self.create_lambda(key))
            layout = navRight if "next" in key else navLeft
            layout.addWidget(button, 1)
        
        # Setup tree label
        self.tree = QLabel()
        self.tree.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Assemble the content layout
        contentLayout.addLayout(navLeft, 1)
        contentLayout.addWidget(self.tree, 8)  # Tree gets more space
        contentLayout.addLayout(navRight, 1)
        
        # Add everything to main layout
        self.mainLayout.addWidget(headerWidget, 0, 0)
        self.mainLayout.addWidget(contentWidget, 1, 0)
        self.mainLayout.setRowStretch(0, 1)
        self.mainLayout.setRowStretch(1, 8)

        self.populateComboBoxes()
        self.applyStyles()
    
    def populateComboBoxes(self):
        try:
            self.parentChoice.blockSignals(True)
            self.childChoice.blockSignals(True)
            
            # Sauvegarder les sélections actuelles
            currentParentIndex = self.parentChoice.currentIndex() 
            currentChildIndex = self.childChoice.currentIndex()
            currentParent = self.parentChoice.itemData(currentParentIndex) if currentParentIndex > 0 else ""
            currentChild = self.childChoice.itemData(currentChildIndex) if currentChildIndex > 0 else ""
            # Vider les combobox
            self.parentChoice.clear()
            self.childChoice.clear()
            
            # Ajouter les éléments par défaut
            noneImage = QIcon(self._get_none_path())
            self.parentChoice.addItem(noneImage, self.variablesManager.getText("parent"), "")
            self.childChoice.addItem(noneImage, self.variablesManager.getText("child"), "")
            
            self.usedList = self.variablesManager.getOrderedPalList()
            
            # Ajouter les Pals dans l'ordre approprié
            for pal in self.usedList:
                tradPal = self.variablesManager.getPal(pal)
                if pal not in self.iconCache:
                    icon = QIcon(resourcePath(f"Icons/{pal}.png"))
                    self.iconCache[pal] = icon
                else:
                    icon = self.iconCache[pal]
                self.parentChoice.addItem(icon, tradPal, pal)
                self.childChoice.addItem(icon, tradPal, pal)
                
            if self.combo:
                self.applyCombo(self.combo)
            else:
                self.applyCouple(currentParent, currentChild, self.which)
                
            self.parentChoice.blockSignals(False)
            self.childChoice.blockSignals(False)
        except Exception as e:
            # Restaurer les signaux en cas d'erreur
            self.parentChoice.blockSignals(False)
            self.childChoice.blockSignals(False)
    
    def applyStyles(self):
        # Calculer les tailles
        headerHeight = int(self.height() * 0.1)
        fontSize = int(headerHeight * 0.30)
        arrowWidth = int(headerHeight * 0.37)
        buttonFontSize = int(self.height() * 0.03)  # Maximum de 12px
        style = f"""
            QComboBox {{
                font-size: {fontSize}px;
            }}
            QComboBox::drop-down {{
                width: {arrowWidth}px;
            }}
            QComboBox::down-arrow {{
                width: {arrowWidth}px;
                height: {arrowWidth}px;
            }}
            QComboBox QAbstractItemView {{
                font-size: {fontSize}px;
            }}
            QComboBox QAbstractItemView::item {{
                height: {headerHeight}px;
            }}
            QPushButton {{
                font-size: {buttonFontSize}px;
            }}
            QLabel {{
                font-size: {fontSize}px;
            }}
        """
        self.setStyleSheet(self.styleSheet()+style)
        
    def updateTree(self, which=None):
        if which is not None:
            self.which = which
        currentParentIndex = self.parentChoice.currentIndex() 
        currentChildIndex = self.childChoice.currentIndex()
        currentParent = self.parentChoice.itemData(currentParentIndex) if currentParentIndex > 0 else ""
        currentChild = self.childChoice.itemData(currentChildIndex) if currentChildIndex > 0 else ""
        
        if not currentParent and not currentChild:
            self.paths = []
            self.maximum = -1
            self.update_buttons()
            self.tree.setPixmap(QPixmap(self._get_none_path()).scaled(self.tree.size()))
            return
        
        # Éviter les mises à jour inutiles
        if hasattr(self, 'lastCurrentParent') and hasattr(self, 'lastCurrentChild'):
            if currentParent == self.lastCurrentParent and currentChild == self.lastCurrentChild:
                return
        
        self.lastCurrentParent = currentParent
        self.lastCurrentChild = currentChild
        
        # Get and filter paths
        paths = self.graphManager.getShortestWays(currentParent, currentChild)
        if self.variablesManager.getConfig("order") == "Alphabetical":
            self.paths = sorted(paths, key=lambda x: sorted(x, key=lambda y: self.variablesManager.getPal(y)))
        else:
            self.paths = sorted(paths, key=lambda x: [self.variablesManager.palList.index(i) for i in x])
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
            noneImage = self.treeManager.getNoneImage()
            pixmap = QPixmap(noneImage)
            self.tree.setPixmap(pixmap.scaled(self.tree.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            return
        
        currentPath = self.paths[self.which]
        self.lastPath = None  # Reset cache
        self.lastTree = None
        
        # Générer le nouvel arbre en tenant compte de la taille actuelle
        treeWidth = self.tree.width()
        treeImage = self.treeManager.getShortestGraphs(currentPath, treeWidth)
        pixmap = QPixmap(treeImage)
        self.tree.setPixmap(pixmap.scaled(self.tree.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        # Mettre en cache
        self.lastPath = currentPath
        self.lastTree = pixmap
    
    def goNext(self, value):
        self.which = (self.which + value) % (self.maximum+1)
        self.load()
    
    def goPrev(self, value):
        self.which = (self.which + value) % (self.maximum+1)
        self.load()
    
    def create_lambda(self, key):
        if "prev" in key:
            value = -int(key.split("_")[1])
            return lambda: self.goPrev(value)
        else:
            value = int(key.split("_")[1])
            return lambda: self.goNext(value)
    
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

    def resizeFrame(self, width: int, height: int):
        # Éviter les redimensionnements inutiles
        """Update frame dimensions and refresh UI"""
        self.setFixedSize(width, height)
        # Recalculate button widths
        buttonWidth = int(width * 0.10)
        for button in self.buttons.values():
            button.setFixedWidth(buttonWidth)
        # Recalculate header width
        headerHeight = int(height * 0.1)
        self.parentChoice.setFixedHeight(headerHeight)
        self.childChoice.setFixedHeight(headerHeight)
        self.text.setFixedHeight(headerHeight)
        
        # Ajuster la taille des icônes en fonction de la nouvelle taille
        iconSize = int(headerHeight * 0.9)
        self.parentChoice.setIconSize(QSize(iconSize, iconSize))
        self.childChoice.setIconSize(QSize(iconSize, iconSize))

        self.tree.pixmap().scaled(QSize(width, height))
            
        self.applyStyles()  # Update font sizes

    def notify(self, notification_type=NotificationTypes.ALL):
        if notification_type == NotificationTypes.ORDER or notification_type == NotificationTypes.ALL:
            self.onOrderChanged()
        if notification_type == NotificationTypes.LANGUAGE or notification_type == NotificationTypes.ALL:
            self.onLanguageChanged()
        if notification_type == NotificationTypes.THEME or notification_type == NotificationTypes.ALL:
            self.onThemeChanged()
    
    def onThemeChanged(self):
        """Appelé quand le thème change"""
        # Recharger les icônes des premiers elements des combobox
        self.parentChoice.setItemIcon(0, QIcon(self._get_none_path()))
        self.childChoice.setItemIcon(0, QIcon(self._get_none_path()))
        self.treeManager.imagesCache.clear()  # Vider le cache pour régénérer les images avec le nouveau thème
        if self.maximum < 0:
            self.tree.setPixmap(QPixmap(self._get_none_path()).scaled(self.tree.size()))
        else:
            self.load()
        
    def onOrderChanged(self):
        """Appelé quand l'ordre des Pals change"""
        self.populateComboBoxes()
        self.updateTree(self.which)
        
    def onLanguageChanged(self):
        """Appelé quand la langue change"""
        print(self.variablesManager.getConfig("language"))
        self.text.setText(self.variablesManager.getText("between"))
        self.populateComboBoxes()
        self.popupMenu = PopupMenu(self)

    def show_context_menu(self, position):
        self.popupMenu.exec(self.tree.mapToGlobal(position))
        
    def setLocked(self, locked):
        self.locked = locked
        self.parentChoice.setEnabled(not locked)
        self.childChoice.setEnabled(not locked)
        self.update_buttons()

    def _get_none_path(self):
        return resourcePath("Icons/DarkNone.png" if self.variablesManager.getConfig("darkMode") else "Icons/LightNone.png")