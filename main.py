import sys
import os

from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from interface_graphique import FenetrePrincipale, BoutonCustom
from interface_messagerie import InterfaceMessagerie
from interface_login import InterfaceLogin

# Exécution de l'application
def main():
    import os
    os.environ["HTTP_PROXY"] = "http://192.168.228.254:3128"
    os.environ["HTTPS_PROXY"] = "http://192.168.228.254:3128"

    app = QApplication(sys.argv)
    app.setStyle("fusion")

    #icone = QIcon(obtenir_vrai_chemin(""))
    #app.setWindowIcon(icone)

    fenetre_principale_instance = FenetrePrincipale()

    interface_login_instance = InterfaceLogin(fenetre_principale_instance)
    fenetre_principale_instance.ajouter_interface(interface_login_instance)





    fenetre_principale_instance.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()