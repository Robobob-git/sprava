from PyQt6.QtCore import QObject, QThread, pyqtSignal


class RequettesWorker(QObject):
    """
    Worker qui exécute une requête dans un thread séparé.
    
    Signals:
        succes: Émis quand la requête réussit (avec le résultat)
        erreur: Émis en cas d'erreur (avec l'exception)
    """
    
    succes = pyqtSignal(object)  # Résultat de la requête
    erreur = pyqtSignal(Exception)
    
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


class RequettesManager:
    """
    Gestionnaire de requêtes threadées.
    
    Permet d'exécuter des requêtes HTTP sans bloquer l'UI.
    Gère automatiquement la création et la destruction des threads.
    """
    
    def __init__(self):
        self.threads_actifs = []
        self.workers_actifs = []
    
    def executer(self, func, func_succes = None, func_erreur = None):
        """
        Exécute une méthode de façon asynchrone dans un thread séparé.
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
            thread.quit()
            thread.wait()
            if thread in self.threads_actifs:
                self.threads_actifs.remove(thread)
            if worker in self.workers_actifs:
                self.workers_actifs.remove(worker)
        
        # Garder une référence au thread ET au worker pour éviter le garbage collector
        self.threads_actifs.append(thread)
        self.workers_actifs.append(worker)
        
        # Démarrer le thread
        thread.start()
    
    def cleanup_all(self):
        """
        Arrête tous les threads actifs et attend leur terminaison.
        """

        for thread in self.threads_actifs:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        self.threads_actifs.clear()
        self.workers_actifs.clear()
