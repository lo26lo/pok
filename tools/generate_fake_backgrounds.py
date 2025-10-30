#!/usr/bin/env python3
"""
Script pour générer des images de fond (fake backgrounds) pour mosaic.py
"""
import cv2
import numpy as np
import os

FAKE_DIR = "fakeimg"
os.makedirs(FAKE_DIR, exist_ok=True)

# Taille des images de fond
WIDTH, HEIGHT = 1920, 1080

# 1. Fond blanc
white = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255
cv2.imwrite(os.path.join(FAKE_DIR, "white_bg.png"), white)

# 2. Fond noir
black = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
cv2.imwrite(os.path.join(FAKE_DIR, "black_bg.png"), black)

# 3. Fond gris
gray = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 128
cv2.imwrite(os.path.join(FAKE_DIR, "gray_bg.png"), gray)

# 4. Fond bleu clair
blue_light = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8)
blue_light[:, :] = [230, 200, 150]  # BGR
cv2.imwrite(os.path.join(FAKE_DIR, "blue_light_bg.png"), blue_light)

# 5. Fond vert clair
green_light = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8)
green_light[:, :] = [180, 220, 180]  # BGR
cv2.imwrite(os.path.join(FAKE_DIR, "green_light_bg.png"), green_light)

# 6. Texture bruit aléatoire
noise = np.random.randint(100, 200, (HEIGHT, WIDTH, 3), dtype=np.uint8)
cv2.imwrite(os.path.join(FAKE_DIR, "noise_bg.png"), noise)

# 7. Dégradé horizontal
gradient_h = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
for i in range(WIDTH):
    gradient_h[:, i] = int(255 * i / WIDTH)
cv2.imwrite(os.path.join(FAKE_DIR, "gradient_h_bg.png"), gradient_h)

# 8. Dégradé vertical
gradient_v = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
for i in range(HEIGHT):
    gradient_v[i, :] = int(255 * i / HEIGHT)
cv2.imwrite(os.path.join(FAKE_DIR, "gradient_v_bg.png"), gradient_v)

# 9. Texture damier
checker = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
square_size = 100
for i in range(0, HEIGHT, square_size):
    for j in range(0, WIDTH, square_size):
        if ((i // square_size) + (j // square_size)) % 2 == 0:
            checker[i:i+square_size, j:j+square_size] = 255
        else:
            checker[i:i+square_size, j:j+square_size] = 200
cv2.imwrite(os.path.join(FAKE_DIR, "checker_bg.png"), checker)

# 10. Fond avec motif circulaire
circles = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 220
center_x, center_y = WIDTH // 2, HEIGHT // 2
for radius in range(50, min(WIDTH, HEIGHT) // 2, 100):
    cv2.circle(circles, (center_x, center_y), radius, (180, 180, 180), 2)
cv2.imwrite(os.path.join(FAKE_DIR, "circles_bg.png"), circles)

print(f"✓ 10 images de fond générées dans '{FAKE_DIR}/'")
