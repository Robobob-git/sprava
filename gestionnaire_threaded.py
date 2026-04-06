from PyQt6.QtCore import QObject, QThread, pyqtSignal


class RequettesWorker(QObject):
    """
    Worker qui exécute une requête dans un thread séparé.
    
    Signals:
        success: Émis quand la requête réussit (avec le résultat)
        error: Émis en cas d'erreur (avec l'exception)
        finished: Émis à la fin de l'exécution (succès ou erreur)
    """
    
    succes = pyqtSignal(object)  # Résultat de la requête
    erreur = pyqtSignal(Exception)
    fini = pyqtSignal()  # Signal de fin
    
    def __init__(self, func):
        """
        Args:
            func: La fonction/méthode à exécuter (sans arguments)
        """
        super().__init__()
        self.func = func
        self._is_running = False
    
    def run(self):
        self._is_running = True
        try:
            resultat = self.func()
            self.succes.emit(resultat)
            print(f'resultat : {resultat}')
        except Exception as e:
            print(f"[RequettesWorker] Erreur: {e}")
            self.erreur.emit(e)
        finally:
            self._is_running = False
            self.fini.emit()


class RequettesManager:
    """
    Gestionnaire de requêtes threadées pour PyQt6.
    
    Permet d'exécuter des requêtes HTTP sans bloquer l'UI.
    Gère automatiquement la création et la destruction des threads.
    """
    
    def __init__(self):
        self.threads_actifs = []
        self.workers_actifs = []
    
    def executer(self, func, func_succes = None, func_erreur = None, func_fini = None):
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
            manager.executer(
                method=lambda: self.gestionnaire.obtenir_amis(toutes_infos=True),
                on_success=lambda resultat: print(f"Amis: {resultat}"),
            )
        """
        # Créer le thread et le worker
        thread = QThread()
        worker = RequettesWorker(func)
        
        # Déplacer le worker dans le thread
        worker.moveToThread(thread)
        
        # Connecter les signaux
        thread.started.connect(worker.run)
        
        if func_succes:
            worker.succes.connect(func_succes)

        if func_erreur:
            worker.erreur.connect(func_erreur)
        
        # Cleanup automatique à la fin
        def cleanup():
            if func_fini:
                func_fini()
            thread.quit()
            thread.wait()
            if thread in self.threads_actifs:
                self.threads_actifs.remove(thread)
            if worker in self.workers_actifs:
                self.workers_actifs.remove(worker)
        
        worker.fini.connect(cleanup)
        
        # Garder une référence au thread ET au worker pour éviter le garbage collection
        self.threads_actifs.append(thread)
        self.workers_actifs.append(worker)
        
        # Démarrer le thread
        thread.start()
    
    def cleanup_all(self):
        """
        Arrête tous les threads actifs et attend leur terminaison.
        À appeler avant de fermer l'application.
        """
        for thread in self.threads_actifs:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        self.threads_actifs.clear()
        self.workers_actifs.clear()
