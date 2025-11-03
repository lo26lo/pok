#!/usr/bin/env python3
"""
API REST Flask pour détection de cartes Pokémon
Endpoint /detect pour détecter les cartes depuis d'autres applications
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
from pathlib import Path
import os
import tempfile
from datetime import datetime


app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin

# Configuration
MODEL_PATH = "runs/train/pokemon_detector/weights/best.pt"
UPLOAD_FOLDER = "uploads"
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# Charger le modèle au démarrage
model = None

def load_model():
    """Charge le modèle YOLO"""
    global model
    try:
        from ultralytics import YOLO
        model = YOLO(MODEL_PATH)
        print(f"✅ Modèle chargé: {MODEL_PATH}")
        return True
    except Exception as e:
        print(f"❌ Erreur chargement modèle: {e}")
        return False


@app.route('/')
def index():
    """Page d'accueil de l'API"""
    return jsonify({
        "name": "Pokemon Card Detector API",
        "version": "1.0",
        "endpoints": {
            "/detect": "POST - Détecter des cartes dans une image",
            "/health": "GET - Vérifier le statut de l'API",
            "/models": "GET - Lister les modèles disponibles"
        },
        "status": "running",
        "model_loaded": model is not None
    })


@app.route('/health')
def health():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy" if model is not None else "no_model",
        "timestamp": datetime.now().isoformat(),
        "model_path": MODEL_PATH,
        "model_loaded": model is not None
    })


@app.route('/detect', methods=['POST'])
def detect():
    """
    Détecte des cartes Pokémon dans une image
    
    Request:
        - Multipart form avec fichier 'image'
        - Paramètres optionnels: confidence (0-1), iou (0-1)
    
    Response:
        JSON avec liste des détections
    """
    if model is None:
        return jsonify({"error": "Modèle non chargé"}), 500
    
    # Vérifier qu'un fichier a été envoyé
    if 'image' not in request.files:
        return jsonify({"error": "Aucun fichier 'image' dans la requête"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400
    
    # Paramètres optionnels
    confidence = float(request.form.get('confidence', 0.5))
    iou = float(request.form.get('iou', 0.45))
    
    try:
        # Lire l'image
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({"error": "Image invalide"}), 400
        
        # Détecter
        results = model(img, conf=confidence, iou=iou)
        
        # Extraire les résultats
        detections = []
        
        for r in results:
            boxes = r.boxes
            for i in range(len(boxes)):
                box = boxes[i]
                
                # Coordonnées de la bounding box
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Classe et confiance
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Nom de la classe
                class_name = r.names[cls]
                
                detections.append({
                    "class_id": cls,
                    "class_name": class_name,
                    "confidence": conf,
                    "bbox": {
                        "x1": float(x1),
                        "y1": float(y1),
                        "x2": float(x2),
                        "y2": float(y2)
                    }
                })
        
        return jsonify({
            "success": True,
            "image_size": {
                "width": img.shape[1],
                "height": img.shape[0]
            },
            "detections": detections,
            "count": len(detections)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/detect_annotated', methods=['POST'])
def detect_annotated():
    """
    Détecte et retourne l'image annotée
    
    Response:
        Image PNG avec bounding boxes dessinées
    """
    if model is None:
        return jsonify({"error": "Modèle non chargé"}), 500
    
    if 'image' not in request.files:
        return jsonify({"error": "Aucun fichier 'image' dans la requête"}), 400
    
    file = request.files['image']
    
    try:
        # Lire l'image
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Détecter et annoter
        results = model(img)
        annotated = results[0].plot()
        
        # Sauvegarder temporairement
        temp_path = os.path.join(UPLOAD_FOLDER, f"result_{datetime.now().timestamp()}.png")
        cv2.imwrite(temp_path, annotated)
        
        # Retourner l'image
        return send_file(temp_path, mimetype='image/png')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/models', methods=['GET'])
def list_models():
    """Liste les modèles disponibles"""
    models_dir = Path("runs/train")
    
    if not models_dir.exists():
        return jsonify({"models": []})
    
    models = []
    for model_dir in models_dir.iterdir():
        if model_dir.is_dir():
            weights_path = model_dir / "weights" / "best.pt"
            if weights_path.exists():
                models.append({
                    "name": model_dir.name,
                    "path": str(weights_path),
                    "size_mb": weights_path.stat().st_size / (1024 * 1024)
                })
    
    return jsonify({"models": models})


@app.route('/switch_model', methods=['POST'])
def switch_model():
    """Change le modèle actif"""
    global model, MODEL_PATH
    
    data = request.get_json()
    new_model_path = data.get('model_path')
    
    if not new_model_path:
        return jsonify({"error": "model_path requis"}), 400
    
    if not Path(new_model_path).exists():
        return jsonify({"error": "Modèle non trouvé"}), 404
    
    try:
        from ultralytics import YOLO
        model = YOLO(new_model_path)
        MODEL_PATH = new_model_path
        
        return jsonify({
            "success": True,
            "model_path": MODEL_PATH
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    """Lance le serveur"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API REST Pokemon Card Detector")
    parser.add_argument("--model", default=MODEL_PATH, help="Chemin du modèle YOLO")
    parser.add_argument("--host", default="0.0.0.0", help="Hôte")
    parser.add_argument("--port", type=int, default=5000, help="Port")
    parser.add_argument("--debug", action="store_true", help="Mode debug")
    args = parser.parse_args()
    
    global MODEL_PATH
    MODEL_PATH = args.model
    
    print("=" * 60)
    print("🚀 POKEMON CARD DETECTOR API")
    print("=" * 60)
    print(f"📂 Modèle: {MODEL_PATH}")
    print(f"🌐 Hôte: {args.host}:{args.port}")
    print()
    
    # Charger le modèle
    if load_model():
        print("✅ API prête!")
    else:
        print("⚠️  API lancée sans modèle (utilisez /switch_model)")
    
    print()
    print("📚 Documentation:")
    print(f"   GET  http://{args.host}:{args.port}/          - Info API")
    print(f"   GET  http://{args.host}:{args.port}/health    - Health check")
    print(f"   POST http://{args.host}:{args.port}/detect    - Détecter cartes")
    print()
    print("💡 Exemple cURL:")
    print(f'   curl -X POST -F "image=@pikachu.jpg" http://localhost:{args.port}/detect')
    print()
    print("=" * 60)
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
