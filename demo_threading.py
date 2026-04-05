"""
DÉMONSTRATION complète du système de threading pour PyQt6.

Ce fichier contient:
1. Une application PyQt6 minimale qui teste le threading
2. Des exemples de requêtes bloquantes vs non-bloquantes
3. Une comparaison visuelle de l'impact sur l'UI
"""

import sys
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer

from gestionnaire_threaded import ThreadedRequestManager, SimpleThreadedRequestManager


class DemoWindow(QMainWindow):
    """Fenêtre de démonstration du threading."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Démonstration Threading PyQt6")
        self.setGeometry(100, 100, 800, 600)
        
        # Managers de requêtes
        self.threaded_manager = ThreadedRequestManager()
        self.simple_manager = SimpleThreadedRequestManager()
        
        self._setup_ui()
        
        # Timer pour montrer que l'UI reste réactive
        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_counter)
        self.timer.start(100)  # Mise à jour tous les 100ms
    
    def _setup_ui(self):
        """Créer l'interface utilisateur."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Titre
        title = QLabel("Démonstration: UI Bloquante vs UI Fluide")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Compteur pour montrer la réactivité
        self.counter_label = QLabel("Compteur UI: 0")
        self.counter_label.setStyleSheet("font-size: 14px; color: green;")
        layout.addWidget(self.counter_label)
        
        # Barre de progression pour montrer la réactivité
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Section 1: Requête BLOQUANTE (mauvais)
        layout.addWidget(self._create_section_bloquante())
        
        # Section 2: Requête THREADÉE (bon)
        layout.addWidget(self._create_section_threadee())
        
        # Zone de log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(200)
        layout.addWidget(QLabel("Logs:"))
        layout.addWidget(self.log_area)
    
    def _create_section_bloquante(self):
        """Créer la section avec requête bloquante."""
        widget = QWidget()
        widget.setStyleSheet("background-color: #ffe6e6; padding: 10px; border-radius: 5px;")
        layout = QVBoxLayout(widget)
        
        label = QLabel("❌ REQUÊTE BLOQUANTE (à éviter)")
        label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(label)
        
        desc = QLabel(
            "Cliquez sur ce bouton: l'UI va se FIGER pendant 3 secondes.\n"
            "Le compteur s'arrête, l'UI ne répond plus."
        )
        layout.addWidget(desc)
        
        btn = QPushButton("Faire une requête BLOQUANTE (3s)")
        btn.clicked.connect(self._requete_bloquante)
        layout.addWidget(btn)
        
        return widget
    
    def _create_section_threadee(self):
        """Créer la section avec requête threadée."""
        widget = QWidget()
        widget.setStyleSheet("background-color: #e6ffe6; padding: 10px; border-radius: 5px;")
        layout = QVBoxLayout(widget)
        
        label = QLabel("✅ REQUÊTE THREADÉE (recommandé)")
        label.setStyleSheet("font-weight: bold; color: green;")
        layout.addWidget(label)
        
        desc = QLabel(
            "Cliquez sur ce bouton: l'UI reste FLUIDE pendant les 3 secondes.\n"
            "Le compteur continue, vous pouvez interagir avec l'interface."
        )
        layout.addWidget(desc)
        
        btn_row = QHBoxLayout()
        
        btn1 = QPushButton("Requête THREADÉE (3s)")
        btn1.clicked.connect(self._requete_threadee)
        btn_row.addWidget(btn1)
        
        btn2 = QPushButton("Requête SIMPLE (3s)")
        btn2.clicked.connect(self._requete_simple)
        btn_row.addWidget(btn2)
        
        btn3 = QPushButton("3 Requêtes en PARALLÈLE")
        btn3.clicked.connect(self._requetes_paralleles)
        btn_row.addWidget(btn3)
        
        layout.addLayout(btn_row)
        
        return widget
    
    def _update_counter(self):
        """Mettre à jour le compteur pour montrer la réactivité."""
        self.counter += 1
        self.counter_label.setText(f"Compteur UI: {self.counter} (si ce compteur s'arrête, l'UI est figée)")
        self.progress_bar.setValue((self.counter * 2) % 100)
    
    def _log(self, message):
        """Ajouter un message au log."""
        self.log_area.append(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    # ========== MÉTHODES BLOQUANTES (MAUVAIS) ==========
    
    def _requete_bloquante(self):
        """Simulation d'une requête HTTP bloquante."""
        self._log("🔴 DÉBUT requête bloquante...")
        
        # Simule une requête HTTP qui prend 3 secondes
        # Pendant ce temps, L'UI EST FIGÉE
        time.sleep(3)
        
        self._log("🔴 FIN requête bloquante (UI était figée)")
    
    # ========== MÉTHODES THREADÉES (BON) ==========
    
    def _requete_threadee(self):
        """Simulation d'une requête HTTP threadée."""
        self._log("🟢 DÉBUT requête threadée (UI reste fluide)...")
        
        def faire_requete():
            """Cette fonction s'exécute dans un thread séparé."""
            time.sleep(3)
            return {"status": "success", "data": "Résultat de la requête"}
        
        self.threaded_manager.execute(
            method=faire_requete,
            on_success=lambda result: self._log(f"🟢 FIN requête threadée: {result}"),
            on_error=lambda e: self._log(f"❌ Erreur: {e}")
        )
        
        self._log("→ La requête s'exécute en arrière-plan, l'UI reste réactive!")
    
    def _requete_simple(self):
        """Utilisation de SimpleThreadedRequestManager."""
        self._log("🔵 DÉBUT requête simple...")
        
        def faire_requete():
            time.sleep(3)
            return "Données reçues"
        
        self.simple_manager.execute_simple(
            request_func=faire_requete,
            success_callback=lambda result: self._log(f"🔵 FIN requête simple: {result}"),
            error_message="Erreur lors de la requête simple"
        )
    
    def _requetes_paralleles(self):
        """Lancer 3 requêtes en parallèle."""
        self._log("🟣 Lancement de 3 requêtes EN PARALLÈLE...")
        
        def requete_1():
            time.sleep(2)
            return "Résultat requête 1"
        
        def requete_2():
            time.sleep(3)
            return "Résultat requête 2"
        
        def requete_3():
            time.sleep(1)
            return "Résultat requête 3"
        
        self.threaded_manager.execute(
            method=requete_1,
            on_success=lambda r: self._log(f"🟣 Requête 1 terminée: {r}")
        )
        
        self.threaded_manager.execute(
            method=requete_2,
            on_success=lambda r: self._log(f"🟣 Requête 2 terminée: {r}")
        )
        
        self.threaded_manager.execute(
            method=requete_3,
            on_success=lambda r: self._log(f"🟣 Requête 3 terminée: {r}")
        )
        
        self._log("→ Les 3 requêtes s'exécutent simultanément!")
    
    def closeEvent(self, event):
        """Nettoyer les threads à la fermeture."""
        self._log("🔄 Nettoyage des threads...")
        self.threaded_manager.cleanup_all()
        self.simple_manager.cleanup_all()
        event.accept()


def main():
    """Point d'entrée de l'application de démo."""
    app = QApplication(sys.argv)
    
    # Style sombre optionnel
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QPushButton {
            background-color: #0d7377;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #14a085;
        }
        QTextEdit {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #3e3e3e;
        }
        QProgressBar {
            border: 1px solid #3e3e3e;
            border-radius: 5px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #0d7377;
        }
    """)
    
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
