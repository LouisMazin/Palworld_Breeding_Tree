from PyQt6.QtWidgets import QWidget, QGridLayout
from ui.widgets.tree_frame import TreeFrame
from core.variables_manager import VariablesManager
from core.observer_manager import ObserverManager, notification_types

class TreeWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.dpi = self.app.primaryScreen().devicePixelRatio()
        self.variables_manager = VariablesManager()
        
        self.observer_manager = ObserverManager.get_instance()
        self.observer_manager.add_observer(self)
        self.visible_frames = 0
        self.minimumSquareSize = int(455/self.dpi)  # Taille minimum fixe pour les frames
        
        # Créer les frames en fonction du paramètre combo
        self.tree_frames = []
        for combo in self.variables_manager.config["locked"][:3]:
            self.tree_frames.append(TreeFrame(self.minimumSquareSize, combo))
        for _ in range(3 - len(self.tree_frames)):
            self.tree_frames.append(TreeFrame(self.minimumSquareSize))
        # Cache pour la dernière taille calculée
        self._last_calculated_size = None
        
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()
        # Réduire les marges au minimum
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)  # Réduire l'espacement entre les frames
        self.setLayout(self.layout)
        self.do_resize()  # Appeler do_resize après l'initialisation de l'interface utilisateur

    def calculate_optimal_frame_count(self, total_width):
        # Un frame par tranche de 300px de largeur disponible
        max_frames = total_width // self.minimumSquareSize
        return min(self.variables_manager.get("max_trees"), max(1, max_frames))

    def resizeEvent(self, event):
        # Sauvegarder la nouvelle taille
        self.variables_manager.config["windowSize"] = {
            "width": int(self.size().width() * self.dpi),
            "height": int(self.size().height() * self.dpi)
        }
        self.variables_manager.save_config()
        self.do_resize()  # Appeler do_resize pour redimensionner les frames

    def do_resize(self):
        size = self.size()
        width = size.width()
        height = size.height()
        
        # Calcul du nombre optimal de frames
        optimal_frame_count = min(
            self.variables_manager.config["max_trees"],
            max(1, width // self.minimumSquareSize)
        )
        
        # Recalculer la taille des frames
        available_width = width - (optimal_frame_count + 1) * 2
        width_per_frame = available_width // optimal_frame_count
        square_size = min(width_per_frame, height - int(40 / self.dpi))  # Ajuster pour les marges en fonction du DPI
        
        # Mise à jour des frames
        if optimal_frame_count != self.visible_frames:
            # Nettoyer le layout existant
            for i in reversed(range(self.layout.count())): 
                self.layout.itemAt(i).widget().hide()
                self.layout.removeItem(self.layout.itemAt(i))
            
            # Ajouter les nouveaux frames
            for i in range(optimal_frame_count):
                frame = self.tree_frames[i]
                self.layout.addWidget(frame, 0, i)
                frame.resize_frame(square_size, square_size)
                self.tree_frames[i].load()
                frame.show()
            
            self.visible_frames = optimal_frame_count
        else:
            # Juste redimensionner
            for i in range(optimal_frame_count):
                self.tree_frames[i].resize_frame(square_size, square_size)
                self.tree_frames[i].load()  # Recharger l'image de l'arbre après redimensionnement

    def notify(self, notification_type=notification_types.ALL):
        if notification_type == notification_types.MAX_TREES or notification_type == notification_types.ALL:
            self.do_resize()


