"""
Gestionnaire de requêtes HTTP asynchrones avec QThread pour PyQt6.

Ce module fournit un système de worker/thread permettant d'exécuter
les requêtes HTTP sans bloquer l'interface utilisateur PyQt6.

Usage:
    # Dans votre interface PyQt6
    manager = ThreadedRequestManager()
    
    # Exécuter une méthode de façon asynchrone
    manager.execute(
        method=lambda: self.gestionnaire_connexions.connexion(mail="test@example.com", mdp="password"),
        on_success=self.handle_success,
        on_error=self.handle_error
    )
"""

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from typing import Callable, Any, Optional
import traceback


class RequestWorker(QObject):
    """
    Worker qui exécute une requête dans un thread séparé.
    
    Signals:
        success: Émis quand la requête réussit (avec le résultat)
        error: Émis en cas d'erreur (avec l'exception)
        finished: Émis à la fin de l'exécution (succès ou erreur)
    """
    
    success = pyqtSignal(object)  # Résultat de la requête
    error = pyqtSignal(Exception)  # Exception en cas d'erreur
    finished = pyqtSignal()  # Signal de fin
    
    def __init__(self, method: Callable[[], Any]):
        """
        Args:
            method: La fonction/méthode à exécuter (sans arguments)
        """
        super().__init__()
        self.method = method
        self._is_running = False
    
    def run(self):
        """Exécute la méthode et émet les signaux appropriés."""
        self._is_running = True
        try:
            result = self.method()
            self.success.emit(result)
        except Exception as e:
            print(f"[RequestWorker] Erreur: {e}")
            traceback.print_exc()
            self.error.emit(e)
        finally:
            self._is_running = False
            self.finished.emit()


class ThreadedRequestManager:
    """
    Gestionnaire de requêtes threadées pour PyQt6.
    
    Permet d'exécuter des requêtes HTTP sans bloquer l'UI.
    Gère automatiquement la création et la destruction des threads.
    """
    
    def __init__(self):
        self.active_threads = []
    
    def execute(
        self,
        method: Callable[[], Any],
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_finished: Optional[Callable[[], None]] = None
    ):
        """
        Exécute une méthode de façon asynchrone dans un thread séparé.
        
        Args:
            method: La fonction/méthode à exécuter (doit être sans arguments)
                   Utilisez lambda pour passer des paramètres:
                   lambda: self.gestionnaire.connexion(mail="...", mdp="...")
            on_success: Callback appelé en cas de succès (reçoit le résultat)
            on_error: Callback appelé en cas d'erreur (reçoit l'exception)
            on_finished: Callback appelé à la fin (succès ou erreur)
        
        Exemple:
            manager.execute(
                method=lambda: self.gestionnaire.obtenir_amis(toutes_infos=True),
                on_success=lambda result: print(f"Amis: {result}"),
                on_error=lambda e: print(f"Erreur: {e}")
            )
        """
        # Créer le thread et le worker
        thread = QThread()
        worker = RequestWorker(method)
        
        # Déplacer le worker dans le thread
        worker.moveToThread(thread)
        
        # Connecter les signaux
        thread.started.connect(worker.run)
        
        if on_success:
            worker.success.connect(on_success)
        
        if on_error:
            worker.error.connect(on_error)
        
        # Cleanup automatique à la fin
        def cleanup():
            if on_finished:
                on_finished()
            thread.quit()
            thread.wait()
            if thread in self.active_threads:
                self.active_threads.remove(thread)
        
        worker.finished.connect(cleanup)
        
        # Garder une référence au thread pour éviter le garbage collection
        self.active_threads.append(thread)
        
        # Démarrer le thread
        thread.start()
    
    def cleanup_all(self):
        """
        Arrête tous les threads actifs et attend leur terminaison.
        À appeler avant de fermer l'application.
        """
        for thread in self.active_threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        self.active_threads.clear()


class SimpleThreadedRequestManager:
    """
    Version simplifiée qui exécute directement une fonction et gère le résultat.
    
    Utilisation encore plus simple pour les cas courants.
    """
    
    def __init__(self):
        self.manager = ThreadedRequestManager()
    
    def execute_simple(
        self,
        request_func: Callable[[], Any],
        success_callback: Callable[[Any], None],
        error_message: str = "Une erreur est survenue"
    ):
        """
        Exécute une requête avec gestion d'erreur simplifiée.
        
        Args:
            request_func: Fonction qui fait la requête
            success_callback: Fonction appelée avec le résultat si succès
            error_message: Message d'erreur par défaut
        """
        def on_error(e):
            print(f"{error_message}: {e}")
        
        self.manager.execute(
            method=request_func,
            on_success=success_callback,
            on_error=on_error
        )
    
    def cleanup_all(self):
        """Nettoie tous les threads."""
        self.manager.cleanup_all()
