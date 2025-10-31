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
        
        # Créer les onglets (ordre logique du workflow)
        self.create_dashboard_tab()          # 📊 Vue d'ensemble
        self.create_workflow_tab()           # 🚀 Workflow Automatique (NOUVEAU)
        self.create_augmentation_tab()       # 🎨 Étape 1: Augmentation
        self.create_mosaic_tab()             # 🧩 Étape 2: Mosaïques
        self.create_validation_tab()         # ✅ Étape 3: Validation
        self.create_training_tab()           # 🎓 Étape 4: Entraînement
        self.create_detection_tab()          # 📹 Étape 5: Test & Détection
        self.create_export_tab()             # 📦 Étape 6: Export
        self.create_fakeimg_tab()            # 🎲 Outils: Fausses Cartes
        self.create_utilities_tab()          # 🛠️ Outils: Utilitaires
        self.create_logs_tab()               # 📜 Logs
        
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
    
    def create_workflow_tab(self):
        """🚀 Onglet Workflow Automatique - Interface Pro"""
        tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(tab, text="🚀 Workflow Auto")
        
        # ============ HEADER avec description ============
        header = ttk.Frame(tab)
        header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(header, text="🚀 Workflow Automatique Complet", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        desc_label = ttk.Label(header, 
                              text="Génération complète du dataset en un clic : Augmentation → Mosaïques → Validation → Export",
                              foreground='gray')
        desc_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # ============ SECTION 1: Configuration Rapide ============
        config_frame = ttk.LabelFrame(tab, text="⚙️ Configuration Rapide", padding="15")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Ligne 1: Augmentation
        ttk.Label(config_frame, text="1️⃣ Augmentations:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.workflow_aug_var = tk.IntVar(value=15)
        aug_spinbox = ttk.Spinbox(config_frame, from_=5, to=100, textvariable=self.workflow_aug_var, width=10)
        aug_spinbox.grid(row=0, column=1, padx=10)
        ttk.Label(config_frame, text="variations par carte", foreground='gray').grid(row=0, column=2, sticky=tk.W)
        
        # Ligne 2: Mosaïques
        ttk.Label(config_frame, text="2️⃣ Mosaïques:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.workflow_mosaic_var = tk.StringVar(value="standard")
        mosaic_combo = ttk.Combobox(config_frame, textvariable=self.workflow_mosaic_var, 
                                    values=["rapide (200)", "standard (500)", "complet (900)", "custom"], 
                                    width=20, state='readonly')
        mosaic_combo.grid(row=1, column=1, padx=10)
        ttk.Label(config_frame, text="layouts générés", foreground='gray').grid(row=1, column=2, sticky=tk.W)
        
        # Ligne 3: Options avancées
        ttk.Label(config_frame, text="3️⃣ Options:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=10)
        
        self.workflow_validate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Valider dataset", 
                       variable=self.workflow_validate_var).grid(row=0, column=0, sticky=tk.W)
        
        self.workflow_balance_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Auto-balancing classes", 
                       variable=self.workflow_balance_var).grid(row=0, column=1, padx=15, sticky=tk.W)
        
        self.workflow_train_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Entraîner modèle YOLO", 
                       variable=self.workflow_train_var).grid(row=0, column=2, padx=15, sticky=tk.W)
        
        # ============ SECTION 2: Étapes du Workflow ============
        steps_frame = ttk.LabelFrame(tab, text="📋 Étapes du Workflow", padding="15")
        steps_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.workflow_steps = []
        steps = [
            ("1️⃣", "Génération cartes augmentées", "images augmentées"),
            ("2️⃣", "Génération mosaïques YOLO", "layouts avec annotations"),
            ("3️⃣", "Validation du dataset", "rapport qualité"),
            ("4️⃣", "Auto-balancing (optionnel)", "équilibrage classes"),
            ("5️⃣", "Entraînement YOLO (optionnel)", "modèle .pt"),
        ]
        
        for i, (emoji, step, result) in enumerate(steps):
            step_frame = ttk.Frame(steps_frame)
            step_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=3)
            
            # Emoji + Texte
            label = ttk.Label(step_frame, text=f"{emoji} {step}", font=('Arial', 9))
            label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            
            # Status badge
            status = ttk.Label(step_frame, text="⏳ En attente", foreground='gray', 
                             font=('Arial', 8))
            status.grid(row=0, column=1, sticky=tk.W)
            self.workflow_steps.append(status)
            
            # Résultat attendu
            result_label = ttk.Label(step_frame, text=f"→ {result}", 
                                    foreground='#666', font=('Arial', 8, 'italic'))
            result_label.grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # ============ SECTION 3: Progress Bar Globale ============
        progress_frame = ttk.Frame(tab)
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.workflow_progress_label = ttk.Label(progress_frame, text="Prêt à démarrer", 
                                                font=('Arial', 9))
        self.workflow_progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.workflow_progress = ttk.Progressbar(progress_frame, mode='determinate', length=500)
        self.workflow_progress.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # ============ SECTION 4: Boutons d'Action ============
        action_frame = ttk.Frame(tab)
        action_frame.grid(row=4, column=0, pady=20)
        
        self.workflow_start_btn = ttk.Button(action_frame, text="🚀 LANCER LE WORKFLOW COMPLET", 
                                            command=self.start_automatic_workflow,
                                            style='Accent.TButton')
        self.workflow_start_btn.grid(row=0, column=0, padx=5, ipadx=20, ipady=10)
        
        ttk.Button(action_frame, text="⏹️ Arrêter", 
                  command=self.stop_workflow).grid(row=0, column=1, padx=5)
        
        ttk.Button(action_frame, text="🔄 Réinitialiser", 
                  command=self.reset_workflow).grid(row=0, column=2, padx=5)
        
        # ============ SECTION 5: Résumé Final ============
        summary_frame = ttk.LabelFrame(tab, text="📊 Résumé", padding="10")
        summary_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.workflow_summary = ttk.Label(summary_frame, text="Aucun workflow exécuté", 
                                         foreground='gray', justify=tk.LEFT)
        self.workflow_summary.grid(row=0, column=0, sticky=tk.W)
    
    def create_augmentation_tab(self):
        """Onglet Augmentation"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🎨 1. Augmentation")
        
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
        self.notebook.add(tab, text="🧩 2. Mosaïques")
        
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
    
    def create_validation_tab(self):
        """Onglet Validation du Dataset"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="✅ 3. Validation")
        
        # Description
        ttk.Label(tab, text="Validation du Dataset", font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        info = """🔍 Valide la qualité du dataset YOLO
        
✅ Vérifie les annotations (format, valeurs 0-1)
✅ Détecte les images corrompues
✅ Analyse la distribution des classes
✅ Statistiques des bounding boxes
✅ Génère un rapport HTML"""
        
        ttk.Label(tab, text=info, foreground="gray").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Paramètres
        params_frame = ttk.LabelFrame(tab, text="Paramètres", padding="10")
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(params_frame, text="Dataset à valider:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.validation_dataset_var = tk.StringVar(value=os.path.join("output", "yolov8"))
        dataset_combo = ttk.Combobox(params_frame, textvariable=self.validation_dataset_var, width=40)
        dataset_combo['values'] = [
            os.path.join("output", "yolov8"),
            os.path.join("output", "augmented")
        ]
        dataset_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        self.validation_html_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Générer rapport HTML", 
                       variable=self.validation_html_var).grid(row=1, column=0, columnspan=2, 
                                                              sticky=tk.W, pady=5)
        
        params_frame.columnconfigure(1, weight=1)
        
        # Boutons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="▶️ Valider Dataset", 
                  command=self.validate_dataset, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Ouvrir Rapport", 
                  command=lambda: self.open_file("validation_report.html"), 
                  width=20).pack(side=tk.LEFT, padx=5)
        
        tab.columnconfigure(0, weight=1)
    
    def create_training_tab(self):
        """Onglet Entraînement YOLO"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🎓 4. Entraînement")
        
        # Description
        ttk.Label(tab, text="Entraînement YOLOv8", font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        info = """🤖 Entraîne un modèle YOLOv8 sur votre dataset
        
⚡ Entraînement GPU si disponible
📊 Logs et métriques en temps réel
💾 Sauvegarde automatique du meilleur modèle
📈 Graphiques de progression (loss, mAP)"""
        
        ttk.Label(tab, text=info, foreground="gray").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Paramètres
        params_frame = ttk.LabelFrame(tab, text="Paramètres", padding="10")
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Modèle
        ttk.Label(params_frame, text="Modèle:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.training_model_var = tk.StringVar(value="yolov8n.pt")
        model_combo = ttk.Combobox(params_frame, textvariable=self.training_model_var, width=30)
        model_combo['values'] = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"]
        model_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(params_frame, text="(n=nano, s=small, m=medium, l=large, x=xlarge)", 
                 foreground="gray", font=('Arial', 8)).grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Epochs
        ttk.Label(params_frame, text="Epochs:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.training_epochs_var = tk.IntVar(value=100)
        ttk.Spinbox(params_frame, from_=10, to=500, textvariable=self.training_epochs_var, 
                   width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Batch size
        ttk.Label(params_frame, text="Batch size:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.training_batch_var = tk.IntVar(value=16)
        batch_combo = ttk.Combobox(params_frame, textvariable=self.training_batch_var, width=10)
        batch_combo['values'] = [4, 8, 16, 32, 64]
        batch_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Image size
        ttk.Label(params_frame, text="Image size:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.training_imgsz_var = tk.IntVar(value=640)
        imgsz_combo = ttk.Combobox(params_frame, textvariable=self.training_imgsz_var, width=10)
        imgsz_combo['values'] = [320, 416, 512, 640, 1280]
        imgsz_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Device
        ttk.Label(params_frame, text="Device:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.training_device_var = tk.StringVar(value="0")
        device_combo = ttk.Combobox(params_frame, textvariable=self.training_device_var, width=10)
        device_combo['values'] = ["0", "cpu", "0,1", "0,1,2,3"]
        device_combo.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(params_frame, text="(0=GPU, cpu=CPU, 0,1=multi-GPU)", 
                 foreground="gray", font=('Arial', 8)).grid(row=4, column=2, sticky=tk.W, padx=5)
        
        params_frame.columnconfigure(1, weight=1)
        
        # Boutons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="▶️ Entraîner", 
                  command=self.start_training, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📂 Ouvrir résultats", 
                  command=lambda: self.open_folder("runs/train"), 
                  width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📊 Voir graphiques", 
                  command=self.show_training_plots, width=20).pack(side=tk.LEFT, padx=5)
        
        tab.columnconfigure(0, weight=1)
    
    def create_detection_tab(self):
        """Onglet Détection Live (Webcam)"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="📹 5. Détection")
        
        # Description
        ttk.Label(tab, text="Détection en Temps Réel", font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        info = """📹 Teste ton modèle avec la webcam !
        
🎥 Détection en temps réel
🎯 Affiche les bounding boxes et noms
💾 Enregistre les détections
📸 Prend des screenshots"""
        
        ttk.Label(tab, text=info, foreground="gray").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Paramètres
        params_frame = ttk.LabelFrame(tab, text="Paramètres", padding="10")
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Modèle
        ttk.Label(params_frame, text="Modèle:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.detection_model_var = tk.StringVar(value="runs/train/pokemon_detector/weights/best.pt")
        
        model_frame = ttk.Frame(params_frame)
        model_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Entry(model_frame, textvariable=self.detection_model_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(model_frame, text="📂", width=3, 
                  command=lambda: self.browse_file(self.detection_model_var, 
                                                   "Modèle YOLO (*.pt)",
                                                   [("PyTorch Model", "*.pt")])).pack(side=tk.LEFT, padx=(5, 0))
        
        # Confiance
        ttk.Label(params_frame, text="Confiance minimale:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.detection_conf_var = tk.DoubleVar(value=0.5)
        
        conf_frame = ttk.Frame(params_frame)
        conf_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        conf_scale = ttk.Scale(conf_frame, from_=0.1, to=1.0, 
                              variable=self.detection_conf_var, orient=tk.HORIZONTAL)
        conf_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        conf_label = ttk.Label(conf_frame, textvariable=self.detection_conf_var, width=5)
        conf_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Caméra
        ttk.Label(params_frame, text="Caméra:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.detection_camera_var = tk.IntVar(value=0)
        ttk.Spinbox(params_frame, from_=0, to=3, textvariable=self.detection_camera_var, 
                   width=10).grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        params_frame.columnconfigure(1, weight=1)
        
        # Boutons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="▶️ Démarrer Webcam", 
                  command=self.start_webcam_detection, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🖼️ Détecter Image", 
                  command=self.detect_single_image, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📂 Détecter Dossier", 
                  command=self.detect_folder, width=20).pack(side=tk.LEFT, padx=5)
        
        tab.columnconfigure(0, weight=1)
    
    def create_export_tab(self):
        """Onglet Export Multi-Format"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="📦 6. Export")
        
        # Description
        ttk.Label(tab, text="Export Multi-Format", font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        info = """📦 Exporte ton dataset dans différents formats
        
📄 COCO JSON (Detectron2, MMDetection)
📝 Pascal VOC XML (Faster R-CNN)
🗜️ ZIP Roboflow (cloud training)
📊 TFRecord (TensorFlow)"""
        
        ttk.Label(tab, text=info, foreground="gray").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Options
        options_frame = ttk.LabelFrame(tab, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Format
        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.export_format_var = tk.StringVar(value="all")
        format_combo = ttk.Combobox(options_frame, textvariable=self.export_format_var, width=30)
        format_combo['values'] = ["all", "coco", "voc", "roboflow"]
        format_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Dataset source
        ttk.Label(options_frame, text="Dataset:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.export_dataset_var = tk.StringVar(value=os.path.join("output", "yolov8"))
        dataset_combo = ttk.Combobox(options_frame, textvariable=self.export_dataset_var, width=30)
        dataset_combo['values'] = [
            os.path.join("output", "yolov8"),
            os.path.join("output", "augmented")
        ]
        dataset_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Options supplémentaires
        self.export_split_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Train/Val split (80/20)", 
                       variable=self.export_split_var).grid(row=2, column=0, columnspan=2, 
                                                           sticky=tk.W, pady=5)
        
        self.export_readme_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Générer README.txt", 
                       variable=self.export_readme_var).grid(row=3, column=0, columnspan=2, 
                                                            sticky=tk.W, pady=5)
        
        options_frame.columnconfigure(1, weight=1)
        
        # Boutons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="📤 Exporter", 
                  command=self.export_dataset, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🌈 Effet Holographique", 
                  command=self.apply_holographic, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⚖️ Auto-Balancing", 
                  command=self.auto_balance_dataset, width=20).pack(side=tk.LEFT, padx=5)
        
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
    
    # === 🚀 MÉTHODES WORKFLOW AUTOMATIQUE ===
    
    def start_automatic_workflow(self):
        """Démarrer le workflow automatique configuré"""
        if self.is_running:
            messagebox.showwarning("Attention", "Une opération est déjà en cours!")
            return
        
        # Récupérer la configuration
        num_aug = self.workflow_aug_var.get()
        mosaic_mode = self.workflow_mosaic_var.get()
        do_validate = self.workflow_validate_var.get()
        do_balance = self.workflow_balance_var.get()
        do_train = self.workflow_train_var.get()
        
        # Mapper le mode mosaïque
        mosaic_counts = {
            "rapide (200)": "200",
            "standard (500)": "500", 
            "complet (900)": "all",
            "custom": "1"
        }
        mosaic_param = mosaic_counts.get(mosaic_mode, "1")
        
        # Confirmation
        steps_text = f"""
Configuration du workflow :

1️⃣ Augmentation : {num_aug} variations par carte
2️⃣ Mosaïques : Mode {mosaic_mode}
3️⃣ Validation : {'✅ Activée' if do_validate else '❌ Désactivée'}
4️⃣ Auto-balancing : {'✅ Activé' if do_balance else '❌ Désactivé'}
5️⃣ Entraînement YOLO : {'✅ Activé' if do_train else '❌ Désactivé'}

Durée estimée : {self._estimate_duration(num_aug, mosaic_param, do_train)}

Continuer ?
"""
        
        if not messagebox.askyesno("🚀 Lancer Workflow", steps_text):
            return
        
        # Désactiver le bouton
        self.workflow_start_btn.config(state='disabled')
        
        # Réinitialiser les status
        self.reset_workflow_steps()
        
        # Lancer dans un thread
        def workflow():
            self.start_operation("Workflow Automatique")
            total_steps = 2 + (1 if do_validate else 0) + (1 if do_balance else 0) + (1 if do_train else 0)
            current_step = 0
            
            try:
                # ÉTAPE 1: Augmentation
                current_step += 1
                self._update_workflow_step(0, "⏳ En cours...", "orange")
                self._update_workflow_progress(current_step, total_steps, "Augmentation des cartes...")
                
                self.log(f"📋 Étape 1/{total_steps}: Augmentation ({num_aug} variations)...")
                cmd = [sys.executable, "augmentation.py", "--num_aug", str(num_aug), "--target", "augmented"]
                
                if self._run_subprocess(cmd):
                    self._update_workflow_step(0, "✅ Terminé", "green")
                    self.log("✅ Augmentation terminée")
                else:
                    raise Exception("Échec de l'augmentation")
                
                # ÉTAPE 2: Mosaïques
                current_step += 1
                self._update_workflow_step(1, "⏳ En cours...", "orange")
                self._update_workflow_progress(current_step, total_steps, "Génération des mosaïques...")
                
                self.log(f"\n📋 Étape 2/{total_steps}: Mosaïques (mode {mosaic_mode})...")
                
                if mosaic_param == "all":
                    cmd = [sys.executable, "mosaic.py", "all"]
                elif mosaic_param in ["200", "500"]:
                    # Générer plusieurs variations
                    num_variations = int(mosaic_param) // 18  # 18 combos possibles (3×3×2)
                    self.log(f"Génération de {mosaic_param} mosaïques (~{num_variations} variations par combo)...")
                    cmd = [sys.executable, "mosaic.py", "all"]  # Utiliser mode all pour l'instant
                else:
                    cmd = [sys.executable, "mosaic.py", "1", "0", "0"]
                
                if self._run_subprocess(cmd):
                    self._update_workflow_step(1, "✅ Terminé", "green")
                    self.log("✅ Mosaïques générées")
                else:
                    raise Exception("Échec de la génération des mosaïques")
                
                # ÉTAPE 3: Validation (optionnelle)
                if do_validate:
                    current_step += 1
                    self._update_workflow_step(2, "⏳ En cours...", "orange")
                    self._update_workflow_progress(current_step, total_steps, "Validation du dataset...")
                    
                    self.log(f"\n📋 Étape 3/{total_steps}: Validation du dataset...")
                    cmd = [sys.executable, "dataset_validator.py", "output/yolov8", "--html"]
                    
                    if self._run_subprocess(cmd):
                        self._update_workflow_step(2, "✅ Terminé", "green")
                        self.log("✅ Validation terminée - Voir validation_report.html")
                    else:
                        self._update_workflow_step(2, "⚠️ Erreur", "red")
                        self.log("⚠️ Validation échouée (non bloquant)")
                else:
                    self._update_workflow_step(2, "⏭️ Ignoré", "gray")
                
                # ÉTAPE 4: Auto-balancing (optionnel)
                if do_balance:
                    current_step += 1
                    self._update_workflow_step(3, "⏳ En cours...", "orange")
                    self._update_workflow_progress(current_step, total_steps, "Équilibrage des classes...")
                    
                    self.log(f"\n📋 Étape 4/{total_steps}: Auto-balancing...")
                    cmd = [sys.executable, "auto_balancer.py", "output/yolov8", 
                           "--strategy", "augment", "--target", "50"]
                    
                    if self._run_subprocess(cmd):
                        self._update_workflow_step(3, "✅ Terminé", "green")
                        self.log("✅ Classes équilibrées")
                    else:
                        self._update_workflow_step(3, "⚠️ Erreur", "red")
                        self.log("⚠️ Auto-balancing échoué (non bloquant)")
                else:
                    self._update_workflow_step(3, "⏭️ Ignoré", "gray")
                
                # ÉTAPE 5: Entraînement YOLO (optionnel)
                if do_train:
                    current_step += 1
                    self._update_workflow_step(4, "⏳ En cours...", "orange")
                    self._update_workflow_progress(current_step, total_steps, "Entraînement du modèle YOLO...")
                    
                    self.log(f"\n📋 Étape 5/{total_steps}: Entraînement YOLO (cela peut prendre longtemps)...")
                    
                    # Lancer l'entraînement (version simplifiée)
                    try:
                        from ultralytics import YOLO
                        model = YOLO('yolov8n.pt')
                        results = model.train(
                            data='output/yolov8/data.yaml',
                            epochs=50,
                            imgsz=640,
                            batch=16,
                            name='pokemon_detector'
                        )
                        self._update_workflow_step(4, "✅ Terminé", "green")
                        self.log("✅ Entraînement terminé - Modèle sauvegardé dans runs/train/")
                    except Exception as e:
                        self._update_workflow_step(4, "⚠️ Erreur", "red")
                        self.log(f"⚠️ Entraînement échoué: {e}")
                else:
                    self._update_workflow_step(4, "⏭️ Ignoré", "gray")
                
                # WORKFLOW TERMINÉ
                self._update_workflow_progress(total_steps, total_steps, "✅ Workflow terminé!")
                
                # Résumé final
                summary = self._generate_workflow_summary()
                self.workflow_summary.config(text=summary, foreground='green')
                
                self.log("\n" + "="*50)
                self.log("🎉 WORKFLOW AUTOMATIQUE TERMINÉ AVEC SUCCÈS!")
                self.log("="*50)
                self.log(summary)
                
                messagebox.showinfo("Succès", 
                                  f"🎉 Workflow terminé!\n\n{summary}\n\nConsultez l'onglet Logs pour les détails.")
                
            except Exception as e:
                self.log(f"\n❌ ERREUR WORKFLOW: {str(e)}")
                self.workflow_summary.config(text=f"❌ Erreur: {str(e)}", foreground='red')
                messagebox.showerror("Erreur", f"Le workflow a échoué:\n{str(e)}")
            
            finally:
                self.end_operation()
                self.workflow_start_btn.config(state='normal')
                self.update_statistics()
        
        thread = threading.Thread(target=workflow, daemon=True)
        thread.start()
    
    def stop_workflow(self):
        """Arrêter le workflow en cours"""
        if self.is_running:
            response = messagebox.askyesno("Arrêter Workflow", 
                                          "Voulez-vous vraiment arrêter le workflow?\n\n"
                                          "L'étape en cours sera terminée.")
            if response:
                self.log("⏹️ Arrêt du workflow demandé...")
                # Note: L'arrêt complet nécessiterait de gérer les subprocess
        else:
            messagebox.showinfo("Info", "Aucun workflow en cours")
    
    def reset_workflow(self):
        """Réinitialiser l'interface du workflow"""
        self.workflow_progress['value'] = 0
        self.workflow_progress_label.config(text="Prêt à démarrer")
        self.workflow_summary.config(text="Aucun workflow exécuté", foreground='gray')
        self.reset_workflow_steps()
        self.log("🔄 Workflow réinitialisé")
    
    def reset_workflow_steps(self):
        """Réinitialiser tous les status des étapes"""
        for status_label in self.workflow_steps:
            status_label.config(text="⏳ En attente", foreground='gray')
    
    def _update_workflow_step(self, step_index, text, color):
        """Mettre à jour le status d'une étape"""
        if step_index < len(self.workflow_steps):
            self.workflow_steps[step_index].config(text=text, foreground=color)
            self.root.update_idletasks()
    
    def _update_workflow_progress(self, current, total, message):
        """Mettre à jour la barre de progression"""
        percentage = (current / total) * 100
        self.workflow_progress['value'] = percentage
        self.workflow_progress_label.config(text=f"{message} ({current}/{total})")
        self.root.update_idletasks()
    
    def _run_subprocess(self, cmd):
        """Exécuter une commande subprocess avec logs"""
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                  stderr=subprocess.STDOUT, text=True)
        
        for line in iter(process.stdout.readline, ''):
            if line:
                self.log(line.strip())
        
        process.wait()
        return process.returncode == 0
    
    def _estimate_duration(self, num_aug, mosaic_param, do_train):
        """Estimer la durée du workflow"""
        duration = 0
        duration += num_aug * 0.5  # ~0.5s par augmentation
        
        if mosaic_param == "all":
            duration += 900 * 0.2  # ~0.2s par mosaïque
        elif mosaic_param == "500":
            duration += 500 * 0.2
        elif mosaic_param == "200":
            duration += 200 * 0.2
        else:
            duration += 161 * 0.2
        
        if do_train:
            duration += 30 * 60  # ~30 min pour entraînement
        
        if duration < 60:
            return f"{int(duration)}s"
        elif duration < 3600:
            return f"{int(duration/60)} min"
        else:
            return f"{int(duration/3600)}h {int((duration%3600)/60)}min"
    
    def _generate_workflow_summary(self):
        """Générer le résumé final du workflow"""
        import os
        
        summary_lines = []
        
        # Compter les fichiers générés
        aug_path = "output/augmented/images"
        yolo_path = "output/yolov8/images"
        
        if os.path.exists(aug_path):
            aug_count = len([f for f in os.listdir(aug_path) if f.endswith(('.jpg', '.png'))])
            summary_lines.append(f"✅ {aug_count} cartes augmentées")
        
        if os.path.exists(yolo_path):
            yolo_count = len([f for f in os.listdir(yolo_path) if f.endswith(('.jpg', '.png'))])
            summary_lines.append(f"✅ {yolo_count} mosaïques YOLO")
        
        if os.path.exists("validation_report.html"):
            summary_lines.append("✅ Rapport de validation généré")
        
        if os.path.exists("runs/train/pokemon_detector/weights/best.pt"):
            summary_lines.append("✅ Modèle YOLO entraîné")
        
        return "\n".join(summary_lines) if summary_lines else "Workflow terminé"
    
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
    
    # === Méthodes pour les nouveaux onglets ===
    
    def validate_dataset(self):
        """Valide le dataset YOLO"""
        dataset_dir = self.validation_dataset_var.get()
        generate_html = self.validation_html_var.get()
        
        self.log(f"🔍 Validation du dataset: {dataset_dir}")
        self.start_operation("Validation")
        
        def task():
            try:
                from dataset_validator import DatasetValidator
                
                validator = DatasetValidator(dataset_dir)
                results = validator.validate()
                validator.print_report()
                
                if generate_html:
                    validator.save_report_html("validation_report.html")
                    self.log("📄 Rapport HTML généré: validation_report.html")
                
                # Résumé
                errors = len(results['corrupted_images']) + len(results['annotations_out_of_bounds'])
                warnings = len(results['warnings'])
                
                if errors == 0:
                    messagebox.showinfo("Succès", 
                        f"✅ Validation terminée!\n\n"
                        f"Aucune erreur détectée\n"
                        f"{warnings} avertissements")
                else:
                    messagebox.showwarning("Validation", 
                        f"⚠️ Validation terminée\n\n"
                        f"{errors} erreurs\n"
                        f"{warnings} avertissements")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Erreur:\n{str(e)}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def start_training(self):
        """Entraîne un modèle YOLOv8"""
        model_name = self.training_model_var.get()
        epochs = self.training_epochs_var.get()
        batch = self.training_batch_var.get()
        imgsz = self.training_imgsz_var.get()
        device = self.training_device_var.get()
        
        data_yaml = os.path.join("output", "yolov8", "data.yaml")
        
        if not os.path.exists(data_yaml):
            messagebox.showerror("Erreur", 
                f"Fichier data.yaml non trouvé!\n{data_yaml}\n\n"
                "Générez d'abord les mosaïques.")
            return
        
        self.log(f"🎓 Entraînement YOLOv8: {model_name}")
        self.log(f"   Epochs: {epochs}, Batch: {batch}, ImgSz: {imgsz}, Device: {device}")
        self.start_operation("Entraînement")
        
        def task():
            try:
                from ultralytics import YOLO
                
                # Charger le modèle
                model = YOLO(model_name)
                
                # Entraîner
                results = model.train(
                    data=data_yaml,
                    epochs=epochs,
                    imgsz=imgsz,
                    batch=batch,
                    device=device,
                    patience=50,
                    save=True,
                    project="runs/train",
                    name="pokemon_detector",
                    exist_ok=True,
                    verbose=True
                )
                
                self.log("✅ Entraînement terminé!")
                self.log(f"📊 Modèle sauvegardé: runs/train/pokemon_detector/weights/best.pt")
                
                messagebox.showinfo("Succès", 
                    "✅ Entraînement terminé!\n\n"
                    "Modèle sauvegardé dans:\n"
                    "runs/train/pokemon_detector/weights/best.pt")
                
            except ImportError:
                self.log("❌ Ultralytics non installé!")
                messagebox.showerror("Erreur", 
                    "Package ultralytics non installé!\n\n"
                    "Installation:\n"
                    "pip install -r requirements_extra.txt")
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Erreur", f"Erreur:\n{str(e)}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def show_training_plots(self):
        """Affiche les graphiques d'entraînement"""
        plots_dir = Path("runs/train/pokemon_detector")
        
        if not plots_dir.exists():
            messagebox.showwarning("Attention", "Aucun entraînement trouvé!")
            return
        
        # Chercher results.png
        results_png = plots_dir / "results.png"
        
        if results_png.exists():
            import cv2
            img = cv2.imread(str(results_png))
            cv2.imshow("Training Results", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            messagebox.showinfo("Info", 
                f"Graphiques non trouvés.\n\n"
                f"Cherchez dans: {plots_dir}")
    
    def start_webcam_detection(self):
        """Démarre la détection webcam"""
        model_path = self.detection_model_var.get()
        conf = self.detection_conf_var.get()
        camera = self.detection_camera_var.get()
        
        if not os.path.exists(model_path):
            messagebox.showerror("Erreur", 
                f"Modèle non trouvé!\n{model_path}\n\n"
                "Entraînez d'abord un modèle.")
            return
        
        self.log(f"📹 Démarrage détection webcam...")
        self.log(f"   Modèle: {model_path}")
        self.log(f"   Confiance: {conf}")
        self.log(f"   Caméra: {camera}")
        
        def task():
            try:
                from ultralytics import YOLO
                import cv2
                
                # Charger le modèle
                model = YOLO(model_path)
                
                # Ouvrir la webcam
                cap = cv2.VideoCapture(camera)
                
                if not cap.isOpened():
                    self.log("❌ Impossible d'ouvrir la caméra!")
                    messagebox.showerror("Erreur", "Impossible d'ouvrir la caméra!")
                    return
                
                self.log("✅ Webcam démarrée! (appuyez sur 'q' pour quitter)")
                
                while True:
                    ret, frame = cap.read()
                    
                    if not ret:
                        break
                    
                    # Détecter
                    results = model(frame, conf=conf)
                    
                    # Dessiner les bounding boxes
                    annotated = results[0].plot()
                    
                    # Afficher
                    cv2.imshow('Pokemon Card Detector', annotated)
                    
                    # Quitter avec 'q'
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                cap.release()
                cv2.destroyAllWindows()
                
                self.log("✅ Webcam arrêtée")
                
            except ImportError:
                self.log("❌ Ultralytics non installé!")
                messagebox.showerror("Erreur", "Package ultralytics non installé!")
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Erreur:\n{str(e)}")
        
        threading.Thread(target=task, daemon=True).start()
    
    def detect_single_image(self):
        """Détecte les cartes dans une image"""
        model_path = self.detection_model_var.get()
        
        if not os.path.exists(model_path):
            messagebox.showerror("Erreur", "Modèle non trouvé!")
            return
        
        # Choisir une image
        img_path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[("Images", "*.png *.jpg *.jpeg"), ("Tous", "*.*")]
        )
        
        if not img_path:
            return
        
        self.log(f"🔍 Détection sur: {img_path}")
        
        def task():
            try:
                from ultralytics import YOLO
                import cv2
                
                model = YOLO(model_path)
                
                # Détecter
                results = model(img_path)
                
                # Afficher le résultat
                annotated = results[0].plot()
                cv2.imshow('Detection Result', annotated)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
                # Log des détections
                boxes = results[0].boxes
                self.log(f"✅ {len(boxes)} cartes détectées")
                
                for i, box in enumerate(boxes):
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    name = results[0].names[cls]
                    self.log(f"   {i+1}. {name} ({conf:.2%})")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Erreur:\n{str(e)}")
        
        threading.Thread(target=task, daemon=True).start()
    
    def detect_folder(self):
        """Détecte les cartes dans toutes les images d'un dossier"""
        model_path = self.detection_model_var.get()
        
        if not os.path.exists(model_path):
            messagebox.showerror("Erreur", "Modèle non trouvé!")
            return
        
        # Choisir un dossier
        folder_path = filedialog.askdirectory(title="Choisir un dossier d'images")
        
        if not folder_path:
            return
        
        self.log(f"📂 Détection sur le dossier: {folder_path}")
        self.start_operation("Détection")
        
        def task():
            try:
                from ultralytics import YOLO
                from pathlib import Path
                
                model = YOLO(model_path)
                
                # Créer dossier de sortie
                output_dir = Path(folder_path) / "detections"
                output_dir.mkdir(exist_ok=True)
                
                # Lister les images
                image_files = list(Path(folder_path).glob("*.png")) + \
                             list(Path(folder_path).glob("*.jpg")) + \
                             list(Path(folder_path).glob("*.jpeg"))
                
                self.log(f"📊 {len(image_files)} images trouvées")
                
                # Détecter chaque image
                for idx, img_path in enumerate(image_files, 1):
                    self.log(f"   {idx}/{len(image_files)}: {img_path.name}")
                    
                    results = model(str(img_path))
                    annotated = results[0].plot()
                    
                    # Sauvegarder
                    import cv2
                    output_path = output_dir / f"detect_{img_path.name}"
                    cv2.imwrite(str(output_path), annotated)
                
                self.log(f"✅ Détection terminée! Résultats dans: {output_dir}")
                messagebox.showinfo("Succès", 
                    f"✅ Détection terminée!\n\n"
                    f"{len(image_files)} images traitées\n"
                    f"Résultats dans: {output_dir}")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Erreur:\n{str(e)}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def export_dataset(self):
        """Exporte le dataset dans différents formats"""
        dataset_dir = self.export_dataset_var.get()
        export_format = self.export_format_var.get()
        
        self.log(f"📦 Export du dataset: {export_format}")
        self.start_operation("Export")
        
        def task():
            try:
                from dataset_exporter import DatasetExporter
                
                exporter = DatasetExporter(dataset_dir)
                
                if export_format in ['coco', 'all']:
                    exporter.export_coco("dataset_coco.json")
                
                if export_format in ['voc', 'all']:
                    exporter.export_pascal_voc("dataset_voc")
                
                if export_format in ['roboflow', 'all']:
                    exporter.export_roboflow_zip("dataset_roboflow.zip")
                
                self.log("✅ Export terminé!")
                messagebox.showinfo("Succès", 
                    f"✅ Export terminé!\n\n"
                    f"Format: {export_format}")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Erreur", f"Erreur:\n{str(e)}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def apply_holographic(self):
        """Applique l'effet holographique aux cartes"""
        # Demander le dossier source
        source_dir = filedialog.askdirectory(
            title="Dossier source des cartes",
            initialdir="images"
        )
        
        if not source_dir:
            return
        
        output_dir = os.path.join(source_dir + "_holographic")
        
        self.log(f"🌈 Application effet holographique...")
        self.log(f"   Source: {source_dir}")
        self.log(f"   Sortie: {output_dir}")
        self.start_operation("Holographie")
        
        def task():
            try:
                from holographic_augmenter import HolographicAugmenter
                
                augmenter = HolographicAugmenter()
                augmenter.augment_directory(source_dir, output_dir, num_variations=3)
                
                self.log("✅ Effet holographique appliqué!")
                messagebox.showinfo("Succès", 
                    f"✅ Effet holographique appliqué!\n\n"
                    f"Images dans: {output_dir}")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Erreur:\n{str(e)}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def auto_balance_dataset(self):
        """Rééquilibre automatiquement le dataset"""
        dataset_dir = self.export_dataset_var.get()
        
        # Demander la stratégie
        strategy = messagebox.askquestion("Stratégie", 
            "Augmenter les classes sous-représentées?\n\n"
            "Oui = Augmenter\n"
            "Non = Réduire les sur-représentées")
        
        strategy = "augment" if strategy == "yes" else "reduce"
        
        self.log(f"⚖️ Auto-balancing: {strategy}")
        self.start_operation("Balancing")
        
        def task():
            try:
                from auto_balancer import DatasetBalancer
                
                balancer = DatasetBalancer(dataset_dir, strategy=strategy)
                balancer.balance()
                
                self.log("✅ Balancing terminé!")
                messagebox.showinfo("Succès", 
                    "✅ Balancing terminé!\n\n"
                    "Le dataset est maintenant équilibré.")
                
            except Exception as e:
                self.log(f"❌ Erreur: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Erreur", f"Erreur:\n{str(e)}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()

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
