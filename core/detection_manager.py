"""
Detection Manager - Gestion de la détection YOLO
=================================================

Ce module gère la détection de cartes Pokemon avec des modèles YOLOv8.

Fonctionnalités:
- Détection webcam en temps réel
- Détection sur image unique
- Détection batch sur dossier
- Export des résultats annotés

Auteur: Pokemon Dataset Generator Team
Version: 3.0.0
"""

import os
import sys
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any, Tuple
from dataclasses import dataclass
import logging
import yaml

logger = logging.getLogger(__name__)

try:
    from .base_manager import BaseManager
except ImportError:
    from base_manager import BaseManager


@dataclass
class DetectionConfig:
    """Configuration pour la détection"""
    model_path: Path
    confidence: float = 0.25
    iou_threshold: float = 0.45
    max_detections: int = 300
    device: str = "0"  # "0", "cpu"
    
    # Webcam
    camera_id: int = 0
    display_fps: bool = True
    
    # Visualisation
    line_thickness: int = 2
    show_labels: bool = True
    show_confidence: bool = True
    
    # Affichage des prix
    show_prices: bool = False
    excel_path: str = "excel/cards_info.xlsx"
    data_yaml_path: Optional[str] = None  # Auto-détecté si None

    # Identification fine (F01) : crop bbox -> embedding -> index k-NN
    identify_cards: bool = False
    identify_index_dir: Optional[str] = None   # None = models/card_index
    identify_min_score: float = 0.5            # similarité cosinus minimale

    def __post_init__(self):
        """Validation"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Modèle non trouvé: {self.model_path}")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence doit être entre 0 et 1")
        if not 0 <= self.iou_threshold <= 1:
            raise ValueError("iou_threshold doit être entre 0 et 1")
        if not -1 <= self.identify_min_score <= 1:
            raise ValueError("identify_min_score doit être entre -1 et 1")


@dataclass
class Detection:
    """Représente une détection"""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2

    # Identification fine (F01) — renseignés si identify_cards est actif
    card_id: Optional[str] = None            # ex: "swsh7_003"
    exact_name: Optional[str] = None         # ex: "Skiploom [swsh7 003]"
    identify_score: Optional[float] = None   # similarité cosinus du top-1

    def __repr__(self) -> str:
        if self.card_id:
            return (f"Detection({self.class_name} -> {self.card_id}, "
                    f"{self.confidence:.2%}, bbox={self.bbox})")
        return f"Detection({self.class_name}, {self.confidence:.2%}, bbox={self.bbox})"


class DetectionManager(BaseManager):
    """
    Gestionnaire de détection YOLO
    
    Exemple:
        >>> config = DetectionConfig(
        ...     model_path=Path("runs/train/pokemon_detector/weights/best.pt"),
        ...     confidence=0.5
        ... )
        >>> manager = DetectionManager(config)
        >>> detections = manager.detect_image("test.jpg")
        >>> for det in detections:
        ...     print(f"{det.class_name}: {det.confidence:.2%}")
    """
    
    def __init__(self, config: DetectionConfig):
        """
        Initialise le gestionnaire de détection
        
        Args:
            config: Configuration de détection
        """
        super().__init__()
        self.config = config
        self._model = None
        self._prices: Dict[str, Dict[str, Any]] = {}
        self._class_names: Dict[int, str] = {}
        self._identifier = None

        # Charger les prix si demandé
        if self.config.show_prices:
            self._load_prices()
            self._load_class_names()

        # Identification fine (F01) — best effort, ne bloque jamais la détection
        if self.config.identify_cards:
            self._load_identifier()

    def _load_identifier(self) -> None:
        """Charge l'index d'identification (F01) — best effort"""
        try:
            from .card_identifier import CardIdentifier
        except ImportError:
            from card_identifier import CardIdentifier
        try:
            self._identifier = CardIdentifier(self.config.identify_index_dir)
            meta = self._identifier.index.meta
            self._log(f"🎴 Index d'identification chargé: {meta['count']} cartes "
                      f"(méthode '{meta['method']}', backend "
                      f"{self._identifier.index.backend})")
        except Exception as e:
            self._identifier = None
            self._log(f"⚠️ Identification désactivée: {e}")

    def _identify_crop(self, frame, bbox) -> Optional[Any]:
        """
        Identifie la carte d'une bbox (frame PROPRE, avant annotations).

        Returns:
            IdentificationResult si le score atteint identify_min_score, sinon None
        """
        if self._identifier is None:
            return None
        try:
            h, w = frame.shape[:2]
            x1, y1, x2, y2 = map(int, bbox)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 - x1 < 16 or y2 - y1 < 16:
                return None
            result = self._identifier.identify(frame[y1:y2, x1:x2])
            if result and result.score >= self.config.identify_min_score:
                return result
            return None
        except Exception as e:
            self._log(f"⚠️ Erreur identification: {e}")
            return None


    def _load_prices(self) -> None:
        """Charge les prix : base YAML recouverte par le cache F10 (snapshot)"""
        try:
            from .card_mapping import get_card_id_from_class_name
            from .price_cache import load_prices_with_cache, snapshot_status

            self._prices = load_prices_with_cache()
            self._get_card_id = get_card_id_from_class_name  # Stocker la fonction de mapping

            if self._prices:
                status = snapshot_status()
                extra = f" ({status})" if status else ""
                self._log(f"💰 {len(self._prices)} prix chargés{extra}")
            else:
                self._log("⚠️ Aucun prix trouvé (YAML et cache vides) — "
                          "préchargez avec tools/preload_prices.py")
        except Exception as e:
            self._log(f"⚠️ Impossible de charger les prix: {e}")
            self._prices = {}
    
    def _load_class_names(self) -> None:
        """Charge les noms de classes depuis data.yaml"""
        try:
            # Auto-détecter data.yaml si non spécifié
            if self.config.data_yaml_path is None:
                # Chercher dans output/dataset/data.yaml
                data_yaml = Path("output/dataset/data.yaml")
                if not data_yaml.exists():
                    # Chercher dans le même dossier que le modèle
                    model_dir = self.config.model_path.parent.parent.parent
                    data_yaml = model_dir / "data.yaml"
            else:
                data_yaml = Path(self.config.data_yaml_path)
            
            if data_yaml.exists():
                with open(data_yaml, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    names = data.get('names', [])
                    self._class_names = {i: name for i, name in enumerate(names)}
                    self._log(f"📋 {len(self._class_names)} classes chargées depuis {data_yaml}")
            else:
                self._log(f"⚠️ data.yaml non trouvé: {data_yaml}")
                
        except Exception as e:
            self._log(f"⚠️ Impossible de charger data.yaml: {e}")
            self._class_names = {}
    
    def _get_card_info(self, class_id: int,
                       ident=None) -> Tuple[str, Optional[float], Optional[float]]:
        """
        Récupère les infos d'une carte (nom, prix, prix_max)

        Args:
            class_id: ID de la classe
            ident: IdentificationResult F01 (optionnel) — si fourni, le nom
                   exact remplace le nom de classe et le prix est cherché
                   directement par card_id (sans passer par le mapping)

        Returns:
            Tuple (card_name, price, price_max)
        """
        if ident is not None:
            card_name = ident.display_name
            card_id = ident.card_id
        else:
            # Récupérer le nom de la carte
            card_name = self._class_names.get(class_id, f"class_{class_id}")

            # Convertir le nom de classe en card_id via le mapping
            card_id = self._get_card_id(card_name) if hasattr(self, '_get_card_id') else None

        # Récupérer le prix si disponible (avec le card_id)
        if card_id:
            card_info = self._prices.get(card_id, {})
        else:
            card_info = {}

        price = card_info.get('price')
        price_max = card_info.get('price_max')

        return card_name, price, price_max

    def _annotate_frame(self, frame, boxes):
        """
        Annote une frame avec les labels personnalisés (prix et/ou
        identification F01). L'identification se fait sur la frame PROPRE
        avant tout dessin.

        Args:
            frame: Image BGR non annotée
            boxes: Boîtes du résultat YOLO (results[0].boxes)

        Returns:
            Copie annotée de la frame
        """
        idents = [self._identify_crop(frame, box.xyxy[0].tolist())
                  for box in boxes]
        annotated = frame.copy()
        for box, ident in zip(boxes, idents):
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            bbox = box.xyxy[0].tolist()
            annotated = self._draw_detection_with_price(annotated, bbox,
                                                        cls_id, conf, ident)
        return annotated

    def _boxes_to_detections(self, result, frame) -> List[Detection]:
        """
        Convertit les boxes d'un résultat YOLO en Detection (avec
        identification F01 si active) — utilisé par le scan de collection.
        """
        detections = []
        names = result.names
        for box in result.boxes:
            cls_id = int(box.cls[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            det = Detection(class_id=cls_id, class_name=names[cls_id],
                            confidence=float(box.conf[0]),
                            bbox=(x1, y1, x2, y2))
            ident = self._identify_crop(frame, (x1, y1, x2, y2))
            if ident:
                det.card_id = ident.card_id
                det.exact_name = ident.display_name
                det.identify_score = ident.score
            detections.append(det)
        return detections

    @property
    def _custom_overlay(self) -> bool:
        """Vrai si l'annotation personnalisée remplace le plot() Ultralytics"""
        return self.config.show_prices or self._identifier is not None

    def _draw_detection_with_price(self, frame, box, class_id: int,
                                   confidence: float, ident=None):
        """
        Dessine une détection avec le prix sur l'image

        Args:
            frame: Image (numpy array)
            box: Boîte [x1, y1, x2, y2]
            class_id: ID de la classe
            confidence: Confiance de détection
            ident: IdentificationResult F01 (optionnel)

        Returns:
            Image annotée
        """
        import cv2

        x1, y1, x2, y2 = map(int, box)

        # Récupérer infos carte
        card_name, price, price_max = self._get_card_info(class_id, ident)
        
        # Couleur selon confiance
        if confidence >= 0.8:
            color = (0, 255, 0)  # Vert
        elif confidence >= 0.6:
            color = (0, 165, 255)  # Orange
        else:
            color = (0, 0, 255)  # Rouge
        
        # Dessiner rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.config.line_thickness)
        
        # Créer label
        if self.config.show_prices and price is not None:
            if price_max and price_max != price:
                price_text = f": {price:.2f}€-{price_max:.2f}€"
            else:
                price_text = f": {price:.2f}€"
        else:
            price_text = ""
        
        conf_text = f" ({confidence:.2f})" if self.config.show_confidence else ""
        label = f"{card_name}{price_text}{conf_text}"
        
        # Calculer taille du texte
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
        
        # Fond pour le texte
        cv2.rectangle(frame, 
                     (x1, y1 - text_height - baseline - 5), 
                     (x1 + text_width, y1),
                     color, -1)
        
        # Texte
        cv2.putText(frame, label, (x1, y1 - baseline - 5),
                   font, font_scale, (255, 255, 255), thickness)
        
        return frame
    
    def _load_model(self):
        """Charge le modèle YOLO (lazy loading)"""
        if self._model is None:
            try:
                from ultralytics import YOLO
                self._log(f"📦 Chargement du modèle: {self.config.model_path}")
                self._model = YOLO(str(self.config.model_path))
                self._log("✅ Modèle chargé")
            except ImportError:
                self._log("❌ Package ultralytics non installé!")
                raise
            except Exception as e:
                self._log(f"❌ Erreur chargement modèle: {e}")
                raise
    
    def detect_image(self, 
                     image_path: str | Path,
                     save_path: Optional[str | Path] = None) -> List[Detection]:
        """
        Détecte les cartes dans une image
        
        Args:
            image_path: Chemin de l'image
            save_path: Chemin de sauvegarde (optionnel)
            
        Returns:
            Liste des détections
        """
        self._load_model()
        
        try:
            self._log(f"🔍 Détection sur: {image_path}")
            
            # Prédire
            results = self._model.predict(
                source=str(image_path),
                conf=self.config.confidence,
                iou=self.config.iou_threshold,
                max_det=self.config.max_detections,
                device=self.config.device,
                verbose=False
            )
            
            # Parser les résultats
            detections = self._parse_results(results[0])
            
            self._log(f"✅ {len(detections)} carte(s) détectée(s)")
            
            # Sauvegarder si demandé
            if save_path:
                if self._custom_overlay:
                    # Dessiner avec prix/identification personnalisés
                    import cv2
                    annotated = self._annotate_frame(cv2.imread(str(image_path)),
                                                     results[0].boxes)
                else:
                    # Utiliser l'annotation YOLO standard
                    annotated = results[0].plot(
                        line_width=self.config.line_thickness,
                        labels=self.config.show_labels,
                        conf=self.config.show_confidence
                    )
                
                import cv2
                cv2.imwrite(str(save_path), annotated)
                self._log(f"💾 Image annotée sauvegardée: {save_path}")
            
            return detections
            
        except Exception as e:
            self._log(f"❌ Erreur détection: {e}")
            raise
    
    def detect_folder(self,
                      folder_path: str | Path,
                      output_folder: Optional[str | Path] = None,
                      extensions: List[str] = [".png", ".jpg", ".jpeg"]) -> Dict[str, List[Detection]]:
        """
        Détecte les cartes dans toutes les images d'un dossier
        
        Args:
            folder_path: Chemin du dossier
            output_folder: Dossier de sortie (créé automatiquement)
            extensions: Extensions d'images à traiter
            
        Returns:
            Dictionnaire {nom_fichier: [détections]}
        """
        self._load_model()
        
        folder_path = Path(folder_path)
        
        # Créer dossier de sortie
        if output_folder is None:
            output_folder = folder_path / "detections"
        else:
            output_folder = Path(output_folder)
        
        output_folder.mkdir(exist_ok=True, parents=True)
        
        # Lister les images
        image_files = []
        for ext in extensions:
            image_files.extend(folder_path.glob(f"*{ext}"))
        
        self._log(f"📂 Détection sur {len(image_files)} images")
        
        all_detections = {}
        
        for idx, img_path in enumerate(image_files, 1):
            self._log(f"   [{idx}/{len(image_files)}] {img_path.name}")
            
            output_path = output_folder / f"detect_{img_path.name}"
            detections = self.detect_image(img_path, save_path=output_path)
            all_detections[img_path.name] = detections
        
        self._log(f"✅ Détection terminée! Résultats dans: {output_folder}")
        
        return all_detections
    
    def detect_webcam(self,
                      quit_key: str = 'q',
                      save_video: bool = False,
                      output_path: Optional[str | Path] = None,
                      scanner=None) -> None:
        """
        Détection en temps réel sur webcam

        Args:
            quit_key: Touche pour quitter
            save_video: Enregistrer la vidéo
            output_path: Chemin de sauvegarde vidéo
            scanner: CollectionScanner (F03) optionnel — reçoit les
                     détections de chaque frame et affiche un compteur live
        """
        self._load_model()
        
        try:
            import cv2
            import time
            
            self._log(f"📹 Démarrage webcam (caméra {self.config.camera_id})")
            self._log(f"   Appuyez sur '{quit_key}' pour quitter")
            
            # Ouvrir webcam
            cap = cv2.VideoCapture(self.config.camera_id)
            
            if not cap.isOpened():
                self._log("❌ Impossible d'ouvrir la caméra!")
                raise RuntimeError("Caméra inaccessible")
            
            # Config vidéo writer
            video_writer = None
            if save_video:
                if output_path is None:
                    output_path = f"detection_{int(time.time())}.mp4"
                
                fps = int(cap.get(cv2.CAP_PROP_FPS) or 30)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
                self._log(f"🎥 Enregistrement: {output_path}")
            
            self._log("✅ Webcam démarrée!")
            
            frame_count = 0
            start_time = time.time()
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    self._log("⚠️ Échec lecture frame")
                    break
                
                frame_count += 1
                
                # Détecter
                results = self._model.predict(
                    source=frame,
                    conf=self.config.confidence,
                    iou=self.config.iou_threshold,
                    device=self.config.device,
                    verbose=False
                )
                
                # Scan de collection (F03) : accumuler les détections
                if scanner is not None:
                    detections = self._boxes_to_detections(results[0], frame)
                    for card in scanner.observe_frame(detections):
                        label = card.name if card.card_id is None \
                            else f"{card.name} ({card.card_id})"
                        self._log(f"🧺 Carte ajoutée à l'inventaire: {label}")

                # Annoter
                if self._custom_overlay:
                    # Dessiner avec prix/identification personnalisés
                    annotated = self._annotate_frame(frame, results[0].boxes)
                else:
                    # Utiliser l'annotation YOLO standard
                    annotated = results[0].plot(
                        line_width=self.config.line_thickness,
                        labels=self.config.show_labels,
                        conf=self.config.show_confidence
                    )
                
                # Afficher FPS
                if self.config.display_fps:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Compteur live du scan de collection (F03)
                if scanner is not None:
                    s = scanner.summary()
                    counter = (f"Scan: {s['unique_cards']} cartes "
                               f"({s['total_quantity']} ex.) | "
                               f"{s['total_value']:.2f} EUR")
                    cv2.putText(annotated, counter, (10, 65),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
                
                # Afficher
                cv2.imshow('Pokemon Card Detector', annotated)
                
                # Enregistrer
                if video_writer:
                    video_writer.write(annotated)
                
                # Quitter
                key = cv2.waitKey(1) & 0xFF
                if key == ord(quit_key):
                    self._log(f"🛑 Arrêt demandé (touche '{quit_key}')")
                    break
            
            # Cleanup
            cap.release()
            if video_writer:
                video_writer.release()
            cv2.destroyAllWindows()
            
            elapsed = time.time() - start_time
            avg_fps = frame_count / elapsed if elapsed > 0 else 0
            
            self._log("✅ Webcam arrêtée")
            self._log(f"📊 Stats: {frame_count} frames en {elapsed:.1f}s (avg: {avg_fps:.1f} FPS)")
            
        except ImportError:
            self._log("❌ OpenCV non installé!")
            self._log("   Installation: pip install opencv-python")
            raise
            
        except Exception as e:
            self._log(f"❌ Erreur webcam: {e}")
            raise
    
    def _parse_results(self, result) -> List[Detection]:
        """
        Parse les résultats YOLO en objets Detection
        
        Args:
            result: Objet résultat YOLO
            
        Returns:
            Liste de Detection
        """
        detections = []

        boxes = result.boxes
        names = result.names
        # Frame propre pour l'identification F01 (fournie par Ultralytics)
        orig_img = getattr(result, 'orig_img', None)

        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detection = Detection(
                class_id=cls_id,
                class_name=names[cls_id],
                confidence=conf,
                bbox=(x1, y1, x2, y2)
            )

            if self._identifier is not None and orig_img is not None:
                ident = self._identify_crop(orig_img, (x1, y1, x2, y2))
                if ident:
                    detection.card_id = ident.card_id
                    detection.exact_name = ident.display_name
                    detection.identify_score = ident.score

            detections.append(detection)

            # Log détection
            if detection.card_id:
                self._log(f"   • {detection.class_name} -> {detection.exact_name} "
                          f"(sim {detection.identify_score:.2f}, conf {conf:.2%})")
            else:
                self._log(f"   • {detection.class_name} ({conf:.2%})")

        return detections
    
    def show_image(self, image_path: str | Path) -> None:
        """
        Affiche une image avec détections
        
        Args:
            image_path: Chemin de l'image
        """
        try:
            import cv2
            
            detections = self.detect_image(image_path)
            
            # Réafficher avec annotations
            results = self._model.predict(
                source=str(image_path),
                conf=self.config.confidence,
                verbose=False
            )
            
            # Annoter avec ou sans prix/identification
            if self._custom_overlay:
                annotated = self._annotate_frame(cv2.imread(str(image_path)),
                                                 results[0].boxes)
            else:
                annotated = results[0].plot()
            
            cv2.imshow('Detection Result', annotated)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except Exception as e:
            self._log(f"❌ Erreur affichage: {e}")
            raise


def main():
    """Point d'entrée pour exécution standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Détection YOLOv8")
    parser.add_argument("model", help="Chemin du modèle (.pt)")
    parser.add_argument("--image", help="Chemin d'une image")
    parser.add_argument("--folder", help="Chemin d'un dossier")
    parser.add_argument("--webcam", action="store_true", help="Mode webcam")
    parser.add_argument("--conf", type=float, default=0.25, help="Seuil de confiance")
    parser.add_argument("--camera", type=int, default=0, help="ID caméra")
    parser.add_argument("--output", help="Dossier/fichier de sortie")
    parser.add_argument("--identify", action="store_true",
                        help="Identification fine F01 (nécessite l'index — "
                             "cf. tools/build_card_index.py)")
    parser.add_argument("--scan", action="store_true",
                        help="Scan de collection F03 en mode webcam "
                             "(inventaire + export CSV/Excel, implique --identify)")

    args = parser.parse_args()

    # Configuration
    config = DetectionConfig(
        model_path=Path(args.model),
        confidence=args.conf,
        camera_id=args.camera,
        identify_cards=args.identify or args.scan
    )
    
    # Manager
    manager = DetectionManager(config)
    manager.set_log_callback(print)
    
    try:
        if args.webcam:
            scanner = None
            if args.scan:
                try:
                    from .collection_scanner import CollectionScanner
                except ImportError:
                    from collection_scanner import CollectionScanner
                scanner = CollectionScanner()
            manager.detect_webcam(scanner=scanner)
            if scanner is not None:
                s = scanner.summary()
                csv_path = scanner.export_csv()
                xlsx_path = scanner.export_excel()
                print(f"\n🧺 Scan terminé: {s['unique_cards']} cartes uniques, "
                      f"{s['total_quantity']} exemplaires, "
                      f"valeur {s['total_value']:.2f}-{s['total_value_max']:.2f} EUR")
                print(f"   Inventaire: {csv_path}"
                      + (f" et {xlsx_path}" if xlsx_path else ""))
        elif args.image:
            detections = manager.detect_image(args.image, save_path=args.output)
            print(f"\n✅ {len(detections)} détection(s)")
        elif args.folder:
            all_detections = manager.detect_folder(args.folder, output_folder=args.output)
            total = sum(len(dets) for dets in all_detections.values())
            print(f"\n✅ {total} détection(s) sur {len(all_detections)} images")
        else:
            parser.print_help()
            sys.exit(1)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
