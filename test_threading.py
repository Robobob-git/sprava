"""
Tests unitaires pour gestionnaire_threaded.py

Ce fichier teste le bon fonctionnement du système de threading.
Exécution: python test_threading.py
"""

import time
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QEventLoop

from gestionnaire_threaded import ThreadedRequestManager, SimpleThreadedRequestManager


class TestResults:
    """Stocke les résultats des tests."""
    def __init__(self):
        self.results = []
        self.errors = []
    
    def add_success(self, test_name):
        self.results.append((test_name, True))
        print(f"✅ {test_name}")
    
    def add_failure(self, test_name, error):
        self.results.append((test_name, False))
        self.errors.append((test_name, error))
        print(f"❌ {test_name}: {error}")
    
    def summary(self):
        total = len(self.results)
        passed = sum(1 for _, success in self.results if success)
        failed = total - passed
        
        print("\n" + "="*60)
        print(f"Tests: {passed}/{total} passés")
        if failed > 0:
            print(f"\n❌ {failed} test(s) échoué(s):")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        else:
            print("✅ Tous les tests sont passés!")
        print("="*60)
        
        return failed == 0


def wait_for_event(timeout_ms=1000):
    """Attend que les événements Qt soient traités."""
    loop = QEventLoop()
    QTimer.singleShot(timeout_ms, loop.quit)
    loop.exec()


class TestThreading:
    """Tests pour le système de threading."""
    
    def __init__(self):
        self.results = TestResults()
        self.app = QApplication.instance() or QApplication(sys.argv)
    
    def run_all_tests(self):
        """Exécute tous les tests."""
        print("\n" + "="*60)
        print("Tests du système de threading PyQt6")
        print("="*60 + "\n")
        
        self.test_simple_success()
        self.test_simple_error()
        self.test_multiple_parallel()
        self.test_callback_order()
        self.test_cleanup()
        self.test_simple_manager()
        
        return self.results.summary()
    
    def test_simple_success(self):
        """Test: Exécution simple avec succès."""
        test_name = "Test 1: Requête simple (succès)"
        
        manager = ThreadedRequestManager()
        result_container = {"value": None, "called": False}
        
        def request_func():
            time.sleep(0.1)
            return "test_result"
        
        def on_success(result):
            result_container["value"] = result
            result_container["called"] = True
        
        manager.execute(
            method=request_func,
            on_success=on_success
        )
        
        # Attendre que la requête se termine
        wait_for_event(500)
        
        if result_container["called"] and result_container["value"] == "test_result":
            self.results.add_success(test_name)
        else:
            self.results.add_failure(test_name, f"Résultat inattendu: {result_container}")
        
        manager.cleanup_all()
    
    def test_simple_error(self):
        """Test: Gestion d'erreur."""
        test_name = "Test 2: Gestion d'erreur"
        
        manager = ThreadedRequestManager()
        error_container = {"error": None, "called": False}
        
        def request_func():
            raise ValueError("Erreur de test")
        
        def on_error(error):
            error_container["error"] = error
            error_container["called"] = True
        
        manager.execute(
            method=request_func,
            on_error=on_error
        )
        
        wait_for_event(500)
        
        if error_container["called"] and isinstance(error_container["error"], ValueError):
            self.results.add_success(test_name)
        else:
            self.results.add_failure(test_name, f"Erreur non capturée: {error_container}")
        
        manager.cleanup_all()
    
    def test_multiple_parallel(self):
        """Test: Plusieurs requêtes en parallèle."""
        test_name = "Test 3: Requêtes parallèles"
        
        manager = ThreadedRequestManager()
        results = {"count": 0, "values": []}
        
        def request_func(value):
            time.sleep(0.1)
            return value
        
        def on_success(result):
            results["count"] += 1
            results["values"].append(result)
        
        # Lancer 3 requêtes en parallèle
        for i in range(3):
            manager.execute(
                method=lambda v=i: request_func(v),
                on_success=on_success
            )
        
        wait_for_event(800)
        
        if results["count"] == 3 and len(results["values"]) == 3:
            self.results.add_success(test_name)
        else:
            self.results.add_failure(test_name, f"Résultats inattendus: {results}")
        
        manager.cleanup_all()
    
    def test_callback_order(self):
        """Test: Ordre des callbacks (success puis finished)."""
        test_name = "Test 4: Ordre des callbacks"
        
        manager = ThreadedRequestManager()
        order = []
        
        def request_func():
            time.sleep(0.1)
            return "done"
        
        def on_success(result):
            order.append("success")
        
        def on_finished():
            order.append("finished")
        
        manager.execute(
            method=request_func,
            on_success=on_success,
            on_finished=on_finished
        )
        
        wait_for_event(500)
        
        if order == ["success", "finished"]:
            self.results.add_success(test_name)
        else:
            self.results.add_failure(test_name, f"Ordre incorrect: {order}")
        
        manager.cleanup_all()
    
    def test_cleanup(self):
        """Test: Nettoyage des threads."""
        test_name = "Test 5: Cleanup des threads"
        
        manager = ThreadedRequestManager()
        
        def request_func():
            time.sleep(0.1)
            return "done"
        
        # Lancer plusieurs requêtes
        for _ in range(3):
            manager.execute(method=request_func)
        
        # Vérifier que des threads sont actifs
        initial_count = len(manager.active_threads)
        
        wait_for_event(500)
        
        # Cleanup
        manager.cleanup_all()
        
        # Vérifier que tous les threads sont nettoyés
        final_count = len(manager.active_threads)
        
        if initial_count > 0 and final_count == 0:
            self.results.add_success(test_name)
        else:
            self.results.add_failure(test_name, f"Threads: initial={initial_count}, final={final_count}")
    
    def test_simple_manager(self):
        """Test: SimpleThreadedRequestManager."""
        test_name = "Test 6: SimpleThreadedRequestManager"
        
        manager = SimpleThreadedRequestManager()
        result_container = {"value": None}
        
        def request_func():
            time.sleep(0.1)
            return "simple_result"
        
        def success_callback(result):
            result_container["value"] = result
        
        manager.execute_simple(
            request_func=request_func,
            success_callback=success_callback
        )
        
        wait_for_event(500)
        
        if result_container["value"] == "simple_result":
            self.results.add_success(test_name)
        else:
            self.results.add_failure(test_name, f"Résultat inattendu: {result_container}")
        
        manager.cleanup_all()


def main():
    """Point d'entrée des tests."""
    tester = TestThreading()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
