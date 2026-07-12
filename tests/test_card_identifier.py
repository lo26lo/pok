"""
Tests de l'identification fine des cartes (F01).

Couvre : parsing des noms de fichiers TCGdex, embedders (forme, norme,
déterminisme, latence), construction/sauvegarde/chargement de l'index,
recherche k-NN (FAISS et fallback numpy), API identify(), intégration
DetectionManager, et précision top-1/top-5 sur les cartes réelles du dépôt
(backgrounds/original) avec requêtes perturbées type webcam.
"""
import json
import time
from pathlib import Path

import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from core.card_identifier import (  # noqa: E402
    CardIdentifier,
    CardIndex,
    ClassicEmbedder,
    DnnEmbedder,
    IdentificationResult,
    card_id_from_filename,
    create_embedder,
    embed_reference,
    reference_views,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REAL_CARDS_DIR = PROJECT_ROOT / "backgrounds" / "original"
ONNX_PATH = PROJECT_ROOT / "models" / "mobilenetv2_embeddings.onnx"

needs_real_cards = pytest.mark.skipif(
    not REAL_CARDS_DIR.is_dir() or len(list(REAL_CARDS_DIR.glob("*.png"))) < 20,
    reason="cartes réelles (backgrounds/original) absentes",
)
needs_onnx = pytest.mark.skipif(
    not ONNX_PATH.exists(), reason="modèle ONNX absent (models/)",
)


def make_card(seed: int, size=(300, 220)) -> np.ndarray:
    """Pseudo-carte déterministe : fond coloré + motifs uniques par seed."""
    rng = np.random.default_rng(seed)
    h, w = size
    img = np.full((h, w, 3), rng.integers(40, 220, 3, dtype=np.uint8),
                  dtype=np.uint8)
    for _ in range(8):
        color = tuple(int(c) for c in rng.integers(0, 255, 3))
        p1 = (int(rng.integers(0, w)), int(rng.integers(0, h)))
        p2 = (int(rng.integers(0, w)), int(rng.integers(0, h)))
        cv2.rectangle(img, p1, p2, color, -1)
    cv2.rectangle(img, (0, 0), (w - 1, h - 1), (230, 220, 60), 10)
    return img


@pytest.fixture
def fake_images_dir(tmp_path):
    """Dossier d'images façon TCGdex : 8 cartes + fichiers à ignorer."""
    d = tmp_path / "images"
    d.mkdir()
    for i in range(8):
        cv2.imwrite(str(d / f"tst_{i + 1:03d}_en.png"), make_card(i))
    # Doublon de langue (même carte) et fichiers non-cartes
    cv2.imwrite(str(d / "tst_001_fr.png"), make_card(0))
    (d / "manifest.csv").write_text("id,name\n", encoding="utf-8")
    (d / "notes.txt").write_text("pas une image", encoding="utf-8")
    return d


@pytest.fixture
def classic_index(fake_images_dir):
    return CardIndex.build(fake_images_dir, method="classic",
                           database_yaml="/nonexistent.yaml",
                           progress_callback=lambda *a: None)


# ==================== Parsing des noms de fichiers ====================

class TestCardIdFromFilename:
    def test_numeric_is_zero_padded(self):
        assert card_id_from_filename("swsh7_3_en.png") == "swsh7_003"
        assert card_id_from_filename("sv08_019_fr.png") == "sv08_019"

    def test_alphanumeric_kept_as_is(self):
        assert card_id_from_filename("xyp_XY05_en.png") == "xyp_XY05"

    def test_set_with_dot(self):
        assert card_id_from_filename("sv04.5_231_en.webp") == "sv04.5_231"

    def test_rejects_non_card_files(self):
        assert card_id_from_filename("manifest.csv") is None
        assert card_id_from_filename("random.png") is None
        assert card_id_from_filename("tst_001_en_aug_042.png") is None


# ==================== Embedders ====================

class TestClassicEmbedder:
    def test_shape_norm_dtype(self):
        emb = ClassicEmbedder()
        vec = emb.embed(make_card(1))
        assert vec.shape == (emb.dim,)
        assert vec.dtype == np.float32
        assert np.isclose(np.linalg.norm(vec), 1.0, atol=1e-5)

    def test_deterministic(self):
        emb = ClassicEmbedder()
        img = make_card(2)
        assert np.array_equal(emb.embed(img), emb.embed(img))

    def test_discriminates_cards(self):
        emb = ClassicEmbedder()
        a, b = emb.embed(make_card(1)), emb.embed(make_card(2))
        self_sim = float(emb.embed(make_card(1)) @ a)
        cross_sim = float(a @ b)
        assert self_sim > 0.99 > cross_sim

    def test_latency_under_budget(self):
        emb = ClassicEmbedder()
        img = make_card(3, size=(400, 300))
        emb.embed(img)  # warmup
        t0 = time.perf_counter()
        for _ in range(10):
            emb.embed(img)
        assert (time.perf_counter() - t0) / 10 < 0.05  # critère F01: < 50 ms

    def test_create_embedder_factory(self):
        assert create_embedder("classic").name == "classic"
        with pytest.raises(ValueError):
            create_embedder("inconnu")


@needs_onnx
class TestDnnEmbedder:
    def test_shape_norm_and_latency(self):
        emb = DnnEmbedder()
        assert emb.dim == 1280  # modèle livré = tronqué à la couche pool
        img = make_card(1)
        vec = emb.embed(img)
        assert vec.shape == (emb.dim,)
        assert np.isclose(np.linalg.norm(vec), 1.0, atol=1e-5)
        t0 = time.perf_counter()
        for _ in range(5):
            emb.embed(img)
        assert (time.perf_counter() - t0) / 5 < 0.05  # critère F01: < 50 ms

    def test_missing_model_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            DnnEmbedder(str(tmp_path / "absent.onnx"))

    def test_auto_prefers_dnn_when_model_present(self):
        assert create_embedder("auto").name == "dnn"


class TestReferenceViews:
    def test_large_image_gets_three_views(self):
        views = reference_views(make_card(1, size=(825, 600)))
        assert len(views) == 3
        assert views[1].shape[0] == 300

    def test_small_image_single_view(self):
        assert len(reference_views(make_card(1, size=(200, 150)))) == 1

    def test_embed_reference_normalized(self):
        vec = embed_reference(ClassicEmbedder(), make_card(1, size=(825, 600)))
        assert np.isclose(np.linalg.norm(vec), 1.0, atol=1e-5)


# ==================== Index ====================

class TestCardIndex:
    def test_build_dedups_languages_and_skips_junk(self, classic_index):
        assert classic_index.meta["count"] == 8  # tst_001_fr est un doublon
        ids = [c["card_id"] for c in classic_index.cards]
        assert len(set(ids)) == 8
        assert "tst_001" in ids

    def test_save_load_roundtrip(self, classic_index, tmp_path):
        out = classic_index.save(tmp_path / "index")
        assert (out / "embeddings.npy").exists()
        loaded = CardIndex.load(out)
        assert loaded.meta == classic_index.meta
        assert np.allclose(loaded.embeddings, classic_index.embeddings)
        assert loaded.cards == classic_index.cards

    def test_load_missing_dir_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            CardIndex.load(tmp_path / "nope")

    def test_future_version_rejected(self, classic_index, tmp_path):
        out = classic_index.save(tmp_path / "index")
        meta = json.loads((out / "meta.json").read_text(encoding="utf-8"))
        meta["version"] = 999
        (out / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
        with pytest.raises(ValueError):
            CardIndex.load(out)

    def test_inconsistent_index_rejected(self):
        with pytest.raises(ValueError):
            CardIndex(np.zeros((3, 8), np.float32), [{"card_id": "a"}],
                      {"version": 1})

    def test_search_self_is_top1(self, classic_index):
        for i in [0, 3, 7]:
            neighbors = classic_index.search(classic_index.embeddings[i], k=3)
            assert neighbors[0][0] == i
            assert neighbors[0][1] > 0.99

    def test_search_k_clamped(self, classic_index):
        assert len(classic_index.search(classic_index.embeddings[0], k=50)) == 8
        assert classic_index.search(classic_index.embeddings[0], k=0) == []

    def test_numpy_fallback_matches_faiss(self, classic_index, monkeypatch):
        query = embed_reference(ClassicEmbedder(), make_card(5))
        got = classic_index.search(query, k=4)
        # Index identique sans FAISS (fallback produit matriciel)
        no_faiss = CardIndex.__new__(CardIndex)
        no_faiss.embeddings = classic_index.embeddings
        no_faiss.cards = classic_index.cards
        no_faiss.meta = classic_index.meta
        no_faiss._faiss_index = None
        assert no_faiss.backend == "numpy"
        fallback = no_faiss.search(query, k=4)
        assert [i for i, _ in fallback] == [i for i, _ in got]
        for (_, s1), (_, s2) in zip(fallback, got):
            assert abs(s1 - s2) < 1e-5


# ==================== Identifier ====================

class TestCardIdentifier:
    @pytest.fixture
    def identifier(self, classic_index, tmp_path):
        classic_index.save(tmp_path / "index")
        return CardIdentifier(tmp_path / "index")

    def test_identify_clean_card(self, identifier):
        result = identifier.identify(make_card(4))
        assert result.card_id == "tst_005"
        assert result.score > 0.99
        assert result.top_k[0][0] == "tst_005"
        assert len(result.top_k) == 5

    def test_identify_perturbed_card(self, identifier):
        img = make_card(6).astype(np.float32) * 0.8 + 20
        img = cv2.GaussianBlur(img.astype(np.uint8), (5, 5), 0)
        img = cv2.resize(img, (110, 150))
        result = identifier.identify(img)
        assert result.card_id == "tst_007"

    def test_identify_rejects_degenerate_crops(self, identifier):
        assert identifier.identify(None) is None
        assert identifier.identify(np.zeros((0, 0, 3), np.uint8)) is None
        assert identifier.identify(np.zeros((8, 8, 3), np.uint8)) is None

    def test_display_name(self):
        r = IdentificationResult(card_id="swsh7_003", score=0.9,
                                 name="Skiploom", set_id="swsh7",
                                 local_id="003")
        assert r.display_name == "Skiploom [swsh7 003]"
        anonymous = IdentificationResult(card_id="swsh7_003", score=0.9,
                                         set_id="swsh7", local_id="003")
        assert anonymous.display_name == "swsh7_003 [swsh7 003]"


# ==================== Intégration DetectionManager ====================

class TestDetectionManagerIntegration:
    @pytest.fixture
    def manager(self, classic_index, tmp_path):
        from core.detection_manager import DetectionConfig, DetectionManager
        model = PROJECT_ROOT / "models" / "yolo11n.pt"
        if not model.exists():
            pytest.skip("modèle YOLO absent")
        classic_index.save(tmp_path / "index")
        config = DetectionConfig(model_path=model, identify_cards=True,
                                 identify_index_dir=str(tmp_path / "index"))
        return DetectionManager(config)

    def test_identifier_loaded(self, manager):
        assert manager._identifier is not None
        assert manager._custom_overlay

    def test_identify_crop_and_threshold(self, manager):
        frame = np.full((400, 600, 3), 90, np.uint8)
        card = make_card(2)
        frame[50:350, 100:320] = cv2.resize(card, (220, 300))
        ident = manager._identify_crop(frame, (100, 50, 320, 350))
        assert ident is not None and ident.card_id == "tst_003"
        # Seuil haut → rejet
        manager.config.identify_min_score = 0.999
        frame_noise = (np.random.default_rng(0).random((300, 220, 3)) * 255
                       ).astype(np.uint8)
        assert manager._identify_crop(frame_noise, (0, 0, 220, 300)) is None

    def test_identify_crop_clips_bbox(self, manager):
        frame = np.zeros((100, 100, 3), np.uint8)
        frame[:] = 120
        # bbox partiellement hors cadre : ne doit pas lever
        manager._identify_crop(frame, (-50, -50, 80, 80))
        # bbox trop petite → None
        assert manager._identify_crop(frame, (0, 0, 10, 10)) is None

    def test_annotate_frame_draws_exact_name(self, manager):
        frame = np.full((400, 600, 3), 90, np.uint8)
        frame[50:350, 100:320] = cv2.resize(make_card(1), (220, 300))

        class FakeBox:
            xyxy = np.array([[100.0, 50.0, 320.0, 350.0]], np.float32)
            cls = np.array([0])
            conf = np.array([0.9])

        annotated = manager._annotate_frame(frame, [FakeBox()])
        assert annotated.shape == frame.shape
        assert (annotated != frame).any()

    def test_missing_index_never_blocks(self, tmp_path):
        from core.detection_manager import DetectionConfig, DetectionManager
        model = PROJECT_ROOT / "models" / "yolo11n.pt"
        if not model.exists():
            pytest.skip("modèle YOLO absent")
        config = DetectionConfig(model_path=model, identify_cards=True,
                                 identify_index_dir=str(tmp_path / "absent"))
        manager = DetectionManager(config)  # ne doit pas lever
        assert manager._identifier is None
        assert manager._identify_crop(np.zeros((100, 100, 3), np.uint8),
                                      (0, 0, 100, 100)) is None


# ==================== Précision sur cartes réelles ====================

@pytest.fixture(scope="module")
def real_identifier(tmp_path_factory):
    """Identifier dnn construit sur 40 cartes réelles du dépôt."""
    files = sorted(REAL_CARDS_DIR.glob("swsh7_*_en.png"))[:40]
    d = tmp_path_factory.mktemp("real_index_src")
    for f in files:
        (d / f.name).symlink_to(f)
    index = CardIndex.build(d, method="dnn",
                            progress_callback=lambda *a: None)
    out = tmp_path_factory.mktemp("real_index")
    index.save(out)
    return CardIdentifier(out)


@needs_real_cards
@needs_onnx
class TestRealCardsAccuracy:
    """
    Critère d'acceptation F01 : top-1 ≥ 90 % sur cartes bien cadrées.
    Mesuré sur 40 cartes réelles du dépôt avec requêtes perturbées
    (éclairage, flou, bruit, JPEG, basse résolution) — benchmark complet :
    tools/benchmark_card_embeddings.py.
    """

    @staticmethod
    def perturb(img, rng):
        img = cv2.convertScaleAbs(img, alpha=float(rng.uniform(0.8, 1.2)),
                                  beta=float(rng.uniform(-25, 25)))
        h = int(rng.integers(200, 400))
        img = cv2.resize(img, (max(24, img.shape[1] * h // img.shape[0]), h),
                         interpolation=cv2.INTER_AREA)
        img = cv2.GaussianBlur(img, (3, 3), 0)
        _, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY,
                                            int(rng.integers(50, 90))])
        return cv2.imdecode(buf, cv2.IMREAD_COLOR)

    def test_top1_top5_on_real_cards(self, real_identifier):
        rng = np.random.default_rng(123)
        files = sorted(REAL_CARDS_DIR.glob("swsh7_*_en.png"))[:40]
        top1 = top5 = total = 0
        for f in files:
            true_id = card_id_from_filename(f.name)
            img = cv2.imread(str(f))
            for _ in range(2):
                result = real_identifier.identify(self.perturb(img, rng))
                total += 1
                top1 += result.card_id == true_id
                top5 += true_id in [cid for cid, _ in result.top_k]
        assert top1 / total >= 0.90, f"top-1 {top1 / total:.1%} < 90%"
        assert top5 / total >= 0.95, f"top-5 {top5 / total:.1%} < 95%"
