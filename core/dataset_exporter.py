#!/usr/bin/env python3
"""
Module d'export de dataset dans différents formats
YOLO, COCO JSON, Pascal VOC XML, TFRecord, ZIP Roboflow
"""
import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
import zipfile
from datetime import datetime

# Import safe_print pour gérer l'encodage Unicode sur Windows
try:
    from .utils import safe_print
except ImportError:
    from utils import safe_print


class DatasetExporter:
    """Exporte un dataset YOLO vers différents formats"""
    
    def __init__(self, dataset_dir, class_names=None):
        """
        Initialise l'exporteur
        
        Args:
            dataset_dir: Dossier contenant images/ et labels/
            class_names: Liste des noms de classes (optionnel)
        """
        self.dataset_dir = Path(dataset_dir)
        self.images_dir = self.dataset_dir / "images"
        self.labels_dir = self.dataset_dir / "labels"
        self.class_names = class_names or {}
    
    def export_coco(self, output_path="dataset_coco.json", split_ratio=0.8):
        """
        Exporte au format COCO JSON
        
        Args:
            output_path: Chemin du fichier JSON de sortie
            split_ratio: Ratio train/val (0.8 = 80% train, 20% val)
        
        Returns:
            Chemin du fichier généré
        """
        safe_print("📦 Export au format COCO JSON...")
        
        coco_data = {
            "info": {
                "description": "Pokemon Card Dataset",
                "version": "1.0",
                "year": 2025,
                "date_created": datetime.now().isoformat()
            },
            "licenses": [],
            "categories": [],
            "images": [],
            "annotations": []
        }
        
        # Créer les catégories
        unique_classes = set()
        for label_file in self.labels_dir.glob("*.txt"):
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        unique_classes.add(int(parts[0]))
        
        for class_id in sorted(unique_classes):
            coco_data["categories"].append({
                "id": class_id,
                "name": self.class_names.get(class_id, f"class_{class_id}"),
                "supercategory": "pokemon_card"
            })
        
        # Parcourir les images
        image_files = list(self.images_dir.glob("*.png")) + \
                      list(self.images_dir.glob("*.jpg")) + \
                      list(self.images_dir.glob("*.jpeg"))
        
        annotation_id = 1
        
        for image_id, img_path in enumerate(image_files, 1):
            # Lire les dimensions de l'image
            import cv2
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            height, width = img.shape[:2]
            
            # Ajouter l'image
            coco_data["images"].append({
                "id": image_id,
                "file_name": img_path.name,
                "width": width,
                "height": height
            })
            
            # Lire les annotations
            label_path = self.labels_dir / (img_path.stem + ".txt")
            if not label_path.exists():
                continue
            
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 5:
                        continue
                    
                    class_id = int(parts[0])
                    x_center = float(parts[1]) * width
                    y_center = float(parts[2]) * height
                    bbox_width = float(parts[3]) * width
                    bbox_height = float(parts[4]) * height
                    
                    # COCO utilise [x_min, y_min, width, height]
                    x_min = x_center - bbox_width / 2
                    y_min = y_center - bbox_height / 2
                    
                    coco_data["annotations"].append({
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": class_id,
                        "bbox": [x_min, y_min, bbox_width, bbox_height],
                        "area": bbox_width * bbox_height,
                        "iscrowd": 0
                    })
                    
                    annotation_id += 1
        
        # Sauvegarder
        with open(output_path, 'w') as f:
            json.dump(coco_data, f, indent=2)
        
        safe_print(f"✅ Export COCO terminé: {output_path}")
        safe_print(f"   Images: {len(coco_data['images'])}")
        safe_print(f"   Annotations: {len(coco_data['annotations'])}")
        safe_print(f"   Catégories: {len(coco_data['categories'])}")
        
        return output_path
    
    def export_pascal_voc(self, output_dir="dataset_voc"):
        """
        Exporte au format Pascal VOC XML
        
        Args:
            output_dir: Dossier de sortie
        
        Returns:
            Chemin du dossier généré
        """
        safe_print("📦 Export au format Pascal VOC...")
        
        output_path = Path(output_dir)
        annotations_dir = output_path / "Annotations"
        images_out_dir = output_path / "JPEGImages"
        
        annotations_dir.mkdir(parents=True, exist_ok=True)
        images_out_dir.mkdir(parents=True, exist_ok=True)
        
        image_files = list(self.images_dir.glob("*.png")) + \
                      list(self.images_dir.glob("*.jpg")) + \
                      list(self.images_dir.glob("*.jpeg"))
        
        for img_path in image_files:
            # Copier l'image
            shutil.copy(img_path, images_out_dir / img_path.name)
            
            # Lire les dimensions
            import cv2
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            height, width, depth = img.shape
            
            # Créer le XML
            annotation = ET.Element("annotation")
            
            ET.SubElement(annotation, "folder").text = "JPEGImages"
            ET.SubElement(annotation, "filename").text = img_path.name
            
            size = ET.SubElement(annotation, "size")
            ET.SubElement(size, "width").text = str(width)
            ET.SubElement(size, "height").text = str(height)
            ET.SubElement(size, "depth").text = str(depth)
            
            # Lire les annotations YOLO
            label_path = self.labels_dir / (img_path.stem + ".txt")
            if not label_path.exists():
                continue
            
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 5:
                        continue
                    
                    class_id = int(parts[0])
                    x_center = float(parts[1]) * width
                    y_center = float(parts[2]) * height
                    bbox_width = float(parts[3]) * width
                    bbox_height = float(parts[4]) * height
                    
                    xmin = int(x_center - bbox_width / 2)
                    ymin = int(y_center - bbox_height / 2)
                    xmax = int(x_center + bbox_width / 2)
                    ymax = int(y_center + bbox_height / 2)
                    
                    obj = ET.SubElement(annotation, "object")
                    ET.SubElement(obj, "name").text = self.class_names.get(class_id, f"class_{class_id}")
                    ET.SubElement(obj, "pose").text = "Unspecified"
                    ET.SubElement(obj, "truncated").text = "0"
                    ET.SubElement(obj, "difficult").text = "0"
                    
                    bndbox = ET.SubElement(obj, "bndbox")
                    ET.SubElement(bndbox, "xmin").text = str(xmin)
                    ET.SubElement(bndbox, "ymin").text = str(ymin)
                    ET.SubElement(bndbox, "xmax").text = str(xmax)
                    ET.SubElement(bndbox, "ymax").text = str(ymax)
            
            # Sauvegarder le XML
            tree = ET.ElementTree(annotation)
            xml_path = annotations_dir / (img_path.stem + ".xml")
            tree.write(xml_path, encoding='utf-8', xml_declaration=True)
        
        safe_print(f"✅ Export Pascal VOC terminé: {output_dir}")
        safe_print(f"   Images: {len(list(images_out_dir.iterdir()))}")
        safe_print(f"   Annotations: {len(list(annotations_dir.iterdir()))}")
        
        return output_dir
    
    def export_roboflow_zip(self, output_path="dataset_roboflow.zip"):
        """
        Crée un ZIP compatible avec Roboflow
        
        Args:
            output_path: Chemin du fichier ZIP
        
        Returns:
            Chemin du fichier ZIP
        """
        safe_print("📦 Export au format Roboflow ZIP...")
        
        # Créer un dossier temporaire
        temp_dir = Path("temp_roboflow")
        temp_dir.mkdir(exist_ok=True)
        
        train_dir = temp_dir / "train"
        valid_dir = temp_dir / "valid"
        
        (train_dir / "images").mkdir(parents=True, exist_ok=True)
        (train_dir / "labels").mkdir(parents=True, exist_ok=True)
        (valid_dir / "images").mkdir(parents=True, exist_ok=True)
        (valid_dir / "labels").mkdir(parents=True, exist_ok=True)
        
        # Split 80/20
        image_files = list(self.images_dir.glob("*.png")) + \
                      list(self.images_dir.glob("*.jpg")) + \
                      list(self.images_dir.glob("*.jpeg"))
        
        import random
        random.shuffle(image_files)
        split_idx = int(len(image_files) * 0.8)
        
        train_images = image_files[:split_idx]
        valid_images = image_files[split_idx:]
        
        # Copier les fichiers
        for img_list, split_dir in [(train_images, train_dir), (valid_images, valid_dir)]:
            for img_path in img_list:
                # Copier image
                shutil.copy(img_path, split_dir / "images" / img_path.name)
                
                # Copier label
                label_path = self.labels_dir / (img_path.stem + ".txt")
                if label_path.exists():
                    shutil.copy(label_path, split_dir / "labels" / (img_path.stem + ".txt"))
        
        # Créer data.yaml
        yaml_content = f"""train: train/images
val: valid/images
nc: {len(set(self.class_names.keys())) if self.class_names else 1}
names: {list(self.class_names.values()) if self.class_names else ['class_0']}
"""
        
        with open(temp_dir / "data.yaml", 'w') as f:
            f.write(yaml_content)
        
        # Créer README
        readme = f"""# Pokemon Card Dataset
        
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Split
- Train: {len(train_images)} images
- Valid: {len(valid_images)} images

## Usage
This dataset is ready to use with YOLOv8:
```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model.train(data='data.yaml', epochs=100)
```
"""
        
        with open(temp_dir / "README.md", 'w') as f:
            f.write(readme)
        
        # Créer le ZIP
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        # Nettoyer
        shutil.rmtree(temp_dir)
        
        safe_print(f"✅ Export Roboflow ZIP terminé: {output_path}")
        safe_print(f"   Train: {len(train_images)} images")
        safe_print(f"   Valid: {len(valid_images)} images")
        
        return output_path


def main():
    """Fonction de test"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Export de dataset multi-format")
    parser.add_argument("dataset_dir", help="Dossier du dataset YOLO")
    parser.add_argument("--format", choices=['coco', 'voc', 'roboflow', 'all'],
                        default='all', help="Format d'export")
    args = parser.parse_args()
    
    exporter = DatasetExporter(args.dataset_dir)
    
    if args.format in ['coco', 'all']:
        exporter.export_coco()
    
    if args.format in ['voc', 'all']:
        exporter.export_pascal_voc()
    
    if args.format in ['roboflow', 'all']:
        exporter.export_roboflow_zip()
    
    safe_print("\n✅ Export(s) terminé(s)!")


if __name__ == "__main__":
    main()
