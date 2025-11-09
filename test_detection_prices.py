"""
Script de test pour la détection avec affichage des prix
Utilise les bons chemins du modèle et data.yaml
"""
import sys
from pathlib import Path

# Chemins corrects
MODEL_PATH = "runs/train/pokemon_detector/weights/best.pt"
DATA_YAML = "output/dataset/data.yaml"
EXCEL_PATH = "excel/cards_info.xlsx"

print("=" * 60)
print("  TEST DÉTECTION AVEC PRIX")
print("=" * 60)
print()

# Vérifications
model_exists = Path(MODEL_PATH).exists()
data_exists = Path(DATA_YAML).exists()
excel_exists = Path(EXCEL_PATH).exists()

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
    excel_path=EXCEL_PATH,
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
