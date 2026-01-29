import sys
import os
from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

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
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contenu_widget.setLayout(self.layout)

        # Met le widget de contenu dans le layout principal
        main_layout.addWidget(contenu_widget)

        self.menu_principal_bouton()

        #self.construire_logo()
        self.restore_menu_principal() # Construit la fenêtre principale (la première fois), cette fonction peut être rappelée plus tard pour re-afficher la fenêtre principale

    def ajouter_interface(self, interface):
        self.layout.addWidget(interface)

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
    def __init__(self, texte:str, taille=(200, 200), marge:float or int = 20, chemin_image:str = None, custom_command = None, nouvelle_page:bool = False, layout_horizontal:bool=False):
        super().__init__()
        self.custom_custom_command = custom_command
        self.nouvelle_page = nouvelle_page
        
        # Fixe les tailles maximales/minimales
        self.setMaximumSize(*taille)
        self.setMinimumSize(*taille)

        # Crée un layout dans le bouton-même pour organiser texte et image
        if not layout_horizontal:
          bouton_layout = QVBoxLayout(self)
        else:
          bouton_layout = QHBoxLayout(self)


        # Met le texte en tant que Label affiché sur le haut du bouton 
        text_label = QLabel(texte)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Centre le texte
        if not layout_horizontal:
          bouton_layout.addWidget(text_label)

        # Si il y a un chemin d'image associé, met une image sur le bouton en dessous du texte
        if chemin_image:
            pixmap = QPixmap(chemin_image)
            scaled_pixmap = pixmap.scaled(taille[0]-marge, taille[1]-marge, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bouton_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)
            if layout_horizontal:
              bouton_layout.addWidget(text_label)

        # Ajoute un évènement quand on clique sur le bouton
        self.clicked.connect(self.on_bouton_clicked)

    def on_bouton_clicked(self):
        if self.custom_custom_command:
            self.custom_custom_command()

class ListeElements(QWidget):
    def __init__(self, donnees:list, widget_type, on_click):
        super().__init__()

        self.layout = QVBoxLayout(self)
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
        for donnee in donnees:
            item = QListWidgetItem(self.liste)
            item.setData(Qt.ItemDataRole.UserRole, donnee)
            #item.setSizeHint(QSize(280, 60))

            widget = widget_type(donnee)
            self.liste.setItemWidget(item, widget)

            self.liste_contacts.setItemWidget(item, self.layout)

        if on_click:
            self.liste.itemClicked.connect(on_click)

        self.layout.addWidget(self.liste)
        

        
def main():
    app = QApplication(sys.argv)
    app.setStyle("fusion")

    #icone = QIcon(obtenir_vrai_chemin(""))
    #app.setWindowIcon(icone)

    fenetre = fenetre_principale()
    fenetre.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()