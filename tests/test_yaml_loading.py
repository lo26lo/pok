"""
Tests pour le chargement des données depuis YAML
Teste load_prices_from_yaml(), load_prices(), et compatibilité Excel
"""

import pytest
import sys
from pathlib import Path
import yaml
import tempfile
import shutil

# Ajouter core/ au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import load_prices_from_yaml, load_prices, load_prices_from_excel


class TestYAMLLoading:
    """Tests pour le chargement YAML"""
    
    @pytest.fixture
    def sample_yaml_data(self):
        """Données YAML de test"""
        return {
            'metadata': {
                'version': '1.0',
                'total_cards': 3,
                'last_updated': '2025-11-11'
            },
            'cards': {
                'test_001': {
                    'name': 'Pikachu',
                    'set': 'Test Set',
                    'set_full': '001/100',
                    'type': 'Pokemon',
                    'rarity': 'Common',
                    'price': 1.50,
                    'price_max': 2.00,
                    'price_source': 'TCGdex',
                    'last_updated': '2025-11-11'
                },
                'test_002': {
                    'name': 'Charizard',
                    'set': 'Test Set',
                    'set_full': '002/100',
                    'type': 'Pokemon',
                    'rarity': 'Rare',
                    'price': 50.00,
                    'price_max': 75.00,
                    'price_source': 'TCGdex',
                    'last_updated': '2025-11-11'
                },
                'test_003': {
                    'name': 'Mewtwo',
                    'set': 'Test Set',
                    'set_full': '003/100',
                    'type': 'Pokemon',
                    'rarity': 'Ultra Rare',
                    'price': None,  # Pas de prix
                    'price_max': None,
                    'price_source': '',
                    'last_updated': '2025-11-11'
                }
            }
        }
    
    @pytest.fixture
    def temp_yaml_file(self, sample_yaml_data, tmp_path):
        """Créer un fichier YAML temporaire"""
        yaml_file = tmp_path / "test_cards.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_yaml_data, f, allow_unicode=True, sort_keys=False)
        return yaml_file
    
    def test_load_prices_from_yaml_success(self, temp_yaml_file):
        """Test chargement YAML réussi"""
        prices = load_prices_from_yaml(str(temp_yaml_file))
        
        assert len(prices) == 3
        assert 'test_001' in prices
        assert prices['test_001']['name'] == 'Pikachu'
        assert prices['test_001']['price'] == 1.50
        assert prices['test_001']['price_max'] == 2.00
    
    def test_load_prices_from_yaml_missing_file(self):
        """Test avec fichier inexistant"""
        prices = load_prices_from_yaml("nonexistent_file.yaml")
        
        assert prices == {}
    
    def test_load_prices_from_yaml_invalid_structure(self, tmp_path):
        """Test avec structure YAML invalide"""
        invalid_yaml = tmp_path / "invalid.yaml"
        with open(invalid_yaml, 'w', encoding='utf-8') as f:
            yaml.dump({'wrong': 'structure'}, f)
        
        prices = load_prices_from_yaml(str(invalid_yaml))
        
        assert prices == {}
    
    def test_load_prices_from_yaml_empty_cards(self, tmp_path):
        """Test avec section cards vide"""
        empty_yaml = tmp_path / "empty.yaml"
        data = {'metadata': {'version': '1.0'}, 'cards': {}}
        with open(empty_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)
        
        prices = load_prices_from_yaml(str(empty_yaml))
        
        assert prices == {}
    
    def test_load_prices_from_yaml_none_prices(self, temp_yaml_file):
        """Test avec prix None (non définis)"""
        prices = load_prices_from_yaml(str(temp_yaml_file))
        
        # Mewtwo n'a pas de prix
        assert prices['test_003']['price'] is None
        assert prices['test_003']['price_max'] is None
    
    def test_load_prices_auto_detection_yaml_priority(self, temp_yaml_file, tmp_path):
        """Test auto-détection: YAML prioritaire sur Excel"""
        # Créer un fichier Excel factice
        excel_file = tmp_path / "test_excel.xlsx"
        excel_file.touch()
        
        # load_prices() devrait détecter YAML en premier
        prices = load_prices(str(temp_yaml_file), str(excel_file))
        
        # Devrait charger depuis YAML
        assert len(prices) == 3
        assert 'test_001' in prices
    
    def test_load_prices_auto_detection_excel_fallback(self, tmp_path):
        """Test auto-détection: Fallback Excel si pas de YAML"""
        yaml_file = tmp_path / "nonexistent.yaml"
        excel_file = Path("excel/cards_info.xlsx")
        
        if excel_file.exists():
            prices = load_prices(str(yaml_file), str(excel_file))
            # Devrait fallback sur Excel
            assert isinstance(prices, dict)
        else:
            # Si pas d'Excel non plus, retourner dict vide
            prices = load_prices(str(yaml_file), "nonexistent.xlsx")
            assert prices == {}
    
    def test_load_prices_no_files(self):
        """Test sans aucun fichier disponible"""
        prices = load_prices("nonexistent.yaml", "nonexistent.xlsx")
        
        assert prices == {}
    
    def test_yaml_structure_compatibility(self, sample_yaml_data):
        """Test que la structure YAML est compatible avec l'ancien Excel"""
        # Les clés essentielles doivent être présentes
        for card_id, card_data in sample_yaml_data['cards'].items():
            assert 'name' in card_data
            assert 'price' in card_data
            assert 'price_max' in card_data
            
            # Les valeurs peuvent être None
            if card_data['price'] is not None:
                assert isinstance(card_data['price'], (int, float))


class TestYAMLVsExcelCompatibility:
    """Tests de compatibilité YAML/Excel"""
    
    def test_real_yaml_file_if_exists(self):
        """Test le vrai fichier YAML s'il existe"""
        yaml_path = Path("models/cards_database.yaml")
        
        if yaml_path.exists():
            prices = load_prices_from_yaml(str(yaml_path))
            
            assert isinstance(prices, dict)
            assert len(prices) > 0
            
            # Vérifier structure d'une carte
            first_card = next(iter(prices.values()))
            assert 'name' in first_card
            assert 'price' in first_card
            
            print(f"✅ Chargé {len(prices)} cartes depuis YAML réel")
        else:
            pytest.skip("Fichier YAML réel non trouvé")
    
    def test_real_excel_file_if_exists(self):
        """Test le vrai fichier Excel s'il existe (rétrocompatibilité)"""
        excel_path = Path("excel/cards_info.xlsx")
        
        if excel_path.exists():
            prices = load_prices_from_excel(str(excel_path))
            
            assert isinstance(prices, dict)
            assert len(prices) > 0
            
            # Vérifier structure d'une carte
            first_card = next(iter(prices.values()))
            assert 'name' in first_card
            assert 'price' in first_card
            
            print(f"✅ Chargé {len(prices)} cartes depuis Excel réel")
        else:
            pytest.skip("Fichier Excel réel non trouvé")
    
    def test_load_prices_with_real_files(self):
        """Test load_prices() avec les vrais fichiers"""
        yaml_path = Path("models/cards_database.yaml")
        excel_path = Path("excel/cards_info.xlsx")
        
        prices = load_prices(str(yaml_path), str(excel_path))
        
        # Devrait charger quelque chose si au moins un fichier existe
        if yaml_path.exists() or excel_path.exists():
            assert isinstance(prices, dict)
            print(f"✅ load_prices() a chargé {len(prices)} cartes")
        else:
            assert prices == {}


class TestYAMLPerformance:
    """Tests de performance YAML vs Excel"""
    
    def test_yaml_loading_speed(self, temp_yaml_file):
        """Mesurer vitesse de chargement YAML"""
        import time
        
        start = time.time()
        for _ in range(100):
            load_prices_from_yaml(str(temp_yaml_file))
        end = time.time()
        
        yaml_time = end - start
        print(f"\n⏱️ YAML: {yaml_time:.3f}s pour 100 chargements")
        
        # YAML devrait être rapide
        assert yaml_time < 5.0  # Moins de 5 secondes pour 100 chargements


def test_main():
    """Point d'entrée pour pytest"""
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    test_main()
