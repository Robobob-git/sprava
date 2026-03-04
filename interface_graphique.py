import sys
import os
from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem, QButtonGroup, QToolButton
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont, QCursor

from autre_fonctions import obtenir_vrai_chemin

class FenetrePrincipale(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre
        self.setWindowTitle("Sprava")
        self.setGeometry(100, 100, 800, 600)

        # Création du widget principal qui va tout contenir
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Création du layout principal que l'on met dans le widget principal
        main_layout = QVBoxLayout()
        self.central_widget.setLayout(main_layout)

        # Création du layout en grille pour le contenu
        contenu_widget = QWidget()
        self.layout = QGridLayout()
        #self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contenu_widget.setLayout(self.layout)

        # Met le widget de contenu dans le layout principal
        main_layout.addWidget(contenu_widget)

        self.menu_principal_bouton()

        #self.construire_logo()
        self.restore_menu_principal() # Construit la fenêtre principale (la première fois), cette fonction peut être rappelée plus tard pour re-afficher la fenêtre principale

    def ajouter_interface(self, interface, ligne, col):
        self.layout.addWidget(interface, ligne, col)

    def changer_interface(self, interface):
        self.clear_layout()
        interface.show()

    def nouvelle_page(self):
      self.clear_layout()

    def clear_layout(self):
      # Boucle qui cache tous les widgets dans le layout
      for i in range(self.layout.count()):
        child = self.layout.itemAt(i)
        if child.widget():
          child.widget().hide()

    def restore_menu_principal(self):
      self.clear_layout()
      #self.logo_menu_principal.show()
    
    def menu_principal_bouton(self):
      menu_principal_bouton = BoutonCustom("Menu principal", taille=(100, 50), custom_command=self.restore_menu_principal, nouvelle_page=False)
      menu_principal_bouton.hide()
      self.central_widget.layout().addWidget(menu_principal_bouton, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)


class BoutonCustom(QPushButton):
    def __init__(self, texte:str=None, taille=(200, 200), marge:int = 0, style:str=None, chemin_image:str = None, custom_command = None, nouvelle_page:bool = False):
        super().__init__()
        self.custom_custom_command = custom_command
        self.nouvelle_page = nouvelle_page

        self.setFixedSize(*taille)

        if texte:
            self.setText(texte)
        
        if chemin_image:
            self.setIcon(QIcon(chemin_image))
            self.setIconSize(QSize(*taille))
        
        self.setStyleSheet(f"""
        QPushButton {{
            background-color: #2f3136;      /* gris foncé */
            color: #ffffff;                 /* texte blanc */
            border-radius: 6px;             /* arrondi léger */
            border: none;                   /* pas de bordure */
            padding: {marge}px;              /* espace intérieur */
            font-size: 13px;                /* taille du texte */
        }}

        QPushButton:hover {{
            background-color: #404249;      /* un peu plus clair au hover */
        }}

        QPushButton:focus {{
            outline: none;
            border: none;
        }}
        """)

        if style:
            self.setStyleSheet(style)
            
        # Ajoute un évènement quand on clique sur le bouton
        self.clicked.connect(self.on_bouton_clicked)

    def on_bouton_clicked(self):
        if self.custom_custom_command:
            self.custom_custom_command()

class BoutonCustomVetical(QToolButton):
    def __init__(self, texte:str, taille=(200, 200), marge:int = 0, style:str=None, chemin_image:str = None, custom_command = None, nouvelle_page:bool = False):
        super().__init__()
        self.custom_custom_command = custom_command
        self.nouvelle_page = nouvelle_page

        self.setText(texte)
        self.setFixedSize(*taille)

        
        if chemin_image:
            self.setIcon(QIcon(chemin_image))
            self.setIconSize(taille)
            self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        self.setStyleSheet(f"""
        QPushButton {{
            background-color: #5865F2;
            border-radius: 8px;
            color: white;
            padding: {marge}px;   /* espace entre bord et contenu */
        }}
        QPushButton:hover {{
            background-color: #4752C4;
        }}
        """)

        if style:
            self.setStyleSheet(style)
            
        # Ajoute un évènement quand on clique sur le bouton
        self.clicked.connect(self.on_bouton_clicked)

    def on_bouton_clicked(self):
        if self.custom_custom_command:
            self.custom_custom_command()

class TexteEtImage(QWidget):
    def __init__(self, texte:str, chemin_image:str):
        super().__init__()

        layout = QHBoxLayout()

        image_label = QLabel()
        pixmap = QPixmap(chemin_image).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(pixmap)
        label = QLabel(texte)

        layout.addWidget(image_label)
        layout.addWidget(label)

        self.setLayout(layout)


class ListeElements(QListWidget):
    def __init__(self, parent=None, horizontal:bool=False, custom_command=None):
        super().__init__(parent)

        self.setSpacing(2)
        self.setFrameShape(QListWidget.Shape.NoFrame)

        if horizontal:
            self.setFlow(QListView.Flow.LeftToRight)
            self.setWrapping(False)  # pas de retour à la ligne automatique
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1f22;
            }
            QListWidget::item {
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #2b2d31;
            }
            QListWidget::item:selected {
                background-color: #404249;
            }
        """)

        if custom_command:
            self.itemClicked.connect(custom_command)

    def ajouter_item(self, data, widget: QWidget, largeur=120, hauteur=42):
        item = QListWidgetItem(self)
        item.setSizeHint(QSize(largeur, hauteur))
        item.setData(Qt.ItemDataRole.UserRole, data)
        self.addItem(item)
        self.setItemWidget(item, widget)


class GroupeBoutons(QWidget):
    def __init__(self, boutons:list[QPushButton]):
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)

        for btn in boutons:
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.layout.addWidget(btn)
        
        self.setStyleSheet("""
        QPushButton {
            background-color: #2b2d31;
            color: white;
            border-radius: 12px;
            padding: 6px 14px;
            border: none;
            font-size: 13px;
        }

        QPushButton:hover {
            background-color: #3a3c43;
        }

        QPushButton:checked {
            background-color: #404249;
        }

        QPushButton#ajouter {
            background-color: #5865F2;
            padding: 6px 16px;
        }

        QPushButton#ajouter:hover {
            background-color: #4752C4;
        }
        """)

class LigneCategorie(QWidget):
        def __init__(self):
            super().__init__()

            self.layout = QHBoxLayout()
            self.setLayout(self.layout)

            self.liste_categories = []
            self.categorie_actuelle = None

        def ajouter_categorie(self, categorie:QWidget):
            self.layout.addWidget(categorie)
            self.liste_categories.append(categorie)
            categorie.hide()
        
        def changer_categorie(self, categorie:QWidget):
            if categorie == self.categorie_actuelle:
                return

            if categorie in self.liste_categories:
                if self.categorie_actuelle:
                    self.categorie_actuelle.hide()

                categorie.show()
                self.categorie_actuelle = categorie
            else:
                print(f"Catégorie {categorie} innexistante")

class MenuDeroulable(QMenu):
    def __init__(self, actions:list, pos_separateurs:list[int]=None, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 6px 0px;
                min-width: 220px;
            }
            QMenu::item {
                color: #ffffff;
                font-size: 14px;
                padding: 10px 20px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3a3a3a;
                margin: 4px 10px;
            }
        """)

        for i, action in enumerate(actions):
            if i in pos_separateurs:
                self.addSeparator()
            self.addAction(action)




def main():
    app = QApplication(sys.argv)
    app.setStyle("fusion")

    fenetre = fenetre_principale()
    fenetre.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()