import sys
import os

from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from interfaces.interface_graphique import FenetrePrincipale, BoutonCustom
from interfaces.interface_messagerie import InterfaceMessagerie
from interfaces.interface_login import InterfaceLogin

#docs : https://sprava-api-fc44f5e02dd0.herokuapp.com/docs#/
#proxy cmd : set HTTP_PROXY=http://192.168.228.254:3128&set HTTPS_PROXY=http://192.168.228.254:3128&git pull

# Exécution de l'application
def main():
    '''import os
    os.environ["HTTP_PROXY"] = "http://192.168.228.254:3128"
    os.environ["HTTPS_PROXY"] = "http://192.168.228.254:3128"'''

    app = QApplication(sys.argv)
    app.setStyle("fusion")

    #icone = QIcon(obtenir_vrai_chemin(""))
    #app.setWindowIcon(icone)

    fenetre_principale_instance = FenetrePrincipale()

    interface_login_instance = InterfaceLogin(fenetre_principale_instance)
    fenetre_principale_instance.ajouter_interface(interface=interface_login_instance, ligne=0, col=0)





    fenetre_principale_instance.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()