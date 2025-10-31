"""
Workflow Manager - Orchestration automatique du pipeline
========================================================

Ce module gère l'exécution automatique du workflow complet :
1. Augmentation d'images
2. Génération de mosaïques
3. Validation du dataset (optionnel)
4. Auto-balancing des classes (optionnel)
5. Entraînement YOLO (optionnel)

Auteur: Pokemon Dataset Generator Team
Version: 3.0.0
"""

import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

# Import safe_print - gère import relatif ET absolu
try:
    from .utils import safe_print
except ImportError:
    from utils import safe_print
from enum import Enum
import logging

# Configuration du logger
logger = logging.getLogger(__name__)


class WorkflowStep(Enum):
    """Énumération des étapes du workflow"""
    AUGMENTATION = "augmentation"
    MOSAIC = "mosaic"
    VALIDATION = "validation"
    BALANCING = "balancing"
    TRAINING = "training"


class StepStatus(Enum):
    """Statut d'une étape"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowConfig:
    """Configuration du workflow automatique"""
    # Étape 1: Augmentation
    num_augmentations: int = 15
    
    # Étape 2: Mosaïques
    mosaic_mode: str = "standard"  # "quick", "standard", "complete", "custom"
    mosaic_count: Optional[int] = None  # Pour mode custom
    
    # Étapes optionnelles
    enable_validation: bool = True
    enable_balancing: bool = False
    enable_training: bool = False
    
    # Configuration balancing
    balance_strategy: str = "augment"  # "augment", "undersample", "remove"
    balance_target: int = 50
    
    # Configuration training
    training_epochs: int = 50
    training_batch: int = 16
    training_imgsz: int = 640
    
    # Chemins
    output_dir: Path = Path("output")
    yolo_dir: Path = Path("output/yolov8")
    
    def __post_init__(self):
        """Validation après initialisation"""
        if self.num_augmentations < 1:
            raise ValueError("num_augmentations doit être >= 1")
        
        if self.mosaic_mode not in ["quick", "standard", "complete", "custom"]:
            raise ValueError(f"mosaic_mode invalide: {self.mosaic_mode}")
        
        if self.mosaic_mode == "custom" and self.mosaic_count is None:
            raise ValueError("mosaic_count requis pour mode custom")


@dataclass
class StepResult:
    """Résultat d'une étape du workflow"""
    step: WorkflowStep
    status: StepStatus
    duration: float  # secondes
    message: str
    error: Optional[Exception] = None


class WorkflowManager:
    """
    Gestionnaire de workflow automatique
    
    Exemple:
        >>> config = WorkflowConfig(num_augmentations=20, enable_validation=True)
        >>> manager = WorkflowManager(config)
        >>> manager.set_log_callback(lambda msg: print(msg))
        >>> results = manager.run()
        >>> if manager.is_success():
        ...     print("Workflow réussi!")
    """
    
    def __init__(self, config: WorkflowConfig):
        """
        Initialise le gestionnaire de workflow
        
        Args:
            config: Configuration du workflow
        """
        self.config = config
        self.results: List[StepResult] = []
        self._log_callback: Optional[Callable[[str], None]] = None
        self._progress_callback: Optional[Callable[[int, int, str], None]] = None
        self._is_running = False
        
    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """
        Définit la fonction callback pour les logs
        
        Args:
            callback: Fonction prenant un message string en paramètre
        """
        self._log_callback = callback
    
    def set_progress_callback(self, 
                             callback: Callable[[int, int, str], None]) -> None:
        """
        Définit la fonction callback pour la progression
        
        Args:
            callback: Fonction (current_step, total_steps, message)
        """
        self._progress_callback = callback
    
    def _log(self, message: str) -> None:
        """Log un message via callback ou logger"""
        logger.info(message)
        if self._log_callback:
            self._log_callback(message)
    
    def _update_progress(self, current: int, total: int, message: str) -> None:
        """Met à jour la progression via callback"""
        if self._progress_callback:
            self._progress_callback(current, total, message)
    
    def run(self) -> List[StepResult]:
        """
        Exécute le workflow complet
        
        Returns:
            Liste des résultats de chaque étape
            
        Raises:
            RuntimeError: Si workflow déjà en cours
        """
        if self._is_running:
            raise RuntimeError("Workflow déjà en cours d'exécution")
        
        self._is_running = True
        self.results.clear()
        
        try:
            # Calculer nombre d'étapes
            total_steps = self._count_active_steps()
            current_step = 0
            
            self._log("🚀 Démarrage du workflow automatique")
            self._log(f"Configuration: {total_steps} étapes actives")
            
            # Étape 1: Augmentation (toujours active)
            current_step += 1
            result = self._run_augmentation(current_step, total_steps)
            self.results.append(result)
            if result.status == StepStatus.FAILED:
                raise Exception(f"Échec augmentation: {result.message}")
            
            # Étape 2: Mosaïques (toujours active)
            current_step += 1
            result = self._run_mosaic(current_step, total_steps)
            self.results.append(result)
            if result.status == StepStatus.FAILED:
                raise Exception(f"Échec mosaïques: {result.message}")
            
            # Étape 3: Validation (optionnelle)
            if self.config.enable_validation:
                current_step += 1
                result = self._run_validation(current_step, total_steps)
                self.results.append(result)
                # Non bloquant si échec
            
            # Étape 4: Balancing (optionnel)
            if self.config.enable_balancing:
                current_step += 1
                result = self._run_balancing(current_step, total_steps)
                self.results.append(result)
                # Non bloquant si échec
            
            # Étape 5: Training (optionnel)
            if self.config.enable_training:
                current_step += 1
                result = self._run_training(current_step, total_steps)
                self.results.append(result)
                # Non bloquant si échec
            
            self._log("="*50)
            self._log("🎉 WORKFLOW TERMINÉ AVEC SUCCÈS!")
            self._log("="*50)
            self._log(self.get_summary())
            
            return self.results
            
        finally:
            self._is_running = False
    
    def _count_active_steps(self) -> int:
        """Compte le nombre d'étapes actives"""
        count = 2  # Augmentation + Mosaïques (toujours)
        if self.config.enable_validation:
            count += 1
        if self.config.enable_balancing:
            count += 1
        if self.config.enable_training:
            count += 1
        return count
    
    def _run_augmentation(self, current: int, total: int) -> StepResult:
        """Exécute l'étape d'augmentation"""
        import time
        start_time = time.time()
        
        self._log(f"\n📋 Étape {current}/{total}: Augmentation")
        self._update_progress(current, total, "Augmentation des cartes...")
        
        try:
            cmd = [
                sys.executable, 
                "core/augmentation.py",
                "--num_aug", str(self.config.num_augmentations),
                "--target", "augmented"
            ]
            
            success = self._run_subprocess(cmd)
            duration = time.time() - start_time
            
            if success:
                self._log(f"✅ Augmentation terminée ({duration:.1f}s)")
                return StepResult(
                    step=WorkflowStep.AUGMENTATION,
                    status=StepStatus.SUCCESS,
                    duration=duration,
                    message=f"{self.config.num_augmentations} variations générées"
                )
            else:
                return StepResult(
                    step=WorkflowStep.AUGMENTATION,
                    status=StepStatus.FAILED,
                    duration=duration,
                    message="Échec du processus"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            self._log(f"❌ Erreur augmentation: {e}")
            return StepResult(
                step=WorkflowStep.AUGMENTATION,
                status=StepStatus.FAILED,
                duration=duration,
                message=str(e),
                error=e
            )
    
    def _run_mosaic(self, current: int, total: int) -> StepResult:
        """Exécute l'étape de génération de mosaïques"""
        import time
        start_time = time.time()
        
        self._log(f"\n📋 Étape {current}/{total}: Mosaïques")
        self._update_progress(current, total, "Génération des mosaïques...")
        
        try:
            # Déterminer la commande selon le mode
            if self.config.mosaic_mode == "complete":
                cmd = [sys.executable, "core/mosaic.py", "all"]
            elif self.config.mosaic_mode == "custom":
                cmd = [sys.executable, "core/mosaic.py", str(self.config.mosaic_count), "0", "0"]
            else:
                # quick ou standard = all pour l'instant
                cmd = [sys.executable, "core/mosaic.py", "all"]
            
            success = self._run_subprocess(cmd)
            duration = time.time() - start_time
            
            if success:
                self._log(f"✅ Mosaïques générées ({duration:.1f}s)")
                return StepResult(
                    step=WorkflowStep.MOSAIC,
                    status=StepStatus.SUCCESS,
                    duration=duration,
                    message=f"Mode {self.config.mosaic_mode}"
                )
            else:
                return StepResult(
                    step=WorkflowStep.MOSAIC,
                    status=StepStatus.FAILED,
                    duration=duration,
                    message="Échec du processus"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            self._log(f"❌ Erreur mosaïques: {e}")
            return StepResult(
                step=WorkflowStep.MOSAIC,
                status=StepStatus.FAILED,
                duration=duration,
                message=str(e),
                error=e
            )
    
    def _run_validation(self, current: int, total: int) -> StepResult:
        """Exécute l'étape de validation"""
        import time
        start_time = time.time()
        
        self._log(f"\n📋 Étape {current}/{total}: Validation")
        self._update_progress(current, total, "Validation du dataset...")
        
        try:
            cmd = [
                sys.executable,
                "core/dataset_validator.py",
                str(self.config.yolo_dir),
                "--html"
            ]
            
            success = self._run_subprocess(cmd)
            duration = time.time() - start_time
            
            if success:
                self._log(f"✅ Validation terminée ({duration:.1f}s)")
                self._log("📄 Rapport: validation_report.html")
                return StepResult(
                    step=WorkflowStep.VALIDATION,
                    status=StepStatus.SUCCESS,
                    duration=duration,
                    message="Rapport généré"
                )
            else:
                self._log("⚠️ Validation échouée (non bloquant)")
                return StepResult(
                    step=WorkflowStep.VALIDATION,
                    status=StepStatus.FAILED,
                    duration=duration,
                    message="Échec non bloquant"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            self._log(f"⚠️ Erreur validation: {e} (non bloquant)")
            return StepResult(
                step=WorkflowStep.VALIDATION,
                status=StepStatus.FAILED,
                duration=duration,
                message=str(e),
                error=e
            )
    
    def _run_balancing(self, current: int, total: int) -> StepResult:
        """Exécute l'étape d'auto-balancing"""
        import time
        start_time = time.time()
        
        self._log(f"\n📋 Étape {current}/{total}: Auto-balancing")
        self._update_progress(current, total, "Équilibrage des classes...")
        
        try:
            cmd = [
                sys.executable,
                "core/auto_balancer.py",
                str(self.config.yolo_dir),
                "--strategy", self.config.balance_strategy,
                "--target", str(self.config.balance_target)
            ]
            
            success = self._run_subprocess(cmd)
            duration = time.time() - start_time
            
            if success:
                self._log(f"✅ Classes équilibrées ({duration:.1f}s)")
                return StepResult(
                    step=WorkflowStep.BALANCING,
                    status=StepStatus.SUCCESS,
                    duration=duration,
                    message=f"Target: {self.config.balance_target}"
                )
            else:
                self._log("⚠️ Auto-balancing échoué (non bloquant)")
                return StepResult(
                    step=WorkflowStep.BALANCING,
                    status=StepStatus.FAILED,
                    duration=duration,
                    message="Échec non bloquant"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            self._log(f"⚠️ Erreur balancing: {e} (non bloquant)")
            return StepResult(
                step=WorkflowStep.BALANCING,
                status=StepStatus.FAILED,
                duration=duration,
                message=str(e),
                error=e
            )
    
    def _run_training(self, current: int, total: int) -> StepResult:
        """Exécute l'étape d'entraînement YOLO"""
        import time
        start_time = time.time()
        
        self._log(f"\n📋 Étape {current}/{total}: Entraînement YOLO")
        self._update_progress(current, total, "Entraînement du modèle...")
        
        try:
            from ultralytics import YOLO
            
            self._log(f"Configuration: {self.config.training_epochs} epochs, "
                     f"batch={self.config.training_batch}")
            
            model = YOLO('yolov8n.pt')
            results = model.train(
                data=str(self.config.yolo_dir / 'data.yaml'),
                epochs=self.config.training_epochs,
                imgsz=self.config.training_imgsz,
                batch=self.config.training_batch,
                name='pokemon_detector',
                verbose=False  # Réduire les logs YOLO
            )
            
            duration = time.time() - start_time
            self._log(f"✅ Entraînement terminé ({duration:.1f}s)")
            self._log("📁 Modèle sauvegardé: runs/detect/pokemon_detector/")
            
            return StepResult(
                step=WorkflowStep.TRAINING,
                status=StepStatus.SUCCESS,
                duration=duration,
                message=f"{self.config.training_epochs} epochs"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self._log(f"⚠️ Erreur training: {e} (non bloquant)")
            return StepResult(
                step=WorkflowStep.TRAINING,
                status=StepStatus.FAILED,
                duration=duration,
                message=str(e),
                error=e
            )
    
    def _run_subprocess(self, cmd: List[str]) -> bool:
        """
        Exécute une commande subprocess avec logs
        
        Args:
            cmd: Liste des arguments de commande
            
        Returns:
            True si succès (code retour 0), False sinon
        """
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Lire et logger la sortie
            for line in iter(process.stdout.readline, ''):
                if line:
                    self._log(line.rstrip())
            
            process.wait()
            return process.returncode == 0
            
        except Exception as e:
            self._log(f"Erreur subprocess: {e}")
            return False
    
    def is_success(self) -> bool:
        """
        Vérifie si le workflow s'est terminé avec succès
        
        Returns:
            True si toutes les étapes critiques ont réussi
        """
        if not self.results:
            return False
        
        # Les 2 premières étapes (augmentation + mosaic) sont critiques
        critical_steps = [r for r in self.results 
                         if r.step in [WorkflowStep.AUGMENTATION, WorkflowStep.MOSAIC]]
        
        return all(r.status == StepStatus.SUCCESS for r in critical_steps)
    
    def get_summary(self) -> str:
        """
        Génère un résumé textuel du workflow
        
        Returns:
            String multi-lignes avec statistiques
        """
        if not self.results:
            return "Aucun workflow exécuté"
        
        total_duration = sum(r.duration for r in self.results)
        success_count = sum(1 for r in self.results if r.status == StepStatus.SUCCESS)
        failed_count = sum(1 for r in self.results if r.status == StepStatus.FAILED)
        
        lines = [
            f"Durée totale: {total_duration:.1f}s",
            f"Étapes réussies: {success_count}/{len(self.results)}",
            f"Étapes échouées: {failed_count}"
        ]
        
        for result in self.results:
            status_icon = {
                StepStatus.SUCCESS: "✅",
                StepStatus.FAILED: "❌",
                StepStatus.SKIPPED: "⏭️"
            }.get(result.status, "❓")
            
            lines.append(f"{status_icon} {result.step.value}: {result.message} "
                        f"({result.duration:.1f}s)")
        
        return "\n".join(lines)
    
    def estimate_duration(self) -> str:
        """
        Estime la durée du workflow
        
        Returns:
            String représentant la durée estimée
        """
        # Estimations approximatives
        aug_time = self.config.num_augmentations * 2  # ~2s par augmentation
        mosaic_time = 30  # ~30s pour mosaïques
        val_time = 10 if self.config.enable_validation else 0
        balance_time = 20 if self.config.enable_balancing else 0
        train_time = self.config.training_epochs * 10 if self.config.enable_training else 0
        
        total_seconds = aug_time + mosaic_time + val_time + balance_time + train_time
        
        if total_seconds < 60:
            return f"~{total_seconds}s"
        elif total_seconds < 3600:
            return f"~{total_seconds//60}min"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"~{hours}h{minutes}min"


def main():
    """Point d'entrée pour exécution standalone"""
    # Configuration par défaut
    config = WorkflowConfig(
        num_augmentations=15,
        mosaic_mode="standard",
        enable_validation=True,
        enable_balancing=False,
        enable_training=False
    )
    
    # Créer et exécuter le workflow
    manager = WorkflowManager(config)
    manager.set_log_callback(print)
    
    try:
        results = manager.run()
        print("\n" + "="*50)
        print(manager.get_summary())
        print("="*50)
        
        sys.exit(0 if manager.is_success() else 1)
        
    except KeyboardInterrupt:
        safe_print("\n⏹️ Workflow interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        safe_print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
