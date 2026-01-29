import os

def obtenir_vrai_chemin(chemin_relatif): # Retourne le chemin absolu pour éviter les soucis de chemins
    # Si l'application est exécutée comme script Python :
    chemin_brut = os.path.dirname(os.path.abspath(__file__))
    
    # Construit et retourne le chemin absolu
    return os.path.join(chemin_brut, chemin_relatif)