#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
card_identifier.py — F01 : identification fine de la carte (2ᵉ étage de pipeline)
=================================================================================

Après la localisation YOLO (« c'est une carte »), ce module identifie *quelle*
carte exacte est détectée (set + numéro) par recherche du plus proche voisin
dans un index d'embeddings construit sur les images TCGdex déjà téléchargées
(`images/`). Plus besoin de réentraîner YOLO pour chaque nouveau set.

Pipeline : crop de la bbox → embedding → recherche k-NN (cosinus) → card_id.

Deux embedders disponibles :
- ``classic`` (défaut) : descripteur couleur (grille Lab) + gradients orientés,
  pur OpenCV/numpy — aucune dépendance, < 5 ms par carte sur CPU.
- ``dnn`` : features MobileNetV2 (couche global-pool, 1280-d) via cv2.dnn —
  nécessite le fichier ONNX (livré dans models/, ~9 Mo), ~7 ms par carte.

Dépendances optionnelles (comme ultralytics pour l'entraînement) :
- ``faiss-cpu`` : accélère la recherche k-NN ; fallback numpy automatique
  (produit matriciel — largement suffisant jusqu'à ~100k cartes).

Usage :
    >>> from core.card_identifier import CardIdentifier
    >>> identifier = CardIdentifier()          # charge models/card_index/
    >>> result = identifier.identify(crop_bgr)
    >>> result.card_id, result.score
    ('swsh7_003', 0.98)

Construction de l'index : ``python tools/build_card_index.py`` (ou
``CardIndex.build()``).
"""
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

try:
    from .utils import PATHS, safe_print
except ImportError:
    from utils import PATHS, safe_print

# ==================== Constantes ====================

INDEX_VERSION = 1

# Fichiers de l'index (dans le dossier d'index, ex: models/card_index/)
EMBEDDINGS_FILE = "embeddings.npy"
CARDS_FILE = "cards.json"
META_FILE = "meta.json"

DEFAULT_INDEX_DIR = PATHS.get('directories', {}).get('card_index', 'models/card_index')
DEFAULT_ONNX_PATH = PATHS.get('files', {}).get('embedding_model_onnx',
                                               'models/mobilenetv2_embeddings.onnx')

# MobileNetV2 ImageNet (opset 7) — dépôt officiel onnx/models (licence Apache-2.0).
# Le fichier livré dans models/ est TRONQUÉ à la couche global-pool (features
# 1280-d, 9 Mo) : tools/build_card_index.py --download-model refait cette
# troncature depuis l'URL ci-dessous (le modèle complet fonctionne aussi,
# mais ses logits 1000-d sont moins discriminants — cf. benchmark F01).
EMBEDDING_MODEL_URL = (
    "https://media.githubusercontent.com/media/onnx/models/main/"
    "validated/vision/classification/mobilenet/model/mobilenetv2-7.onnx"
)
EMBEDDING_MODEL_POOL_OUTPUT = "mobilenetv20_features_pool0_fwd"

# Nom de fichier des images TCGdex : {set_id}_{localId}_{lang}.{ext}
# (cf. core/image_downloader.py). set_id peut contenir un point (sv04.5),
# localId peut être alphanumérique (XY05).
_FILENAME_PATTERN = re.compile(
    r'^(?P<set>[A-Za-z0-9.\-]+)_(?P<num>[A-Za-z0-9]+)_(?P<lang>[a-z]{2})$'
)

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')


def card_id_from_filename(filename: str) -> Optional[str]:
    """
    Déduit le card_id canonique depuis un nom de fichier TCGdex.

    Le card_id suit la convention de models/cards_database.yaml :
    numéro zero-paddé à 3 chiffres s'il est numérique.

    >>> card_id_from_filename("swsh7_3_en.png")
    'swsh7_003'
    >>> card_id_from_filename("xyp_XY05_fr.png")
    'xyp_XY05'
    >>> card_id_from_filename("manifest.csv") is None
    True
    """
    stem = Path(filename).stem
    match = _FILENAME_PATTERN.match(stem)
    if not match:
        return None
    num = match.group('num')
    if num.isdigit():
        num = num.zfill(3)
    return f"{match.group('set')}_{num}"


# ==================== Embedders ====================

class ClassicEmbedder:
    """
    Descripteur « classique » pur OpenCV : grille de couleurs Lab + histogrammes
    de gradients orientés. Conçu pour la recherche de quasi-doublons (la carte
    de référence a exactement le même artwork que le crop requête).

    - Robuste à l'exposition (canal L standardisé) et au bruit (travail à
      basse résolution 96×132).
    - Aucune dépendance au-delà du socle du projet, < 5 ms par carte.
    """

    name = "classic"

    # Résolution canonique (ratio carte TCG ~600:825)
    _SIZE = (96, 132)          # (largeur, hauteur)
    _COLOR_GRID = (6, 8)       # (cols, rows) pour la grille Lab
    _GRAD_GRID = (3, 4)        # (cols, rows) pour les gradients
    _GRAD_BINS = 8             # orientations non signées [0, π)

    @property
    def dim(self) -> int:
        cols, rows = self._COLOR_GRID
        gcols, grows = self._GRAD_GRID
        return cols * rows * 3 + gcols * grows * self._GRAD_BINS

    def embed(self, image_bgr: np.ndarray) -> np.ndarray:
        """Calcule l'embedding L2-normalisé (float32) d'un crop BGR."""
        img = cv2.resize(image_bgr, self._SIZE, interpolation=cv2.INTER_AREA)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab).astype(np.float32)

        # Standardiser le canal L (robustesse exposition/éclairage)
        L = lab[:, :, 0]
        lab[:, :, 0] = (L - L.mean()) / (L.std() + 1e-6) * 25.0 + 128.0

        color = self._grid_means(lab, self._COLOR_GRID)
        grad = self._gradient_histograms(lab[:, :, 0])

        # Normalisation par bloc puis globale : aucun bloc ne domine
        color /= (np.linalg.norm(color) + 1e-9)
        grad /= (np.linalg.norm(grad) + 1e-9)
        vec = np.concatenate([color, grad]).astype(np.float32)
        vec /= (np.linalg.norm(vec) + 1e-9)
        return vec

    @staticmethod
    def _grid_means(lab: np.ndarray, grid: Tuple[int, int]) -> np.ndarray:
        cols, rows = grid
        h, w = lab.shape[:2]
        cells = []
        for r in range(rows):
            for c in range(cols):
                y0, y1 = r * h // rows, (r + 1) * h // rows
                x0, x1 = c * w // cols, (c + 1) * w // cols
                cells.append(lab[y0:y1, x0:x1].reshape(-1, 3).mean(axis=0))
        return np.concatenate(cells) / 255.0

    def _gradient_histograms(self, gray: np.ndarray) -> np.ndarray:
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag = np.sqrt(gx * gx + gy * gy)
        ang = np.mod(np.arctan2(gy, gx), np.pi)  # orientations non signées
        bins = np.minimum((ang / np.pi * self._GRAD_BINS).astype(np.int32),
                          self._GRAD_BINS - 1)

        cols, rows = self._GRAD_GRID
        h, w = gray.shape
        hists = []
        for r in range(rows):
            for c in range(cols):
                y0, y1 = r * h // rows, (r + 1) * h // rows
                x0, x1 = c * w // cols, (c + 1) * w // cols
                hist = np.bincount(bins[y0:y1, x0:x1].ravel(),
                                   weights=mag[y0:y1, x0:x1].ravel(),
                                   minlength=self._GRAD_BINS)
                hists.append(hist / (hist.sum() + 1e-9))
        return np.concatenate(hists)


class DnnEmbedder:
    """
    Features MobileNetV2 (ImageNet) via cv2.dnn.

    Le modèle livré (models/mobilenetv2_embeddings.onnx, ~9 Mo) est tronqué à
    la couche global-pool → features 1280-d. Le modèle complet fonctionne
    aussi (logits 1000-d, moins précis) : la dimension est sondée au
    chargement. Aucune dépendance Python supplémentaire : OpenCV suffit.
    """

    name = "dnn"

    _MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    _STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def __init__(self, model_path: str = None):
        self.model_path = str(model_path or DEFAULT_ONNX_PATH)
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Modèle ONNX non trouvé: {self.model_path}\n"
                f"Récupérez-le avec: python tools/build_card_index.py "
                f"--download-model (source: {EMBEDDING_MODEL_URL})"
            )
        self._net = cv2.dnn.readNetFromONNX(self.model_path)
        # Sonder la dimension de sortie (1280 pool tronqué / 1000 logits)
        self.dim = int(self._forward(np.zeros((32, 32, 3), np.uint8)).size)

    def _forward(self, image_bgr: np.ndarray) -> np.ndarray:
        img = cv2.resize(image_bgr, (224, 224), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        rgb = (rgb - self._MEAN) / self._STD
        self._net.setInput(rgb.transpose(2, 0, 1)[np.newaxis])  # NCHW
        return self._net.forward().reshape(-1).astype(np.float32)

    def embed(self, image_bgr: np.ndarray) -> np.ndarray:
        """Calcule l'embedding L2-normalisé (float32) d'un crop BGR."""
        out = self._forward(image_bgr)
        out /= (np.linalg.norm(out) + 1e-9)
        return out


def reference_views(image_bgr: np.ndarray) -> List[np.ndarray]:
    """
    Vues d'une image de référence pour l'index : native + 300 px + 300 px
    floutée. Moyenner les embeddings de ces vues rapproche la référence du
    domaine webcam (basse résolution, flou) — mesuré au benchmark F01 :
    top-1 80 % → 91,4 % (MobileNetV2, 245 cartes, requêtes dégradées).
    """
    h, w = image_bgr.shape[:2]
    views = [image_bgr]
    if h > 300:
        small = cv2.resize(image_bgr, (max(24, w * 300 // h), 300),
                           interpolation=cv2.INTER_AREA)
        views.append(small)
        views.append(cv2.GaussianBlur(small, (5, 5), 0))
    return views


def embed_reference(embedder, image_bgr: np.ndarray) -> np.ndarray:
    """Embedding L2-normalisé d'une image de référence (moyenne des vues)."""
    vec = np.mean([embedder.embed(v) for v in reference_views(image_bgr)],
                  axis=0)
    return (vec / (np.linalg.norm(vec) + 1e-9)).astype(np.float32)


def create_embedder(method: str, model_path: str = None):
    """
    Instancie un embedder par nom : ``classic`` ou ``dnn``.

    ``auto`` choisit ``dnn`` si le fichier ONNX est présent, sinon ``classic``.
    """
    method = (method or "classic").lower()
    if method == "auto":
        onnx = Path(model_path or DEFAULT_ONNX_PATH)
        method = "dnn" if onnx.exists() else "classic"
    if method == "classic":
        return ClassicEmbedder()
    if method == "dnn":
        return DnnEmbedder(model_path)
    raise ValueError(f"Embedder inconnu: {method} (attendu: classic, dnn, auto)")


# ==================== Résultat d'identification ====================

@dataclass
class IdentificationResult:
    """Résultat de ``CardIdentifier.identify()``."""
    card_id: str                    # ex: "swsh7_003"
    score: float                    # similarité cosinus [−1, 1] du top-1
    name: Optional[str] = None      # ex: "Skiploom" (si connu)
    set_id: Optional[str] = None    # ex: "swsh7"
    local_id: Optional[str] = None  # ex: "003"
    top_k: List[Tuple[str, float]] = field(default_factory=list)  # [(card_id, score)]

    @property
    def display_name(self) -> str:
        """Libellé court pour l'overlay : « Skiploom [swsh7 003] »."""
        base = self.name or self.card_id
        if self.set_id and self.local_id:
            return f"{base} [{self.set_id} {self.local_id}]"
        return base


# ==================== Index ====================

class CardIndex:
    """
    Index d'embeddings de cartes : construction depuis un dossier d'images
    TCGdex, sauvegarde/chargement, recherche k-NN cosinus (FAISS si installé,
    sinon numpy).
    """

    def __init__(self, embeddings: np.ndarray, cards: List[Dict], meta: Dict):
        if embeddings.ndim != 2 or len(cards) != embeddings.shape[0]:
            raise ValueError(
                f"Index incohérent: {embeddings.shape} embeddings "
                f"pour {len(cards)} cartes"
            )
        self.embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
        self.cards = cards
        self.meta = meta
        self._faiss_index = self._try_build_faiss(self.embeddings)

    # ---------- Construction ----------

    @classmethod
    def build(cls,
              images_dir: str,
              method: str = "classic",
              model_path: str = None,
              database_yaml: str = None,
              progress_callback=None) -> "CardIndex":
        """
        Construit l'index depuis un dossier d'images TCGdex.

        Args:
            images_dir: dossier contenant les {set}_{num}_{lang}.png
            method: embedder ("classic", "dnn", "auto")
            model_path: chemin ONNX pour la méthode dnn
            database_yaml: models/cards_database.yaml pour enrichir les
                           métadonnées (nom, set) — optionnel
            progress_callback: callback(message, current, total) optionnel
        """
        images_dir = Path(images_dir)
        if not images_dir.is_dir():
            raise FileNotFoundError(f"Dossier d'images non trouvé: {images_dir}")

        files = sorted(
            p for p in images_dir.iterdir()
            if p.suffix.lower() in IMAGE_EXTENSIONS and card_id_from_filename(p.name)
        )
        if not files:
            raise ValueError(
                f"Aucune image de carte reconnue dans {images_dir} "
                f"(format attendu: {{set}}_{{num}}_{{lang}}.png)"
            )

        embedder = create_embedder(method, model_path)
        names = _load_card_names(database_yaml)

        def log(msg, cur=0, tot=0):
            if progress_callback:
                progress_callback(msg, cur, tot)
            else:
                safe_print(msg)

        log(f"🧬 Embeddings '{embedder.name}' sur {len(files)} cartes...", 0, len(files))

        vectors = np.zeros((len(files), embedder.dim), dtype=np.float32)
        cards: List[Dict] = []
        seen_ids: Dict[str, int] = {}
        kept = 0
        for i, path in enumerate(files):
            img = cv2.imread(str(path), cv2.IMREAD_COLOR)
            if img is None:
                log(f"⚠️ Image illisible ignorée: {path.name}", i + 1, len(files))
                continue
            card_id = card_id_from_filename(path.name)
            if card_id in seen_ids:
                # Même carte dans plusieurs langues : on garde la première
                # (l'artwork est identique, seul le texte change)
                continue
            vectors[kept] = embed_reference(embedder, img)
            seen_ids[card_id] = kept
            set_id, local_id = card_id.rsplit('_', 1)
            cards.append({
                "card_id": card_id,
                "set_id": set_id,
                "local_id": local_id,
                "name": names.get(card_id),
                "file": path.name,
            })
            kept += 1
            if (i + 1) % 50 == 0 or i + 1 == len(files):
                log(f"   {i + 1}/{len(files)} images traitées", i + 1, len(files))

        vectors = vectors[:kept]
        meta = {
            "version": INDEX_VERSION,
            "method": embedder.name,
            "dim": embedder.dim,
            "count": kept,
            "built_from": str(images_dir),
            "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        log(f"✅ Index construit: {kept} cartes uniques, dim={embedder.dim}")
        return cls(vectors, cards, meta)

    # ---------- Persistance ----------

    def save(self, index_dir: str = None) -> Path:
        """Sauvegarde l'index (embeddings.npy + cards.json + meta.json)."""
        index_dir = Path(index_dir or DEFAULT_INDEX_DIR)
        index_dir.mkdir(parents=True, exist_ok=True)
        np.save(index_dir / EMBEDDINGS_FILE, self.embeddings)
        with open(index_dir / CARDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.cards, f, ensure_ascii=False, indent=1)
        with open(index_dir / META_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=1)
        return index_dir

    @classmethod
    def load(cls, index_dir: str = None) -> "CardIndex":
        """Charge un index sauvegardé par :meth:`save`."""
        index_dir = Path(index_dir or DEFAULT_INDEX_DIR)
        emb_path = index_dir / EMBEDDINGS_FILE
        if not emb_path.exists():
            raise FileNotFoundError(
                f"Index non trouvé: {index_dir}\n"
                f"Construisez-le avec: python tools/build_card_index.py"
            )
        embeddings = np.load(emb_path)
        with open(index_dir / CARDS_FILE, 'r', encoding='utf-8') as f:
            cards = json.load(f)
        with open(index_dir / META_FILE, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        if meta.get("version", 0) > INDEX_VERSION:
            raise ValueError(
                f"Index version {meta.get('version')} plus récent que le code "
                f"(max supporté: {INDEX_VERSION})"
            )
        return cls(embeddings, cards, meta)

    # ---------- Recherche ----------

    @staticmethod
    def _try_build_faiss(embeddings: np.ndarray):
        """Construit un IndexFlatIP FAISS si la lib est installée, sinon None."""
        try:
            import faiss
        except ImportError:
            return None
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        return index

    @property
    def backend(self) -> str:
        """Backend de recherche effectif : 'faiss' ou 'numpy'."""
        return "faiss" if self._faiss_index is not None else "numpy"

    def search(self, vector: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
        """
        Recherche les k plus proches voisins (similarité cosinus, les
        embeddings étant L2-normalisés).

        Returns:
            Liste [(indice_carte, score)] triée par score décroissant.
        """
        k = min(k, len(self.cards))
        if k <= 0:
            return []
        query = np.ascontiguousarray(vector.reshape(1, -1), dtype=np.float32)

        if self._faiss_index is not None:
            scores, indices = self._faiss_index.search(query, k)
            return [(int(i), float(s)) for i, s in zip(indices[0], scores[0])
                    if i >= 0]

        scores = self.embeddings @ query[0]
        top = np.argpartition(scores, -k)[-k:]
        top = top[np.argsort(scores[top])[::-1]]
        return [(int(i), float(scores[i])) for i in top]


def _load_card_names(database_yaml: str = None) -> Dict[str, str]:
    """Charge {card_id: name} depuis models/cards_database.yaml (best effort)."""
    path = Path(database_yaml or PATHS['files'].get('cards_database_yaml',
                                                    'models/cards_database.yaml'))
    if not path.exists():
        return {}
    try:
        import yaml
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return {cid: info.get('name') for cid, info in (data or {}).get('cards', {}).items()}
    except Exception as e:
        safe_print(f"⚠️ Lecture de {path} impossible ({e}) — noms indisponibles")
        return {}


# ==================== Identifier ====================

class CardIdentifier:
    """
    Façade F01 : charge l'index + l'embedder correspondant, expose
    ``identify(crop) -> IdentificationResult``.

    L'embedder utilisé est celui enregistré dans les métadonnées de l'index
    (l'index et les requêtes DOIVENT partager le même embedder).
    """

    def __init__(self, index_dir: str = None, model_path: str = None):
        self.index = CardIndex.load(index_dir)
        self.embedder = create_embedder(self.index.meta["method"], model_path)
        if self.embedder.dim != self.index.embeddings.shape[1]:
            raise ValueError(
                f"Dimension embedder ({self.embedder.dim}) ≠ index "
                f"({self.index.embeddings.shape[1]}) — reconstruisez l'index"
            )

    def identify(self, crop_bgr: np.ndarray, k: int = 5) -> Optional[IdentificationResult]:
        """
        Identifie la carte d'un crop BGR (bbox YOLO découpée dans la frame).

        Args:
            crop_bgr: image BGR (numpy) de la carte, cadrage approximatif accepté
            k: nombre de voisins retournés dans top_k

        Returns:
            IdentificationResult (top-1 + top_k), ou None si le crop est
            inexploitable (vide / trop petit).
        """
        if crop_bgr is None or crop_bgr.size == 0 \
                or min(crop_bgr.shape[:2]) < 16:
            return None
        vector = self.embedder.embed(crop_bgr)
        neighbors = self.index.search(vector, k=k)
        if not neighbors:
            return None
        best_idx, best_score = neighbors[0]
        card = self.index.cards[best_idx]
        return IdentificationResult(
            card_id=card["card_id"],
            score=best_score,
            name=card.get("name"),
            set_id=card.get("set_id"),
            local_id=card.get("local_id"),
            top_k=[(self.index.cards[i]["card_id"], s) for i, s in neighbors],
        )
