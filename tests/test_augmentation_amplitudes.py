"""
Anti-régression des AMPLITUDES EFFECTIVES du pool d'augmentation.

Raison d'être : albumentations 2.x IGNORE SILENCIEUSEMENT les arguments
1.x renommés (var_limit, quality_lower/upper, *_lower/*_upper…) et retombe
sur ses valeurs par défaut — aucun crash, aucun warning, la suite passe,
mais la calibration F06 est fausse. Ces tests instancient le pool et
vérifient les valeurs réellement portées par les transforms, pas juste
qu'ils s'exécutent. (Découvert lors de la migration 1.x → 2.x, cf.
docs/MIGRATION_ALBUMENTATIONS_2X.md.)
"""
import math
import sys
from pathlib import Path

import pytest

pytest.importorskip("albumentations")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.augmentation_albumentations import build_transform_pool  # noqa: E402


def _by_class(pool):
    """Indexe le pool par nom de classe -> liste d'instances."""
    out = {}
    for t in pool:
        out.setdefault(t.__class__.__name__, []).append(t)
    return out


def _approx(pair, expected, tol=1e-6):
    return all(abs(float(a) - float(b)) <= tol for a, b in zip(pair, expected))


class TestEffectiveAmplitudes:
    """Valeurs effectives à intensité 1.0 (production historique)."""

    def setup_method(self):
        self.pool = _by_class(build_transform_pool(intensity=1.0))

    def test_gauss_noise_std_range(self):
        # var_limit 1.x (10, 40) converti en std_range 2.x = sqrt(var)/255
        (t,) = self.pool["GaussNoise"]
        expected = (math.sqrt(10.0) / 255.0, math.sqrt(40.0) / 255.0)
        assert _approx(t.std_range, expected), t.std_range

    def test_image_compression_quality_range(self):
        (t,) = self.pool["ImageCompression"]
        assert tuple(t.quality_range) == (60, 95), t.quality_range

    def test_sun_flare_ranges(self):
        (t,) = self.pool["RandomSunFlare"]
        assert tuple(t.num_flare_circles_range) == (3, 6), t.num_flare_circles_range
        assert _approx(t.angle_range, (0.0, 1.0)), t.angle_range

    def test_fog_coef_range(self):
        (t,) = self.pool["RandomFog"]
        assert _approx(t.fog_coef_range, (0.1, 0.3)), t.fog_coef_range

    def test_sample_of_unchanged_transforms(self):
        # Échantillon des transforms dont les arguments n'ont pas été
        # renommés : garantit qu'ils sont toujours honorés
        (gamma,) = self.pool["RandomGamma"]
        assert _approx(gamma.gamma_limit, (70, 130)), gamma.gamma_limit
        (hsv,) = self.pool["HueSaturationValue"]
        assert _approx(hsv.hue_shift_limit, (-20, 20)), hsv.hue_shift_limit
        (persp,) = self.pool["Perspective"]
        assert _approx(persp.scale, (0.02, 0.08)), persp.scale
        (rot,) = self.pool["SafeRotate"]
        assert _approx(rot.limit, (-10.0, 10.0)), rot.limit
        (shadow,) = self.pool["RandomShadow"]
        assert tuple(shadow.num_shadows_limit) == (1, 2), shadow.num_shadows_limit


class TestIntensityScaling:
    """La calibration F06 (multiplicateur d'intensité) agit réellement."""

    def test_intensity_scales_noise_and_fog(self):
        pool_2x = _by_class(build_transform_pool(intensity=2.0))
        (noise,) = pool_2x["GaussNoise"]
        assert _approx(noise.std_range,
                       (math.sqrt(10.0) / 255.0, math.sqrt(80.0) / 255.0)), \
            noise.std_range
        (fog,) = pool_2x["RandomFog"]
        assert _approx(fog.fog_coef_range, (0.1, 0.6)), fog.fog_coef_range

    def test_low_intensity_keeps_ranges_ordered(self):
        # À i=0.1, les bornes hautes rejoignent les basses sans s'inverser
        # (albumentations 2.x valide l'ordre des ranges)
        pool_low = _by_class(build_transform_pool(intensity=0.1))
        (noise,) = pool_low["GaussNoise"]
        lo, hi = noise.std_range
        assert lo <= hi
        (fog,) = pool_low["RandomFog"]
        lo, hi = fog.fog_coef_range
        assert lo <= hi
