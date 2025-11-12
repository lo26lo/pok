"""
Script de migration : Excel → YAML
Convertit excel/cards_info.xlsx vers models/cards_database.yaml
"""

import sys
import json
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Charger paths depuis config
def load_paths():
    config_path = Path("config/paths.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

PATHS = load_paths()

def migrate_excel_to_yaml():
    """Migre Excel vers YAML"""
    import pandas as pd
    import yaml
    from datetime import datetime
    
    excel_path = Path(PATHS['files']['cards_info_excel'])
    yaml_path = Path(PATHS['files']['cards_database_yaml'])
    backup_path = Path("excel/cards_info_backup.xlsx")
    
    print("=" * 70)
    print("  MIGRATION EXCEL → YAML")
    print("=" * 70)
    print()
    
    # Vérifier que le fichier Excel existe
    if not excel_path.exists():
        print(f"❌ Fichier Excel non trouvé: {excel_path}")
        print("   Rien à migrer.")
        return False
    
    # Backup de l'Excel
    print(f"📦 Backup de l'Excel...")
    import shutil
    shutil.copy(excel_path, backup_path)
    print(f"   ✅ Backup créé: {backup_path}")
    print()
    
    # Lire l'Excel
    print(f"📖 Lecture de {excel_path}...")
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        print(f"   ✅ {len(df)} cartes trouvées")
    except Exception as e:
        print(f"   ❌ Erreur lecture Excel: {e}")
        return False
    
    print()
    print(f"📊 Colonnes trouvées: {list(df.columns)}")
    print()
    
    # Construire la structure YAML
    yaml_data = {
        'metadata': {
            'version': '1.0',
            'format': 'YOLO-compatible card database',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Migrated from Excel',
            'total_cards': len(df),
            'comment': 'Bounding boxes are generated dynamically during mosaic/augmentation'
        },
        'cards': {}
    }
    
    # Convertir chaque ligne
    print("🔄 Conversion des cartes...")
    for idx, row in df.iterrows():
        # Récupérer les colonnes (avec fallback)
        card_id = str(row.get('Set #', '')).strip()
        name = str(row.get('Name', 'Unknown')).strip()
        
        # Extraire set et number depuis card_id (ex: sv08_019)
        if '_' in card_id:
            set_code, number = card_id.split('_')
            set_full = f"{number}/191"  # Assumer 191 par défaut
        else:
            set_code = "unknown"
            number = "000"
            set_full = "000/191"
        
        # Prix
        price = row.get('Prix', None)
        price_max = row.get('Prix max', None)
        price_source = row.get('SourcePrix', '')
        
        # Nettoyer les valeurs NaN
        if pd.isna(price):
            price = None
        if pd.isna(price_max):
            price_max = None
        if pd.isna(price_source):
            price_source = ''
        
        # Autres infos (si disponibles)
        card_type = str(row.get('Type', 'Pokemon')).strip() if 'Type' in df.columns else 'Pokemon'
        rarity = str(row.get('Rarity', 'Common')).strip() if 'Rarity' in df.columns else 'Common'
        
        # Ajouter à la structure
        yaml_data['cards'][card_id] = {
            'name': name,
            'set': 'Surging Sparks',  # À adapter si nécessaire
            'set_full': set_full,
            'type': card_type,
            'rarity': rarity,
            'price': price,
            'price_max': price_max,
            'price_source': price_source,
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
        
        print(f"   ✅ {card_id}: {name}")
    
    print()
    
    # Sauvegarder le YAML
    print(f"💾 Sauvegarde vers {yaml_path}...")
    yaml_path.parent.mkdir(exist_ok=True)
    
    try:
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"   ✅ YAML créé avec succès!")
    except Exception as e:
        print(f"   ❌ Erreur sauvegarde YAML: {e}")
        return False
    
    print()
    print("=" * 70)
    print("✅ MIGRATION TERMINÉE!")
    print("=" * 70)
    print()
    print(f"📄 Nouveau fichier: {yaml_path}")
    print(f"📦 Backup Excel: {backup_path}")
    print()
    print("💡 Le projet utilisera maintenant le fichier YAML automatiquement.")
    print("   Vous pouvez éditer {yaml_path} avec n'importe quel éditeur de texte.")
    print()
    
    return True


if __name__ == "__main__":
    print()
    success = migrate_excel_to_yaml()
    print()
    
    if success:
        print("🎉 Migration réussie!")
    else:
        print("❌ Migration échouée.")
    
    print()
    input("Appuyez sur Entrée pour quitter...")
