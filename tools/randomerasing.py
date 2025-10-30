import os
import random
import numpy as np
from math import sqrt
from PIL import Image
import argparse

def random_erasing(image, p=0.5, sl=0.02, sh=0.4, r1=0.3, r2=3.3):
    """
    Applique l'algorithme de random erasing sur une image PIL.
    
    Paramètres:
      - image : objet PIL.Image en mode RGB.
      - p     : probabilité d'appliquer l'effacement.
      - sl    : fraction minimale de la surface de l'image à effacer.
      - sh    : fraction maximale de la surface de l'image à effacer.
      - r1    : ratio d'aspect minimum du rectangle à effacer.
      - r2    : ratio d'aspect maximum.
      
    Retourne:
      Un tuple (image_modifiée, modified) où image_modifiée est l'image PIL (modifiée ou non)
      et modified est un booléen indiquant si l'augmentation a été appliquée.
    """
    # Tirage aléatoire pour décider d'appliquer l'effacement
    if random.random() >= p:
        return image, False

    img_np = np.array(image)
    H, W, C = img_np.shape  # Hauteur, largeur, nombre de canaux
    S = W * H               # Aire totale de l'image

    # Boucle pour sélectionner une région valide
    while True:
        # Calcul de l'aire du rectangle à effacer : Se = Rand(sl, sh) * S
        Se = random.uniform(sl, sh) * S
        # Choix aléatoire du ratio d'aspect dans [r1, r2]
        re = random.uniform(r1, r2)
        # Calcul de la hauteur et de la largeur du rectangle
        He = int(round(sqrt(Se * re)))
        We = int(round(sqrt(Se / re)))
        # Choix d'un point de départ aléatoire dans l'image
        xe = random.randint(0, W - 1)
        ye = random.randint(0, H - 1)
        # Vérifier que le rectangle tient dans l'image
        if xe + We <= W and ye + He <= H:
            # Remplissage de la zone avec des valeurs aléatoires pour chaque canal
            erase_area = np.random.randint(0, 256, size=(He, We, C), dtype=np.uint8)
            img_np[ye:ye+He, xe:xe+We, :] = erase_area
            break

    return Image.fromarray(img_np), True

def process_images(input_dir, output_dir, p, sl, sh, r1, r2):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            image_path = os.path.join(input_dir, filename)
            img = Image.open(image_path)
            # Conversion pour éviter le warning pour les PNG en mode palette
            if img.mode == 'P':
                img = img.convert('RGBA')
            # Conversion en RGB (si la transparence n'est pas nécessaire)
            img = img.convert('RGB')
            
            # Sauvegarder l'image d'origine pour retenter l'augmentation
            orig_img = img
            
            # Application du random erasing avec la valeur initiale de p
            image_erased, modified = random_erasing(orig_img, p=p, sl=sl, sh=sh, r1=r1, r2=r2)
            p_current = p
            
            # Pour les PNG non modifiés, augmenter p par incréments de 0.1 jusqu'à modification ou p=1.0
            if filename.lower().endswith(".png") and not modified:
                while not modified and p_current < 1.0:
                    p_current = round(min(1.0, p_current + 0.1), 1)
                    image_erased, modified = random_erasing(orig_img, p=p_current, sl=sl, sh=sh, r1=r1, r2=r2)
                if modified:
                    print(f"Traitement de {filename} modifié après augmentation de p à {p_current:.1f}.")
                else:
                    print(f"Traitement de {filename} non modifié malgré p atteignant {p_current:.1f}.")
            else:
                if modified:
                    print(f"Traitement de {filename} effectué (modifié) avec p = {p_current:.1f}.")
                else:
                    print(f"Traitement de {filename} effectué (non modifié).")
            
            # Sauvegarde de l'image transformée
            output_path = os.path.join(output_dir, "aug_" + filename)
            image_erased.save(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Applique le random erasing sur un répertoire d'images avec augmentation de p pour les PNG non modifiés."
    )
    parser.add_argument("--input_dir", type=str, default="fakeimg",
                        help="Répertoire contenant les images d'entrée")
    parser.add_argument("--output_dir", type=str, default="fakeimg_augmented",
                        help="Répertoire où enregistrer les images transformées")
    parser.add_argument("--p", type=float, default=0.5,
                        help="Probabilité initiale d'appliquer le random erasing (entre 0.0 et 1.0)")
    parser.add_argument("--sl", type=float, default=0.02,
                        help="Fraction minimale de l'aire à effacer")
    parser.add_argument("--sh", type=float, default=0.4,
                        help="Fraction maximale de l'aire à effacer")
    parser.add_argument("--r1", type=float, default=0.3,
                        help="Ratio d'aspect minimum")
    parser.add_argument("--r2", type=float, default=3.3,
                        help="Ratio d'aspect maximum")
    
    args = parser.parse_args()
    
    process_images(args.input_dir, args.output_dir, args.p, args.sl, args.sh, args.r1, args.r2)
