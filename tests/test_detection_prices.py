"""
Script de test pour la détection avec affichage des prix
Utilise les bons chemins du modèle et data.yaml
"""
import sys
import pytest
from pathlib import Path

# Chemins corrects
MODEL_PATH = "runs/train/pokemon_detector/weights/best.pt"
DATA_YAML = "output/dataset/data.yaml"
EXCEL_PATH = "excel/cards_info.xlsx"

# Vérifications au niveau module
model_exists = Path(MODEL_PATH).exists()
data_exists = Path(DATA_YAML).exists()
excel_exists = Path(EXCEL_PATH).exists()

# Skip si fichiers manquants (au lieu de sys.exit)
pytestmark = pytest.mark.skipif(
    not all([model_exists, data_exists, excel_exists]),
    reason="Fichiers requis manquants (modèle, data.yaml ou excel)"
)

def test_detection_setup():
    """Vérifie que tous les fichiers nécessaires existent"""
    print("=" * 60)
    print("  TEST DÉTECTION AVEC PRIX")
    print("=" * 60)
    print()
    
    print(f"✓ Modèle: {MODEL_PATH}")
    print(f"  {'✅ Trouvé' if model_exists else '❌ Non trouvé'}")
    print()
    print(f"✓ Data.yaml: {DATA_YAML}")
    print(f"  {'✅ Trouvé' if data_exists else '❌ Non trouvé'}")
    print()
    print(f"✓ Excel prix: {EXCEL_PATH}")
    print(f"  {'✅ Trouvé' if excel_exists else '❌ Non trouvé'}")
    print()
    
    assert model_exists, f"Modèle non trouvé: {MODEL_PATH}"
    assert data_exists, f"data.yaml non trouvé: {DATA_YAML}"
    assert excel_exists, f"Excel non trouvé: {EXCEL_PATH}"
    
    print("✅ Tous les fichiers sont présents")

if __name__ == "__main__":
    # Code d'origine pour exécution standalone
    print("=" * 60)
    print("  TEST DÉTECTION AVEC PRIX")
    print("=" * 60)
    print()
    
    print(f"✓ Modèle: {MODEL_PATH}")
    print(f"  {'✅ Trouvé' if model_exists else '❌ Non trouvé'}")
    print()
    print(f"✓ Data.yaml: {DATA_YAML}")
    print(f"  {'✅ Trouvé' if data_exists else '❌ Non trouvé'}")
    print()
    print(f"✓ Excel prix: {EXCEL_PATH}")
    print(f"  {'✅ Trouvé' if excel_exists else '❌ Non trouvé'}")
    print()
    
    if not all([model_exists, data_exists, excel_exists]):
        print("❌ Fichiers manquants, impossible de continuer")
        sys.exit(1)
    
    print("🚀 Lancement de la détection avec webcam...")
    print("   Appuie sur 'q' pour quitter")
    print()

# Import et lancement
from core.detection_with_prices import PriceDetector

detector = PriceDetector(
    model_path=MODEL_PATH,
    yaml_path="models/cards_database.yaml",  # Utilise YAML au lieu d'Excel
    data_yaml_path=DATA_YAML
)

# Lancer la détection webcam (conf sera géré dans le modèle YOLO)
try:
    detector.detect_video(source=0, conf_threshold=0.3)
except KeyboardInterrupt:
    print("\n⚠️ Arrêt demandé (Ctrl+C)")
except Exception as e:
    print(f"\n❌ Erreur: {e}")
finally:
    import cv2
    cv2.destroyAllWindows()
    print("✅ Fenêtres fermées")
