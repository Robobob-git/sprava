from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QScrollArea, QLabel, QLineEdit, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QFont
from datetime import datetime
import sys


class AvatarLabel(QLabel):
    """Label qui affiche une image ronde comme avatar"""
    
    def __init__(self, color="#3498db", size=40):
        super().__init__()
        self.color = color
        self.avatar_size = size
        self.setFixedSize(size, size)
        self.create_avatar()
    
    def create_avatar(self):
        """Crée un avatar coloré rond (simulé sans image)"""
        pixmap = QPixmap(self.avatar_size, self.avatar_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dessiner un cercle coloré
        painter.setBrush(QColor(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.avatar_size, self.avatar_size)
        
        painter.end()
        self.setPixmap(pixmap)


class MessageWidget(QWidget):
    """Widget représentant un message dans le chat"""
    
    def __init__(self, auteur, heure, message, avatar_color="#3498db", show_header=True):
        super().__init__()
        self.auteur = auteur
        self.heure = heure
        self.message = message
        self.show_header = show_header
        self.avatar_color = avatar_color
        
        self.init_ui()

    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(10)
        
        # Avatar (ou espace vide si message groupé)
        if self.show_header:
            avatar = AvatarLabel(color=self.avatar_color, size=40)
            layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignTop)
        else:
            # Espace pour aligner avec les messages qui ont un avatar
            layout.addSpacing(50)
        
        # Contenu du message
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        if self.show_header:
            # Header : Nom + Heure
            header_layout = QHBoxLayout()
            
            nom_label = QLabel(self.auteur)
            nom_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
            header_layout.addWidget(nom_label)
            
            heure_label = QLabel(self.heure)
            heure_label.setStyleSheet("color: #888; font-size: 11px;")
            header_layout.addWidget(heure_label)
            
            header_layout.addStretch()
            content_layout.addLayout(header_layout)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #dcddde; font-size: 13px; line-height: 1.4;")
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content_layout.addWidget(message_label)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        self.setLayout(layout)


class DateSeparator(QWidget):
    """Séparateur de date entre les messages"""
    
    def __init__(self, date_text):
        super().__init__()
        self.date_text = date_text
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Ligne gauche
        left_line = QFrame()
        left_line.setFrameShape(QFrame.Shape.HLine)
        left_line.setStyleSheet("background-color: #3a3a3a; max-height: 1px;")
        
        # Date
        date_label = QLabel(self.date_text)
        date_label.setStyleSheet("color: #888; font-size: 11px; font-weight: bold; padding: 0 10px;")
        
        # Ligne droite
        right_line = QFrame()
        right_line.setFrameShape(QFrame.Shape.HLine)
        right_line.setStyleSheet("background-color: #3a3a3a; max-height: 1px;")
        
        layout.addWidget(left_line)
        layout.addWidget(date_label)
        layout.addWidget(right_line)
        
        self.setLayout(layout)


class ChatWidget(QWidget):
    """Widget principal du chat"""
    
    def __init__(self):
        super().__init__()
        self.messages = []
        self.init_ui()
        self.add_example_messages()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Zone de scroll pour les messages
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #36393f;
            }
            QScrollBar:vertical {
                background-color: #2f3136;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #202225;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #18191c;
            }
        """)
        
        # Container pour les messages
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setContentsMargins(0, 10, 0, 10)
        self.messages_layout.setSpacing(0)
        self.messages_layout.addStretch()
        self.messages_container.setLayout(self.messages_layout)
        self.messages_container.setStyleSheet("background-color: #36393f;")
        
        scroll_area.setWidget(self.messages_container)
        
        # Zone de saisie
        input_widget = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Envoyer un message...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #40444b;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                color: white;
                font-size: 14px;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        
        send_button = QPushButton("Envoyer")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #5865f2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
        """)
        send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_button)
        input_widget.setLayout(input_layout)
        
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(input_widget)
        
        self.setLayout(main_layout)
        self.scroll_area = scroll_area
    
    def add_message(self, auteur, message, heure=None, avatar_color="#3498db", show_header=True):
        """Ajoute un message au chat"""
        if heure is None:
            heure = datetime.now().strftime("Hier à %H:%M")
        
        message_widget = MessageWidget(auteur, heure, message, avatar_color, show_header)
        
        # Insérer avant le stretch
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_widget)
        self.messages.append(message_widget)
        
        # Scroller en bas
        self.scroll_to_bottom()
    
    def add_date_separator(self, date_text):
        """Ajoute un séparateur de date"""
        separator = DateSeparator(date_text)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, separator)
    
    def scroll_to_bottom(self):
        """Scroll automatiquement vers le bas"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Envoie un message (simulé)"""
        text = self.message_input.text().strip()
        if text:
            self.add_message("Vous", text, datetime.now().strftime("Maintenant"), "#e74c3c", show_header=True)
            self.message_input.clear()
    
    def add_example_messages(self):
        """Ajoute des messages d'exemple"""
        self.add_date_separator("5 avril 2026")
        
        self.add_message("Florian", "Je te chercher à 18h50 environ\n?", "Hier à 14:30", "#e67e22", show_header=True)
        
        self.add_message("Robobob", "Ouais", "Hier à 14:42", "#3498db", show_header=True)
        
        self.add_message("Robobob", "Y'a moyen on va aussi chercher marwan chez lui?", "Hier à 14:53", "#3498db", show_header=False)
        
        self.add_message("Florian", "Ouai", "Hier à 14:53", "#e67e22", show_header=True)
        self.add_message("Florian", "C'est bien là où je t'ai montré hier", "Hier à 14:53", "#e67e22", show_header=False)
        
        self.add_message("Robobob", "Exactement là", "Hier à 14:54", "#3498db", show_header=True)
        
        self.add_message("Florian", "Carré", "Hier à 14:54", "#e67e22", show_header=True)
        self.add_message("Florian", "Je te cherche d'abord toi et apres lui", "Hier à 14:54", "#e67e22", show_header=False)
        
        self.add_message("Robobob", "Ui", "Hier à 14:55", "#3498db", show_header=True)
        
        self.add_message("Florian", "J'arrive dans 15-20min", "Hier à 18:34", "#e67e22", show_header=True)
        self.add_message("Florian", "Soit deja dehors jai la flemme de me garer", "Hier à 18:34", "#e67e22", show_header=False)
        
        self.add_message("Robobob", "Oui", "Hier à 18:41", "#3498db", show_header=True)
        
        self.add_date_separator("6 avril 2026")
        
        self.add_message("Florian", "invincible ?", "00:40", "#e67e22", show_header=True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Messages Privés")
        self.setGeometry(100, 100, 800, 600)
        
        # Style global
        self.setStyleSheet("""
            QMainWindow {
                background-color: #36393f;
            }
        """)
        
        # Widget central
        chat_widget = ChatWidget()
        self.setCentralWidget(chat_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Police par défaut
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
