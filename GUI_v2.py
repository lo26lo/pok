#!/usr/bin/env python3
"""
GUI Modernisé pour la génération de Dataset Pokémon
Version 2.0.2 - Interface améliorée avec settings, progression, validation et utilitaires API
Améliorations API: Session persistante, retry automatique, health checks
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
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class PokemonDatasetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokemon Dataset Generator v2.0.2")
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
        
        # Charger la clé API
        self.api_key = self.load_api_key()
        
        # Variables pour le threading
        self.current_process = None
        self.is_running = False
        
        # Session API réutilisable (sera créée à la demande)
        self.api_session = None
        
        # Créer l'interface
        self.create_menu()
        self.create_main_interface()
    
    def create_api_session(self):
        """
        Crée une session requests optimisée avec retry automatique.
        Réutilise la connexion TCP pour de meilleures performances.
        """
        self.log("🔧 Création de la session API...")
        
        # Activer les logs urllib3 pour voir les retries
        import logging
        urllib3_logger = logging.getLogger('urllib3.connectionpool')
        urllib3_logger.setLevel(logging.DEBUG)
        
        # Handler pour rediriger vers notre log
        class LogHandler(logging.Handler):
            def __init__(self, log_func):
                super().__init__()
                self.log_func = log_func
                
            def emit(self, record):
                msg = self.format(record)
                if 'Retry' in msg or 'retry' in msg.lower():
                    self.log_func(f"🔁 {msg}")
                elif 'timeout' in msg.lower():
                    self.log_func(f"⏱️  {msg}")
        
        handler = LogHandler(self.log)
        handler.setFormatter(logging.Formatter('%(message)s'))
        urllib3_logger.addHandler(handler)
        
        session = requests.Session()
        
        # Configuration du retry automatique
        # - 5 tentatives maximum
        # - Backoff exponentiel (1, 2, 4, 8, 16 secondes)
        # - Retry sur les erreurs 429 (rate limit), 500, 502, 503, 504
        self.log("⚙️  Configuration: 5 retries, backoff exponentiel (1→2→4→8→16s)")
        self.log("⚙️  Retry sur codes: 429, 500, 502, 503, 504")
        
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        # Pas de mount http:// - l'API Pokemon TCG n'accepte que HTTPS
        
        # Headers par défaut
        session.headers.update({
            'User-Agent': 'Pokemon-Dataset-Generator/2.0.2',
            'X-Api-Key': self.api_key
        })
        
        self.log("✅ Session créée avec User-Agent et API Key")
        
        return session
    
    def get_api_session(self):
        """Retourne la session API, la crée si nécessaire"""
        if self.api_session is None:
            self.api_session = self.create_api_session()
        return self.api_session
    
    def check_api_health(self):
        """
        Vérifie que l'API est accessible avant de lancer des opérations longues.
        Retourne (is_healthy, message)
        """
        self.log("🏥 Test de santé de l'API en cours...")
        self.log("📡 Requête: GET https://api.pokemontcg.io/v2/sets (timeout: 30s)")
        self.log("⏳ En attente de la réponse (cela peut prendre jusqu'à 30 secondes)...")
        
        try:
            session = self.get_api_session()
            import time
            start = time.time()
            
            # Ajouter un callback pour montrer la progression
            response = session.get("https://api.pokemontcg.io/v2/sets", timeout=30)
            
            elapsed = time.time() - start
            self.log(f"⏱️  Réponse health check en {elapsed:.2f}s (status: {response.status_code})")
            
            if response.status_code == 200:
                return True, "API opérationnelle"
            else:
                return False, f"API retourne le code {response.status_code}"
        except requests.exceptions.Timeout:
            self.log("⚠️  Health check timeout (>30s)")
            return False, "API lente (timeout) - mais vous pouvez essayer de continuer"
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Health check erreur: {str(e)[:100]}")
            return False, f"Erreur de connexion: {str(e)}"
    
    def load_api_key(self):
        """Charge la clé API depuis api_config.json"""
        api_config_file = "api_config.json"
        try:
            if os.path.exists(api_config_file):
                with open(api_config_file, 'r') as f:
                    config = json.load(f)
                    return config.get("pokemon_tcg_api_key", "")
            else:
                messagebox.showwarning(
                    "Configuration API manquante",
                    f"Le fichier '{api_config_file}' est manquant.\n\n"
                    "Créez-le à partir de 'api_config.json.example' et ajoutez votre clé API.\n"
                    "Fonctionnalités API désactivées jusqu'à configuration."
                )
                return ""
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de la clé API: {str(e)}")
            return ""
        
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
        settings_menu.add_command(label="Configuration API", command=self.open_api_settings)
        
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
    
    def open_api_settings(self):
        """Ouvrir la fenêtre de configuration API"""
        api_window = tk.Toplevel(self.root)
        api_window.title("🔧 Configuration API TCGdex")
        api_window.geometry("500x300")
        
        # Charger la config actuelle
        try:
            with open('api_config.json', 'r') as f:
                api_config = json.load(f)
        except:
            api_config = {
                "api_source": "tcgdex",
                "tcgdex": {
                    "language": "en"
                }
            }
        
        # Frame principal
        main_frame = ttk.Frame(api_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === SECTION: TCGdex API ===
        ttk.Label(main_frame, text="🌍 TCGdex API - Gratuit", 
                 font=('Arial', 14, 'bold'), foreground='green').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(main_frame, text="✅ Aucune authentification requise", 
                 foreground="green", font=('Arial', 10)).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(main_frame, text="💰 Prix Cardmarket (EUR) + TCGPlayer (USD)", 
                 foreground="green", font=('Arial', 10)).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        tcgdex_config = api_config.get("tcgdex", {})
        
        ttk.Label(main_frame, text="Langue:", font=('Arial', 11)).grid(row=4, column=0, sticky=tk.W, pady=10)
        tcgdex_lang_var = tk.StringVar(value=tcgdex_config.get("language", "en"))
        tcgdex_lang_combo = ttk.Combobox(main_frame, textvariable=tcgdex_lang_var, width=30, state='readonly',
                                         font=('Arial', 11))
        tcgdex_lang_combo['values'] = ('en - English', 'fr - Français', 'es - Español', 'it - Italiano', 
                                        'pt - Português', 'de - Deutsch', 'ja - 日本語', 'zh - 中文', 
                                        'id - Indonesia', 'th - ไทย')
        
        # Mapper les valeurs affichées aux codes
        lang_map = {
            'en - English': 'en', 'fr - Français': 'fr', 'es - Español': 'es', 'it - Italiano': 'it',
            'pt - Português': 'pt', 'de - Deutsch': 'de', 'ja - 日本語': 'ja', 'zh - 中文': 'zh',
            'id - Indonesia': 'id', 'th - ไทย': 'th'
        }
        lang_reverse_map = {v: k for k, v in lang_map.items()}
        
        # Sélectionner la langue actuelle
        current_lang = tcgdex_config.get("language", "en")
        tcgdex_lang_combo.set(lang_reverse_map.get(current_lang, 'en - English'))
        tcgdex_lang_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        ttk.Label(main_frame, text="🌍 Support multilingue : 10+ langues", 
                 foreground="gray", font=('Arial', 9, 'italic')).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Configurer la colonne pour qu'elle s'étende
        main_frame.columnconfigure(1, weight=1)
        
        # === BOUTONS ===
        button_frame = ttk.Frame(api_window, padding="10")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        def save_api_config():
            """Sauvegarder la configuration API"""
            selected = tcgdex_lang_combo.get()
            lang_code = lang_map.get(selected, 'en')
            
            new_config = {
                "api_source": "tcgdex",
                "tcgdex": {
                    "language": lang_code
                }
            }
            
            try:
                with open('api_config.json', 'w') as f:
                    json.dump(new_config, f, indent=4)
                
                messagebox.showinfo("Succès", f"Configuration sauvegardée!\nLangue: {selected}")
                self.log(f"✅ Configuration API sauvegardée - TCGdex ({lang_code})")
                api_window.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
        
        def test_api_connection():
            """Tester la connexion à l'API TCGdex"""
            self.log(f"🧪 Test de connexion à TCGdex...")
            
            try:
                from tcgdex_api import TCGdexAPI
                selected = tcgdex_lang_combo.get()
                lang_code = lang_map.get(selected, 'en')
                
                tcgdex = TCGdexAPI(language=lang_code)
                
                # Test de recherche simple
                cards = tcgdex.search_cards("Pikachu")
                if cards:
                    # Test de récupération de prix
                    price_avg, price_max, details = tcgdex.search_card_with_prices("Pikachu")
                    if price_avg:
                        messagebox.showinfo("Succès", 
                            f"✅ Connexion TCGdex réussie!\n\n"
                            f"🃏 {len(cards)} cartes Pikachu trouvées\n"
                            f"💰 Prix: {price_avg}€\n"
                            f"🌍 Langue: {selected}")
                        self.log(f"✅ Test TCGdex API: OK ({len(cards)} cartes, prix disponibles)")
                    else:
                        messagebox.showinfo("Succès", 
                            f"✅ Connexion TCGdex réussie!\n\n"
                            f"🃏 {len(cards)} cartes Pikachu trouvées\n"
                            f"🌍 Langue: {selected}\n\n"
                            f"(Prix non disponibles pour cette carte)")
                        self.log(f"✅ Test TCGdex API: OK ({len(cards)} cartes)")
                else:
                    messagebox.showwarning("Attention", "Aucune carte trouvée. Vérifiez votre connexion internet.")
                    self.log(f"⚠️ Test TCGdex API: Aucune carte trouvée")
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Erreur de connexion TCGdex:\n\n{str(e)}")
                self.log(f"❌ Test TCGdex API échoué: {str(e)}")
        
        ttk.Button(button_frame, text="🧪 Tester la connexion", 
                  command=test_api_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Sauvegarder", 
                  command=save_api_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Annuler", 
                  command=api_window.destroy).pack(side=tk.LEFT, padx=5)
    
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
        """Générer un fichier Excel depuis l'API TCGdex pour une extension"""
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
                import pandas as pd
                import requests
                from tcgdex_api import TCGdexAPI
                
                self.log("=" * 60)
                self.log("🚀 GÉNÉRATION AVEC TCGdex (GRATUIT)")
                self.log("=" * 60)
                
                # Charger la config API pour la langue
                try:
                    with open('api_config.json', 'r') as f:
                        api_config = json.load(f)
                except:
                    api_config = {"tcgdex": {"language": "en"}}
                
                tcgdex_config = api_config.get("tcgdex", {})
                language = tcgdex_config.get("language", "en")
                
                self.log(f"🌍 Langue: {language}")
                self.log(f"🌐 API: TCGdex v2 (gratuite, sans authentification)")
                
                # Initialiser le client TCGdex
                tcgdex = TCGdexAPI(language=language)
                
                # Déterminer si c'est un ID ou un nom de set
                set_lower = extension.lower().strip()
                set_code = tcgdex.set_mapping.get(set_lower)
                
                if set_code:
                    self.log(f"✅ Set reconnu: '{extension}' → ID TCGdex: '{set_code}'")
                    set_id = set_code
                elif '-' in extension or len(extension) <= 6:
                    self.log(f"🔍 Extension semble être un ID: '{extension}'")
                    set_id = extension
                else:
                    # Essayer de chercher le set par nom
                    self.log(f"🔍 Recherche du set par nom: '{extension}'...")
                    try:
                        url = f"https://api.tcgdex.net/v2/{language}/sets"
                        response = requests.get(url, timeout=15)
                        response.raise_for_status()
                        sets = response.json()
                        
                        # Chercher le set
                        found_sets = [s for s in sets if extension.lower() in s.get('name', '').lower()]
                        
                        if not found_sets:
                            self.log(f"❌ Set '{extension}' non trouvé")
                            self.log(f"💡 Essayez avec un ID (ex: sv08, sv07, base1, etc.)")
                            messagebox.showerror("Erreur", f"Set '{extension}' non trouvé.\nEssayez avec l'ID du set (ex: sv08, sv07, etc.)")
                            return
                        
                        best_match = found_sets[0]
                        set_id = best_match.get('id')
                        set_name = best_match.get('name')
                        
                        self.log(f"✅ Set trouvé: '{set_name}' (ID: {set_id})")
                        
                    except Exception as e:
                        self.log(f"❌ Erreur lors de la recherche du set: {e}")
                        messagebox.showerror("Erreur", f"Impossible de trouver le set.\nEssayez avec l'ID (ex: sv08)")
                        return
                
                # Récupérer toutes les cartes du set
                self.log(f"📡 Récupération des cartes du set '{set_id}'...")
                
                try:
                    url = f"https://api.tcgdex.net/v2/{language}/sets/{set_id}"
                    response = requests.get(url, timeout=15)
                    response.raise_for_status()
                    set_data = response.json()
                    
                    set_name = set_data.get('name', extension)
                    card_count = set_data.get('cardCount', {})
                    total_cards = card_count.get('total', 0)
                    official_cards = card_count.get('official', 0)
                    
                    self.log(f"📊 Set: {set_name}")
                    self.log(f"� Cartes officielles: {official_cards}")
                    self.log(f"📊 Cartes totales (avec variantes): {total_cards}")
                    
                    # Récupérer la liste des cartes
                    cards_list = set_data.get('cards', [])
                    
                    if not cards_list:
                        self.log(f"❌ Aucune carte trouvée dans le set")
                        messagebox.showwarning("Attention", f"Aucune carte trouvée pour '{set_name}'")
                        return
                    
                    self.log(f"✅ {len(cards_list)} cartes récupérées")
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        self.log(f"❌ Set '{set_id}' non trouvé (404)")
                        messagebox.showerror("Erreur", f"Set '{set_id}' non trouvé.\nVérifiez l'ID du set.")
                    else:
                        self.log(f"❌ Erreur HTTP: {e}")
                        messagebox.showerror("Erreur", f"Erreur lors de la récupération: {e}")
                    return
                except Exception as e:
                    self.log(f"❌ Erreur: {e}")
                    messagebox.showerror("Erreur", f"Erreur: {e}")
                    return
                
                # Créer le DataFrame
                self.log(f"\n📝 Création du fichier Excel...")
                self.log(f"📁 Fichier: {output}")
                
                rows = []
                for card_brief in cards_list:
                    card_number = card_brief.get('localId', '')
                    name = card_brief.get('name', '')
                    
                    # Format: 001/191
                    if official_cards > 0:
                        set_number = f"{card_number}/{official_cards}"
                    else:
                        set_number = card_number
                    
                    rows.append({
                        "Set #": set_number,
                        "Name": name,
                        "Set": set_name
                    })
                
                df = pd.DataFrame(rows)
                
                # Trier par numéro de carte
                df['_sort'] = df['Set #'].str.extract(r'(\d+)').astype(int)
                df = df.sort_values('_sort').drop(columns=['_sort'])
                
                self.log(f"💾 Écriture dans Excel...")
                df.to_excel(output, index=False)
                
                file_size = os.path.getsize(output) / 1024
                
                self.log(f"\n{'='*60}")
                self.log(f"✅ SUCCÈS")
                self.log(f"{'='*60}")
                self.log(f"📁 Fichier: {output}")
                self.log(f"💾 Taille: {file_size:.1f} KB")
                self.log(f"📊 Cartes: {len(rows)}")
                self.log(f"🌐 Source: TCGdex API (gratuite)")
                self.log(f"{'='*60}")
                
                messagebox.showinfo("Succès", f"Fichier généré avec succès!\n\n{len(rows)} cartes de '{set_name}'\n\nSource: TCGdex (gratuit)")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Erreur", f"Une erreur est survenue:\n{str(e)}")
        
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
    
    def update_card_prices(self):
        """Mettre à jour les prix des cartes dans un fichier Excel avec TCGdex"""
        input_file = self.price_input_var.get().strip()
        output_file = self.price_output_var.get().strip()
        
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Erreur", f"Le fichier d'entrée '{input_file}' n'existe pas!")
            return
        
        if not output_file:
            messagebox.showerror("Erreur", "Veuillez saisir le nom du fichier de sortie!")
            return
        
        # Charger la config API
        try:
            with open('api_config.json', 'r') as f:
                api_config = json.load(f)
        except:
            api_config = {"tcgdex": {"language": "en"}}
        
        self.log(f"💰 Mise à jour des prix depuis: {input_file}")
        self.log(f"🌐 API: TCGdex (gratuit)")
        
        # Utiliser TCGdex uniquement
        self._update_prices_tcgdex(input_file, output_file, api_config)
    
    def _update_prices_tcgdex(self, input_file, output_file, api_config):
        """Mise à jour des prix avec l'API TCGdex (gratuit, agrège Cardmarket + TCGPlayer)"""
        def task():
            try:
                import pandas as pd
                import concurrent.futures
                import time
                from tcgdex_api import TCGdexAPI
                
                tcgdex_config = api_config.get("tcgdex", {})
                language = tcgdex_config.get("language", "en")
                
                # Créer le client TCGdex
                self.log(f"🔧 Initialisation du client TCGdex (langue: {language})...")
                tcgdex_api = TCGdexAPI(language=language)
                
                # Charger Excel
                df = pd.read_excel(input_file, engine="openpyxl")
                if "Prix" not in df.columns:
                    df["Prix"] = None
                if "Prix max" not in df.columns:
                    df["Prix max"] = None
                if "SourcePrix" not in df.columns:
                    df["SourcePrix"] = None
                
                total = len(df)
                processed = 0
                last_log = [0]
                failed = []
                
                def worker(idx, row):
                    """Worker thread pour traiter une carte TCGdex"""
                    nonlocal processed
                    
                    name = str(row.get("Name", "")).strip()
                    set_name = str(row.get("Set", "")).strip() if "Set" in row else None
                    set_hash = str(row.get("Set #", "")).strip() if "Set #" in row else None
                    
                    # Délai entre requêtes (API gratuite, pas de rate limit strict)
                    if processed > 0:
                        time.sleep(0.3)  # 0.3s = rapide
                    
                    # Rechercher sur TCGdex
                    try:
                        price, pmax, details = tcgdex_api.search_card_with_prices(name, set_name, set_hash)
                        
                        if details:
                            # Extraire la source réelle
                            pricing = details.get('pricing', {})
                            if pricing.get('cardmarket'):
                                source = "TCGdex(Cardmarket)"
                            elif pricing.get('tcgplayer'):
                                source = "TCGdex(TCGPlayer)"
                            else:
                                source = "TCGdex"
                        else:
                            source = None
                    except Exception as e:
                        price, pmax, source = None, None, None
                        failed.append((name, set_hash or "", str(e)))
                    
                    processed += 1
                    now = time.time()
                    if processed % 10 == 0 or (now - last_log[0]) >= 5:
                        self.log(f"📊 Progression: {processed}/{total} ({int(processed/total*100)}%)")
                        last_log[0] = now
                    
                    return idx, price, pmax, source
                
                self.log(f"🔄 Traitement de {total} cartes avec TCGdex (gratuit)")
                self.log(f"💡 Prix automatiques: Cardmarket (EUR) + TCGPlayer (USD)")
                self.log(f"⚡ Pas de rate limit: traitement rapide (~{total * 0.3:.0f}s estimé)")
                
                start = time.time()
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    futures = [ex.submit(worker, idx, row) for idx, row in df.iterrows()]
                    for fut in concurrent.futures.as_completed(futures):
                        idx, price, pmax, source = fut.result()
                        
                        if price is not None:
                            df.at[idx, "Prix"] = price
                        if pmax is not None:
                            df.at[idx, "Prix max"] = pmax
                        if source:
                            df.at[idx, "SourcePrix"] = source
                
                elapsed = time.time() - start
                
                # Sauvegarder
                df.to_excel(output_file, index=False)
                
                success_count = df["Prix"].notna().sum()
                self.log(f"✅ Fichier généré: {output_file}")
                self.log(f"📊 Prix trouvés: {success_count}/{total} ({int(success_count/total*100)}%)")
                self.log(f"⏱️  Temps total: {elapsed:.1f}s (~{(elapsed/total if total else 0):.2f}s/carte)")
                
                if failed:
                    self.log(f"⚠️  {len(failed)} cartes échouées (exemples):")
                    for c, num, e in failed[:5]:
                        self.log(f"   • {c} #{num}: {e[:50]}")
                
                messagebox.showinfo("Terminé", f"Prix mis à jour!\n{success_count}/{total} cartes avec prix")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Erreur:\n{str(e)}")
        
        threading.Thread(target=task, daemon=True).start()
    
    def _update_prices_cardmarket(self, input_file, output_file, api_config):
        """Mise à jour des prix avec l'API Cardmarket"""
        def task():
            try:
                import pandas as pd
                import concurrent.futures
                import time
                from cardmarket_api import CardmarketAPI
                
                cm_config = api_config.get("cardmarket", {})
                
                # Vérifier les credentials
                if not all([cm_config.get("app_token"), cm_config.get("app_secret"), 
                           cm_config.get("access_token"), cm_config.get("access_token_secret")]):
                    self.log("❌ Credentials Cardmarket incomplets")
                    messagebox.showerror("Erreur", "Configurez vos credentials Cardmarket dans Settings > Configuration API")
                    return
                
                # Créer le client Cardmarket
                self.log("🔧 Initialisation du client Cardmarket...")
                cm_api = CardmarketAPI(
                    app_token=cm_config["app_token"],
                    app_secret=cm_config["app_secret"],
                    access_token=cm_config["access_token"],
                    access_token_secret=cm_config["access_token_secret"]
                )
                
                # Charger Excel
                df = pd.read_excel(input_file, engine="openpyxl")
                if "Prix" not in df.columns:
                    df["Prix"] = None
                if "Prix max" not in df.columns:
                    df["Prix max"] = None
                if "SourcePrix" not in df.columns:
                    df["SourcePrix"] = None
                
                total = len(df)
                processed = 0
                last_log = [0]
                failed = []
                
                def worker(idx, row):
                    """Worker thread pour traiter une carte Cardmarket"""
                    nonlocal processed
                    
                    name = str(row.get("Name", "")).strip()
                    set_name = str(row.get("Set", "")).strip() if "Set" in row else None
                    set_hash = str(row.get("Set #", "")).strip() if "Set #" in row else None
                    
                    # Délai entre requêtes
                    if processed > 0:
                        time.sleep(1)  # 1s pour Cardmarket (rate limit strict)
                    
                    # Rechercher sur Cardmarket
                    try:
                        price, pmax, details = cm_api.search_card_with_prices(name, set_name, set_hash)
                    except Exception as e:
                        price, pmax, details = None, None, None
                        failed.append((name, set_hash or "", str(e)))
                    
                    processed += 1
                    now = time.time()
                    if processed % 5 == 0 or (now - last_log[0]) >= 5:
                        self.log(f"📊 Progression: {processed}/{total} ({int(processed/total*100)}%)")
                        last_log[0] = now
                    
                    return idx, price, pmax, details
                
                self.log(f"🔄 Traitement de {total} cartes sur Cardmarket (Europe)")
                self.log(f"⚠️  Rate limit Cardmarket: 1s entre chaque carte (~{total}s estimé)")
                
                start = time.time()
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    futures = [ex.submit(worker, idx, row) for idx, row in df.iterrows()]
                    for fut in concurrent.futures.as_completed(futures):
                        idx, price, pmax, details = fut.result()
                        
                        if price is not None:
                            df.at[idx, "Prix"] = price
                        if pmax is not None:
                            df.at[idx, "Prix max"] = pmax
                        if price or pmax:
                            df.at[idx, "SourcePrix"] = "Cardmarket"
                
                elapsed = time.time() - start
                
                # Sauvegarder
                df.to_excel(output_file, index=False)
                
                success_count = df["Prix"].notna().sum()
                self.log(f"✅ Fichier généré: {output_file}")
                self.log(f"📊 Prix trouvés: {success_count}/{total} ({int(success_count/total*100)}%)")
                self.log(f"⏱️  Temps total: {elapsed:.1f}s (~{(elapsed/total if total else 0):.2f}s/carte)")
                
                if failed:
                    self.log(f"⚠️  {len(failed)} cartes échouées (exemples):")
                    for c, num, e in failed[:5]:
                        self.log(f"   • {c} #{num}: {e[:50]}")
                
                messagebox.showinfo("Terminé", f"Prix mis à jour!\n{success_count}/{total} cartes avec prix")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Erreur:\n{str(e)}")
        
        threading.Thread(target=task, daemon=True).start()
    
    def _update_prices_pokemontcg(self, input_file, output_file, api_config):
        """Mise à jour des prix avec l'API Pokemon TCG (méthode originale)"""
        
        def task():
            try:
                import pandas as pd
                import concurrent.futures
                import time
                
                BASE_CARDS = "https://api.pokemontcg.io/v2/cards"
                BASE_SETS = "https://api.pokemontcg.io/v2/sets"
                
                # Charger ou utiliser la clé de la config
                pokemon_key = api_config.get("pokemon_tcg_api_key", self.api_key)
                
                if not pokemon_key:
                    self.log("❌ Clé API Pokemon TCG non configurée")
                    messagebox.showerror("Erreur", "Clé API Pokemon TCG non configurée. Voir Settings > Configuration API")
                    return
                
                # Health check
                is_healthy, health_msg = self.check_api_health()
                self.log(f"🏥 Health check: {health_msg}")
                if not is_healthy:
                    if "lente" in health_msg.lower():
                        self.log(f"⚠️  L'API est lente mais on essaie quand même...")
                    else:
                        response = messagebox.askyesno(
                            "API en difficulté", 
                            f"L'API semble avoir des problèmes:\n{health_msg}\n\nVoulez-vous quand même essayer?"
                        )
                        if not response:
                            return
                
                # Utiliser la session réutilisable
                session = self.get_api_session()
                HEADERS = {"X-Api-Key": self.api_key}
                
                # Charger Excel
                df = pd.read_excel(input_file, engine="openpyxl")
                if "Prix" not in df.columns:
                    df["Prix"] = None
                if "Prix max" not in df.columns:
                    df["Prix max"] = None
                if "SourcePrix" not in df.columns:
                    df["SourcePrix"] = None
                if "Set" not in df.columns:
                    df["Set"] = None
                
                # Helpers
                set_id_cache = {}
                
                def resolve_set_id(set_name):
                    """Résout un nom d'extension vers son ID"""
                    if not set_name:
                        return None
                    key = set_name.lower().strip()
                    if key in set_id_cache:
                        return set_id_cache[key]
                    
                    try:
                        r = session.get(BASE_SETS, params={"q": f'name:"{set_name}"'}, headers=HEADERS, timeout=45)
                        if r.status_code == 200:
                            data = r.json().get("data", []) or []
                            # Chercher une correspondance exacte
                            exact = [s for s in data if s.get("name", "").lower() == key]
                            chosen = exact[0] if exact else (data[0] if data else None)
                            sid = chosen.get("id") if chosen else None
                            set_id_cache[key] = sid
                            return sid
                    except Exception as e:
                        self.log(f"⚠️  resolve_set_id error: {e}")
                    
                    set_id_cache[key] = None
                    return None
                
                def parse_number(set_hash):
                    """Extrait le numéro de carte: '057/153' -> '57'"""
                    if not set_hash or not isinstance(set_hash, str):
                        return None
                    num = set_hash.split("/")[0].strip()
                    num = num.lstrip("0") or "0"
                    return num
                
                def extract_prices(card_obj):
                    """Extrait les prix d'une carte (TCGplayer puis Cardmarket)"""
                    # 1) TCGplayer (US)
                    tcg = (card_obj.get("tcgplayer") or {}).get("prices") or {}
                    tcg_vals = []
                    for variant_data in tcg.values():
                        if isinstance(variant_data, dict) and isinstance(variant_data.get("market"), (int, float)):
                            tcg_vals.append(variant_data["market"])
                    
                    if tcg_vals:
                        return tcg_vals[0], max(tcg_vals), "TCGPlayer"
                    
                    # 2) Cardmarket (EU)
                    cm = (card_obj.get("cardmarket") or {}).get("prices") or {}
                    candidates = []
                    main_price = None
                    
                    # Priorité: trendPrice > averageSellPrice > avg7 > avg30 > lowPrice > suggestedPrice
                    for key in ("trendPrice", "averageSellPrice", "avg7", "avg30", "lowPrice", "suggestedPrice"):
                        val = cm.get(key)
                        if isinstance(val, (int, float)):
                            candidates.append(val)
                            if main_price is None:
                                main_price = val
                    
                    if candidates:
                        return main_price, max(candidates), "Cardmarket"
                    
                    return None, None, None
                
                cache = {}
                total = len(df)
                processed = 0
                last_log = [0]
                
                def fetch_card_best(name, set_hash=None, set_name=None):
                    """Cherche une carte avec résolution d'extension"""
                    key = f"{name}|{set_hash}|{set_name}"
                    if key in cache:
                        return cache[key]
                    
                    # Construire la query
                    q_parts = [f'name:"{name}"']
                    num = parse_number(set_hash) if set_hash else None
                    sid = resolve_set_id(set_name) if set_name else None
                    
                    if sid:
                        q_parts.append(f'set.id:"{sid}"')
                    
                    params = {"q": " ".join(q_parts), "pageSize": 50}
                    
                    # Gestion du rate limiting 429
                    while True:
                        try:
                            r = session.get(BASE_CARDS, params=params, headers=HEADERS, timeout=45)
                        except requests.exceptions.RequestException as e:
                            cache[key] = (None, f"Erreur réseau: {e}")
                            return cache[key]
                        
                        if r.status_code == 429:
                            retry_after = int(r.headers.get("Retry-After", "5"))
                            self.log(f"⏸️  Rate limit (429) - attente {retry_after}s")
                            time.sleep(retry_after)
                            continue
                        
                        if r.status_code != 200:
                            cache[key] = (None, f"HTTP {r.status_code}")
                            return cache[key]
                        
                        break
                    
                    results = r.json().get("data", []) or []
                    if not results:
                        cache[key] = (None, "Aucun résultat")
                        return cache[key]
                    
                    # Filtrage intelligent
                    selected = None
                    
                    # 1) Par numéro de carte
                    if num:
                        for c in results:
                            if c.get("number", "").lstrip("0") == num:
                                selected = c
                                break
                    
                    # 2) Par nom d'extension
                    if not selected and set_name:
                        for c in results:
                            if (c.get("set", {}).get("name", "")).lower() == set_name.lower():
                                selected = c
                                break
                    
                    # 3) Premier résultat
                    if not selected:
                        selected = results[0]
                    
                    cache[key] = (selected, None)
                    return cache[key]
                
                def worker(idx, row):
                    """Worker thread pour traiter une carte"""
                    nonlocal processed
                    
                    name = str(row.get("Name", "")).strip()
                    set_hash = str(row.get("Set #", "")).strip() if "Set #" in row else None
                    set_name_val = str(row.get("Set", "")).strip() if "Set" in row else None
                    
                    # Petit délai pour laisser respirer l'API
                    if processed > 0:
                        time.sleep(0.5)  # 0.5s entre chaque carte
                    
                    card, err = fetch_card_best(name, set_hash, set_name_val)
                    price, pmax, src = (None, None, None)
                    
                    if card:
                        price, pmax, src = extract_prices(card)
                    
                    processed += 1
                    now = time.time()
                    if processed % 10 == 0 or (now - last_log[0]) >= 5:
                        self.log(f"📊 Progression: {processed}/{total} ({int(processed/total*100)}%)")
                        last_log[0] = now
                    
                    return idx, price, pmax, src, err
                
                self.log(f"🔄 Traitement de {total} cartes SÉQUENTIELLEMENT (1 à la fois)")
                self.log(f"💡 Sources de prix: TCGPlayer (US) puis Cardmarket (EU)")
                self.log(f"⚠️  Mode lent: L'API est surchargée, patience requise (~{total * 0.5:.0f}s estimé)")
                
                start = time.time()
                failed = []
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    futures = [ex.submit(worker, idx, row) for idx, row in df.iterrows()]
                    for fut in concurrent.futures.as_completed(futures):
                        idx, price, pmax, src, err = fut.result()
                        
                        if price is not None:
                            df.at[idx, "Prix"] = price
                        if pmax is not None:
                            df.at[idx, "Prix max"] = pmax
                        if src:
                            df.at[idx, "SourcePrix"] = src
                        
                        if err and price is None:
                            card_name = df.at[idx, "Name"]
                            card_num = df.at[idx, "Set #"] if "Set #" in df.columns else ""
                            failed.append((card_name, card_num, err))
                
                elapsed = time.time() - start
                
                # Sauvegarder
                df.to_excel(output_file, index=False)
                
                self.log(f"✅ Fichier généré: {output_file}")
                self.log(f"⏱️  Temps total: {elapsed:.1f}s (~{(elapsed/total if total else 0):.2f}s/carte)")
                
                if failed:
                    self.log(f"⚠️  {len(failed)} cartes sans prix (exemples):")
                    for c, num, e in failed[:8]:
                        self.log(f"   - {c} ({num}): {e}")
                
                messagebox.showinfo("Succès",
                    f"Mise à jour terminée!\nFichier: {output_file}\n"
                    f"Prix trouvés: {total-len(failed)}/{total}\nErreurs: {len(failed)}")
            
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Erreur", f"Une erreur est survenue:\n{str(e)}")
        
        threading.Thread(target=task, daemon=True).start()
    
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
                BASE_URL = "https://api.pokemontcg.io/v2/cards"
                
                if not self.api_key:
                    self.log("❌ Clé API non configurée")
                    messagebox.showerror("Erreur", "Clé API non configurée. Voir api_config.json")
                    return
                
                # Utiliser la session réutilisable
                session = self.get_api_session()
                
                params = {"q": f'name:"{card_name}"'}
                
                try:
                    response = session.get(BASE_URL, params=params, timeout=15)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Erreur API: {str(e)}")
                    messagebox.showerror("Erreur", f"Erreur réseau: {str(e)}")
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
