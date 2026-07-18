#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
price_cache.py — F10 : cache API hors-ligne (snapshot local des prix)
=====================================================================

Snapshot SQLite des prix TCGdex pour utiliser la détection et le scan de
collection **sans réseau** après un préchargement.

Principes :
- **Append-only** : chaque relevé est un snapshot horodaté — la table sert
  aussi d'historique de prix (socle de F09).
- **TTL de fraîcheur** (défaut 24 h) : il pilote le *rafraîchissement* via
  l'API, pas la validité — hors-ligne, une entrée périmée est toujours
  servie, avec sa date (« prix du JJ/MM »).
- **Fusion transparente** : `load_prices_with_cache()` renvoie la même
  structure que `core.utils.load_prices()` (YAML) en la recouvrant avec les
  snapshots plus récents du cache — la détection et le scanner en profitent
  sans changement d'API.

Usage :
    >>> cache = PriceCache()                        # models/price_cache.db
    >>> cache.put("sv08_019", 0.15, 0.25, "TCGdex(Cardmarket)")
    >>> entry = cache.get("sv08_019")
    >>> entry.price, entry.is_stale, entry.date_str
    (0.15, False, '2026-07-12')

Préchargement : ``python tools/preload_prices.py --set sv08`` (ou le bouton
« ⬇ Preload Prices » de la vue Detection).
"""
import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

try:
    from .utils import PATHS, load_prices, safe_print
except ImportError:
    from utils import PATHS, load_prices, safe_print

DEFAULT_DB_PATH = PATHS.get('files', {}).get('price_cache_db',
                                             'models/price_cache.db')
DEFAULT_TTL_HOURS = 24.0

_SCHEMA = """
CREATE TABLE IF NOT EXISTS price_snapshots (
    card_id    TEXT NOT NULL,          -- clé canonique, ex: "sv08_019"
    price      REAL,                   -- prix bas/tendance
    price_max  REAL,                   -- prix haut
    source     TEXT,                   -- ex: "TCGdex(Cardmarket)"
    currency   TEXT DEFAULT 'EUR',
    fetched_at REAL NOT NULL,          -- epoch UTC (time.time())
    PRIMARY KEY (card_id, fetched_at)
);
CREATE INDEX IF NOT EXISTS idx_snapshots_card
    ON price_snapshots (card_id, fetched_at DESC);

-- F09 : alertes de seuil. 'armed' évite les répétitions : l'alerte se
-- déclenche quand la condition devient vraie, se désarme, et se réarme
-- automatiquement quand la condition redevient fausse.
CREATE TABLE IF NOT EXISTS price_alerts (
    card_id      TEXT NOT NULL,
    threshold    REAL NOT NULL,
    direction    TEXT NOT NULL CHECK (direction IN ('above', 'below')),
    armed        INTEGER NOT NULL DEFAULT 1,
    created_at   REAL NOT NULL,
    triggered_at REAL,                 -- dernier déclenchement
    PRIMARY KEY (card_id, direction)
);
"""


def normalize_card_id(card_id: str) -> str:
    """
    Clé canonique du projet depuis un identifiant TCGdex ou local :
    tirets -> underscores, numéro final zero-paddé à 3 s'il est numérique.

    >>> normalize_card_id("swsh7-3")
    'swsh7_003'
    >>> normalize_card_id("sv08_019")
    'sv08_019'
    >>> normalize_card_id("xyp-XY05")
    'xyp_XY05'
    """
    key = card_id.strip().replace('-', '_')
    if '_' in key:
        prefix, num = key.rsplit('_', 1)
        if num.isdigit():
            key = f"{prefix}_{num.zfill(3)}"
    return key


def tcgdex_id_candidates(card_id: str) -> List[str]:
    """
    Identifiants TCGdex possibles pour une clé canonique (le zero-padding
    du localId dépend du set : "sv08-019" mais "swsh7-3").

    >>> tcgdex_id_candidates("swsh7_003")
    ['swsh7-003', 'swsh7-3']
    """
    key = normalize_card_id(card_id)
    set_part, num = key.rsplit('_', 1) if '_' in key else (key, '')
    candidates = [f"{set_part}-{num}"]
    if num.isdigit() and num != num.lstrip('0'):
        stripped = num.lstrip('0') or '0'
        candidates.append(f"{set_part}-{stripped}")
    return candidates


@dataclass
class PriceAlert:
    """Une alerte de seuil (F09)."""
    card_id: str
    threshold: float
    direction: str                  # 'above' ou 'below'
    armed: bool
    created_at: float
    triggered_at: Optional[float] = None

    def describe(self) -> str:
        arrow = "≥" if self.direction == 'above' else "≤"
        return f"{self.card_id} {arrow} {self.threshold:.2f}€"


@dataclass
class TriggeredAlert:
    """Résultat d'un franchissement de seuil (pour la notification GUI)."""
    alert: PriceAlert
    price: float
    name: Optional[str] = None

    def describe(self) -> str:
        label = self.name or self.alert.card_id
        verb = ("dépasse" if self.alert.direction == 'above'
                else "passe sous")
        return (f"{label} : {self.price:.2f}€ {verb} le seuil "
                f"de {self.alert.threshold:.2f}€")


@dataclass
class PriceEntry:
    """Un snapshot de prix pour une carte."""
    card_id: str
    price: Optional[float]
    price_max: Optional[float]
    source: Optional[str]
    currency: str
    fetched_at: float               # epoch UTC
    is_stale: bool = False          # plus vieux que le TTL du cache

    @property
    def date_str(self) -> str:
        """Date du snapshot pour l'affichage (« prix du JJ/MM »)."""
        return time.strftime("%Y-%m-%d", time.localtime(self.fetched_at))


class PriceCache:
    """
    Cache/hors-ligne des prix, stocké en SQLite (append-only).

    Args:
        db_path: chemin du .db (défaut: models/price_cache.db)
        ttl_hours: fraîcheur — au-delà, ``get()`` marque l'entrée is_stale
                   (elle reste utilisable hors-ligne)
    """

    def __init__(self, db_path: str = None, ttl_hours: float = DEFAULT_TTL_HOURS):
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.ttl_seconds = ttl_hours * 3600.0
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        # Connexion par opération : simple et sûr avec les ThreadPool du
        # préchargement (volumes très faibles, pas de contention réelle)
        return sqlite3.connect(self.db_path, timeout=10.0)

    # ---------- Écriture ----------

    def put(self, card_id: str, price: Optional[float],
            price_max: Optional[float], source: Optional[str] = None,
            currency: str = 'EUR',
            fetched_at: Optional[float] = None) -> PriceEntry:
        """Enregistre un snapshot (nouvelle ligne d'historique)."""
        key = normalize_card_id(card_id)
        now = fetched_at if fetched_at is not None else time.time()
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO price_snapshots "
                "(card_id, price, price_max, source, currency, fetched_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (key, price, price_max, source, currency, now))
        return PriceEntry(key, price, price_max, source, currency, now)

    def put_many(self, entries: Iterable[Tuple[str, Optional[float],
                                               Optional[float], Optional[str]]]) -> int:
        """Enregistre plusieurs snapshots (card_id, price, price_max, source)."""
        now = time.time()
        rows = [(normalize_card_id(cid), p, pm, src, 'EUR', now)
                for cid, p, pm, src in entries]
        with self._connect() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO price_snapshots "
                "(card_id, price, price_max, source, currency, fetched_at) "
                "VALUES (?, ?, ?, ?, ?, ?)", rows)
        return len(rows)

    # ---------- Lecture ----------

    def _row_to_entry(self, row, now: float) -> PriceEntry:
        card_id, price, price_max, source, currency, fetched_at = row
        return PriceEntry(card_id, price, price_max, source, currency,
                          fetched_at,
                          is_stale=(now - fetched_at) > self.ttl_seconds)

    def get(self, card_id: str) -> Optional[PriceEntry]:
        """Dernier snapshot d'une carte (is_stale selon le TTL), ou None."""
        key = normalize_card_id(card_id)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT card_id, price, price_max, source, currency, fetched_at "
                "FROM price_snapshots WHERE card_id = ? "
                "ORDER BY fetched_at DESC LIMIT 1", (key,)).fetchone()
        return self._row_to_entry(row, time.time()) if row else None

    def latest_all(self) -> Dict[str, PriceEntry]:
        """Dernier snapshot de CHAQUE carte : {card_id: PriceEntry}."""
        now = time.time()
        with self._connect() as conn:
            # Jointure explicite sur le max plutôt que le comportement
            # SQLite « bare columns avec MAX() » (correct en SQLite mais
            # non portable et facilement cassé par un refactor)
            rows = conn.execute(
                "SELECT p.card_id, p.price, p.price_max, p.source, "
                "       p.currency, p.fetched_at "
                "FROM price_snapshots p "
                "JOIN (SELECT card_id, MAX(fetched_at) AS max_fetched "
                "      FROM price_snapshots GROUP BY card_id) m "
                "  ON p.card_id = m.card_id "
                " AND p.fetched_at = m.max_fetched").fetchall()
        return {row[0]: self._row_to_entry(row, now) for row in rows}

    def history(self, card_id: str, limit: int = 100) -> List[PriceEntry]:
        """
        Historique d'une carte, du plus récent au plus ancien
        (socle de F09 : sparklines et alertes).
        """
        key = normalize_card_id(card_id)
        now = time.time()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT card_id, price, price_max, source, currency, fetched_at "
                "FROM price_snapshots WHERE card_id = ? "
                "ORDER BY fetched_at DESC LIMIT ?", (key, limit)).fetchall()
        return [self._row_to_entry(row, now) for row in rows]

    def stats(self) -> Dict:
        """État du cache (pour l'indicateur GUI et --check)."""
        with self._connect() as conn:
            cards, snapshots, newest, oldest = conn.execute(
                "SELECT COUNT(DISTINCT card_id), COUNT(*), "
                "       MAX(fetched_at), MIN(fetched_at) "
                "FROM price_snapshots").fetchone()
        fmt = (lambda t: time.strftime("%Y-%m-%d %H:%M", time.localtime(t))
               if t else None)
        return {"cards": cards, "snapshots": snapshots,
                "newest": fmt(newest), "oldest": fmt(oldest)}

    # ---------- Alertes de seuil (F09) ----------

    def set_alert(self, card_id: str, threshold: float,
                  direction: str = 'above') -> PriceAlert:
        """
        Crée ou remplace une alerte : notifier quand le prix de la carte
        dépasse (``above``) ou passe sous (``below``) le seuil.
        """
        if direction not in ('above', 'below'):
            raise ValueError("direction doit être 'above' ou 'below'")
        if threshold <= 0:
            raise ValueError("threshold doit être > 0")
        key = normalize_card_id(card_id)
        now = time.time()
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO price_alerts "
                "(card_id, threshold, direction, armed, created_at) "
                "VALUES (?, ?, ?, 1, ?)", (key, threshold, direction, now))
        return PriceAlert(key, threshold, direction, True, now)

    def remove_alert(self, card_id: str, direction: str = None) -> int:
        """Supprime les alertes d'une carte (une direction ou toutes)."""
        key = normalize_card_id(card_id)
        with self._connect() as conn:
            if direction:
                cur = conn.execute(
                    "DELETE FROM price_alerts WHERE card_id = ? "
                    "AND direction = ?", (key, direction))
            else:
                cur = conn.execute(
                    "DELETE FROM price_alerts WHERE card_id = ?", (key,))
            return cur.rowcount

    def list_alerts(self) -> List[PriceAlert]:
        """Toutes les alertes configurées."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT card_id, threshold, direction, armed, created_at, "
                "       triggered_at FROM price_alerts "
                "ORDER BY card_id, direction").fetchall()
        return [PriceAlert(r[0], r[1], r[2], bool(r[3]), r[4], r[5])
                for r in rows]

    def check_alerts(self) -> List[TriggeredAlert]:
        """
        Évalue toutes les alertes contre les derniers snapshots (à appeler
        après chaque relevé, ex. fin de préchargement).

        Une alerte armée dont la condition est vraie se déclenche puis se
        désarme ; une alerte désarmée se réarme dès que la condition
        redevient fausse. Retourne les alertes déclenchées maintenant.
        """
        latest = self.latest_all()
        triggered: List[TriggeredAlert] = []
        now = time.time()
        with self._connect() as conn:
            for alert in self.list_alerts():
                entry = latest.get(alert.card_id)
                if entry is None or entry.price is None:
                    continue
                condition = (entry.price >= alert.threshold
                             if alert.direction == 'above'
                             else entry.price <= alert.threshold)
                if condition and alert.armed:
                    conn.execute(
                        "UPDATE price_alerts SET armed = 0, triggered_at = ? "
                        "WHERE card_id = ? AND direction = ?",
                        (now, alert.card_id, alert.direction))
                    alert.armed = False
                    alert.triggered_at = now
                    triggered.append(TriggeredAlert(alert, entry.price))
                elif not condition and not alert.armed:
                    conn.execute(
                        "UPDATE price_alerts SET armed = 1 "
                        "WHERE card_id = ? AND direction = ?",
                        (alert.card_id, alert.direction))
        return triggered

    # ---------- Entretien ----------

    def purge(self, keep_per_card: int = 30) -> int:
        """
        Borne la taille : garde les ``keep_per_card`` snapshots les plus
        récents de chaque carte. Retourne le nombre de lignes supprimées.
        """
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM price_snapshots WHERE (card_id, fetched_at) IN ("
                "  SELECT card_id, fetched_at FROM ("
                "    SELECT card_id, fetched_at, ROW_NUMBER() OVER ("
                "      PARTITION BY card_id ORDER BY fetched_at DESC) AS rn "
                "    FROM price_snapshots) WHERE rn > ?)", (keep_per_card,))
            return cursor.rowcount


# ==================== Fusion YAML + cache ====================

def load_prices_with_cache(yaml_path: str = None,
                           db_path: str = None,
                           ttl_hours: float = DEFAULT_TTL_HOURS) -> Dict[str, Dict]:
    """
    Prix pour la détection/le scan : base YAML recouverte par les snapshots
    du cache (le cache gagne — il est alimenté par un préchargement
    explicite, donc plus récent que le YAML).

    Structure retournée identique à ``core.utils.load_prices()`` :
    {card_id: {'name', 'price', 'price_max'}} + clés 'price_source' et
    'price_date' quand le prix vient du cache.
    """
    prices = load_prices(yaml_path)
    try:
        cache = PriceCache(db_path, ttl_hours=ttl_hours)
        entries = cache.latest_all()
    except Exception as e:
        safe_print(f"⚠️ Cache de prix illisible ({e}) — YAML seul")
        return prices

    for card_id, entry in entries.items():
        if entry.price is None:
            continue
        info = prices.setdefault(card_id, {'name': None, 'price': None,
                                           'price_max': None})
        info['price'] = entry.price
        info['price_max'] = entry.price_max
        info['price_source'] = entry.source
        info['price_date'] = entry.date_str
    return prices


def snapshot_status(db_path: str = None) -> Optional[str]:
    """
    Libellé court de l'état du snapshot pour la GUI
    (« 152 prix, snapshot du 2026-07-12 14:03 »), ou None si cache vide.
    """
    try:
        stats = PriceCache(db_path).stats()
    except Exception:
        return None
    if not stats["cards"]:
        return None
    return f"{stats['cards']} prix, snapshot du {stats['newest']}"


# ==================== Préchargement ====================

def _resolve_set_card_ids(set_id: str, language: str = 'en') -> List[str]:
    """Identifiants TCGdex de toutes les cartes d'un set (1 appel API)."""
    import requests
    url = f"https://api.tcgdex.net/v2/{language}/sets/{set_id}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    cards = r.json().get('cards') or []
    return [c['id'] for c in cards if c.get('id')]


def preload_prices(card_ids: Iterable[str] = None,
                   set_id: str = None,
                   language: str = 'en',
                   workers: int = 8,
                   db_path: str = None,
                   progress_callback: Optional[Callable] = None) -> Dict:
    """
    Précharge les prix dans le cache pour un set (``set_id``) ou une liste
    de cartes (``card_ids``, clés canoniques OU identifiants TCGdex).

    Returns:
        {'requested', 'fetched', 'priced', 'failed'} — 'priced' compte les
        cartes avec au moins un prix.
    """
    try:
        from .tcgdex_api import TCGdexAPI
    except ImportError:
        from tcgdex_api import TCGdexAPI

    def log(msg, cur=0, tot=0):
        if progress_callback:
            progress_callback(msg, cur, tot)
        else:
            safe_print(msg)

    cache = PriceCache(db_path)
    api = TCGdexAPI(language=language, cache=cache)

    if set_id:
        log(f"🔍 Cartes du set '{set_id}'...")
        targets = _resolve_set_card_ids(set_id, language)
    else:
        targets = list(card_ids or [])
    if not targets:
        log("⚠️ Aucune carte à précharger")
        return {"requested": 0, "fetched": 0, "priced": 0, "failed": 0,
                "alerts": []}

    log(f"⬇️  Préchargement des prix de {len(targets)} cartes "
        f"({workers} workers)...", 0, len(targets))

    fetched = priced = failed = 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {executor.submit(api.get_card_prices, cid): cid
                   for cid in targets}
        for i, future in enumerate(as_completed(futures), 1):
            entry = future.result()
            if entry is None:
                failed += 1
            else:
                fetched += 1
                if entry.price is not None:
                    priced += 1
            if i % 25 == 0 or i == len(targets):
                log(f"   {i}/{len(targets)} cartes traitées", i, len(targets))

    stats = cache.stats()
    log(f"✅ Préchargement terminé: {priced} cartes avec prix, "
        f"{failed} échecs — cache: {stats['cards']} cartes "
        f"(snapshot du {stats['newest']})")

    # F09 : évaluer les alertes de seuil sur les nouveaux relevés
    triggered = cache.check_alerts()
    for t in triggered:
        log(f"🔔 ALERTE PRIX: {t.describe()}")

    return {"requested": len(targets), "fetched": fetched,
            "priced": priced, "failed": failed, "alerts": triggered}


def database_card_ids(yaml_path: str = None) -> List[str]:
    """Clés de toutes les cartes de models/cards_database.yaml."""
    return list(load_prices(yaml_path).keys())


def inventory_card_ids(csv_path: str) -> List[str]:
    """Clés card_id d'un export de scan de collection (F03)."""
    import csv as csv_mod
    ids = []
    with open(csv_path, encoding='utf-8') as f:
        for row in csv_mod.DictReader(f):
            cid = (row.get('card_id') or '').strip()
            if cid and not cid.startswith('yolo:') and re.match(r'^[^_]+_', cid):
                ids.append(cid)
    return ids
