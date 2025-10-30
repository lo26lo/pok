#!/usr/bin/env python3
import os
import sys
import cv2
import pandas as pd
import numpy as np
from glob import glob
import re
import random
import math
import time
import requests

# ----- Paramètres globaux pour la transformation 3D -----
THETA_MIN = -30    # Pour transform_mode==1 en mode 1 ou 3
THETA_MAX = 30
PHI_MIN   = -15
PHI_MAX   = 15

# Pour layout_mode 2 avec transform_mode 1, rotations plus prononcées :
THETA_MIN_MODE2 = -180
THETA_MAX_MODE2 = 180
PHI_MIN_MODE2   = -30
PHI_MAX_MODE2   = 30

# Nombre de layouts à générer par combinaison en mode ALL
NUM_VARIATIONS_ALL = 50

# Répertoires d'entrée et de sortie
INPUT_DIRS = [os.path.join("output", "augmented", "images")]
FAKE_DIR = "fakeimg_augmented"  # Utilise les fausses cartes augmentées
MOSAIC_DIR = "mosaic"  # pour background_mode==1

# ----- Nouveaux dossiers pour YOLOv8 -----
YOLO_OUTPUT_DIR = os.path.join("output", "yolov8")
YOLO_IMAGES_DIR = os.path.join(YOLO_OUTPUT_DIR, "images")
YOLO_LABELS_DIR = os.path.join(YOLO_OUTPUT_DIR, "labels")
os.makedirs(YOLO_IMAGES_DIR, exist_ok=True)
os.makedirs(YOLO_LABELS_DIR, exist_ok=True)

# ----- Fonctions de chargement et de traitement des images -----
def load_card_data(excel_path):
    df = pd.read_excel(excel_path, usecols=["Set #", "Name"])
    card_dict = {}
    class_map = {}
    for _, row in df.iterrows():
        number = row["Set #"].split('/')[0].zfill(3)
        name = row["Name"].replace(" ", "_")
        if number not in card_dict:
            card_dict[number] = name
            # L'ID YOLO = le numéro de la carte (001 → ID 1, 050 → ID 50, etc.)
            class_map[number] = int(number)
    return card_dict, class_map

def extract_card_number(filename):
    """
    Extrait le numéro de carte à partir du nom de fichier.
    Supporte plusieurs formats:
    - pokemon_en_001_xyz_aug_1.jpg -> "001"
    - SSP_001_R_EN_SM_aug_000.png -> "001"
    """
    # Format: _en_XXX_ (ancien format)
    match = re.search(r'_en_(\d{3})_', filename, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Format: XXX_XXX_XXX (nouveau format, ex: SSP_001_R_EN_SM.png)
    match = re.search(r'_(\d{3})_', filename)
    if match:
        return match.group(1)
    
    # Format: XXX au début ou dans le nom
    match = re.search(r'(\d{3})', filename)
    if match:
        return match.group(1)
    
    return None

def resize_cards(image_paths, target_size=(280,380)):
    resized_images = []
    for img_path in image_paths:
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            continue
        
        # Convertir RGBA en RGB si nécessaire
        if len(img.shape) == 3 and img.shape[2] == 4:
            # Image a un canal alpha, le convertir en BGR
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        resized_images.append((img, img_path))
    return resized_images

# ----- Transformation 2D classique -----
def rotate_image(image, angle):
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = np.abs(rot_matrix[0,0])
    sin = np.abs(rot_matrix[0,1])
    new_w = int((h*sin)+(w*cos))
    new_h = int((h*cos)+(w*sin))
    rot_matrix[0,2] += (new_w/2) - center[0]
    rot_matrix[1,2] += (new_h/2) - center[1]
    rotated = cv2.warpAffine(image, rot_matrix, (new_w,new_h), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    return rotated, rot_matrix

# ----- Transformation 3D par projection perspective -----
def rotate_image_3d(image, theta=None, phi=None):
    """
    Applique une rotation 3D à l'image par projection perspective, en conservant ses proportions.
    Si theta et phi ne sont pas fournis, ils sont choisis aléatoirement dans les plages par défaut.
    Pour layout_mode 2 (avec transform_mode==1), des plages élargies peuvent être utilisées via l'appel explicite.
    
    Renvoie :
      - warped : l'image transformée (en BGRA),
      - H : la matrice d'homographie,
      - projected_adjusted : les points projetés ajustés (pour annotation).
    """
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    h, w = image.shape[:2]
    
    if theta is None:
        theta = random.uniform(THETA_MIN, THETA_MAX)
    if phi is None:
        phi = random.uniform(PHI_MIN, PHI_MAX)
    
    theta_rad = np.deg2rad(theta)
    phi_rad = np.deg2rad(phi)
    
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(phi_rad), -np.sin(phi_rad)],
                    [0, np.sin(phi_rad), np.cos(phi_rad)]])
    R_y = np.array([[np.cos(theta_rad), 0, np.sin(theta_rad)],
                    [0, 1, 0],
                    [-np.sin(theta_rad), 0, np.cos(theta_rad)]])
    R = R_y @ R_x

    corners_3d = np.array([[0,0,0],
                           [w,0,0],
                           [w,h,0],
                           [0,h,0]], dtype=np.float32)
    rotated_corners = np.dot(corners_3d, R.T)
    
    f = 1.0 * max(w, h)
    projected = []
    for point in rotated_corners:
        X, Y, Z = point
        factor = f / (Z + f)
        projected.append([X * factor, Y * factor])
    projected = np.array(projected, dtype=np.float32)
    
    x_min = np.min(projected[:,0])
    y_min = np.min(projected[:,1])
    x_max = np.max(projected[:,0])
    y_max = np.max(projected[:,1])
    output_w = int(x_max - x_min)
    output_h = int(y_max - y_min)
    
    projected_adjusted = projected - np.array([x_min, y_min], dtype=np.float32)
    src = np.array([[0,0],[w,0],[w,h],[0,h]], dtype=np.float32)
    H = cv2.getPerspectiveTransform(src, projected_adjusted)
    warped = cv2.warpPerspective(image, H, (output_w, output_h), flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    
    return warped, H, projected_adjusted

# ----- Superposition sur le canevas -----
def overlay_on_canvas(canvas, overlay, x, y):
    h, w = overlay.shape[:2]
    canvas_h, canvas_w = canvas.shape[:2]
    x_start = max(x, 0)
    y_start = max(y, 0)
    x_end = min(x+w, canvas_w)
    y_end = min(y+h, canvas_h)
    if x_end <= x_start or y_end <= y_start:
        return canvas
    overlay_x_start = x_start - x
    overlay_y_start = y_start - y
    overlay_x_end = overlay_x_start + (x_end - x_start)
    overlay_y_end = overlay_y_start + (y_end - y_start)
    roi = canvas[y_start:y_end, x_start:x_end].astype(float)
    if overlay.shape[2] == 4:
        overlay_rgb = overlay[overlay_y_start:overlay_y_end, overlay_x_start:overlay_x_end, :3].astype(float)
        alpha = overlay[overlay_y_start:overlay_y_end, overlay_x_start:overlay_x_end, 3].astype(float) / 255.0
        alpha = np.stack([alpha, alpha, alpha], axis=2)
        blended = overlay_rgb * alpha + roi * (1 - alpha)
        canvas[y_start:y_end, x_start:x_end] = blended.astype(np.uint8)
    else:
        canvas[y_start:y_end, x_start:x_end] = overlay[overlay_y_start:overlay_y_end, overlay_x_start:overlay_x_end]
    return canvas

# ----- Création de la mosaïque de fond -----
def create_mosaic_background(canvas, fake_images):
    canvas_h, canvas_w = canvas.shape[:2]
    fake_w, fake_h = 280, 380
    step_x = int(fake_w * 0.5)
    step_y = int(fake_h * 0.5)
    for x in range(-fake_w//2, canvas_w+fake_w//2, step_x):
        for y in range(-fake_h//2, canvas_h+fake_h//2, step_y):
            jitter_x = random.randint(-step_x//4, step_x//4)
            jitter_y = random.randint(-step_y//4, step_y//4)
            pos_x = x + jitter_x
            pos_y = y + jitter_y
            # Utiliser les fake_images déjà chargées au lieu de recharger à chaque fois
            fake_card, _ = random.choice(fake_images)
            angle = random.randint(10,20) * random.choice([-1, 1])
            rotated_fake, _ = rotate_image(fake_card, angle)
            canvas = overlay_on_canvas(canvas, rotated_fake, pos_x, pos_y)
    return canvas

# ----- Choix du fond -----
def get_background(canvas_width, canvas_height, background_mode, fake_images, mosaic_dir="mosaic"):
    if background_mode == 0:
        canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
        canvas = create_mosaic_background(canvas, fake_images)
        return canvas
    elif background_mode == 1:
        image_paths = glob(os.path.join(mosaic_dir, "*.*"))
        if not image_paths:
            return np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
        chosen = random.choice(image_paths)
        bg = cv2.imread(chosen, cv2.IMREAD_COLOR)
        if bg is None:
            return np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
        bg = cv2.resize(bg, (canvas_width, canvas_height), interpolation=cv2.INTER_AREA)
        return bg
    elif background_mode == 2:
        try:
            url = "https://picsum.photos/1920/1080"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                web_dir = "web"
                if not os.path.exists(web_dir):
                    os.makedirs(web_dir)
                filename = os.path.join(web_dir, "background_" + str(int(time.time())) + ".jpg")
                with open(filename, "wb") as f:
                    f.write(resp.content)
                bg = cv2.imread(filename, cv2.IMREAD_COLOR)
                if bg is not None:
                    bg = cv2.resize(bg, (canvas_width, canvas_height), interpolation=cv2.INTER_AREA)
                    return bg
        except Exception as e:
            print("Erreur lors du téléchargement du fond:", e)
        return np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
    else:
        return np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255

# ----- Création d'un layout -----
def create_layout_group(images, group_index, card_dict, class_map, merged_mapping, fake_images,
                        layout_mode=1, background_mode=0, transform_mode=0, columns=4, rows=2, margin=20):
    canvas_width = 1920
    canvas_height = 1080
    canvas_size = (canvas_height, canvas_width, 3)
    layout = get_background(canvas_width, canvas_height, background_mode, fake_images)
    # Ancien code pour masque polygonal (non utilisé pour YOLOv8)
    # mask_image = np.zeros(canvas_size, dtype=np.uint8)
    
    annotations = []  # Pour stocker les annotations YOLO
    used_classes = {}  # (optionnel, si vous souhaitez garder trace des classes utilisées)

    if layout_mode in [1,2]:
        cell_width = (canvas_width - (columns+1)*margin) // columns
        cell_height = (canvas_height - (rows+1)*margin) // rows

    for i, (card, path) in enumerate(images):
        if layout_mode in [1,2]:
            col = i % columns
            row = i // columns
            cell_x = margin + col * (cell_width + margin)
            cell_y = margin + row * (cell_height + margin)
            if layout_mode == 1:
                angle = random.randint(10,20) * random.choice([-1,1])
                if transform_mode == 0:
                    rotated_card, rot_matrix = rotate_image(card, angle)
                    r_h, r_w = rotated_card.shape[:2]
                else:
                    rotated_card, H, poly = rotate_image_3d(card)
                    r_h, r_w = rotated_card.shape[:2]
            elif layout_mode == 2:
                if random.random() < 0.5:
                    card = cv2.flip(card, 1)
                if transform_mode == 0:
                    angle = random.randint(-180,180)
                    rotated_card, rot_matrix = rotate_image(card, angle)
                    r_h, r_w = rotated_card.shape[:2]
                else:
                    theta_val = random.uniform(THETA_MIN_MODE2, THETA_MAX_MODE2)
                    phi_val = random.uniform(PHI_MIN_MODE2, PHI_MAX_MODE2)
                    rotated_card, H, poly = rotate_image_3d(card, theta=theta_val, phi=phi_val)
                    r_h, r_w = rotated_card.shape[:2]
        elif layout_mode == 3:
            if transform_mode == 0:
                angle = random.randint(10,20)*random.choice([-1,1])
                rotated_card, rot_matrix = rotate_image(card, angle)
                r_h, r_w = rotated_card.shape[:2]
            else:
                rotated_card, H, poly = rotate_image_3d(card)
                r_h, r_w = rotated_card.shape[:2]
            cell_x = random.randint(0, canvas_width - r_w)
            cell_y = random.randint(0, canvas_height - r_h)
        else:
            col = i % columns
            row = i // columns
            cell_x = margin + col * (cell_width + margin)
            cell_y = margin + row * (cell_height + margin)
            angle = random.randint(10,20)*random.choice([-1,1])
            if transform_mode == 0:
                rotated_card, rot_matrix = rotate_image(card, angle)
                r_h, r_w = rotated_card.shape[:2]
            else:
                rotated_card, H, poly = rotate_image_3d(card)
                r_h, r_w = rotated_card.shape[:2]
        
        if layout_mode in [1,2]:
            dx = (cell_width - r_w) // 2
            dy = (cell_height - r_h) // 2
            pos_x = cell_x + dx
            pos_y = cell_y + dy
        else:
            pos_x = cell_x
            pos_y = cell_y

        layout = overlay_on_canvas(layout, rotated_card, pos_x, pos_y)

        filename = os.path.basename(path)
        card_number = extract_card_number(filename)
        if card_number in card_dict and card_number in class_map:
            # Récupération du nom et de la nouvelle classe (fusionnée) correspondant
            class_name = card_dict[card_number]
            new_class_id = merged_mapping[card_number]  # déjà en 0-index
            used_classes[new_class_id] = class_name  # (optionnel)
            orig_h, orig_w = card.shape[:2]
            corners = np.array([[0,0],[orig_w,0],[orig_w,orig_h],[0,orig_h]], dtype=np.float32)
            if transform_mode == 1:
                polygon = [(int(px+pos_x), int(py+pos_y)) for px,py in poly]
            else:
                transformed_corners = cv2.transform(np.array([corners]), rot_matrix)[0] + [pos_x, pos_y]
                polygon = [(int(px), int(py)) for px,py in transformed_corners]
            print(f"Groupe {group_index}, Annotation classe {new_class_id}: {polygon}")

            # Calcul de la bounding box à partir du polygone
            xs = [pt[0] for pt in polygon]
            ys = [pt[1] for pt in polygon]
            min_x = min(xs)
            max_x = max(xs)
            min_y = min(ys)
            max_y = max(ys)
            bbox_cx = (min_x + max_x) / 2 / canvas_width
            bbox_cy = (min_y + max_y) / 2 / canvas_height
            bbox_w = (max_x - min_x) / canvas_width
            bbox_h = (max_y - min_y) / canvas_height
            annotation_line = f"{new_class_id} {bbox_cx:.6f} {bbox_cy:.6f} {bbox_w:.6f} {bbox_h:.6f}"
            annotations.append(annotation_line)

    # Enregistrement du layout et des annotations dans les dossiers YOLOv8
    layout_filename = f"layout_{group_index:03d}.png"
    layout_path = os.path.join(YOLO_IMAGES_DIR, layout_filename)
    cv2.imwrite(layout_path, layout)
    
    label_filename = f"layout_{group_index:03d}.txt"
    label_path = os.path.join(YOLO_LABELS_DIR, label_filename)
    with open(label_path, "w") as f:
        f.write("\n".join(annotations))
    
    return layout, annotations

# ----- Fonction principale -----
def main():
    # Chargement des données des cartes depuis Excel
    card_dict, class_map = load_card_data("cards_info.xlsx")
    
    # Utilisation directe de class_map sans fusion des noms
    # Chaque numéro de carte a son propre ID unique (252 IDs au total)
    
    # Collecte des images depuis "output/augmented/images"
    image_paths = []
    for d in [os.path.join("output", "augmented", "images")]:
        image_paths += glob(os.path.join(d, "*.jpg"))
        image_paths += glob(os.path.join(d, "*.png"))
    resized_images = resize_cards(image_paths)
    if not resized_images:
        print("Aucune image valide trouvée dans les répertoires d'images!")
        return

    fake_image_paths = glob(os.path.join(FAKE_DIR, "*.png"))
    fake_image_paths += glob(os.path.join(FAKE_DIR, "*.jpg"))
    fake_images = resize_cards(fake_image_paths)
    if not fake_images:
        print("Aucune image valide trouvée dans le répertoire des fausses cartes!")
        return

    group_index = 1
    # Mode ALL pour générer toutes les variations
    if len(sys.argv) > 1 and sys.argv[1].lower() == "all":
        print("Mode ALL activé : génération de toutes les variations...")
        for lm in [1, 2, 3]:
            for bm in [0, 1, 2]:
                for tm in [0, 1]:
                    for i in range(NUM_VARIATIONS_ALL):
                        group = [random.choice(resized_images) for _ in range(8)]
                        create_layout_group(group, group_index, card_dict, class_map, class_map, fake_images,
                                            layout_mode=lm, background_mode=bm, transform_mode=tm)
                        print(f"Variation {group_index} générée pour (layout_mode={lm}, background_mode={bm}, transform_mode={tm})")
                        group_index += 1
        print("Génération ALL terminée !")
    else:
        layout_mode = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        background_mode = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        transform_mode = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        print("Layout mode choisi :", layout_mode)
        print("Background mode choisi :", background_mode)
        print("Transform mode choisi :", transform_mode)
        random.shuffle(resized_images)
        groups = [resized_images[i:i+8] for i in range(0, len(resized_images), 8)]
        for group in groups:
            create_layout_group(group, group_index, card_dict, class_map, class_map, fake_images,
                                layout_mode=layout_mode, background_mode=background_mode, transform_mode=transform_mode)
            print(f"Groupe {group_index} traité.")
            group_index += 1
        print("Génération terminée pour tous les groupes !")
    
    # Génération du fichier YAML pour YOLOv8 avec IDs = numéros de carte
    yaml_path = os.path.join(YOLO_OUTPUT_DIR, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write("train: images\n")
        f.write("val: images\n")
        # Le nombre de classes correspond au plus grand ID (ex: 191 pour carte 191/191)
        max_id = max(class_map.values())
        f.write(f"nc: {max_id + 1}\n")  # +1 car YOLO compte l'ID 0 aussi
        f.write("names:\n")
        # On crée une liste avec des indices de 0 à max_id
        names_list = ["unused"] * (max_id + 1)
        for card_num, class_id in class_map.items():
            names_list[class_id] = card_dict[card_num]
        for name in names_list:
            f.write(f"  - {name}\n")
    print(f"Fichier YAML généré : {yaml_path}")
    print(f"IDs utilisés: {min(class_map.values())} à {max(class_map.values())}")

if __name__ == "__main__":
    main()
