"""
Création d'une icône Mimikyu pour l'application
"""
from PIL import Image, ImageDraw
import os

def create_pikachu_icon():
    """Crée une icône Mimikyu 256x256"""
    
    # Créer image 256x256 avec fond transparent
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleurs Mimikyu
    cream = (245, 235, 200, 255)  # Beige/crème pour le costume
    light_cream = (255, 248, 220, 255)
    dark_cream = (210, 200, 170, 255)
    black = (0, 0, 0, 255)
    white = (255, 255, 255, 255)
    orange = (255, 140, 80, 255)  # Joues oranges
    brown = (101, 67, 33, 255)  # Parties marron
    
    # Corps fantôme (forme de drap)
    body_center_x = size // 2
    body_center_y = size // 2 + 30
    
    # Forme principale du corps (trapèze/drap)
    body_points = [
        (body_center_x - 85, body_center_y - 80),  # Haut gauche
        (body_center_x + 85, body_center_y - 80),  # Haut droit
        (body_center_x + 95, body_center_y + 70),  # Bas droit
        (body_center_x + 70, body_center_y + 90),  # Bas droit bas
        (body_center_x + 30, body_center_y + 85),  # Ondulation
        (body_center_x, body_center_y + 95),       # Centre bas
        (body_center_x - 30, body_center_y + 85),  # Ondulation
        (body_center_x - 70, body_center_y + 90),  # Bas gauche bas
        (body_center_x - 95, body_center_y + 70),  # Bas gauche
    ]
    draw.polygon(body_points, fill=cream, outline=dark_cream)
    
    # Tête (partie supérieure du costume)
    head_center_x = size // 2
    head_center_y = size // 2 - 50
    
    # Forme de tête irrégulière (comme un drap)
    head_radius = 70
    draw.ellipse([
        head_center_x - head_radius,
        head_center_y - head_radius + 20,
        head_center_x + head_radius,
        head_center_y + head_radius
    ], fill=cream, outline=dark_cream)
    
    # Oreille gauche (penché)
    ear_left_points = [
        (head_center_x - 45, head_center_y - 35),
        (head_center_x - 30, head_center_y - 35),
        (head_center_x - 50, head_center_y - 85),
        (head_center_x - 55, head_center_y - 70)
    ]
    draw.polygon(ear_left_points, fill=cream, outline=dark_cream)
    # Bout noir de l'oreille
    draw.polygon([
        (head_center_x - 52, head_center_y - 75),
        (head_center_x - 48, head_center_y - 75),
        (head_center_x - 50, head_center_y - 85)
    ], fill=black)
    
    # Oreille droite (plus droite)
    ear_right_points = [
        (head_center_x + 30, head_center_y - 35),
        (head_center_x + 45, head_center_y - 35),
        (head_center_x + 40, head_center_y - 90)
    ]
    draw.polygon(ear_right_points, fill=cream, outline=dark_cream)
    # Bout noir de l'oreille
    draw.polygon([
        (head_center_x + 35, head_center_y - 80),
        (head_center_x + 45, head_center_y - 80),
        (head_center_x + 40, head_center_y - 90)
    ], fill=black)
    
    # Yeux dessinés (faux yeux noirs)
    eye_y = head_center_y - 5
    # Oeil gauche (ovale noir avec reflet)
    draw.ellipse([
        head_center_x - 35, eye_y - 18,
        head_center_x - 5, eye_y + 12
    ], fill=black)
    # Reflet blanc
    draw.ellipse([
        head_center_x - 28, eye_y - 8,
        head_center_x - 18, eye_y + 2
    ], fill=white)
    
    # Oeil droit (ovale noir avec reflet)
    draw.ellipse([
        head_center_x + 5, eye_y - 18,
        head_center_x + 35, eye_y + 12
    ], fill=black)
    # Reflet blanc
    draw.ellipse([
        head_center_x + 18, eye_y - 8,
        head_center_x + 28, eye_y + 2
    ], fill=white)
    
    # Joues oranges (cercles)
    cheek_y = head_center_y + 15
    # Joue gauche
    draw.ellipse([
        head_center_x - 55, cheek_y - 8,
        head_center_x - 35, cheek_y + 12
    ], fill=orange)
    # Joue droite
    draw.ellipse([
        head_center_x + 35, cheek_y - 8,
        head_center_x + 55, cheek_y + 12
    ], fill=orange)
    
    # Bouche (zigzag mignon comme un sourire irrégulier)
    mouth_y = head_center_y + 25
    mouth_points = [
        (head_center_x - 15, mouth_y),
        (head_center_x - 8, mouth_y + 5),
        (head_center_x, mouth_y),
        (head_center_x + 8, mouth_y + 5),
        (head_center_x + 15, mouth_y)
    ]
    draw.line(mouth_points, fill=black, width=3)
    
    # Marques sur le costume (trous/coutures)
    # Petit trou/marque à gauche
    mark_left_y = body_center_y + 20
    draw.ellipse([
        body_center_x - 50, mark_left_y - 5,
        body_center_x - 40, mark_left_y + 5
    ], fill=dark_cream, outline=brown)
    
    # Trait de couture à droite
    draw.line([
        (body_center_x + 40, body_center_y),
        (body_center_x + 50, body_center_y + 15)
    ], fill=brown, width=2)
    
    # Queue (forme irrégulière de zigzag dépassant)
    tail_base_x = body_center_x + 75
    tail_base_y = body_center_y - 20
    tail_points = [
        (tail_base_x, tail_base_y),
        (tail_base_x + 15, tail_base_y - 10),
        (tail_base_x + 10, tail_base_y - 5),
        (tail_base_x + 25, tail_base_y - 15),
        (tail_base_x + 18, tail_base_y - 8),
        (tail_base_x + 30, tail_base_y - 20),
        (tail_base_x + 20, tail_base_y - 5),
        (tail_base_x + 10, tail_base_y + 5)
    ]
    draw.polygon(tail_points, fill=cream, outline=dark_cream)
    
    # Sauvegarder en différentes tailles pour l'icône
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    
    for icon_size in icon_sizes:
        resized = img.resize(icon_size, Image.Resampling.LANCZOS)
        images.append(resized)
    
    # Sauvegarder comme .ico
    icon_path = 'pikachu.ico'
    images[0].save(
        icon_path,
        format='ICO',
        sizes=icon_sizes,
        append_images=images[1:]
    )
    
    print(f"✅ Icône Mimikyu créée : {icon_path}")
    print(f"   Tailles : {', '.join([f'{s[0]}x{s[1]}' for s in icon_sizes])}")
    
    # Sauvegarder aussi en PNG pour prévisualisation
    png_path = 'pikachu_preview.png'
    img.save(png_path)
    print(f"✅ Prévisualisation PNG : {png_path}")
    
    return icon_path

if __name__ == "__main__":
    print("🎨 Création de l'icône Mimikyu...")
    create_pikachu_icon()
    print("\n📝 Pour utiliser l'icône dans l'executable :")
    print("   1. Vérifiez pikachu_preview.png pour voir le résultat")
    print("   2. L'icône pikachu.ico est prête à être utilisée")
    print("   3. Elle sera automatiquement utilisée par create_exe.py")
    print("   👻 Mimikyu vous protège maintenant !")
