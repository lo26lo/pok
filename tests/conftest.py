"""
Configuration pytest partagée pour la suite de tests.

- collect_ignore : écarte les benchmarks manuels et les tests nécessitant
  du matériel (GPU) ou des données locales absentes du dépôt.
- Fixtures : mini base de cartes (3 cartes) et images de test générées,
  utilisées par les tests unitaires du mapping, de l'augmentation et du merge.
"""
import sys
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Scripts hérités non collectables par pytest (exécution manuelle uniquement)
collect_ignore = [
    "test_cuda.py",                       # requiert torch + GPU
    "test_gpu_training.py",               # requiert torch + ultralytics
    "test_yaml_generation.py",            # chemin machine codé en dur (legacy)
    "test_autobalancer_performance.py",   # benchmark manuel (arguments requis)
    "test_mosaic_performance.py",         # benchmark manuel (arguments requis)
]


@pytest.fixture
def mini_card_db(tmp_path):
    """
    Base de cartes YAML minimale : 3 cartes, formats variés
    (numéro purement numérique, numéro alphanumérique type XY05,
    nom avec espace pour vérifier la conversion en underscores).
    """
    data = {
        'metadata': {'version': '1.0', 'total_cards': 3},
        'cards': {
            'tst_001': {'name': 'Pika Chu', 'price': 1.50, 'price_max': 2.00},
            'tst_002': {'name': 'Dracaufeu', 'price': 50.00, 'price_max': 75.00},
            'tst_XY03': {'name': 'Mew', 'price': None, 'price_max': None},
        },
    }
    db_path = tmp_path / "cards_database.yaml"
    with open(db_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    return db_path


@pytest.fixture
def card_images_dir(tmp_path):
    """
    Dossier d'images de cartes factices correspondant à mini_card_db,
    plus une image inconnue (absente de la base) pour tester l'exclusion.
    """
    cv2 = pytest.importorskip("cv2")
    np = pytest.importorskip("numpy")

    src = tmp_path / "images_src"
    src.mkdir()
    rng = np.random.default_rng(42)
    for name in ["tst_001_en.png", "tst_002_fr.png", "tst_XY03_en.png",
                 "zzz_unknown_card.png"]:
        img = (rng.random((380, 280, 3)) * 255).astype(np.uint8)
        cv2.imwrite(str(src / name), img)
    return src
