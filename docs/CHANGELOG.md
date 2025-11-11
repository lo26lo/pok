# 📜 Changelog

All notable changes to the Pokémon Dataset Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.2.1] - 2025-11-11

### ♻️ Refactored

#### Code Duplication Removal
- **MAJOR**: Centralized utility functions to eliminate code duplication
- Moved `extract_card_number()`, `load_card_data()`, `resize_cards()` to `core/utils.py`
- Removed duplicated functions from:
  - `core/augmentation.py` (~100 lines)
  - `core/mosaic_optimized.py` (~34 lines)
- **Total reduction**: ~134 lines of duplicated code eliminated (85% reduction)

### 🔧 Improved

- **`core/utils.py`**:
  - Exported regex patterns as public constants (`PATTERN_NEW_FORMAT`, `PATTERN_OLD_FORMAT`, etc.)
  - Added comprehensive NumPy 2.0 compatibility patches
  - Enhanced `load_card_data()` to support both YAML (new) and Excel (legacy) formats
  - Enhanced `resize_cards()` with automatic RGBA→RGB conversion
  - Enhanced `extract_card_number()` to handle augmented filenames (`_aug_XXX`)
  - Improved all docstrings with usage examples

### 🎯 Benefits

- **Maintainability**: Single source of truth for utility functions
- **Bug Fixes**: Fix once, benefits all modules
- **Testing**: Easier to test centralized functions
- **Documentation**: Better centralized documentation
- **Backward Compatibility**: All function signatures preserved

---

## [3.2.0] - 2025-11-11

### 🚀 Major Changes

#### Migration Excel → YAML
- **BREAKING CHANGE**: Card database migrated from Excel to YAML format
- New file: `models/cards_database.yaml` (replaces `excel/cards_info.xlsx`)
- **Benefits**:
  - ~50MB lighter (no pandas/openpyxl required for basic usage)
  - Human-readable and editable format (any text editor)
  - Better Git versioning (clear line-by-line diffs)
  - Faster loading times (~10x faster than Excel)

### ✨ Added

- **YAML Loading** (`core/utils.py`)
  - `load_prices_from_yaml()`: Load card data from YAML
  - `load_prices()`: Auto-detection YAML/Excel with fallback
  - Backward compatible with Excel format

- **Migration Tools** (`scripts/`)
  - `migrate_excel_to_yaml.py`: One-time migration tool for existing users
  - `update_prices_yaml.py`: Update prices in YAML from TCGdex API
  - Updated `init_prices.py` and `init_prices_simple.py` to generate YAML

- **Testing** (`tests/test_yaml_loading.py`)
  - Complete test suite for YAML loading
  - Compatibility tests YAML/Excel
  - Performance benchmarks

- **Documentation**
  - `docs/MIGRATION_EXCEL_TO_YAML.md`: Complete migration guide
  - Updated all docs to reference YAML instead of Excel

### 🔄 Changed

- **GUI** (`GUI_v3.1_modern.py`)
  - Detects YAML instead of Excel
  - `create_sample_excel()` → creates YAML format
  - Updated messages and labels (Excel → YAML)
  - Price display now uses YAML source

- **Core Modules**
  - `core/augmentation.py`: Auto-detect YAML/Excel
  - `core/mosaic.py`: Auto-detect YAML/Excel
  - `core/detection_with_prices.py`: Use `load_prices()` with auto-detection

### 🐛 Fixed

- Excel file locking issues on Windows (YAML doesn't lock)
- Binary diff problems in Git (YAML is text-based)

### 📝 Notes

- **Backward Compatible**: Existing Excel files still work (auto-fallback)
- **Migration**: Run `scripts\run_script.bat migrate_excel_to_yaml`
- **Dependencies**: pandas/openpyxl still in requirements for migration tools only

---

## [3.1.0] - 2025-11-10

### 🎉 Added

#### Card Mapping & Price Detection System
- **Card Mapping Module** (`core/card_mapping.py`)
  - Automatic mapping between class names and TCGdex card IDs
  - Support for `card_name_to_id.json` mapping file
  - Fallback mechanisms for unmapped cards
  
- **Price Detection System** (`core/detection_with_prices.py`)
  - Real-time price display during YOLO detection
  - Integration with Excel price database
  - Support for Cardmarket and TCGPlayer prices
  - Visual price overlays on detected cards

- **Detection Manager Enhancement** (`core/detection_manager.py`)
  - Automatic price loading from Excel
  - Card mapping integration
  - Enhanced detection visualization with pricing info

#### Initialization & Utility Scripts
- **Price Initialization Scripts**
  - `scripts/init_prices.py` - Initialize prices from data.yaml
  - `scripts/init_prices_simple.py` - Simple 8-card training dataset
  - `scripts/init_prices_real.py` - Real card dataset initialization
  
- **Mapping Scripts**
  - `scripts/create_card_mapping.py` - Generate card ID mappings
  - `scripts/create_real_mapping.py` - Create real card mappings
  - `scripts/read_excel_mapping.py` - Excel mapping utilities

- **Debugging & Fixes**
  - `scripts/debug_excel_keys.py` - Debug Excel key issues
  - `scripts/fix_class_mapping.py` - Fix class mapping issues
  - `scripts/fix_class_mapping_correct.py` - Corrected class mapping

#### Testing & Validation Suite
- **Comprehensive Test Files** (moved to `tests/`)
  - `test_annotations.py` - Annotation validation
  - `test_detection_prices.py` - Price detection testing
  - `test_full_chain.py` - End-to-end pipeline testing
  - `test_mapping_debug.py` - Mapping system debugging
  - `test_autobalancer_performance.py` - Auto-balancer benchmarking
  - `test_holographic_performance.py` - Holographic effects testing
  - `test_mosaic_performance.py` - Mosaic generation benchmarking
  
- **Visualization Tools**
  - `visualize_annotations.py` - Visual annotation inspection
  - `visualize_bbox.py` - Bounding box visualization
  
- **Verification Scripts**
  - `verify_data_yaml.py` - Data.yaml validation
  - `verify_detailed.py` - Detailed dataset verification
  - `check_corrupted_images.py` - Image integrity checking

#### Workflow Optimization
- **Optimized Workflow** (`scripts/workflow_optimized.py`)
  - Streamlined pipeline execution
  - Performance improvements
  - Better error handling
  
- **Dataset Management**
  - `scripts/merge_dataset.py` - Dataset merging capabilities
  - Improved dataset organization

### 🔧 Changed

#### Core Module Improvements
- Enhanced `core/augmentation.py` with better error handling
- Improved `core/detection_manager.py` with price integration
- Updated `core/holographic_augmenter.py` for better performance
- Optimized `core/mosaic.py` and `core/mosaic_optimized.py`
- Enhanced `core/random_erasing.py` with new patterns
- Improved `core/training_manager.py` with better logging
- Updated `core/utils.py` with price loading utilities
- Enhanced `core/workflow_manager.py` for better orchestration

#### GUI Enhancements
- Updated `GUI_v3.1_modern.py` with new features
- Enhanced price detection integration in GUI
- Improved configuration management (`gui_config.json`)

### 🗂️ Project Reorganization

#### New Directory Structure
- **`tests/`** - All test and verification scripts
- **`scripts/`** - Utility and initialization scripts
- **`docs/migration/`** - Migration guides and historical documentation
- **`.backups/`** - Project backups (gitignored)

#### Moved Files
- Test files: `test_*.py` → `tests/`
- Visualization: `visualize_*.py` → `tests/`
- Verification: `verify_*.py`, `check_*.py` → `tests/`
- Init scripts: `init_*.py` → `scripts/`
- Utilities: `create_*.py`, `debug_*.py`, `fix_*.py` → `scripts/`
- Workflow: `workflow_optimized.py` → `scripts/`
- Migration docs: `GUIDE_MIGRATION.md`, etc. → `docs/migration/`
- GPU support: `RTX_5070_GPU_SUPPORT.md` → `docs/`

### 🧹 Removed

#### Cleaned Up Files
- Old backup directories (moved to `.backups/`)
- Temporary detection screenshots
- Generated validation reports
- Obsolete dataset exports (COCO, Roboflow)

#### Updated .gitignore
- Added `runs/` - YOLO training outputs
- Added `augmented/`, `augment/` - Generated augmented images
- Added `backup_*/` - Backup directories
- Added `output/holographic/`, `output/yolov8_test/` - Test outputs
- Added `.backups/` - Local backups
- Added `*.cache` - Cache files

### 📚 Documentation

#### New Documentation
- **CHANGELOG.md** - This file, comprehensive project history
- **docs/FEATURES.md** - Detailed feature documentation

#### Updated Documentation
- **README.md** - Updated with new features and organization
- **HELP.md** - Enhanced with price detection and mapping info

### 🐛 Bug Fixes
- Fixed class mapping inconsistencies
- Resolved Excel key matching issues
- Improved error handling in price detection
- Fixed holographic augmentation edge cases

---

## [3.0.0] - 2025-11-08

### Added
- Complete GUI v3.0 with modern interface
- TCGdex API integration for card downloads and prices
- Holographic augmentation effects
- Workflow manager with custom pipelines
- YOLOv8/YOLO11 training integration
- Live detection (webcam/video/image)
- Multi-format dataset export (COCO, VOC, TFRecord, Roboflow)
- Comprehensive settings system with 6 tabs
- Auto-balancing for dataset optimization

### Changed
- Complete UI redesign with modern aesthetics
- Improved mosaic generation with 3 modes
- Enhanced augmentation with 22+ transformation types
- Better error handling and logging

---

## [2.0.0] - 2025-10

### Added
- Initial YOLO pipeline implementation
- Basic augmentation system
- Mosaic generation
- TCGdex API support

### Changed
- Major architecture refactoring
- Improved code organization

---

## [1.0.0] - Initial Release

### Added
- Basic dataset generation
- Simple augmentation
- Command-line interface

---

## 🔗 Links

- **Repository**: https://github.com/lo26lo/pok
- **Documentation**: [HELP.md](HELP.md)
- **Features**: [docs/FEATURES.md](docs/FEATURES.md)
- **TCGdex Integration**: [docs/INTEGRATION_TCGDEX.md](docs/INTEGRATION_TCGDEX.md)

---

## 📝 Notes

### Version Numbering
- **Major** (X.0.0): Breaking changes, major features
- **Minor** (x.X.0): New features, backwards compatible
- **Patch** (x.x.X): Bug fixes, minor improvements

### Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerabilities
