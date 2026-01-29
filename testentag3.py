import sys
from dataclasses import dataclass
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                              QListWidget, QListWidgetItem, QLabel, QHBoxLayout)
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QSize

@dataclass
class Ami:
    username: str
    status: str
    avatar_path: str | None = None

class WidgetAmi(QWidget):
    """Widget personnalisé pour afficher un ami"""
    def __init__(self, ami: Ami):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Avatar
        avatar_label = QLabel()
        avatar = self._creer_avatar(ami, 40)
        avatar_label.setPixmap(avatar)
        avatar_label.setFixedSize(40, 40)
        
        # Infos (nom + statut)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        nom = QLabel(ami.username)
        nom.setStyleSheet("color: white; font-size: 11pt; font-weight: bold;")
        
        statut = QLabel(ami.status)
        couleur = "#43b581" if ami.status == "online" else "#747f8d"
        statut.setStyleSheet(f"color: {couleur}; font-size: 9pt;")
        
        info_layout.addWidget(nom)
        info_layout.addWidget(statut)
        
        layout.addWidget(avatar_label)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _creer_avatar(self, ami: Ami, size: int):
        if ami.avatar_path:
            pix = QPixmap(ami.avatar_path)
            if not pix.isNull():
                return pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
        
        # Avatar par défaut (cercle coloré)
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#5865f2"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()
        return pix

class FenetreAmis(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Liste d'amis avec avatars")
        self.resize(300, 400)
        
        self.liste = QListWidget()
        self.liste.setStyleSheet("""
            QListWidget {
                background-color: #1e1f22;
                border: none;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #2b2d31;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: #292b2f;
            }
            QListWidget::item:selected {
                background-color: #2f3136;
            }
        """)
        
        # Ajouter des amis
        amis = [
            Ami("Alice", "online"),
            Ami("Bob", "offline"),
            Ami("Charlie", "online"),
            Ami("Diana", "offline"),
            Ami("Eve", "online"),
        ]
        
        for ami in amis:
            item = QListWidgetItem(self.liste)
            item.setSizeHint(QSize(280, 60))
            item.setData(Qt.ItemDataRole.UserRole, ami)
            
            widget = WidgetAmi(ami)
            self.liste.setItemWidget(item, widget)
        
        self.liste.itemClicked.connect(self.ami_clique)
        
        layout = QVBoxLayout()
        layout.addWidget(self.liste)
        self.setLayout(layout)
    
    def ami_clique(self, item):
        ami = item.data(Qt.ItemDataRole.UserRole)
        print(f"Ami cliqué : {ami.username}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreAmis()
    fenetre.show()
    sys.exit(app.exec())