import os
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap

def obtenir_vrai_chemin(chemin_relatif): # Retourne le chemin absolu pour éviter les soucis de chemins
    # Si l'application est exécutée comme script Python :
    chemin_brut = os.path.dirname(os.path.abspath(__file__))
    
    # Construit et retourne le chemin absolu
    return os.path.join(chemin_brut, chemin_relatif)

def obtenir_user_chemin(user_id:int, fichier:str=None):
    base = Path("data")
    base.mkdir(parents=True, exist_ok=True)

    user_chemin = base / f"user_{user_id}"
    user_chemin.mkdir(parents=True, exist_ok=True)

    if fichier:
        user_chemin = user_chemin / fichier

    return str(user_chemin)

def obtenir_pp_chemin(user_id:int, pp_id:str):
    if pp_id:
        pp_id = Path(pp_id).stem # Comme ça on évite que les .png se dupliquent

    path = Path(obtenir_user_chemin(user_id=user_id, fichier=f"pp_{pp_id}.png"))
    return str(path) if path.exists() and path.is_file() else ""

def download_pp(pp_id:str, old_pp_id:str, tailles, labels, session):
    if pp_id:
        pp_id = Path(pp_id).stem
    
    old_pp_path = ''
    if old_pp_id != '':
        old_pp_path = obtenir_pp_chemin(session.user_id, old_pp_id)
    pp_path = obtenir_user_chemin(user_id=session.user_id, fichier=f"pp_{pp_id}.png")
    if isinstance(tailles, int):    # Comme ça on peut passer juste une taille sans avoir à le mettre dans une liste
        tailles = [tailles]

    def succes(rep):
        if not rep:
            erreur()
            return
        
        if old_pp_path != '':
            Path(old_pp_path).unlink()  # On supprime l'ancienne pp

        changer_pp(tailles=tailles, labels=labels, path=pp_path)
    def erreur():
        pass

    session.requettes_manager.executer(func=lambda : session.gestionnaire_media.download_pp(pp_id, pp_path), func_succes=succes, func_erreur=erreur)

def changer_pp(tailles, labels, path:str=None, default:bool=False):
    if path == '':
        default = True
    if default:
        path = obtenir_vrai_chemin("images/default_pp.png")
    
    if isinstance(tailles, int):
        tailles = [tailles]

    if isinstance(labels, QLabel):  # Comme ça on peut passer juste un label sans avoir à le mettre dans une liste
        labels = [labels]
    
    for i, l in enumerate(labels):
        pixmap = QPixmap(path).scaled(tailles[i], tailles[i], Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        l.setPixmap(pixmap)