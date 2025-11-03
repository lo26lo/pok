#!/usr/bin/env python3
"""
Script pour créer un executable Windows (.exe) du Pokemon Dataset Generator
Utilise PyInstaller pour empaqueter l'application complète

⚠️ Ce script doit être exécuté depuis la RACINE du projet :
   cd C:\\Users\\...\\Pokemons
   python tools\\create_exe.py
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_working_directory():
    """Vérifie qu'on est dans le bon répertoire"""
    if not os.path.exists("GUI_v3_modern.py"):
        print("❌ Erreur : GUI_v3_modern.py non trouvé")
        print("\n⚠️  Ce script doit être exécuté depuis la RACINE du projet :")
        print("   cd C:\\Users\\...\\Pokemons")
        print("   python tools\\create_exe.py")
        return False
    return True

def check_pyinstaller():
    """Vérifie si PyInstaller est installé"""
    try:
        import PyInstaller
        print("✅ PyInstaller est installé")
        return True
    except ImportError:
        print("❌ PyInstaller n'est pas installé")
        print("\n📦 Installation de PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installé avec succès")
            return True
        except:
            print("❌ Erreur lors de l'installation de PyInstaller")
            return False

def clean_build_folders():
    """Nettoie les dossiers de build précédents"""
    folders_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    print("\n🧹 Nettoyage des fichiers de build précédents...")
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"   Supprimé : {folder}/")
            except:
                print(f"   ⚠️  Impossible de supprimer : {folder}/")
    
    for pattern in files_to_clean:
        for file in Path('.').glob(pattern):
            try:
                file.unlink()
                print(f"   Supprimé : {file}")
            except:
                print(f"   ⚠️  Impossible de supprimer : {file}")

def create_exe():
    """Crée l'executable avec PyInstaller"""
    print("\n🔨 Création de l'executable...")
    print("⏳ Cela peut prendre plusieurs minutes...\n")
    
    # Options PyInstaller
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=Pokemon_Dataset_Generator",
        "--onefile",                    # Un seul fichier exe
        "--windowed",                   # Pas de console (mode GUI)
        "--icon=NONE",                  # Pas d'icône (ou spécifiez un .ico)
        "--add-data=excel/cards_info.xlsx;excel", # Inclure le fichier Excel
        "--add-data=gui_config.json;.", # Inclure la config (si existe)
        "--hidden-import=cv2",
        "--hidden-import=pandas",
        "--hidden-import=numpy",
        "--hidden-import=imgaug",
        "--hidden-import=PIL",
        "--hidden-import=openpyxl",
        "--hidden-import=tkinter",
        "--collect-all=imgaug",
        "--collect-all=imagecorruptions",
    ]
    
    # Ajouter l'icône Pikachu si elle existe
    if os.path.exists("pikachu.ico"):
        cmd.append("--icon=pikachu.ico")
        print("   🎨 Icône Pikachu détectée et ajoutée !")
    
    cmd.append("GUI_v3_modern.py")
    
    try:
        subprocess.check_call(cmd)
        print("\n✅ Executable créé avec succès !")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors de la création de l'executable : {e}")
        return False

def create_portable_package():
    """Crée un package portable avec l'exe et les fichiers nécessaires"""
    print("\n📦 Création du package portable...")
    
    package_name = "Pokemon_Dataset_Generator_Portable"
    package_dir = Path("dist") / package_name
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copier l'exe
    exe_source = Path("dist") / "Pokemon_Dataset_Generator.exe"
    if exe_source.exists():
        shutil.copy(exe_source, package_dir / "Pokemon_Dataset_Generator.exe")
        print(f"   ✅ Copié : Pokemon_Dataset_Generator.exe")
    
    # Créer les dossiers nécessaires
    folders = ["images", "output", "examples", "fakeimg", "fakeimg_augmented"]
    for folder in folders:
        (package_dir / folder).mkdir(exist_ok=True)
        # Ajouter un .gitkeep
        (package_dir / folder / ".gitkeep").write_text("")
        print(f"   ✅ Créé : {folder}/")
    
    # Copier les fichiers essentiels
    files_to_copy = [
        "excel/cards_info.xlsx",
        "README.md",
        "requirements.txt"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy(file, package_dir / file)
            print(f"   ✅ Copié : {file}")
    
    # Créer un README pour le package
    readme_content = """# Pokemon Dataset Generator - Version Portable

## 🚀 Lancement Rapide

Double-cliquez sur : **Pokemon_Dataset_Generator.exe**

## 📂 Structure

- **Pokemon_Dataset_Generator.exe** : Application principale
- **images/** : Placez vos cartes Pokemon ici (format: SSP_XXX_*.png)
- **cards_info.xlsx** : Fichier Excel avec les informations des cartes
- **output/** : Dossiers de sortie (générés automatiquement)
  - augmented/ : Images augmentées
  - yolov8/ : Mosaïques et annotations YOLO
- **fakeimg/** : Fausses cartes (générées)
- **fakeimg_augmented/** : Fausses cartes augmentées (générées)

## 📖 Documentation

Voir README.md pour la documentation complète.

## ⚠️ Note

Cette version portable inclut toutes les dépendances nécessaires.
Aucune installation de Python requise !

## 🐛 Résolution de Problèmes

Si l'application ne démarre pas :
1. Vérifiez que cards_info.xlsx est présent
2. Assurez-vous d'avoir des droits d'écriture dans le dossier
3. Consultez README.md pour plus d'informations

Version : 2.0.1
"""
    
    (package_dir / "README_PORTABLE.txt").write_text(readme_content, encoding='utf-8')
    print(f"   ✅ Créé : README_PORTABLE.txt")
    
    print(f"\n✅ Package portable créé dans : {package_dir}/")
    print(f"\n📦 Vous pouvez zipper ce dossier pour distribution")

def main():
    print("=" * 60)
    print(" 🎮 Pokemon Dataset Generator - Création d'Executable")
    print("=" * 60)
    print()
    
    # Vérifier qu'on est dans le bon dossier
    if not os.path.exists("GUI_v3_modern.py"):
        print("❌ Erreur : GUI_v3_modern.py non trouvé")
        print("   Lancez ce script depuis le dossier Pokemons/")
        input("\nAppuyez sur Entrée pour quitter...")
        return
    
    # Vérifier le répertoire de travail
    if not check_working_directory():
        input("\nAppuyez sur Entrée pour quitter...")
        return
    
    # Vérifier/Installer PyInstaller
    if not check_pyinstaller():
        input("\nAppuyez sur Entrée pour quitter...")
        return
    
    # Nettoyer les builds précédents
    clean_build_folders()
    
    # Créer l'executable
    if not create_exe():
        input("\nAppuyez sur Entrée pour quitter...")
        return
    
    # Créer le package portable
    create_portable_package()
    
    print("\n" + "=" * 60)
    print(" ✅ TERMINÉ !")
    print("=" * 60)
    print()
    print("📂 Fichiers générés :")
    print("   - dist/Pokemon_Dataset_Generator.exe (executable seul)")
    print("   - dist/Pokemon_Dataset_Generator_Portable/ (package complet)")
    print()
    print("💡 Conseil : Testez l'executable avant distribution")
    print()
    
    input("Appuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
