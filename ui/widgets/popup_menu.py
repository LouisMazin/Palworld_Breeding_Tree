from PyQt6.QtWidgets import QMenu, QFileDialog
from PyQt6.QtGui import QGuiApplication, QAction
from PyQt6.QtCore import QDir

class PopupMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = self.parent().tree.pixmap()
        self.variables = self.parent().variables
        self.copy = self.variables.getText("copy")
        self.save = self.variables.getText("save")
        self.tree = self.variables.getText("tree")
        self.lock = self.variables.getText("lock")
        self.unlock = self.variables.getText("unlock")
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
        clipboard.setPixmap(self.parent().tree.pixmap(), mode=clipboard.Mode.Clipboard)

    def save_image(self):
        file_name, _ = QFileDialog.getSaveFileName(self, self.save, QDir.homePath() + self.tree, "Images (*.png)")
        if file_name:
            self.pixmap.save(file_name)

    def lock_tree(self):
        locked = not self.parent().locked
        self.lock_action.setText(self.unlock if locked else self.lock)
        self.parent().setLocked(locked)
        obj = {
            "parent": self.variables.getPalByTranslation(self.parent().parent_choice.currentText()),
            "child": self.variables.getPalByTranslation(self.parent().child_choice.currentText()),
            "number": self.parent().which
        }
        if locked:
            self.variables.addLockedCombo(obj)
        else:
            self.variables.removeLockedCombo(obj)