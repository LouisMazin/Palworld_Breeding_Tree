from PyQt6.QtWidgets import QWidget, QGridLayout
from ui.widgets.tree_frame import TreeFrame
from core.variables_manager import VariablesManager
from core.observer_manager import ObserverManager, NotificationTypes

class TreeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.variablesManager = VariablesManager()
        self.observerManager = ObserverManager.getInstance()
        self.observerManager.addObserver(self)
        self.visibleFrames = 0
        self.minimumSquareSize = int(self.variablesManager.minScreenSize/2.1)  # Taille minimum fixe pour les frames
        
        # Créer les frames en fonction du paramètre combo
        self.treeFrames = []
        locked = self.variablesManager.getConfig("locked")
        for lock in locked:
            self.treeFrames.append(TreeFrame(self.minimumSquareSize,lock))
        for _ in range(3-len(locked)):
            self.treeFrames.append(TreeFrame(self.minimumSquareSize))
        # Cache pour la dernière taille calculée
        self.lastCalculatedSize = None
        self.setupUi()

    def setupUi(self):
        self.mainLayout = QGridLayout()
        # Réduire les marges au minimum
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.mainLayout.setSpacing(2)  # Réduire l'espacement entre les frames
        self.setLayout(self.mainLayout)
        self.doResize()  # Appeler do_resize après l'initialisation de l'interface utilisateur


    def resizeEvent(self, event):
        # Sauvegarder la nouvelle taille
        self.variablesManager.setConfig(
            "windowSize",
            {
                "width": int(self.size().width() * self.variablesManager.dpi),
                "height": int(self.size().height() * self.variablesManager.dpi)
            }
        )
        self.doResize()  # Appeler do_resize pour redimensionner les frames

    def doResize(self):
        size = self.size()
        width = size.width()
        height = size.height()
        
        # Calcul du nombre optimal de frames
        optimalFrameCount = min(
            self.variablesManager.getConfig("maxTrees"),
            max(1, width // self.minimumSquareSize)
        )
        # Recalculer la taille des frames
        availableWidth = width - (optimalFrameCount + 1) * 2
        widthPerFrame = availableWidth // optimalFrameCount
        squareSize = min(widthPerFrame, height - int(40 / self.variablesManager.dpi))  # Ajuster pour les marges en fonction du DPI
        
        # Mise à jour des frames
        if optimalFrameCount != self.visibleFrames:
            # Nettoyer le layout existant
            for i in reversed(range(self.mainLayout.count())): 
                self.mainLayout.itemAt(i).widget().hide()
                self.mainLayout.removeItem(self.mainLayout.itemAt(i))
            
            # Ajouter les nouveaux frames
            for i in range(optimalFrameCount):
                frame = self.treeFrames[i]
                self.mainLayout.addWidget(frame, 0, i)
                frame.resizeFrame(squareSize, squareSize)
                self.treeFrames[i].load()
                frame.show()
            
            self.visibleFrames = optimalFrameCount
        else:
            # Juste redimensionner
            for i in range(optimalFrameCount):
                self.treeFrames[i].resizeFrame(squareSize, squareSize)
                self.treeFrames[i].load()  # Recharger l'image de l'arbre après redimensionnement

    def notify(self, notification_type=NotificationTypes.ALL):
        if notification_type == NotificationTypes.MAXTREES or notification_type == NotificationTypes.ALL:
            self.doResize()


