"""
Tests unitaires du WorkflowManager (validation de config, comptage
d'étapes, logique de succès) — sans lancer de sous-processus.
"""
import pytest

from core.workflow_manager import (
    WorkflowConfig,
    WorkflowManager,
    WorkflowStep,
    StepStatus,
    StepResult,
)


class TestWorkflowConfig:
    def test_defaults_valid(self):
        config = WorkflowConfig()
        assert config.num_augmentations == 15
        assert config.mosaic_mode == "standard"

    def test_rejects_zero_augmentations(self):
        with pytest.raises(ValueError):
            WorkflowConfig(num_augmentations=0)

    def test_rejects_invalid_mosaic_mode(self):
        with pytest.raises(ValueError):
            WorkflowConfig(mosaic_mode="n_importe_quoi")

    def test_custom_mode_requires_count(self):
        with pytest.raises(ValueError):
            WorkflowConfig(mosaic_mode="custom", mosaic_count=None)
        # avec count: OK
        WorkflowConfig(mosaic_mode="custom", mosaic_count=10)


class TestWorkflowSteps:
    def test_merge_step_exists(self):
        """Régression B5: le merge doit avoir sa propre étape."""
        assert WorkflowStep.MERGE.value == "merge"

    def test_count_active_steps(self):
        base = WorkflowManager(WorkflowConfig())
        # augmentation + mosaic + merge + validation (défaut)
        assert base._count_active_steps() == 4

        full = WorkflowManager(WorkflowConfig(
            enable_validation=True, enable_balancing=True, enable_training=True))
        assert full._count_active_steps() == 6

        minimal = WorkflowManager(WorkflowConfig(enable_validation=False))
        assert minimal._count_active_steps() == 3


class TestIsSuccess:
    def _result(self, step, status):
        return StepResult(step=step, status=status, duration=0.0, message="")

    def test_no_results_is_failure(self):
        manager = WorkflowManager(WorkflowConfig())
        assert manager.is_success() is False

    def test_all_critical_success(self):
        manager = WorkflowManager(WorkflowConfig())
        manager.results = [
            self._result(WorkflowStep.AUGMENTATION, StepStatus.SUCCESS),
            self._result(WorkflowStep.MOSAIC, StepStatus.SUCCESS),
            self._result(WorkflowStep.MERGE, StepStatus.SUCCESS),
        ]
        assert manager.is_success() is True

    def test_merge_failure_is_critical(self):
        """Régression B5: un échec du merge doit faire échouer le workflow."""
        manager = WorkflowManager(WorkflowConfig())
        manager.results = [
            self._result(WorkflowStep.AUGMENTATION, StepStatus.SUCCESS),
            self._result(WorkflowStep.MOSAIC, StepStatus.SUCCESS),
            self._result(WorkflowStep.MERGE, StepStatus.FAILED),
        ]
        assert manager.is_success() is False

    def test_validation_failure_not_critical(self):
        manager = WorkflowManager(WorkflowConfig())
        manager.results = [
            self._result(WorkflowStep.AUGMENTATION, StepStatus.SUCCESS),
            self._result(WorkflowStep.MOSAIC, StepStatus.SUCCESS),
            self._result(WorkflowStep.MERGE, StepStatus.SUCCESS),
            self._result(WorkflowStep.VALIDATION, StepStatus.FAILED),
        ]
        assert manager.is_success() is True


class TestSummary:
    def test_estimate_duration_returns_string(self):
        manager = WorkflowManager(WorkflowConfig())
        estimate = manager.estimate_duration()
        assert isinstance(estimate, str)
        assert estimate.startswith("~")

    def test_summary_lists_steps(self):
        manager = WorkflowManager(WorkflowConfig())
        manager.results = [
            StepResult(step=WorkflowStep.MERGE, status=StepStatus.SUCCESS,
                       duration=1.5, message="ok"),
        ]
        summary = manager.get_summary()
        assert "merge" in summary
        assert "1.5s" in summary
