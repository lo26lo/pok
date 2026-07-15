#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preload_prices.py — F10 : préchargement du snapshot de prix hors-ligne
======================================================================

Remplit le cache SQLite (models/price_cache.db) avec les prix TCGdex pour
pouvoir détecter/scanner **sans réseau** ensuite. Chaque exécution ajoute
un snapshot horodaté (historique conservé — socle de F09).

Usage :
    python tools/preload_prices.py --set sv08            # tout un set
    python tools/preload_prices.py --database            # cartes du YAML
    python tools/preload_prices.py --inventory output/collection_scans/scan_X.csv
    python tools/preload_prices.py --check               # état du cache
    python tools/preload_prices.py --purge 30            # borne l'historique
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.price_cache import (  # noqa: E402
    PriceCache, database_card_ids, inventory_card_ids, preload_prices,
)
from core.utils import safe_print  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Préchargement des prix pour le mode hors-ligne (F10)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--set", dest="set_id",
                       help="ID du set TCGdex à précharger (ex: sv08)")
    group.add_argument("--database", action="store_true",
                       help="Précharge les cartes de models/cards_database.yaml")
    group.add_argument("--inventory",
                       help="Précharge les cartes d'un export de scan F03 (CSV)")
    group.add_argument("--check", action="store_true",
                       help="Affiche l'état du cache et quitte")
    group.add_argument("--purge", type=int, metavar="N",
                       help="Garde les N snapshots les plus récents par carte")
    parser.add_argument("--lang", default="en", help="Langue API (défaut: en)")
    parser.add_argument("--workers", type=int, default=8,
                        help="Requêtes simultanées (défaut: 8)")
    parser.add_argument("--db", default=None,
                        help="Chemin du cache (défaut: models/price_cache.db)")
    args = parser.parse_args()

    if args.check:
        stats = PriceCache(args.db).stats()
        if not stats["cards"]:
            safe_print("📭 Cache vide — lancez un préchargement "
                       "(--set, --database ou --inventory)")
        else:
            safe_print(f"✅ Cache: {stats['cards']} cartes, "
                       f"{stats['snapshots']} snapshots")
            safe_print(f"   Snapshot le plus récent: {stats['newest']}")
            safe_print(f"   Snapshot le plus ancien: {stats['oldest']}")
        return 0

    if args.purge is not None:
        deleted = PriceCache(args.db).purge(keep_per_card=args.purge)
        safe_print(f"🧹 {deleted} snapshots supprimés "
                   f"(historique borné à {args.purge}/carte)")
        return 0

    card_ids = None
    if args.database:
        card_ids = database_card_ids()
        if not card_ids:
            safe_print("❌ models/cards_database.yaml vide ou absent")
            return 1
    elif args.inventory:
        card_ids = inventory_card_ids(args.inventory)
        if not card_ids:
            safe_print(f"❌ Aucun card_id exploitable dans {args.inventory}")
            return 1
    elif not args.set_id:
        parser.print_help()
        return 1

    try:
        result = preload_prices(card_ids=card_ids, set_id=args.set_id,
                                language=args.lang, workers=args.workers,
                                db_path=args.db)
    except Exception as e:
        safe_print(f"❌ Préchargement impossible (réseau ?): {e}")
        return 1
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
