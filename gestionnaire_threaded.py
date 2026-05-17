from PyQt6.QtCore import QObject, QThread, pyqtSignal


class RequettesWorker(QObject):
    succes = pyqtSignal(object)  # Résultat de la requête
    erreur = pyqtSignal(Exception)
    
    def __init__(self, func):
        super().__init__()
        self.func = func
        self._is_running = False
    
    def run(self):
        self._is_running = True
        try:
            resultat = self.func()
            self.succes.emit(resultat)
        except Exception as e:
            self.erreur.emit(e)


class RequettesManager:
    def __init__(self):
        self.threads_actifs = []
        self.workers_actifs = []
    
    def executer(self, func, func_succes = None, func_erreur = None):
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
        for thread in self.threads_actifs:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        self.threads_actifs.clear()
        self.workers_actifs.clear()
