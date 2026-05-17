import sys

from PyQt6.QtWidgets import QApplication

from interfaces.interface_graphique import FenetrePrincipale
from interfaces.interface_login import InterfaceLogin

def main():
    '''import os
    os.environ["HTTP_PROXY"] = "http://192.168.228.254:3128"
    os.environ["HTTPS_PROXY"] = "http://192.168.228.254:3128"'''

    app = QApplication(sys.argv)
    app.setStyle("fusion")

    fenetre_principale_instance = FenetrePrincipale()

    interface_login_instance = InterfaceLogin(fenetre_principale_instance)
    fenetre_principale_instance.changer_interface(interface=interface_login_instance)





    fenetre_principale_instance.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()