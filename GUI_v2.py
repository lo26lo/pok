#!/usr/bin/env python3
"""
GUI Modernisé pour la génération de Dataset Pokémon
Version 2.0.1 - Interface améliorée avec settings, progression, validation et utilitaires API
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import sys
import os
import json
import threading
import time
from pathlib import Path
from datetime import datetime

class PokemonDatasetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokemon Dataset Generator v2.0.1")
        self.root.geometry("1000x700")
        
        # Définir l'icône Pikachu si elle existe
        if os.path.exists("pikachu.ico"):
            try:
                self.root.iconbitmap("pikachu.ico")
            except Exception as e:
                print(f"⚠️ Impossible de charger l'icône : {e}")
        
        # Configuration par défaut
        self.config_file = "gui_config.json"
        self.load_config()
        
        # Variables pour le threading
        self.current_process = None
        self.is_running = False
        
        # Créer l'interface
        self.create_menu()
        self.create_main_interface()
        
    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        default_config = {
            "paths": {
                "images_source": "images",
                "fakeimg": "fakeimg",
                "output_augmented": os.path.join("output", "augmented"),
                "output_mosaic": os.path.join("output", "yolov8"),
                "excel_file": "cards_info.xlsx"
            },
            "last_used": {
                "num_aug": 15,
                "target": "augmented",
                "layout_mode": 1,
                "background_mode": 0,
                "transform_mode": 0,
                "random_erasing_p": 0.2
            },
            "theme": "light"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge avec les valeurs par défaut
                    for key in default_config:
                        if key not in loaded:
                            loaded[key] = default_config[key]
                    self.config = loaded
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Sauvegarde la configuration dans le fichier JSON"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def create_menu(self):
        """Créer la barre de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir dossier Images", command=lambda: self.open_folder("images_source"))
        file_menu.add_command(label="Ouvrir dossier Output", command=lambda: self.open_folder("output_augmented"))
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Nettoyer Output", command=self.clean_output)
        tools_menu.add_command(label="Diagnostiquer Environnement", command=self.diagnose_env)
        tools_menu.add_command(label="Réinstaller Dépendances", command=self.reinstall_deps)
        
        # Menu Settings
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Chemins et Configuration", command=self.open_settings)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Guide d'utilisation", command=self.open_guide)
        help_menu.add_command(label="À propos", command=self.show_about)
    
    def create_main_interface(self):
        """Créer l'interface principale avec onglets"""
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurer le redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Titre et statut en haut
        self.create_header(main_frame)
        
        # Notebook (onglets)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Créer les onglets
        self.create_dashboard_tab()
        self.create_augmentation_tab()
        self.create_mosaic_tab()
        self.create_fakeimg_tab()
        self.create_utilities_tab()
        self.create_logs_tab()
        
        # Barre de progression en bas
        self.create_progress_bar(main_frame)
    
    def create_header(self, parent):
        """Créer l'en-tête avec titre et statut"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title = ttk.Label(header_frame, text="🎮 Pokemon Dataset Generator", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, sticky=tk.W)
        
        self.status_label = ttk.Label(header_frame, text="✅ Prêt", 
                                     font=('Arial', 10))
        self.status_label.grid(row=0, column=1, sticky=tk.E)
        header_frame.columnconfigure(1, weight=1)
    
    def create_progress_bar(self, parent):
        """Créer la barre de progression"""
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate', length=300)
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.grid(row=0, column=1)
        
        self.cancel_button = ttk.Button(progress_frame, text="Annuler", 
                                       command=self.cancel_operation, state=tk.DISABLED)
        self.cancel_button.grid(row=0, column=2, padx=(10, 0))
        
        progress_frame.columnconfigure(0, weight=1)
    
    def create_dashboard_tab(self):
        """Onglet Dashboard avec statistiques"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="📊 Dashboard")
        
        # Statistiques
        stats_frame = ttk.LabelFrame(tab, text="Statistiques", padding="10")
        stats_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.stat_labels = {}
        stats = [
            ("images_source", "Images sources"),
            ("fakeimg", "Fausses cartes"),
            ("augmented", "Images augmentées"),
            ("mosaic", "Mosaïques générées")
        ]
        
        for i, (key, label) in enumerate(stats):
            ttk.Label(stats_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            self.stat_labels[key] = ttk.Label(stats_frame, text="Calcul...", 
                                             font=('Arial', 10, 'bold'))
            self.stat_labels[key].grid(row=i, column=1, sticky=tk.W, padx=20)
        
        ttk.Button(stats_frame, text="🔄 Actualiser", 
                  command=self.update_statistics).grid(row=len(stats), column=0, 
                                                       columnspan=2, pady=10)
        
        # Actions rapides
        actions_frame = ttk.LabelFrame(tab, text="Actions Rapides", padding="10")
        actions_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(actions_frame, text="📁 Ouvrir dossier Images", 
                  command=lambda: self.open_folder("images_source")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(actions_frame, text="📊 Ouvrir Excel", 
                  command=self.open_excel).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(actions_frame, text="🗑️ Nettoyer Output", 
                  command=self.clean_output).grid(row=0, column=2, padx=5, pady=5)
        
        # Workflow complet
        workflow_frame = ttk.LabelFrame(tab, text="Workflow Complet", padding="10")
        workflow_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(workflow_frame, text="Lancer le workflow complet automatique:").grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Button(workflow_frame, text="▶️ Démarrer Workflow", 
                  command=self.run_complete_workflow, 
                  style='Accent.TButton').grid(row=1, column=0, columnspan=2, pady=5)
        
        self.update_statistics()
    
    def create_augmentation_tab(self):
        """Onglet Augmentation"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🎨 Augmentation")
        
        # Frame principal
        main = ttk.Frame(tab)
        main.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Validation
        validation_frame = ttk.LabelFrame(main, text="✓ Validation", padding="10")
        validation_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.aug_validation_label = ttk.Label(validation_frame, text="Vérification...")
        self.aug_validation_label.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(validation_frame, text="🔄 Vérifier", 
                  command=self.validate_augmentation).grid(row=0, column=1, padx=10)
        
        # Paramètres de base
        params_frame = ttk.LabelFrame(main, text="Paramètres", padding="10")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(params_frame, text="Nombre d'augmentations:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.num_aug_var = tk.IntVar(value=self.config["last_used"]["num_aug"])
        num_aug_spin = ttk.Spinbox(params_frame, from_=1, to=200, textvariable=self.num_aug_var, width=10)
        num_aug_spin.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(params_frame, text="Dossier cible:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_var = tk.StringVar(value=self.config["last_used"]["target"])
        ttk.Radiobutton(params_frame, text="augmented", variable=self.target_var, 
                       value="augmented").grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(params_frame, text="images_aug", variable=self.target_var, 
                       value="images_aug").grid(row=1, column=2, sticky=tk.W)
        
        # Presets
        preset_frame = ttk.LabelFrame(main, text="⚡ Presets", padding="10")
        preset_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(preset_frame, text="Rapide (5)", 
                  command=lambda: self.num_aug_var.set(5)).grid(row=0, column=0, padx=5)
        ttk.Button(preset_frame, text="Standard (15)", 
                  command=lambda: self.num_aug_var.set(15)).grid(row=0, column=1, padx=5)
        ttk.Button(preset_frame, text="Intensif (100)", 
                  command=lambda: self.num_aug_var.set(100)).grid(row=0, column=2, padx=5)
        
        # Bouton de lancement
        ttk.Button(main, text="▶️ Lancer l'Augmentation", 
                  command=self.launch_augmentation,
                  style='Accent.TButton').grid(row=3, column=0, pady=20)
        
        self.validate_augmentation()
    
    def create_mosaic_tab(self):
        """Onglet Mosaïques"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🧩 Mosaïques")
        
        # Validation
        validation_frame = ttk.LabelFrame(tab, text="✓ Validation", padding="10")
        validation_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.mosaic_validation_label = ttk.Label(validation_frame, text="Vérification...")
        self.mosaic_validation_label.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(validation_frame, text="🔄 Vérifier", 
                  command=self.validate_mosaic).grid(row=0, column=1, padx=10)
        
        # Paramètres
        params_frame = ttk.LabelFrame(tab, text="Paramètres", padding="10")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Layout Mode
        ttk.Label(params_frame, text="Layout Mode:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.layout_mode_var = tk.IntVar(value=self.config["last_used"]["layout_mode"])
        layout_frame = ttk.Frame(params_frame)
        layout_frame.grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(layout_frame, text="1: Grille", variable=self.layout_mode_var, value=1).pack(side=tk.LEFT)
        ttk.Radiobutton(layout_frame, text="2: Rotation forte", variable=self.layout_mode_var, value=2).pack(side=tk.LEFT)
        ttk.Radiobutton(layout_frame, text="3: Aléatoire", variable=self.layout_mode_var, value=3).pack(side=tk.LEFT)
        
        # Background Mode
        ttk.Label(params_frame, text="Background Mode:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.background_mode_var = tk.IntVar(value=self.config["last_used"]["background_mode"])
        bg_frame = ttk.Frame(params_frame)
        bg_frame.grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(bg_frame, text="0: Mosaïque", variable=self.background_mode_var, value=0).pack(side=tk.LEFT)
        ttk.Radiobutton(bg_frame, text="1: Local", variable=self.background_mode_var, value=1).pack(side=tk.LEFT)
        ttk.Radiobutton(bg_frame, text="2: Web", variable=self.background_mode_var, value=2).pack(side=tk.LEFT)
        
        # Transform Mode
        ttk.Label(params_frame, text="Transform Mode:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.transform_mode_var = tk.IntVar(value=self.config["last_used"]["transform_mode"])
        trans_frame = ttk.Frame(params_frame)
        trans_frame.grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(trans_frame, text="0: Rotation 2D", variable=self.transform_mode_var, value=0).pack(side=tk.LEFT)
        ttk.Radiobutton(trans_frame, text="1: 3D Perspective", variable=self.transform_mode_var, value=1).pack(side=tk.LEFT)
        
        # Bouton de lancement
        ttk.Button(tab, text="▶️ Générer les Mosaïques", 
                  command=self.launch_mosaic,
                  style='Accent.TButton').grid(row=2, column=0, pady=20)
        
        self.validate_mosaic()
    
    def create_fakeimg_tab(self):
        """Onglet Gestion des Fausses Images"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🖼️ Fausses Cartes")
        
        # Info
        info_frame = ttk.LabelFrame(tab, text="ℹ️ Information", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        info_text = ("Les fausses cartes sont utilisées comme fond de mosaïque.\n"
                    "Elles sont copiées depuis le dossier Images puis modifiées avec Random Erasing.")
        ttk.Label(info_frame, text=info_text, wraplength=400).pack()
        
        # Paramètres
        params_frame = ttk.LabelFrame(tab, text="Paramètres", padding="10")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(params_frame, text="Nombre de cartes à copier:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.fake_count_var = tk.IntVar(value=20)
        ttk.Scale(params_frame, from_=10, to=50, variable=self.fake_count_var, 
                 orient=tk.HORIZONTAL, length=200).grid(row=0, column=1, sticky=tk.W, padx=10)
        self.fake_count_label = ttk.Label(params_frame, text="20")
        self.fake_count_label.grid(row=0, column=2)
        self.fake_count_var.trace_add("write", lambda *args: self.fake_count_label.config(
            text=str(int(self.fake_count_var.get()))))
        
        self.apply_erasing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Appliquer Random Erasing", 
                       variable=self.apply_erasing_var).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(params_frame, text="Probabilité d'effacement (p):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.erasing_p_var = tk.DoubleVar(value=self.config["last_used"]["random_erasing_p"])
        ttk.Scale(params_frame, from_=0.0, to=1.0, variable=self.erasing_p_var, 
                 orient=tk.HORIZONTAL, length=200).grid(row=2, column=1, sticky=tk.W, padx=10)
        self.erasing_p_label = ttk.Label(params_frame, text="0.2")
        self.erasing_p_label.grid(row=2, column=2)
        self.erasing_p_var.trace_add("write", lambda *args: self.erasing_p_label.config(
            text=f"{self.erasing_p_var.get():.2f}"))
        
        # Bouton de lancement
        ttk.Button(tab, text="▶️ Générer les Fausses Cartes", 
                  command=self.launch_fakeimg_generation,
                  style='Accent.TButton').grid(row=2, column=0, pady=20)
    
    def create_utilities_tab(self):
        """Onglet Utilitaires - API Pokémon TCG"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🔧 Utilitaires")
        
        # Section 1: Générer Excel depuis API
        generate_frame = ttk.LabelFrame(tab, text="📋 Générer Liste de Cartes depuis API", padding="10")
        generate_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(generate_frame, text="Nom de l'extension:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.extension_var = tk.StringVar(value="Surging Sparks")
        ttk.Entry(generate_frame, textvariable=self.extension_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(generate_frame, text="Fichier de sortie:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.extension_output_var = tk.StringVar(value="extension_cards.xlsx")
        output_frame = ttk.Frame(generate_frame)
        output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Entry(output_frame, textvariable=self.extension_output_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="📁", width=3, command=lambda: self.browse_file(self.extension_output_var, save=True)).pack(side=tk.LEFT, padx=(5, 0))
        
        info_text = "Récupère toutes les cartes d'une extension depuis l'API Pokémon TCG\net génère un fichier Excel avec 'Set #' et 'Name'."
        ttk.Label(generate_frame, text=info_text, font=('Arial', 9, 'italic'), foreground='gray').grid(row=2, column=0, columnspan=2, pady=(5, 10))
        
        ttk.Button(generate_frame, text="▶️ Générer Excel", 
                  command=self.generate_extension_excel).grid(row=3, column=0, columnspan=2, pady=5)
        
        generate_frame.columnconfigure(1, weight=1)
        
        # Section 2: Mettre à jour les prix
        price_frame = ttk.LabelFrame(tab, text="💰 Mettre à Jour les Prix des Cartes", padding="10")
        price_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(price_frame, text="Fichier Excel d'entrée:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.price_input_var = tk.StringVar(value="cards_info.xlsx")
        input_frame = ttk.Frame(price_frame)
        input_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Entry(input_frame, textvariable=self.price_input_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="📁", width=3, command=lambda: self.browse_file(self.price_input_var)).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(price_frame, text="Fichier Excel de sortie:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.price_output_var = tk.StringVar(value="cards_info_updated.xlsx")
        output_frame2 = ttk.Frame(price_frame)
        output_frame2.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Entry(output_frame2, textvariable=self.price_output_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame2, text="📁", width=3, command=lambda: self.browse_file(self.price_output_var, save=True)).pack(side=tk.LEFT, padx=(5, 0))
        
        info_text2 = "Lit un fichier Excel avec colonnes 'Set #', 'Name', 'Set'\net ajoute les colonnes 'Prix' et 'Prix max' depuis l'API."
        ttk.Label(price_frame, text=info_text2, font=('Arial', 9, 'italic'), foreground='gray').grid(row=2, column=0, columnspan=2, pady=(5, 10))
        
        ttk.Button(price_frame, text="▶️ Mettre à Jour les Prix", 
                  command=self.update_card_prices).grid(row=3, column=0, columnspan=2, pady=5)
        
        price_frame.columnconfigure(1, weight=1)
        
        # Section 3: Recherche rapide
        search_frame = ttk.LabelFrame(tab, text="🔍 Recherche Rapide de Carte", padding="10")
        search_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(search_frame, text="Nom de la carte:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.search_name_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_name_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(search_frame, text="Numéro (optionnel):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.search_number_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_number_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(search_frame, text="Set (optionnel):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.search_set_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_set_var, width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(search_frame, text="🔍 Rechercher Prix", 
                  command=self.search_card_price).grid(row=3, column=0, columnspan=2, pady=10)
        
        search_frame.columnconfigure(1, weight=1)
        
        tab.columnconfigure(0, weight=1)
    
    def create_logs_tab(self):
        """Onglet Logs"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="📝 Logs")
        
        # Toolbar
        toolbar = ttk.Frame(tab)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(toolbar, text="🗑️ Effacer", 
                  command=lambda: self.log_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📋 Copier", 
                  command=self.copy_logs).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="💾 Sauvegarder", 
                  command=self.save_logs).pack(side=tk.LEFT, padx=2)
        
        # Zone de texte avec scrollbar
        self.log_text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, width=80, height=30)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        
        self.log("✅ Interface initialisée")
    
    # === Méthodes Settings ===
    
    def open_settings(self):
        """Ouvrir la fenêtre de configuration"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Settings - Configuration")
        settings_window.geometry("600x500")
        
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet Chemins
        paths_tab = ttk.Frame(notebook, padding="10")
        notebook.add(paths_tab, text="📁 Chemins")
        
        paths = [
            ("images_source", "Dossier Images Sources"),
            ("fakeimg", "Dossier Fausses Cartes"),
            ("output_augmented", "Sortie Augmentation"),
            ("output_mosaic", "Sortie Mosaïques"),
            ("excel_file", "Fichier Excel")
        ]
        
        self.path_entries = {}
        for i, (key, label) in enumerate(paths):
            ttk.Label(paths_tab, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(paths_tab, width=40)
            entry.insert(0, self.config["paths"][key])
            entry.grid(row=i, column=1, padx=5)
            self.path_entries[key] = entry
            
            ttk.Button(paths_tab, text="📂", 
                      command=lambda k=key, e=entry: self.browse_path(k, e)).grid(row=i, column=2)
        
        # Boutons
        button_frame = ttk.Frame(paths_tab)
        button_frame.grid(row=len(paths), column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="💾 Sauvegarder", 
                  command=lambda: self.save_settings(settings_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Réinitialiser", 
                  command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Annuler", 
                  command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def browse_path(self, key, entry):
        """Choisir un chemin"""
        if "file" in key:
            path = filedialog.askopenfilename(title=f"Choisir {key}")
        else:
            path = filedialog.askdirectory(title=f"Choisir {key}")
        
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)
    
    def save_settings(self, window):
        """Sauvegarder les settings"""
        for key, entry in self.path_entries.items():
            self.config["paths"][key] = entry.get()
        
        self.save_config()
        self.log("✅ Configuration sauvegardée")
        messagebox.showinfo("Succès", "Configuration sauvegardée avec succès!")
        window.destroy()
        self.update_statistics()
    
    def reset_settings(self):
        """Réinitialiser aux valeurs par défaut"""
        if messagebox.askyesno("Confirmation", "Réinitialiser tous les paramètres ?"):
            os.remove(self.config_file)
            self.load_config()
            self.log("🔄 Configuration réinitialisée")
            messagebox.showinfo("Succès", "Paramètres réinitialisés!")
    
    # === Méthodes de validation ===
    
    def validate_augmentation(self):
        """Valider les prérequis pour l'augmentation"""
        images_path = self.config["paths"]["images_source"]
        issues = []
        
        if not os.path.exists(images_path):
            issues.append(f"❌ Dossier {images_path} n'existe pas")
        else:
            count = len([f for f in os.listdir(images_path) 
                        if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
            if count == 0:
                issues.append(f"❌ Aucune image dans {images_path}")
            else:
                issues.append(f"✅ {count} images trouvées")
        
        excel_path = self.config["paths"]["excel_file"]
        if not os.path.exists(excel_path):
            issues.append(f"⚠️ Fichier Excel {excel_path} non trouvé")
        else:
            issues.append(f"✅ Fichier Excel OK")
        
        self.aug_validation_label.config(text=" | ".join(issues))
    
    def validate_mosaic(self):
        """Valider les prérequis pour les mosaïques"""
        augmented_path = os.path.join(self.config["paths"]["output_augmented"], "images")
        fakeimg_path = self.config["paths"]["fakeimg"]
        issues = []
        
        if not os.path.exists(augmented_path):
            issues.append(f"❌ Aucune image augmentée (lancer augmentation d'abord)")
        else:
            count = len([f for f in os.listdir(augmented_path) 
                        if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
            if count == 0:
                issues.append(f"❌ Dossier augmented vide")
            else:
                issues.append(f"✅ {count} images augmentées")
        
        if not os.path.exists(fakeimg_path):
            issues.append(f"⚠️ Dossier fakeimg non trouvé")
        else:
            count = len([f for f in os.listdir(fakeimg_path) 
                        if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
            if count == 0:
                issues.append(f"⚠️ Aucune fausse carte")
            else:
                issues.append(f"✅ {count} fausses cartes")
        
        self.mosaic_validation_label.config(text=" | ".join(issues))
    
    # === Méthodes de lancement ===
    
    def launch_augmentation(self):
        """Lancer l'augmentation dans un thread"""
        if self.is_running:
            messagebox.showwarning("Attention", "Une opération est déjà en cours!")
            return
        
        # Sauvegarder les paramètres
        self.config["last_used"]["num_aug"] = self.num_aug_var.get()
        self.config["last_used"]["target"] = self.target_var.get()
        self.save_config()
        
        num_aug = self.num_aug_var.get()
        target = self.target_var.get()
        
        self.log(f"▶️ Lancement augmentation: {num_aug} augmentations, cible={target}")
        
        cmd = [
            sys.executable, "augmentation.py",
            "--num_aug", str(num_aug),
            "--target", target
        ]
        
        thread = threading.Thread(target=self.run_command, args=(cmd, "Augmentation"))
        thread.start()
    
    def launch_mosaic(self):
        """Lancer la génération de mosaïques"""
        if self.is_running:
            messagebox.showwarning("Attention", "Une opération est déjà en cours!")
            return
        
        # Sauvegarder les paramètres
        self.config["last_used"]["layout_mode"] = self.layout_mode_var.get()
        self.config["last_used"]["background_mode"] = self.background_mode_var.get()
        self.config["last_used"]["transform_mode"] = self.transform_mode_var.get()
        self.save_config()
        
        layout = self.layout_mode_var.get()
        background = self.background_mode_var.get()
        transform = self.transform_mode_var.get()
        
        self.log(f"▶️ Lancement mosaïques: layout={layout}, bg={background}, transform={transform}")
        
        cmd = [
            sys.executable, "mosaic.py",
            str(layout), str(background), str(transform)
        ]
        
        thread = threading.Thread(target=self.run_command, args=(cmd, "Mosaïques"))
        thread.start()
    
    def launch_fakeimg_generation(self):
        """Générer les fausses cartes"""
        if self.is_running:
            messagebox.showwarning("Attention", "Une opération est déjà en cours!")
            return
        
        count = int(self.fake_count_var.get())
        apply_erasing = self.apply_erasing_var.get()
        p_value = self.erasing_p_var.get()
        
        self.config["last_used"]["random_erasing_p"] = p_value
        self.save_config()
        
        self.log(f"▶️ Génération de {count} fausses cartes (Random Erasing: {apply_erasing}, p={p_value})")
        
        def task():
            self.start_operation("Génération Fausses Cartes")
            
            # Copier les images
            import random
            import shutil
            
            images_path = self.config["paths"]["images_source"]
            fakeimg_path = self.config["paths"]["fakeimg"]
            
            os.makedirs(fakeimg_path, exist_ok=True)
            
            # Nettoyer fakeimg
            for f in os.listdir(fakeimg_path):
                os.remove(os.path.join(fakeimg_path, f))
            
            # Copier images aléatoires
            all_images = [f for f in os.listdir(images_path) 
                         if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
            
            if len(all_images) < count:
                self.log(f"⚠️ Seulement {len(all_images)} images disponibles")
                count = len(all_images)
            
            selected = random.sample(all_images, count)
            for img in selected:
                shutil.copy(os.path.join(images_path, img), 
                           os.path.join(fakeimg_path, img))
            
            self.log(f"✅ {count} images copiées dans fakeimg/")
            
            # Appliquer Random Erasing si demandé
            if apply_erasing:
                cmd = [
                    sys.executable, os.path.join("tools", "randomerasing.py"),
                    "--input_dir", fakeimg_path,
                    "--output_dir", "fakeimg_augmented",
                    "--p", str(p_value),
                    "--sh", "0.5"
                ]
                
                self.log(f"🎲 Application Random Erasing (p={p_value})...")
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE, text=True)
                
                stdout, stderr = process.communicate()
                
                if stdout:
                    self.log(stdout)
                if stderr:
                    self.log(f"⚠️ {stderr}")
                
                if process.returncode == 0:
                    self.log("✅ Random Erasing appliqué avec succès")
                else:
                    self.log(f"❌ Erreur lors du Random Erasing")
            
            self.end_operation()
            self.update_statistics()
        
        thread = threading.Thread(target=task)
        thread.start()
    
    def run_complete_workflow(self):
        """Exécuter le workflow complet"""
        if self.is_running:
            messagebox.showwarning("Attention", "Une opération est déjà en cours!")
            return
        
        response = messagebox.askyesno("Workflow Complet", 
                                      "Lancer le workflow complet ?\n\n"
                                      "1. Génération fausses cartes (20 cartes, p=0.8)\n"
                                      "2. Augmentation (15 images)\n"
                                      "3. Mosaïques (layout=1, bg=0, transform=0)")
        
        if not response:
            return
        
        def workflow():
            import random
            import shutil
            
            self.start_operation("Workflow Complet")
            
            try:
                # Étape 1: Fausses cartes
                self.log("📋 Étape 1/3: Génération fausses cartes...")
                
                images_path = self.config["paths"]["images_source"]
                fakeimg_path = self.config["paths"]["fakeimg"]
                count = 20
                p_value = 0.8
                
                os.makedirs(fakeimg_path, exist_ok=True)
                
                # Nettoyer fakeimg
                for f in os.listdir(fakeimg_path):
                    file_path = os.path.join(fakeimg_path, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                
                # Copier images aléatoires
                all_images = [f for f in os.listdir(images_path) 
                             if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                
                if len(all_images) < count:
                    self.log(f"⚠️ Seulement {len(all_images)} images disponibles")
                    count = len(all_images)
                
                selected = random.sample(all_images, count)
                for img in selected:
                    shutil.copy(os.path.join(images_path, img), 
                               os.path.join(fakeimg_path, img))
                
                self.log(f"✅ {count} images copiées dans fakeimg/")
                
                # Appliquer Random Erasing
                cmd = [
                    sys.executable, os.path.join("tools", "randomerasing.py"),
                    "--input_dir", fakeimg_path,
                    "--output_dir", "fakeimg_augmented",
                    "--p", str(p_value),
                    "--sh", "0.5"
                ]
                
                self.log(f"🎲 Application Random Erasing (p={p_value})...")
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                          stderr=subprocess.STDOUT, text=True)
                
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.log(line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.log("✅ Étape 1/3 terminée: Fausses cartes générées")
                else:
                    self.log(f"❌ Erreur lors de la génération des fausses cartes")
                    self.end_operation()
                    return
                
                # Étape 2: Augmentation
                self.log("\n📋 Étape 2/3: Augmentation...")
                cmd = [sys.executable, "augmentation.py", "--num_aug", "15", "--target", "augmented"]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                          stderr=subprocess.STDOUT, text=True)
                
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.log(line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.log("✅ Étape 2/3 terminée: Images augmentées")
                else:
                    self.log(f"❌ Erreur lors de l'augmentation")
                    self.end_operation()
                    return
                
                # Étape 3: Mosaïques
                self.log("\n📋 Étape 3/3: Mosaïques...")
                cmd = [sys.executable, "mosaic.py", "1", "0", "0"]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                          stderr=subprocess.STDOUT, text=True)
                
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.log(line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.log("✅ Étape 3/3 terminée: Mosaïques générées")
                else:
                    self.log(f"❌ Erreur lors de la génération des mosaïques")
                    self.end_operation()
                    return
                
                self.log("\n🎉 Workflow complet terminé avec succès!")
                messagebox.showinfo("Succès", "Workflow complet terminé!\n\nVérifiez les dossiers:\n- fakeimg/\n- output/augmented/\n- output/yolov8/")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Erreur lors du workflow: {str(e)}")
            
            finally:
                self.end_operation()
                self.update_statistics()
        
        thread = threading.Thread(target=workflow)
        thread.start()
    
    # === Méthodes utilitaires ===
    
    def run_command(self, cmd, operation_name):
        """Exécuter une commande dans un thread"""
        self.start_operation(operation_name)
        
        try:
            self.current_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            
            # Lire la sortie en temps réel
            for line in iter(self.current_process.stdout.readline, ''):
                if line:
                    self.log(line.strip())
            
            self.current_process.wait()
            
            if self.current_process.returncode == 0:
                self.log(f"✅ {operation_name} terminé avec succès!")
                messagebox.showinfo("Succès", f"{operation_name} terminé!")
            else:
                self.log(f"❌ {operation_name} a échoué (code {self.current_process.returncode})")
                messagebox.showerror("Erreur", f"{operation_name} a échoué!")
        
        except Exception as e:
            self.log(f"❌ Erreur: {str(e)}")
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
        
        finally:
            self.end_operation()
            self.update_statistics()
    
    def start_operation(self, name):
        """Démarrer une opération"""
        self.is_running = True
        self.status_label.config(text=f"⏳ En cours: {name}")
        self.progress.start()
        self.cancel_button.config(state=tk.NORMAL)
        self.progress_label.config(text=f"Exécution de {name}...")
    
    def end_operation(self):
        """Terminer une opération"""
        self.is_running = False
        self.status_label.config(text="✅ Prêt")
        self.progress.stop()
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_label.config(text="")
        self.current_process = None
    
    def cancel_operation(self):
        """Annuler l'opération en cours"""
        if self.current_process:
            self.current_process.terminate()
            self.log("🛑 Opération annulée par l'utilisateur")
            self.end_operation()
    
    def update_statistics(self):
        """Mettre à jour les statistiques"""
        def count_files(path):
            if not os.path.exists(path):
                return 0
            return len([f for f in os.listdir(path) 
                       if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
        
        stats = {
            "images_source": count_files(self.config["paths"]["images_source"]),
            "fakeimg": count_files(self.config["paths"]["fakeimg"]),
            "augmented": count_files(os.path.join(self.config["paths"]["output_augmented"], "images")),
            "mosaic": count_files(os.path.join(self.config["paths"]["output_mosaic"], "images"))
        }
        
        for key, value in stats.items():
            self.stat_labels[key].config(text=f"{value} images")
    
    def log(self, message):
        """Ajouter un message au log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def copy_logs(self):
        """Copier les logs dans le presse-papier"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_text.get(1.0, tk.END))
        messagebox.showinfo("Copié", "Logs copiés dans le presse-papier!")
    
    def save_logs(self):
        """Sauvegarder les logs dans un fichier"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt")],
            initialfile=f"gui_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log(f"💾 Logs sauvegardés: {filename}")
    
    # === Méthodes Utilitaires API ===
    
    def browse_file(self, var, save=False):
        """Parcourir pour choisir un fichier"""
        if save:
            filename = filedialog.asksaveasfilename(
                title="Choisir le fichier de sortie",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
        else:
            filename = filedialog.askopenfilename(
                title="Choisir un fichier",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
        
        if filename:
            var.set(filename)
    
    def generate_extension_excel(self):
        """Générer un fichier Excel depuis l'API pour une extension"""
        extension = self.extension_var.get().strip()
        output = self.extension_output_var.get().strip()
        
        if not extension:
            messagebox.showerror("Erreur", "Veuillez saisir le nom de l'extension!")
            return
        
        if not output:
            messagebox.showerror("Erreur", "Veuillez saisir le nom du fichier de sortie!")
            return
        
        self.log(f"📋 Génération de la liste pour l'extension: {extension}")
        
        def task():
            try:
                import requests
                import pandas as pd
                
                # URL de base de l'API Pokémon TCG
                BASE_URL = "https://api.pokemontcg.io/v2/cards"
                API_KEY = "d71261e0-202c-41a6-93a9-fdcb3a7f9790"
                HEADERS = {"X-Api-Key": API_KEY}
                
                cards = []
                page = 1
                pageSize = 100
                
                self.log(f"🌐 Récupération des cartes de l'extension '{extension}'...")
                
                while True:
                    params = {
                        "q": f'set.name:"{extension}"',
                        "page": page,
                        "pageSize": pageSize
                    }
                    response = requests.get(BASE_URL, headers=HEADERS, params=params)
                    
                    # Si erreur 404, c'est qu'on a atteint la fin des pages
                    if response.status_code == 404:
                        self.log(f"ℹ️ Fin de la pagination (page {page} non trouvée)")
                        break
                    
                    if response.status_code != 200:
                        self.log(f"❌ Erreur {response.status_code}: {response.text}")
                        messagebox.showerror("Erreur", f"Erreur API: {response.status_code}")
                        return
                    
                    data = response.json()
                    batch = data.get("data", [])
                    
                    if not batch:
                        break
                    
                    cards.extend(batch)
                    self.log(f"📥 Page {page}: {len(batch)} cartes récupérées (Total: {len(cards)})")
                    
                    if len(batch) < pageSize:
                        break
                    
                    page += 1
                
                if not cards:
                    self.log(f"❌ Aucune carte trouvée pour l'extension '{extension}'")
                    messagebox.showwarning("Attention", f"Aucune carte trouvée pour '{extension}'")
                    return
                
                # Créer le DataFrame
                rows = []
                for card in cards:
                    card_number = str(card.get("number", "")).zfill(3)
                    printed_total = card.get("set", {}).get("printedTotal", "")
                    set_number = f"{card_number}/{printed_total}" if printed_total else card_number
                    name = card.get("name", "")
                    rows.append({"Set #": set_number, "Name": name})
                
                df = pd.DataFrame(rows)
                df.to_excel(output, index=False)
                
                self.log(f"✅ Fichier généré: {output} ({len(cards)} cartes)")
                messagebox.showinfo("Succès", f"Fichier généré avec succès!\n{len(cards)} cartes trouvées.")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Une erreur est survenue:\n{str(e)}")
        
        thread = threading.Thread(target=task)
        thread.start()
    
    def update_card_prices(self):
        """Mettre à jour les prix des cartes dans un fichier Excel"""
        input_file = self.price_input_var.get().strip()
        output_file = self.price_output_var.get().strip()
        
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Erreur", f"Le fichier d'entrée '{input_file}' n'existe pas!")
            return
        
        if not output_file:
            messagebox.showerror("Erreur", "Veuillez saisir le nom du fichier de sortie!")
            return
        
        self.log(f"💰 Mise à jour des prix depuis: {input_file}")
        
        def task():
            try:
                import requests
                import pandas as pd
                import concurrent.futures
                
                BASE_URL = "https://api.pokemontcg.io/v2/cards"
                API_KEY = "d71261e0-202c-41a6-93a9-fdcb3a7f9790"
                HEADERS = {"X-Api-Key": API_KEY}
                
                # Cache pour éviter les requêtes répétées
                cache = {}
                
                def search_card(card_name, card_number=None, set_name=None, session=None):
                    """Rechercher une carte et retourner ses prix"""
                    # Clé de cache
                    cache_key = f"{card_name}_{card_number}_{set_name}"
                    if cache_key in cache:
                        return cache[cache_key]
                    
                    params = {"q": f'name:"{card_name}"'}
                    response = session.get(BASE_URL, params=params, headers=HEADERS)
                    
                    if response.status_code != 200:
                        return (None, None)
                    
                    data = response.json()
                    results = data.get("data", [])
                    
                    if not results:
                        return (None, None)
                    
                    selected_card = None
                    
                    # Filtrer par numéro
                    if card_number:
                        if "/" in card_number:
                            target_number = card_number.split('/')[0].lstrip("0")
                        else:
                            target_number = card_number.lstrip("0")
                        
                        for card in results:
                            if "number" in card and card["number"].lstrip("0") == target_number:
                                selected_card = card
                                break
                    
                    # Filtrer par set
                    if not selected_card and set_name:
                        matching = [c for c in results if c.get("set", {}).get("name", "").lower() == set_name.lower()]
                        if matching:
                            selected_card = matching[0]
                    
                    if not selected_card:
                        selected_card = results[0]
                    
                    # Extraire les prix
                    if "tcgplayer" in selected_card and "prices" in selected_card["tcgplayer"]:
                        prices = selected_card["tcgplayer"]["prices"]
                        default_price = None
                        
                        if "normal" in prices and "market" in prices["normal"]:
                            default_price = prices["normal"]["market"]
                        elif "holofoil" in prices and "market" in prices["holofoil"]:
                            default_price = prices["holofoil"]["market"]
                        
                        available_prices = []
                        for fmt, data in prices.items():
                            if "market" in data:
                                available_prices.append(data["market"])
                        
                        highest_price = max(available_prices) if available_prices else None
                        result = (default_price, highest_price)
                        cache[cache_key] = result  # Mettre en cache
                        return result
                    
                    result = (None, None)
                    cache[cache_key] = result
                    return result
                
                # Charger le fichier Excel
                df = pd.read_excel(input_file, engine="openpyxl")
                
                # Créer les colonnes si nécessaire
                if "Prix" not in df.columns:
                    df["Prix"] = None
                if "Prix max" not in df.columns:
                    df["Prix max"] = None
                if "Set" not in df.columns:
                    df["Set"] = None
                
                failed_logs = []
                total = len(df)
                processed = 0
                last_log_time = [0]  # Utiliser une liste pour la mutabilité
                
                def worker(index, row, session):
                    nonlocal processed
                    card_name = row["Name"]
                    card_number = row["Set #"]
                    set_name = row.get("Set", None)
                    
                    try:
                        result = search_card(card_name, card_number=card_number, set_name=set_name, session=session)
                        processed += 1
                        
                        # Logger toutes les 10 cartes ou toutes les 5 secondes
                        import time
                        current_time = time.time()
                        if processed % 10 == 0 or (current_time - last_log_time[0]) >= 5:
                            self.log(f"📊 Progression: {processed}/{total} cartes ({int(processed/total*100)}%)")
                            last_log_time[0] = current_time
                        
                        return index, result
                    except Exception as e:
                        processed += 1
                        return index, (None, None), str(e)
                
                self.log(f"🔄 Traitement de {total} cartes avec 10 workers parallèles...")
                
                import time
                start_time = time.time()
                
                with requests.Session() as session:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                        futures = {
                            executor.submit(worker, idx, row, session): idx
                            for idx, row in df.iterrows()
                        }
                        
                        for future in concurrent.futures.as_completed(futures):
                            idx = futures[future]
                            try:
                                result_tuple = future.result()
                                
                                if len(result_tuple) == 3:
                                    index, (price, highest_price), error_msg = result_tuple
                                    failed_logs.append((df.at[index, "Name"], df.at[index, "Set #"], error_msg))
                                else:
                                    index, (price, highest_price) = result_tuple
                                    
                                    if price is not None:
                                        df.at[index, "Prix"] = price
                                    else:
                                        failed_logs.append((df.at[index, "Name"], df.at[index, "Set #"], "Prix non trouvé"))
                                    
                                    if highest_price is not None:
                                        df.at[index, "Prix max"] = highest_price
                            
                            except Exception as e:
                                failed_logs.append((df.at[idx, "Name"], df.at[idx, "Set #"], str(e)))
                
                elapsed = time.time() - start_time
                avg_time = elapsed / total if total > 0 else 0
                
                # Sauvegarder
                df.to_excel(output_file, index=False)
                
                self.log(f"✅ Fichier généré: {output_file}")
                self.log(f"⏱️ Temps total: {elapsed:.1f}s ({avg_time:.2f}s/carte)")
                
                if failed_logs:
                    self.log(f"⚠️ {len(failed_logs)} cartes avec erreurs:")
                    for card, num, error in failed_logs[:5]:
                        self.log(f"  - {card} ({num}): {error}")
                    if len(failed_logs) > 5:
                        self.log(f"  ... et {len(failed_logs) - 5} autres")
                
                messagebox.showinfo("Succès", 
                    f"Mise à jour terminée!\n"
                    f"Fichier: {output_file}\n"
                    f"Succès: {total - len(failed_logs)}/{total}\n"
                    f"Erreurs: {len(failed_logs)}")
            
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Une erreur est survenue:\n{str(e)}")
        
        thread = threading.Thread(target=task)
        thread.start()
    
    def search_card_price(self):
        """Rechercher le prix d'une carte spécifique"""
        card_name = self.search_name_var.get().strip()
        card_number = self.search_number_var.get().strip() or None
        set_name = self.search_set_var.get().strip() or None
        
        if not card_name:
            messagebox.showerror("Erreur", "Veuillez saisir le nom de la carte!")
            return
        
        self.log(f"🔍 Recherche: {card_name}" + (f" ({card_number})" if card_number else ""))
        
        def task():
            try:
                import requests
                
                BASE_URL = "https://api.pokemontcg.io/v2/cards"
                API_KEY = "d71261e0-202c-41a6-93a9-fdcb3a7f9790"
                HEADERS = {"X-Api-Key": API_KEY}
                
                params = {"q": f'name:"{card_name}"'}
                response = requests.get(BASE_URL, params=params, headers=HEADERS)
                
                if response.status_code != 200:
                    self.log(f"❌ Erreur API: {response.status_code}")
                    messagebox.showerror("Erreur", f"Erreur API: {response.status_code}")
                    return
                
                data = response.json()
                results = data.get("data", [])
                
                if not results:
                    self.log("❌ Aucun résultat trouvé")
                    messagebox.showwarning("Attention", "Aucune carte trouvée!")
                    return
                
                self.log(f"📋 {len(results)} résultat(s) trouvé(s)")
                
                selected_card = None
                
                # Filtrer par numéro
                if card_number:
                    target_number = card_number.split('/')[0].lstrip("0") if "/" in card_number else card_number.lstrip("0")
                    for card in results:
                        if "number" in card and card["number"].lstrip("0") == target_number:
                            selected_card = card
                            break
                
                # Filtrer par set
                if not selected_card and set_name:
                    matching = [c for c in results if c.get("set", {}).get("name", "").lower() == set_name.lower()]
                    if matching:
                        selected_card = matching[0]
                
                if not selected_card:
                    selected_card = results[0]
                
                card_info = f"Carte: {selected_card.get('name', 'N/A')}\n"
                card_info += f"Numéro: {selected_card.get('number', 'N/A')}\n"
                card_info += f"Set: {selected_card.get('set', {}).get('name', 'N/A')}\n\n"
                
                # Extraire les prix
                if "tcgplayer" in selected_card and "prices" in selected_card["tcgplayer"]:
                    prices = selected_card["tcgplayer"]["prices"]
                    card_info += "Prix TCGPlayer:\n"
                    
                    for fmt, data in prices.items():
                        if "market" in data:
                            card_info += f"  {fmt}: ${data['market']}\n"
                    
                    self.log(f"✅ Prix trouvés pour {selected_card.get('name')}")
                else:
                    card_info += "❌ Aucun prix disponible"
                    self.log("❌ Aucun prix trouvé")
                
                messagebox.showinfo("Résultat de la Recherche", card_info)
            
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Une erreur est survenue:\n{str(e)}")
        
        thread = threading.Thread(target=task)
        thread.start()
    
    # === Méthodes diverses ===
    
    def open_folder(self, key):
        """Ouvrir un dossier"""
        path = self.config["paths"][key]
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showwarning("Attention", f"Le dossier {path} n'existe pas!")
    
    def open_excel(self):
        """Ouvrir le fichier Excel"""
        excel_path = self.config["paths"]["excel_file"]
        if os.path.exists(excel_path):
            os.startfile(excel_path)
        else:
            messagebox.showwarning("Attention", f"Le fichier {excel_path} n'existe pas!")
    
    def clean_output(self):
        """Nettoyer les dossiers de sortie"""
        if messagebox.askyesno("Confirmation", "Nettoyer tous les dossiers de sortie ?"):
            import shutil
            
            paths = [
                self.config["paths"]["output_augmented"],
                self.config["paths"]["output_mosaic"]
            ]
            
            for path in paths:
                if os.path.exists(path):
                    shutil.rmtree(path)
                    self.log(f"🗑️ {path} nettoyé")
            
            messagebox.showinfo("Succès", "Dossiers de sortie nettoyés!")
            self.update_statistics()
    
    def diagnose_env(self):
        """Diagnostiquer l'environnement"""
        issues = []
        
        # Vérifier Python
        issues.append(f"✅ Python {sys.version}")
        
        # Vérifier les dossiers
        for key, path in self.config["paths"].items():
            if os.path.exists(path):
                issues.append(f"✅ {key}: {path}")
            else:
                issues.append(f"❌ {key}: {path} (n'existe pas)")
        
        # Vérifier les dépendances
        try:
            import cv2
            issues.append(f"✅ OpenCV {cv2.__version__}")
        except:
            issues.append("❌ OpenCV non installé")
        
        try:
            import pandas
            issues.append(f"✅ Pandas {pandas.__version__}")
        except:
            issues.append("❌ Pandas non installé")
        
        try:
            import numpy
            issues.append(f"✅ NumPy {numpy.__version__}")
        except:
            issues.append("❌ NumPy non installé")
        
        messagebox.showinfo("Diagnostic", "\n".join(issues))
        for issue in issues:
            self.log(issue)
    
    def reinstall_deps(self):
        """Réinstaller les dépendances"""
        if messagebox.askyesno("Confirmation", "Réinstaller toutes les dépendances ?"):
            self.log("📦 Réinstallation des dépendances...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            self.log("✅ Dépendances réinstallées!")
            messagebox.showinfo("Succès", "Dépendances réinstallées!")
    
    def open_guide(self):
        """Ouvrir le guide d'utilisation"""
        if os.path.exists("GUIDE_UTILISATION.md"):
            os.startfile("GUIDE_UTILISATION.md")
        else:
            messagebox.showwarning("Attention", "GUIDE_UTILISATION.md non trouvé!")
    
    def show_about(self):
        """Afficher À propos"""
        messagebox.showinfo("À propos", 
                          "Pokemon Dataset Generator v2.0.1\n\n"
                          "Interface modernisée avec:\n"
                          "✅ Settings personnalisables\n"
                          "✅ Validation automatique\n"
                          "✅ Barre de progression\n"
                          "✅ Multi-threading\n"
                          "✅ Logs détaillés\n"
                          "✅ Utilitaires API Pokémon TCG\n\n"
                          "© 2025")

def main():
    root = tk.Tk()
    
    # Style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Bouton accent
    style.configure('Accent.TButton', foreground='white', background='#0078D4', 
                   font=('Arial', 10, 'bold'))
    
    app = PokemonDatasetGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
