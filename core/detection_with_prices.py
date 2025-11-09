#!/usr/bin/env python3
"""
Détection YOLO avec affichage des prix
Utilise le modèle entraîné et affiche: Nom + Prix + Confiance

Usage:
    python core/detection_with_prices.py --source 0  # Webcam
    python core/detection_with_prices.py --source image.png
    python core/detection_with_prices.py --source video.mp4
    python core/detection_with_prices.py --source 0 --model runs/detect/train/weights/best.pt
"""

import argparse
import cv2
import sys
from pathlib import Path
from ultralytics import YOLO
import yaml

# Ajouter le dossier parent au path pour importer utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.utils import load_prices_from_excel, safe_print
from core.card_mapping import get_card_id_from_class_name


class PriceDetector:
    """Détecteur YOLO avec affichage des prix"""
    
    def __init__(self, model_path: str, excel_path: str = "excel/cards_info.xlsx", 
                 data_yaml_path: str = "output/dataset/data.yaml"):
        """
        Initialise le détecteur
        
        Args:
            model_path: Chemin vers le modèle YOLO (.pt)
            excel_path: Chemin vers le fichier Excel avec prix
            data_yaml_path: Chemin vers data.yaml pour les noms de classes
        """
        safe_print(f"🔧 Initialisation du détecteur...")
        
        # Charger le modèle YOLO
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Modèle non trouvé: {model_path}")
        
        self.model = YOLO(model_path)
        safe_print(f"✅ Modèle chargé: {model_path}")
        
        # Charger les noms de classes depuis data.yaml
        self.class_names = {}
        if Path(data_yaml_path).exists():
            with open(data_yaml_path, 'r') as f:
                data = yaml.safe_load(f)
                names = data.get('names', [])
                if isinstance(names, list):
                    self.class_names = {i: names[i] for i in range(len(names))}
                elif isinstance(names, dict):
                    self.class_names = names
            safe_print(f"✅ {len(self.class_names)} classes chargées depuis data.yaml")
        else:
            safe_print(f"⚠️ data.yaml non trouvé: {data_yaml_path}")
        
        # Charger les prix depuis Excel
        self.prices = load_prices_from_excel(excel_path)
        safe_print(f"✅ {len(self.prices)} prix chargés depuis Excel")
        
    def get_card_info(self, class_id: int) -> tuple:
        """
        Récupère les informations d'une carte
        
        Args:
            class_id: ID de la classe YOLO (0-indexed)
            
        Returns:
            (card_name, price, price_max) ou (class_name, None, None) si prix non trouvé
        """
        # Obtenir le nom de la classe depuis data.yaml
        class_name = self.class_names.get(class_id, f"Class_{class_id}")
        
        # Convertir le nom de classe en card_id via le mapping
        card_id = get_card_id_from_class_name(class_name)
        
        # Chercher le prix dans le dictionnaire avec le card_id
        if card_id and card_id in self.prices:
            info = self.prices[card_id]
            return (info['name'], info['price'], info['price_max'])
        
        # Fallback: retourner le nom de classe sans prix
        return (class_name, None, None)
    
    def draw_detection(self, frame, box, class_id, confidence):
        """
        Dessine la détection avec nom + prix + confiance
        
        Args:
            frame: Image OpenCV
            box: Boîte de détection [x1, y1, x2, y2]
            class_id: ID de la classe
            confidence: Score de confiance
        """
        x1, y1, x2, y2 = map(int, box)
        
        # Récupérer les informations de la carte
        card_name, price, price_max = self.get_card_info(class_id)
        
        # Couleur selon la confiance
        if confidence > 0.8:
            color = (0, 255, 0)  # Vert
        elif confidence > 0.6:
            color = (0, 165, 255)  # Orange
        else:
            color = (0, 0, 255)  # Rouge
        
        # Dessiner le rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Préparer le texte
        if price is not None:
            # Afficher le prix minimum (le moins cher)
            label = f"{card_name}: {price:.2f}E ({confidence:.2f})"
        else:
            label = f"{card_name} ({confidence:.2f})"
        
        # Calculer la taille du texte
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
        
        # Dessiner le fond du texte
        cv2.rectangle(frame, 
                     (x1, y1 - text_height - baseline - 5), 
                     (x1 + text_width, y1), 
                     color, -1)
        
        # Dessiner le texte
        cv2.putText(frame, label, (x1, y1 - baseline), 
                   font, font_scale, (255, 255, 255), thickness)
    
    def detect_image(self, image_path: str, output_path: str = None, conf_threshold: float = 0.5):
        """
        Détection sur une image
        
        Args:
            image_path: Chemin vers l'image
            output_path: Chemin de sortie (optionnel)
            conf_threshold: Seuil de confiance minimum
        """
        safe_print(f"\n📸 Détection sur: {image_path}")
        
        # Charger l'image
        frame = cv2.imread(image_path)
        if frame is None:
            safe_print(f"❌ Impossible de charger l'image: {image_path}")
            return
        
        # Effectuer la détection
        results = self.model(frame, conf=conf_threshold, verbose=False)
        
        # Traiter les résultats
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Extraire les informations
                xyxy = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # Dessiner la détection
                self.draw_detection(frame, xyxy, cls, conf)
        
        # Afficher les résultats
        safe_print(f"✅ {len(boxes)} cartes détectées")
        
        # Sauvegarder ou afficher
        if output_path:
            cv2.imwrite(output_path, frame)
            safe_print(f"💾 Résultat sauvegardé: {output_path}")
        else:
            cv2.imshow('Pokemon Card Detection with Prices', frame)
            safe_print("Press any key to close...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
    def detect_video(self, source, conf_threshold: float = 0.5):
        """
        Détection sur vidéo ou webcam
        
        Args:
            source: 0 pour webcam, chemin vers vidéo sinon
            conf_threshold: Seuil de confiance minimum
        """
        # Ouvrir la source
        if isinstance(source, str) and source.isdigit():
            source = int(source)
            safe_print(f"\n📹 Ouverture de la webcam {source}...")
        else:
            safe_print(f"\n📹 Ouverture de la vidéo: {source}")
        
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            safe_print(f"❌ Impossible d'ouvrir la source: {source}")
            return
        
        safe_print("✅ Source ouverte")
        safe_print("Press 'q' to quit, 's' to save screenshot")
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Effectuer la détection
                results = self.model(frame, conf=conf_threshold, verbose=False)
                
                # Traiter les résultats
                for result in results:
                    boxes = result.boxes
                    
                    for box in boxes:
                        # Extraire les informations
                        xyxy = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        
                        # Dessiner la détection
                        self.draw_detection(frame, xyxy, cls, conf)
                
                # Afficher le frame
                cv2.imshow('Pokemon Card Detection with Prices', frame)
                
                # Gestion des touches
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    screenshot_path = f"detection_screenshot_{frame_count}.png"
                    cv2.imwrite(screenshot_path, frame)
                    safe_print(f"📸 Screenshot sauvegardé: {screenshot_path}")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            safe_print(f"\n✅ Détection terminée ({frame_count} frames traités)")


def main():
    parser = argparse.ArgumentParser(description="Détection YOLO avec affichage des prix")
    
    parser.add_argument('--source', type=str, default='0',
                       help='Source: 0 pour webcam, chemin vers image/video')
    parser.add_argument('--model', type=str, default='runs/detect/train/weights/best.pt',
                       help='Chemin vers le modèle YOLO (.pt)')
    parser.add_argument('--excel', type=str, default='excel/cards_info.xlsx',
                       help='Chemin vers le fichier Excel avec prix')
    parser.add_argument('--data-yaml', type=str, default='output/dataset/data.yaml',
                       help='Chemin vers data.yaml')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Seuil de confiance minimum (0-1)')
    parser.add_argument('--output', type=str, default=None,
                       help='Chemin de sortie pour image (optionnel)')
    
    args = parser.parse_args()
    
    try:
        # Initialiser le détecteur
        detector = PriceDetector(args.model, args.excel, args.data_yaml)
        
        # Déterminer le type de source
        source_path = Path(args.source)
        
        if args.source.isdigit() or args.source == '0':
            # Webcam
            detector.detect_video(args.source, args.conf)
        elif source_path.is_file():
            # Fichier image ou vidéo
            if source_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                # Image
                detector.detect_image(str(source_path), args.output, args.conf)
            elif source_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                # Vidéo
                detector.detect_video(str(source_path), args.conf)
            else:
                safe_print(f"❌ Format non supporté: {source_path.suffix}")
        else:
            safe_print(f"❌ Source non trouvée: {args.source}")
    
    except KeyboardInterrupt:
        safe_print("\n⚠️ Arrêt demandé par l'utilisateur")
    except Exception as e:
        safe_print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
