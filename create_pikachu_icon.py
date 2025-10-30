"""
Création d'une icône Pikachu pour l'application
"""
from PIL import Image, ImageDraw
import os

def create_pikachu_icon():
    """Crée une icône Pikachu 256x256"""
    
    # Créer image 256x256 avec fond transparent
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleurs Pikachu
    yellow = (255, 220, 0, 255)
    dark_yellow = (200, 160, 0, 255)
    black = (0, 0, 0, 255)
    white = (255, 255, 255, 255)
    red = (255, 50, 50, 255)
    
    # Corps (cercle principal)
    body_center_x = size // 2
    body_center_y = size // 2 + 20
    body_radius = 80
    draw.ellipse([
        body_center_x - body_radius,
        body_center_y - body_radius,
        body_center_x + body_radius,
        body_center_y + body_radius
    ], fill=yellow, outline=dark_yellow, width=3)
    
    # Tête (cercle au-dessus)
    head_center_x = size // 2
    head_center_y = size // 2 - 40
    head_radius = 60
    draw.ellipse([
        head_center_x - head_radius,
        head_center_y - head_radius,
        head_center_x + head_radius,
        head_center_y + head_radius
    ], fill=yellow, outline=dark_yellow, width=3)
    
    # Oreille gauche (triangle)
    ear_left_points = [
        (head_center_x - 40, head_center_y - 40),  # Base gauche
        (head_center_x - 25, head_center_y - 40),  # Base droite
        (head_center_x - 35, head_center_y - 90)   # Pointe
    ]
    draw.polygon(ear_left_points, fill=yellow, outline=dark_yellow)
    # Bout noir de l'oreille
    draw.polygon([
        (head_center_x - 40, head_center_y - 80),
        (head_center_x - 30, head_center_y - 80),
        (head_center_x - 35, head_center_y - 90)
    ], fill=black)
    
    # Oreille droite (triangle)
    ear_right_points = [
        (head_center_x + 25, head_center_y - 40),  # Base gauche
        (head_center_x + 40, head_center_y - 40),  # Base droite
        (head_center_x + 35, head_center_y - 90)   # Pointe
    ]
    draw.polygon(ear_right_points, fill=yellow, outline=dark_yellow)
    # Bout noir de l'oreille
    draw.polygon([
        (head_center_x + 30, head_center_y - 80),
        (head_center_x + 40, head_center_y - 80),
        (head_center_x + 35, head_center_y - 90)
    ], fill=black)
    
    # Yeux
    eye_y = head_center_y - 10
    # Oeil gauche
    draw.ellipse([
        head_center_x - 30, eye_y - 12,
        head_center_x - 10, eye_y + 8
    ], fill=black)
    draw.ellipse([
        head_center_x - 25, eye_y - 5,
        head_center_x - 18, eye_y + 2
    ], fill=white)
    
    # Oeil droit
    draw.ellipse([
        head_center_x + 10, eye_y - 12,
        head_center_x + 30, eye_y + 8
    ], fill=black)
    draw.ellipse([
        head_center_x + 18, eye_y - 5,
        head_center_x + 25, eye_y + 2
    ], fill=white)
    
    # Joues roses (cercles rouges)
    cheek_y = head_center_y + 10
    # Joue gauche
    draw.ellipse([
        head_center_x - 50, cheek_y - 10,
        head_center_x - 30, cheek_y + 10
    ], fill=red)
    # Joue droite
    draw.ellipse([
        head_center_x + 30, cheek_y - 10,
        head_center_x + 50, cheek_y + 10
    ], fill=red)
    
    # Bouche (sourire)
    mouth_y = head_center_y + 15
    draw.arc([
        head_center_x - 15, mouth_y - 5,
        head_center_x + 15, mouth_y + 15
    ], start=0, end=180, fill=black, width=3)
    
    # Nez (petit triangle)
    nose_points = [
        (head_center_x - 3, mouth_y - 5),
        (head_center_x + 3, mouth_y - 5),
        (head_center_x, mouth_y)
    ]
    draw.polygon(nose_points, fill=black)
    
    # Bras gauche
    draw.ellipse([
        body_center_x - 100, body_center_y - 20,
        body_center_x - 60, body_center_y + 20
    ], fill=yellow, outline=dark_yellow, width=2)
    
    # Bras droit
    draw.ellipse([
        body_center_x + 60, body_center_y - 20,
        body_center_x + 100, body_center_y + 20
    ], fill=yellow, outline=dark_yellow, width=2)
    
    # Pieds
    # Pied gauche
    draw.ellipse([
        body_center_x - 50, body_center_y + 60,
        body_center_x - 20, body_center_y + 90
    ], fill=yellow, outline=dark_yellow, width=2)
    
    # Pied droit
    draw.ellipse([
        body_center_x + 20, body_center_y + 60,
        body_center_x + 50, body_center_y + 90
    ], fill=yellow, outline=dark_yellow, width=2)
    
    # Queue (éclair)
    tail_points = [
        (body_center_x + 70, body_center_y - 30),
        (body_center_x + 90, body_center_y - 20),
        (body_center_x + 80, body_center_y - 10),
        (body_center_x + 100, body_center_y),
        (body_center_x + 85, body_center_y + 5),
        (body_center_x + 95, body_center_y + 15),
        (body_center_x + 75, body_center_y + 10),
        (body_center_x + 80, body_center_y - 10),
    ]
    draw.polygon(tail_points, fill=yellow, outline=dark_yellow)
    
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
    
    print(f"✅ Icône Pikachu créée : {icon_path}")
    print(f"   Tailles : {', '.join([f'{s[0]}x{s[1]}' for s in icon_sizes])}")
    
    # Sauvegarder aussi en PNG pour prévisualisation
    png_path = 'pikachu_preview.png'
    img.save(png_path)
    print(f"✅ Prévisualisation PNG : {png_path}")
    
    return icon_path

if __name__ == "__main__":
    print("🎨 Création de l'icône Pikachu...")
    create_pikachu_icon()
    print("\n📝 Pour utiliser l'icône dans l'executable :")
    print("   1. Vérifiez pikachu_preview.png pour voir le résultat")
    print("   2. L'icône pikachu.ico est prête à être utilisée")
    print("   3. Elle sera automatiquement utilisée par create_exe.py")
