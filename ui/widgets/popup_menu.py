from PyQt6.QtWidgets import QMenu, QFileDialog
from PyQt6.QtGui import QGuiApplication, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import QDir
from core.variables_manager import VariablesManager
from core.tree_manager import TreeManager
from os import path
class PopupMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.variablesManager = VariablesManager()
        self.treeManager = TreeManager()
        self.copy = self.variablesManager.getText("copy")
        self.save = self.variablesManager.getText("save")
        self.tree = self.variablesManager.getText("tree")
        self.lock = self.variablesManager.getText("lock")
        self.unlock = self.variablesManager.getText("unlock")
        self.init_menu()
    def init_menu(self):
        copy_action = QAction(self.copy, self)
        copy_action.triggered.connect(self.copy_image)
        self.addAction(copy_action)

        save_action = QAction(self.save, self)
        save_action.triggered.connect(self.save_image)
        self.addAction(save_action)
        
        self.lock_action = QAction(self.unlock if self.parent().locked else self.lock, self)
        self.lock_action.triggered.connect(self.lock_tree)
        self.addAction(self.lock_action)

    def copy_image(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setPixmap(self.addBackground(self.parent().tree.pixmap()), mode=clipboard.Mode.Clipboard)
    def addBackground(self, pixmap: QPixmap):
        background = QPixmap(pixmap.size())
        background.fill(QColor(self.variablesManager.getColor("secondaryDarkColor")))
        painter = QPainter(background)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return background
    def save_image(self):
        file_name, _ = QFileDialog.getSaveFileName(self, self.save, path.join(QDir.homePath(),self.tree), "Images (*.png)")
        if file_name:
            self.parent().tree.pixmap().save(file_name)

    def lock_tree(self):
        locked = not self.parent().locked
        self.lock_action.setText(self.unlock if locked else self.lock)
        self.parent().setLocked(locked)
        obj = {
            "parent": self.variablesManager.getPalByTranslation(self.parent().parentChoice.currentText()),
            "child": self.variablesManager.getPalByTranslation(self.parent().childChoice.currentText()),
            "number": self.parent().which
        }
        if locked:
            self.variablesManager.addLockedCombo(obj)
        else:
            self.variablesManager.removeLockedCombo(obj)