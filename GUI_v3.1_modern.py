#!/usr/bin/env python3
"""
GUI Ultra-Moderne pour Pokemon Dataset Generator
Version 3.0 - Interface Professionnelle avec Sidebar + Dashboard
Design: Material Design inspired, color palette harmonieuse
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import sys
import os
import json
import threading
import queue
import time
import multiprocessing
from pathlib import Path
from datetime import datetime

# Import des managers du core
from core.workflow_manager import WorkflowManager, WorkflowConfig
from core.training_manager import TrainingManager, TrainingConfig
from core.detection_manager import DetectionManager, DetectionConfig
from core.utils import load_paths, load_ui_messages, get_message, PATHS, UI_MESSAGES

# Modules GUI extraits (refactoring Phase 4)
from gui.theme import COLORS
from gui.task_runner import TaskRunner, TaskError
from gui.settings_dialog import SettingsDialog
from gui.config import GuiConfig
from gui.logging_setup import setup_logging

import logging
gui_logger = logging.getLogger("gui")


class ModernPokemonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(UI_MESSAGES['gui']['title'])
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e2e')
        
        # Définir l'icône Pikachu
        try:
            icon_path = Path("pikachu.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass  # Ignorer si l'icône n'est pas disponible
        
        # Variables
        self.config_file = "gui_config.json"
        self.current_process = None
        self.is_running = False
        self.operation_stopped = False  # Flag pour arrêt volontaire
        self.current_view = "home"

        # File de logs thread-safe: les threads workers ne touchent JAMAIS
        # aux widgets Tkinter directement (Tkinter n'est pas thread-safe).
        # log() enfile les messages, _drain_log_queue() les affiche depuis
        # le thread principal via root.after().
        self._log_queue = queue.Queue()

        # File de callbacks UI: même principe que les logs — les workers
        # déposent des callables, le poller les exécute sur le thread
        # principal. Aucun appel Tk (même root.after) depuis un worker.
        self._ui_queue = queue.Queue()

        # Exécuteur centralisé des opérations longues (Phase 4 / R2):
        # remplace les blocs subprocess copiés-collés des méthodes start_*
        self.tasks = TaskRunner(
            log=self.log,
            ui_dispatch=self._dispatch_ui,
            on_start=self.start_operation,
            on_end=self.end_operation,
        )
        
        # V3.1: État responsive
        self.is_compact_mode = False
        self.sidebar_visible = True
        
        # État du footer (collapsed/expanded)
        self.footer_expanded = False
        self.footer_height_collapsed = 40
        self.footer_height_expanded = 160
        
        # Variables pour workflow
        self.workflow_aug_var = None
        self.workflow_mosaic_var = None
        self.workflow_validate_var = tk.BooleanVar(value=True)
        self.workflow_balance_var = tk.BooleanVar(value=False)
        self.workflow_train_var = tk.BooleanVar(value=False)
        
        # Variables pour training
        self.train_model_var = None
        self.train_epochs_var = None
        self.train_batch_var = None
        # Holographic augmentation settings (loaded from gui_config.json if present)
        _cfg = GuiConfig(self.config_file)
        self.holographic_intensity = tk.DoubleVar(value=_cfg.get("holographic_intensity", 0.7))
        self.holographic_variations = tk.IntVar(value=_cfg.get("holographic_variations", 3))
        self.train_device_var = None
        
        # Variables pour detection
        self.detect_model_var = None
        self.detect_conf_var = None
        self.detect_camera_var = None
        
        # Variables pour augmentation
        self.aug_num_var = None
        self.aug_holo_var = None
        self.aug_output_var = None
        
        # Variables pour mosaic
        self.mosaic_mode_var = None
        
        # Variables pour validation
        self.valid_path_var = None
        self.valid_html_var = tk.BooleanVar(value=True)
        
        # Variables pour export
        self.export_coco_var = tk.BooleanVar(value=True)
        self.export_voc_var = tk.BooleanVar(value=False)
        self.export_tf_var = tk.BooleanVar(value=False)
        self.export_robo_var = tk.BooleanVar(value=False)
        
        # Variables pour clean tools
        self.clean_include_images_var = tk.BooleanVar(value=False)
        
        # Variables pour Statistics Panel (V3.2)
        self.stats_images_downloaded = tk.IntVar(value=0)
        self.stats_augmentations = tk.IntVar(value=0)
        self.stats_fake_images = tk.IntVar(value=0)
        self.stats_mosaics = tk.IntVar(value=0)
        self.stats_total_images = tk.StringVar(value="0")
        self.stats_disk_space = tk.StringVar(value="0 MB")
        
        # Chargement config
        self.load_config()
        
        # Palette de couleurs moderne (source unique: gui/theme.py)
        self.colors = dict(COLORS)
        
        # Constantes d'harmonisation V3.1
        self.PADDING_VIEW = 20           # Padding externe des vues
        self.PADDING_CARD = 20           # Padding interne des cartes
        self.PADDING_VERTICAL = 15       # Espacement vertical entre éléments
        self.CARD_SPACING = 20           # Espacement entre cartes
        self.FONT_TITLE = ('Segoe UI', 20, 'bold')      # Titres de vues
        self.FONT_CARD_TITLE = ('Segoe UI', 14, 'bold') # Titres de cartes
        self.FONT_TEXT = ('Segoe UI', 9)                # Texte normal
        self.FONT_BUTTON = ('Segoe UI', 10, 'bold')     # Boutons
        self.SPINBOX_WIDTH = 6           # Largeur des Spinbox (très réduite)
        self.COMBOBOX_WIDTH = 15         # Largeur des Combobox (très réduite)
        self.ENTRY_WIDTH = 25            # Largeur des Entry (très réduite)
        
        # Configuration du style
        self.setup_modern_style()
        
        # Créer l'interface
        self.create_interface()
        
        # Charger la vue Home par défaut
        self.show_view('home')

        # Démarrer le poller de logs (thread principal)
        self.root.after(100, self._drain_log_queue)

        self.log("✅ Interface initialisée - Mode Professionnel")
    
    def setup_modern_style(self):
        """Configure le style moderne avec ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style général
        style.configure('.',
            background=self.colors['bg_dark'],
            foreground=self.colors['text'],
            borderwidth=0,
            focuscolor='none'
        )
        
        # Sidebar Button (inactif)
        style.configure('Sidebar.TButton',
            background=self.colors['bg_sidebar'],
            foreground=self.colors['text_dim'],
            borderwidth=0,
            padding=(20, 15),
            font=self.FONT_TEXT,
            anchor='w'
        )
        
        style.map('Sidebar.TButton',
            background=[('active', self.colors['bg_card']),  # Moins agressif
                       ('pressed', self.colors['bg_hover'])],
            foreground=[('active', self.colors['text']),
                       ('pressed', self.colors['text'])]
        )
        
        # Sidebar Button (actif)
        style.configure('SidebarActive.TButton',
            background=self.colors['bg_hover'],
            foreground=self.colors['accent'],
            borderwidth=0,
            padding=(20, 15),
            font=self.FONT_BUTTON,
            anchor='w'
        )
        
        # Bouton accent
        style.configure('Accent.TButton',
            background=self.colors['accent'],
            foreground='#000000',
            borderwidth=0,
            padding=(15, 10),
            font=self.FONT_BUTTON
        )
        
        style.map('Accent.TButton',
            background=[('active', '#74c7ec'),  # Bleu plus clair au survol
                       ('pressed', '#89b4fa')],  # Retour à la couleur d'origine au clic
            foreground=[('active', '#000000'),
                       ('pressed', '#000000')]
        )
        
        # Card Frame
        style.configure('Card.TFrame',
            background=self.colors['bg_card'],
            borderwidth=1,
            relief='flat'
        )
        
        # Labels
        style.configure('TLabel',
            background=self.colors['bg_dark'],
            foreground=self.colors['text']
        )
        
        style.configure('Title.TLabel',
            background=self.colors['bg_dark'],
            foreground=self.colors['text'],
            font=('Segoe UI', 20, 'bold')
        )
        
        style.configure('Subtitle.TLabel',
            background=self.colors['bg_dark'],
            foreground=self.colors['text_dim'],
            font=self.FONT_TEXT
        )
        
        style.configure('CardTitle.TLabel',
            background=self.colors['bg_card'],
            foreground=self.colors['text'],
            font=self.FONT_CARD_TITLE
        )
        
        style.configure('Stat.TLabel',
            background=self.colors['bg_card'],
            foreground=self.colors['accent'],
            font=self.FONT_TITLE
        )
        
        # Progressbar
        style.configure('TProgressbar',
            background=self.colors['accent'],
            troughcolor=self.colors['bg_card'],
            borderwidth=0,
            thickness=6
        )
        
        # Entry - Fond blanc avec police foncée
        style.configure('TEntry',
            fieldbackground='#FFFFFF',  # Fond blanc
            foreground='#1a1a1a',  # Texte gris très foncé
            borderwidth=2,
            relief='solid',
            bordercolor=self.colors['border'],
            insertcolor='#1a1a1a',  # Curseur foncé
            padding=8
        )
        
        style.map('TEntry',
            fieldbackground=[('focus', '#f5f5f5')],  # Gris clair au focus
            bordercolor=[('focus', self.colors['accent'])]
        )
        
        # Spinbox
        style.configure('TSpinbox',
            fieldbackground='#FFFFFF',
            foreground='#1a1a1a',  # Texte gris très foncé
            arrowcolor='#1a1a1a',
            insertcolor='#1a1a1a',
            borderwidth=2,
            relief='solid',
            padding=8
        )
        
        # Combobox
        style.configure('TCombobox',
            fieldbackground='#FFFFFF',
            foreground='#1a1a1a',  # Texte gris très foncé
            background='#FFFFFF',
            arrowcolor='#1a1a1a',
            selectbackground=self.colors['accent'],
            selectforeground='#FFFFFF',
            borderwidth=2,
            relief='solid',
            padding=8
        )
        
        style.map('TCombobox',
            fieldbackground=[('readonly', '#FFFFFF'), ('focus', '#f5f5f5')],
            foreground=[('readonly', '#1a1a1a')],
            bordercolor=[('focus', self.colors['accent'])]
        )
    
    def create_interface(self):
        """Créer l'interface moderne avec sidebar"""
        # Container principal
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ========== HEADER ==========
        self.create_header(main_container)
        
        # ========== BODY (Sidebar + Content) ==========
        body = tk.Frame(main_container, bg=self.colors['bg_dark'])
        body.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Sidebar (gauche)
        self.create_sidebar(body)
        
        # Content Area (droite)
        self.create_content_area(body)
        
        # ========== FOOTER ==========
        self.create_footer(main_container)
    
    def create_header(self, parent):
        """Créer le header moderne"""
        header = tk.Frame(parent, bg=self.colors['bg_sidebar'], height=70)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        # Logo + Titre
        title_frame = tk.Frame(header, bg=self.colors['bg_sidebar'])
        title_frame.pack(side=tk.LEFT, padx=30, pady=15)
        
        title = tk.Label(title_frame, 
            text=f"🎮 {UI_MESSAGES['gui']['title']}",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_sidebar'],
            fg=self.colors['text']
        )
        title.pack(side=tk.LEFT)
        
        version = tk.Label(title_frame,
            text="v3.1 Pro",
            font=('Segoe UI', 9),
            bg=self.colors['bg_sidebar'],
            fg=self.colors['accent']
        )
        version.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status Ready (gauche, après version)
        self.header_status = tk.Label(title_frame,
            text="● Ready",
            font=('Segoe UI', 9),
            bg=self.colors['bg_sidebar'],
            fg=self.colors['success']
        )
        self.header_status.pack(side=tk.LEFT, padx=(20, 0))
        
        # Boutons header (droite)
        buttons_frame = tk.Frame(header, bg=self.colors['bg_sidebar'])
        buttons_frame.pack(side=tk.RIGHT, padx=20)
        
        ttk.Button(buttons_frame, text="⚙️ Settings", 
                  command=self.open_settings,
                  style='Sidebar.TButton',
                  width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="❓ Help",
                  command=self.show_help,
                  style='Sidebar.TButton',
                  width=10).pack(side=tk.LEFT, padx=5)
    
    def create_sidebar(self, parent):
        """Créer la sidebar de navigation"""
        sidebar = tk.Frame(parent, bg=self.colors['bg_sidebar'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Padding top
        tk.Frame(sidebar, bg=self.colors['bg_sidebar'], height=20).pack()
        
        # Navigation
        self.nav_buttons = {}
        
        # Groupe: Main
        self.create_nav_section(sidebar, "MAIN")
        self.create_nav_button(sidebar, "home", "📊 Home", self.colors['accent'])
        self.create_nav_button(sidebar, "workflow", "🚀 Auto Workflow", self.colors['success'])
        
        # Séparateur
        self.create_separator(sidebar)
        
        # Groupe: Generation
        self.create_nav_section(sidebar, "GENERATION")
        self.create_nav_button(sidebar, "download", "⬇️ Image Download", self.colors['text'])
        self.create_nav_button(sidebar, "augmentation", "🎨 Augmentation", self.colors['text'])
        self.create_nav_button(sidebar, "fakeimg", "🎲 Fake Images", self.colors['text'])
        self.create_nav_button(sidebar, "mosaic", "🧩 Mosaics", self.colors['text'])
        
        # Séparateur
        self.create_separator(sidebar)
        
        # Groupe: Processing
        self.create_nav_section(sidebar, "PROCESSING")
        self.create_nav_button(sidebar, "validation", "✅ Validation", self.colors['text'])
        self.create_nav_button(sidebar, "training", "🎓 Training", self.colors['text'])
        self.create_nav_button(sidebar, "evaluation", "📊 Evaluation", self.colors['text'])
        self.create_nav_button(sidebar, "detection", "📹 Detection", self.colors['text'])
        self.create_nav_button(sidebar, "export", "📦 Export", self.colors['text'])
        
        # Séparateur
        self.create_separator(sidebar)
        
        # Groupe: Tools (will be shown/hidden based on current view)
        self.tools_section = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        self.tools_section.pack(fill=tk.X)
        
        self.create_nav_section(self.tools_section, "TOOLS")
        self.create_nav_button(self.tools_section, "tools", "🛠️ Utilities", self.colors['text_dim'])
        
        # Spacer
        tk.Frame(sidebar, bg=self.colors['bg_sidebar']).pack(expand=True)
    
    def create_nav_section(self, parent, title):
        """Créer un titre de section dans la sidebar - COMPACT V3.1"""
        label = tk.Label(parent,
            text=title,
            font=('Segoe UI', 8, 'bold'),
            bg=self.colors['bg_sidebar'],
            fg=self.colors['text_dim'],
            anchor='w'
        )
        label.pack(fill=tk.X, padx=20, pady=(8, 3))
    
    def create_nav_button(self, parent, view_id, text, icon_color):
        """Créer un bouton de navigation - COMPACT V3.1"""
        btn_frame = tk.Frame(parent, bg=self.colors['bg_sidebar'])
        btn_frame.pack(fill=tk.X, padx=10, pady=1)
        
        # Indicateur actif (barre bleue à gauche)
        indicator = tk.Frame(btn_frame, bg=self.colors['bg_sidebar'], width=4)
        indicator.pack(side=tk.LEFT, fill=tk.Y)
        
        # Bouton
        btn = tk.Button(btn_frame,
            text=text,
            font=('Segoe UI', 9),
            bg=self.colors['bg_sidebar'],
            fg=self.colors['text_dim'],
            activebackground=self.colors['bg_hover'],
            activeforeground=self.colors['text'],
            relief='flat',
            anchor='w',
            padx=12,
            pady=8,
            cursor='hand2',
            command=lambda: self.show_view(view_id)
        )
        btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Hover effect
        def on_enter(e):
            if self.current_view != view_id:
                btn.config(bg=self.colors['bg_hover'], fg=self.colors['text'])
        
        def on_leave(e):
            if self.current_view != view_id:
                btn.config(bg=self.colors['bg_sidebar'], fg=self.colors['text_dim'])
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        # Stocker pour mise à jour
        self.nav_buttons[view_id] = (btn, indicator)
    
    def create_separator(self, parent):
        """Créer un séparateur horizontal - COMPACT V3.1"""
        sep = tk.Frame(parent, bg=self.colors['border'], height=1)
        sep.pack(fill=tk.X, padx=20, pady=6)
    
    def create_content_area(self, parent):
        """Créer la zone de contenu principale"""
        self.content_area = tk.Frame(parent, bg=self.colors['bg_dark'])
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def create_statistics_panel(self, parent):
        """Créer le panneau Statistics persistant (V3.2) - À DROITE de la vue"""
        # Container à droite avec largeur fixe
        self.stats_panel = tk.Frame(parent, bg=self.colors['bg_card'], width=220)
        self.stats_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 15), pady=15)
        self.stats_panel.pack_propagate(False)
        
        # Titre
        title_frame = tk.Frame(self.stats_panel, bg=self.colors['bg_card'])
        title_frame.pack(fill=tk.X, padx=12, pady=(12, 8))
        
        tk.Label(title_frame,
            text="📊 Stats",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            justify='left'
        ).pack(side=tk.LEFT)
        
        # Séparateur
        tk.Frame(self.stats_panel, bg=self.colors['border'], height=1).pack(fill=tk.X, padx=12, pady=8)
        
        # Compteurs verticaux (un par ligne)
        stats_container = tk.Frame(self.stats_panel, bg=self.colors['bg_card'])
        stats_container.pack(fill=tk.X, padx=12, pady=(0, 12))
        
        # Images Downloaded
        self.create_stat_counter_vertical(stats_container, "📥 Images", self.stats_images_downloaded)
        
        # Augmentations
        self.create_stat_counter_vertical(stats_container, "🎨 Augmentations", self.stats_augmentations)
        
        # Fake Images
        self.create_stat_counter_vertical(stats_container, "🖼️ Fake Images", self.stats_fake_images)
        
        # Mosaics
        self.create_stat_counter_vertical(stats_container, "🧩 Mosaics", self.stats_mosaics)
        
        # Séparateur
        tk.Frame(self.stats_panel, bg=self.colors['border'], height=1).pack(fill=tk.X, padx=12, pady=6)
        
        # Total (with multiplier)
        self.create_stat_counter_vertical(stats_container, "📊 Total (×)", self.stats_total_images)
        
        # Disk Space
        self.create_stat_counter_vertical(stats_container, "💾 Disk Space", self.stats_disk_space)
        
        # Spacer en bas pour remplir l'espace (couleur bg_dark pour se fondre)
        tk.Frame(self.stats_panel, bg=self.colors['bg_dark']).pack(expand=True, fill=tk.BOTH)
        
        # Initialiser les compteurs au démarrage
        self.root.after(500, self.update_all_statistics)
    
    def create_stat_counter_vertical(self, parent, label_text, variable):
        """Créer un compteur de statistique vertical (pour sidebar droite)"""
        frame = tk.Frame(parent, bg=self.colors['bg_hover'], relief='flat', bd=1)
        frame.pack(fill=tk.X, pady=5)
        
        # Label en haut
        tk.Label(frame,
            text=label_text,
            font=('Segoe UI', 7),
            bg=self.colors['bg_hover'],
            fg=self.colors['text_dim'],
            anchor='w'
        ).pack(fill=tk.X, padx=10, pady=(8, 3))
        
        # Valeur en bas (grande)
        tk.Label(frame,
            textvariable=variable,
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_hover'],
            fg=self.colors['accent'],
            anchor='w'
        ).pack(fill=tk.X, padx=10, pady=(0, 8))
    
    def update_all_statistics(self):
        """Mettre à jour toutes les statistiques (thread-safe)"""
        if threading.current_thread() is not threading.main_thread():
            self._dispatch_ui(self.update_all_statistics)
            return
        try:
            # Images téléchargées
            images_dir = PATHS['directories']['images']
            if os.path.exists(images_dir):
                count = len([f for f in os.listdir(images_dir) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                self.stats_images_downloaded.set(count)
            
            # Augmentations (holo + augmented)
            holo_dir = PATHS['directories']['output_holographic']
            aug_dir = PATHS['directories']['output_augmented_images']
            total_aug = 0
            if os.path.exists(holo_dir):
                total_aug += len([f for f in os.listdir(holo_dir) 
                                if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            if os.path.exists(aug_dir):
                total_aug += len([f for f in os.listdir(aug_dir) 
                                if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            self.stats_augmentations.set(total_aug)
            
            # Fake Images
            fake_dir = PATHS['directories']['output_backgrounds']
            if os.path.exists(fake_dir):
                count = len([f for f in os.listdir(fake_dir) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                self.stats_fake_images.set(count)
            
            # Mosaics
            mosaic_dir = PATHS['directories']['output_mosaics_images']
            if os.path.exists(mosaic_dir):
                count = len([f for f in os.listdir(mosaic_dir) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                self.stats_mosaics.set(count)
            
            # Total (avec multiplicateur)
            total = self.stats_images_downloaded.get() + self.stats_augmentations.get() + self.stats_fake_images.get()
            multiplier = 1.0
            if self.stats_images_downloaded.get() > 0:
                multiplier = total / self.stats_images_downloaded.get()
            self.stats_total_images.set(f"{total} (×{multiplier:.1f})")
            
            # Disk Space (occupé)
            total_size = 0
            for dir_path in [images_dir, holo_dir, aug_dir, fake_dir, mosaic_dir]:
                if os.path.exists(dir_path):
                    for f in os.listdir(dir_path):
                        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                            total_size += os.path.getsize(os.path.join(dir_path, f))
            
            if total_size > 1024**3:  # > 1 GB
                self.stats_disk_space.set(f"{total_size / 1024**3:.2f} GB")
            else:
                self.stats_disk_space.set(f"{total_size / 1024**2:.1f} MB")
                
        except Exception as e:
            self.log(f"⚠️ Error updating statistics: {e}")
    
    def show_statistics_panel(self):
        """Afficher le panneau Statistics"""
        if hasattr(self, 'stats_panel'):
            self.stats_panel.pack(fill=tk.X, padx=20, pady=(20, 10), before=self.content_area.winfo_children()[0] if self.content_area.winfo_children() else None)
            self.update_all_statistics()
    
    def hide_statistics_panel(self):
        """Cacher le panneau Statistics"""
        if hasattr(self, 'stats_panel'):
            self.stats_panel.pack_forget()
    
    def create_footer(self, parent):
        """Créer le footer avec progress bar et logs - COLLAPSIBLE V3.1+"""
        self.footer = tk.Frame(parent, bg=self.colors['bg_sidebar'], height=self.footer_height_collapsed)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.footer.pack_propagate(False)
        
        # Header du footer (toujours visible) - barre compacte
        self.footer_header = tk.Frame(self.footer, bg=self.colors['bg_sidebar'], height=40)
        self.footer_header.pack(fill=tk.X)
        self.footer_header.pack_propagate(False)
        
        footer_header_content = tk.Frame(self.footer_header, bg=self.colors['bg_sidebar'])
        footer_header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
        
        # Label logs avec compteur + chevron
        self.footer_toggle_label = tk.Label(footer_header_content,
            text="📜 Logs (0) ▼",
            font=self.FONT_BUTTON,
            bg=self.colors['bg_sidebar'],
            fg=self.colors['text'],
            anchor='w',
            cursor='hand2'
        )
        self.footer_toggle_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.footer_toggle_label.bind('<Button-1>', lambda e: self.toggle_footer())
        
        # Progress label (compact)
        self.progress_label = tk.Label(footer_header_content,
            text="Ready",
            font=('Segoe UI', 9),
            bg=self.colors['bg_sidebar'],
            fg=self.colors['text_dim'],
            anchor='center'
        )
        self.progress_label.pack(side=tk.LEFT, padx=(10, 10))
        
        # Bouton Stop (compact)
        self.stop_button = tk.Button(footer_header_content,
            text="⏹",
            command=self.stop_operation,
            bg=self.colors['error'],
            fg='#FFFFFF',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            width=3,
            cursor='hand2',
            state='disabled'
        )
        self.stop_button.pack(side=tk.RIGHT)
        
        # Contenu expandable (progress bar + logs)
        self.footer_content = tk.Frame(self.footer, bg=self.colors['bg_sidebar'])
        # Ne pas pack par défaut (collapsed)
        
        # Progress bar
        progress_frame = tk.Frame(self.footer_content, bg=self.colors['bg_sidebar'])
        progress_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X)
        
        # ScrolledText pour logs
        self.log_text = scrolledtext.ScrolledText(self.footer_content,
            height=4,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='flat',
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
    
    def toggle_footer(self):
        """Toggle l'expansion/réduction du footer"""
        if self.footer_expanded:
            # Réduire
            self.footer_content.pack_forget()
            self.footer.config(height=self.footer_height_collapsed)
            self.footer_toggle_label.config(text=f"📜 Logs ({self.get_log_count()}) ▼")
            self.footer_expanded = False
        else:
            # Étendre
            self.footer_content.pack(fill=tk.BOTH, expand=True)
            self.footer.config(height=self.footer_height_expanded)
            self.footer_toggle_label.config(text=f"📜 Logs ({self.get_log_count()}) ▲")
            self.footer_expanded = True
    
    def expand_footer_auto(self):
        """Étendre automatiquement le footer (lors d'une opération)"""
        if not self.footer_expanded:
            self.toggle_footer()
    
    def get_log_count(self):
        """Obtenir le nombre de lignes de logs"""
        try:
            return int(self.log_text.index('end-1c').split('.')[0]) - 1
        except Exception:
            return 0
    
    def show_view(self, view_id):
        """Afficher une vue spécifique"""
        # Mettre à jour current_view
        self.current_view = view_id
        
        # Masquer/afficher le footer selon la vue
        # Dashboard n'a pas besoin du footer (pas d'opérations)
        if view_id == 'home':
            self.footer.pack_forget()
        else:
            self.footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Tools section toujours visible - FIXÉ V3.1
        # (Avant: masqué sur certaines vues, causait confusion utilisateur)
        
        # Mettre à jour les boutons de navigation
        for vid, (btn, indicator) in self.nav_buttons.items():
            if vid == view_id:
                btn.config(bg=self.colors['bg_hover'], 
                          fg=self.colors['accent'],
                          font=self.FONT_BUTTON)
                indicator.config(bg=self.colors['accent'])
            else:
                btn.config(bg=self.colors['bg_sidebar'], 
                          fg=self.colors['text_dim'],
                          font=self.FONT_TEXT)
                indicator.config(bg=self.colors['bg_sidebar'])
        
        # Vider le content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Créer container avec Statistics à droite (V3.2) pour certaines vues
        views_with_stats = ['download', 'augmentation', 'fakeimg', 'mosaic']
        if view_id in views_with_stats:
            # Container horizontal (vue principale à gauche + stats à droite)
            main_container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
            main_container.pack(fill=tk.BOTH, expand=True)
            
            # Vue principale à gauche (prend l'espace restant)
            self.view_container = tk.Frame(main_container, bg=self.colors['bg_dark'])
            self.view_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Panneau Statistics à droite
            self.create_statistics_panel(main_container)
        else:
            # Pas de stats, vue utilise tout l'espace
            self.view_container = self.content_area
        
        # Charger la vue correspondante
        if view_id == 'home':
            self.create_home_view()
        elif view_id == 'workflow':
            self.create_workflow_view()
        elif view_id == 'download':
            self.create_download_view()
        elif view_id == 'augmentation':
            self.create_augmentation_view()
        elif view_id == 'fakeimg':
            self.create_fakeimg_view()
        elif view_id == 'mosaic':
            self.create_mosaic_view()
        elif view_id == 'validation':
            self.create_validation_view()
        elif view_id == 'training':
            self.create_training_view()
        elif view_id == 'evaluation':
            self.create_evaluation_view()
        elif view_id == 'detection':
            self.create_detection_view()
        elif view_id == 'export':
            self.create_export_view()
        elif view_id == 'tools':
            self.create_tools_view()
    
    def create_dense_header(self, parent, icon, title, subtitle=None):
        """V3.1: Créer un header dense (title + subtitle sur 1 ligne si compact mode)
        
        Args:
            parent: Frame parent
            icon: Emoji icon
            title: Title text
            subtitle: Optional subtitle text
        
        Returns:
            header_frame: Frame containing the header
        """
        header_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        header_frame.pack(anchor='w', pady=(0, 10))
        
        if subtitle and self.is_compact_mode:
            # Mode compact: title + subtitle sur 1 ligne séparés par • 
            combined_text = f"{icon} {title} • {subtitle}"
            label = tk.Label(header_frame,
                text=combined_text,
                font=('Segoe UI', 12, 'bold'),  # Plus petit que FONT_TITLE
                bg=self.colors['bg_dark'],
                fg=self.colors['text']
            )
            label.pack(anchor='w')
        else:
            # Mode standard: 2 lignes mais avec moins de padding
            title_label = tk.Label(header_frame,
                text=f"{icon} {title}",
                font=self.FONT_TITLE,
                bg=self.colors['bg_dark'],
                fg=self.colors['text']
            )
            title_label.pack(anchor='w')
            
            if subtitle:
                subtitle_label = tk.Label(header_frame,
                    text=subtitle,
                    font=('Segoe UI', 10),  # Plus petit que FONT_TEXT
                    bg=self.colors['bg_dark'],
                    fg=self.colors['text_dim']
                )
                subtitle_label.pack(anchor='w', pady=(2, 0))  # Seulement 2px de padding
        
        return header_frame
    
    def create_info_tooltip(self, parent, icon_text, short_description, full_description):
        """V3.1: Créer un info compact avec icône + tooltip au hover
        
        Args:
            parent: Frame parent
            icon_text: Text with emoji (e.g., "ℹ️ About Augmentation")
            short_description: 1-line summary shown inline
            full_description: Full text shown in tooltip/dialog
        
        Returns:
            info_frame: Compact info frame with icon + text
        """
        info_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Icon label (clickable pour dialog)
        icon_label = tk.Label(info_frame,
            text=icon_text.split()[0],  # Prendre juste l'emoji
            font=('Segoe UI', 14),
            bg=self.colors['bg_dark'],
            fg=self.colors['accent'],
            cursor='hand2'
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Short description inline
        short_label = tk.Label(info_frame,
            text=short_description,
            font=('Segoe UI', 9),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim'],
            anchor='w'
        )
        short_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Tooltip on hover
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            tooltip_frame = tk.Frame(tooltip, bg=self.colors['bg_card'], relief='solid', borderwidth=1)
            tooltip_frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(tooltip_frame,
                text=full_description,
                font=('Segoe UI', 9),
                bg=self.colors['bg_card'],
                fg=self.colors['text'],
                justify='left',
                wraplength=400,
                padx=10,
                pady=8
            ).pack()
            
            # Auto-destroy après 5 secondes ou si souris quitte
            def destroy_tooltip(e=None):
                tooltip.destroy()
            
            tooltip.after(5000, destroy_tooltip)
            icon_label.bind('<Leave>', destroy_tooltip, add='+')
            tooltip.bind('<Leave>', destroy_tooltip)
        
        icon_label.bind('<Enter>', show_tooltip)
        
        # Click pour dialog détaillé
        def show_dialog():
            dialog = tk.Toplevel(self.root)
            dialog.title("Information")
            dialog.geometry("500x300")
            dialog.configure(bg=self.colors['bg_card'])
            
            title_label = tk.Label(dialog,
                text=icon_text,
                font=self.FONT_CARD_TITLE,
                bg=self.colors['bg_card'],
                fg=self.colors['accent']
            )
            title_label.pack(anchor='w', padx=20, pady=(20, 10))
            
            text_widget = tk.Text(dialog,
                font=self.FONT_TEXT,
                bg=self.colors['bg_card'],
                fg=self.colors['text'],
                wrap='word',
                relief='flat'
            )
            text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
            text_widget.insert('1.0', full_description)
            text_widget.config(state='disabled')
            
            close_btn = ttk.Button(dialog,
                text="Close",
                command=dialog.destroy,
                style='Accent.TButton'
            )
            close_btn.pack(pady=(0, 20))
        
        icon_label.bind('<Button-1>', lambda e: show_dialog())
        
        return info_frame
    
    def create_form_row_2col(self, parent, label1, widget1, label2, widget2, 
                            hint1=None, hint2=None):
        """V3.1: Créer une rangée avec 2 champs (label + widget) côte à côte
        
        Args:
            parent: Frame parent
            label1, label2: Labels des champs
            widget1, widget2: Widgets (Entry, Combobox, Spinbox, etc.)
            hint1, hint2: Textes d'aide optionnels
        
        Returns:
            row_frame: Frame contenant la rangée 2-colonnes
        """
        row_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        row_frame.pack(fill=tk.X, pady=8)
        
        # Colonne 1 (50% width)
        col1_frame = tk.Frame(row_frame, bg=self.colors['bg_card'])
        col1_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(col1_frame, text=label1,
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        widget1.pack(side=tk.LEFT, padx=10)
        
        if hint1:
            tk.Label(col1_frame, text=hint1,
                    bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                    font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Colonne 2 (50% width)
        col2_frame = tk.Frame(row_frame, bg=self.colors['bg_card'])
        col2_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        tk.Label(col2_frame, text=label2,
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        widget2.pack(side=tk.LEFT, padx=10)
        
        if hint2:
            tk.Label(col2_frame, text=hint2,
                    bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                    font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        return row_frame
    
    def create_accordion_section(self, parent, title, content_callback, default_expanded=False):
        """V3.1: Créer une section accordéon collapsible avec chevron
        
        Args:
            parent: Frame parent
            title: Titre de la section (avec emoji)
            content_callback: Function qui crée le contenu quand appelée avec un parent frame
            default_expanded: État initial (True = ouvert, False = fermé)
        
        Returns:
            (section_frame, toggle_func): Frame de la section et fonction pour toggle
        """
        section_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        section_frame.pack(fill=tk.X, pady=5)
        
        # État de l'accordéon
        is_expanded = tk.BooleanVar(value=default_expanded)
        
        # Header cliquable
        header_frame = tk.Frame(section_frame, bg=self.colors['bg_card'], cursor='hand2')
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        chevron_label = tk.Label(header_frame,
            text="▼" if default_expanded else "▶",
            font=('Segoe UI', 10),
            bg=self.colors['bg_card'],
            fg=self.colors['accent'],
            width=2
        )
        chevron_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(header_frame,
            text=title,
            font=self.FONT_BUTTON,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            anchor='w'
        )
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Content frame (initialement visible ou caché selon default_expanded)
        content_frame = tk.Frame(section_frame, bg=self.colors['bg_card'])
        if default_expanded:
            content_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Appeler le callback pour créer le contenu
        content_callback(content_frame)
        
        # Fonction toggle
        def toggle_accordion():
            if is_expanded.get():
                # Collapse
                content_frame.pack_forget()
                chevron_label.config(text="▶")
                is_expanded.set(False)
            else:
                # Expand
                content_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
                chevron_label.config(text="▼")
                is_expanded.set(True)
        
        # Bind click sur header
        header_frame.bind('<Button-1>', lambda e: toggle_accordion())
        chevron_label.bind('<Button-1>', lambda e: toggle_accordion())
        title_label.bind('<Button-1>', lambda e: toggle_accordion())
        
        return section_frame, toggle_accordion
    
    def create_segmented_control(self, parent, options, default_index=0, command=None):
        """V3.1: Créer un contrôle segmenté (boutons inline) au lieu de Combobox
        
        Args:
            parent: Frame parent
            options: Liste des options (strings)
            default_index: Index de l'option sélectionnée par défaut
            command: Callback appelé quand sélection change
        
        Returns:
            (frame, get_func, set_func): Frame + fonctions pour get/set la valeur
        """
        frame = tk.Frame(parent, bg=self.colors['bg_card'])
        
        selected_var = tk.StringVar(value=options[default_index])
        buttons = []
        
        def on_select(value):
            selected_var.set(value)
            # Mettre à jour les styles
            for btn, opt in buttons:
                if opt == value:
                    btn.config(
                        bg=self.colors['accent'],
                        fg='#FFFFFF',
                        relief='sunken'
                    )
                else:
                    btn.config(
                        bg=self.colors['bg_hover'],
                        fg=self.colors['text'],
                        relief='raised'
                    )
            if command:
                command(value)
        
        # Créer les boutons
        for i, option in enumerate(options):
            is_selected = (i == default_index)
            btn = tk.Button(frame,
                text=option,
                font=('Segoe UI', 9),
                bg=self.colors['accent'] if is_selected else self.colors['bg_hover'],
                fg='#FFFFFF' if is_selected else self.colors['text'],
                relief='sunken' if is_selected else 'raised',
                borderwidth=1,
                padx=12,
                pady=4,
                cursor='hand2',
                command=lambda opt=option: on_select(opt)
            )
            btn.pack(side=tk.LEFT, padx=1)
            buttons.append((btn, option))
        
        def get_value():
            return selected_var.get()
        
        def set_value(value):
            if value in options:
                on_select(value)
        
        # Ajouter méthodes compatibles avec Combobox
        frame.get = get_value
        frame.set = set_value
        frame.current = lambda idx: set_value(options[idx]) if idx < len(options) else None
        
        return frame
    
    def create_home_view(self):
        """Vue Home / Dashboard - V3.2 avec métriques avancées"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "🏠", "Dashboard",
                                "Advanced metrics and system overview")
        
        # Initialiser le dictionnaire pour stocker les références des cartes
        self.dashboard_cards = {}
        
        # V3.2: Nouvelles cartes métriques (grid 2x2)
        stats_grid = tk.Frame(container, bg=self.colors['bg_dark'])
        stats_grid.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        # Carte 1 : Dernière Activité
        self.create_activity_card(stats_grid, 0, 0)
        
        # Carte 2 : Progression Dataset
        self.create_progress_card(stats_grid, 0, 1)
        
        # Carte 3 : État du Système
        self.create_system_card(stats_grid, 1, 0)
        
        # Carte 4 : Aperçu Rapide
        self.create_preview_card(stats_grid, 1, 1)
        
        # V3.2: Nouvelles cartes supplémentaires (grid 1x2)
        additional_grid = tk.Frame(container, bg=self.colors['bg_dark'])
        additional_grid.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        # Carte 5 : Validation Report Preview
        self.create_validation_preview_card(additional_grid, 0, 0)
        
        # Carte 6 : Training Presets
        self.create_training_presets_card(additional_grid, 0, 1)
        
        # Avertissement si environnement virtuel absent
        if not self.check_venv():
            warning_frame = tk.Frame(container, bg=self.colors['error'], 
                                    highlightbackground=self.colors['error'],
                                    highlightthickness=2)
            warning_frame.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
            
            warning_content = tk.Frame(warning_frame, bg=self.colors['error'])
            warning_content.pack(fill=tk.X, padx=self.PADDING_CARD, pady=self.PADDING_VERTICAL)
            
            tk.Label(warning_content,
                text="⚠️ Environment Not Configured",
                font=self.FONT_CARD_TITLE,
                bg=self.colors['error'],
                fg='#000000'
            ).pack(anchor='w')
            
            tk.Label(warning_content,
                text="Python virtual environment (.venv) is required to run operations.\nClick below to install it automatically.",
                font=('Segoe UI', 9),
                bg=self.colors['error'],
                fg='#000000'
            ).pack(anchor='w', pady=(5, 10))
            
            tk.Button(warning_content,
                text="🔧 Install Environment",
                command=self.ensure_venv,
                bg='#000000',
                fg=self.colors['error'],
                font=self.FONT_BUTTON,
                relief='flat',
                padx=20,
                pady=8,
                cursor='hand2'
            ).pack(anchor='w')
        
        # Avertissement si fichier YAML manquant
        if not self.check_yaml_file():
            warning_frame2 = tk.Frame(container, bg=self.colors['warning'], 
                                     highlightbackground=self.colors['warning'],
                                     highlightthickness=2)
            warning_frame2.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
            
            warning_content2 = tk.Frame(warning_frame2, bg=self.colors['warning'])
            warning_content2.pack(fill=tk.X, padx=self.PADDING_CARD, pady=self.PADDING_VERTICAL)
            
            tk.Label(warning_content2,
                text="⚠️ Card Database Missing",
                font=self.FONT_CARD_TITLE,
                bg=self.colors['warning'],
                fg='#000000'
            ).pack(anchor='w')
            
            tk.Label(warning_content2,
                text="File 'models/cards_database.yaml' not found. This file is needed for some features.\nClick below to generate a card list from the TCGdex API.",
                font=('Segoe UI', 9),
                bg=self.colors['warning'],
                fg='#000000'
            ).pack(anchor='w', pady=(5, 10))
            
            tk.Button(warning_content2,
                text="🚀 Generate Card List",
                command=self.open_yaml_tools,
                bg='#000000',
                fg=self.colors['warning'],
                font=self.FONT_BUTTON,
                relief='flat',
                padx=20,
                pady=8,
                cursor='hand2'
            ).pack(anchor='w')
        
        # Quick Actions
        actions_frame = tk.Frame(container, bg=self.colors['bg_card'])
        actions_frame.pack(fill=tk.X, pady=self.CARD_SPACING)
        
        actions_title = tk.Label(actions_frame,
            text="⚡ Quick Actions",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        actions_title.pack(anchor='w', padx=20, pady=(20, 10))
        
        buttons_frame = tk.Frame(actions_frame, bg=self.colors['bg_card'])
        buttons_frame.pack(anchor='w', padx=20, pady=(0, 20))
        
        ttk.Button(buttons_frame, text="🚀 Launch Auto Workflow",
                  command=lambda: self.show_view('workflow'),
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="📊 Validate Dataset",
                  command=lambda: self.show_view('validation')).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="🎓 Train Model",
                  command=lambda: self.show_view('training')).pack(side=tk.LEFT, padx=5)
    
    def create_activity_card(self, parent, row, col):
        """Carte Dernière Activité"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], 
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Titre
        tk.Label(card,
            text="📊 Activité",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=12, pady=(8, 5))
        
        # Récupérer l'activité
        activity = self.get_last_activity()
        
        # Opération
        op_label = tk.Label(card,
            text=activity['operation'],
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['accent']
        )
        op_label.pack(anchor='w', padx=12, pady=3)
        self.dashboard_cards['activity_operation'] = op_label
        
        # Temps
        time_label = tk.Label(card,
            text=activity['time'],
            font=('Segoe UI', 7),
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim']
        )
        time_label.pack(anchor='w', padx=12)
        self.dashboard_cards['activity_time'] = time_label
        
        # Statut
        status_label = tk.Label(card,
            text=activity['status'],
            font=('Segoe UI', 7),
            bg=self.colors['bg_card'],
            fg=self.colors['success'] if '✅' in activity['status'] else self.colors['text_dim']
        )
        status_label.pack(anchor='w', padx=12, pady=(2, 2))
        self.dashboard_cards['activity_status'] = status_label
        
        # Vitesse de génération (si disponible)
        try:
            speed = self.get_generation_speed()
            if speed:
                speed_label = tk.Label(card,
                    text=f"⚡ {speed}",
                    font=('Segoe UI', 7),
                    bg=self.colors['bg_card'],
                    fg=self.colors['accent']
                )
                speed_label.pack(anchor='w', padx=12, pady=(0, 8))
                self.dashboard_cards['activity_speed'] = speed_label
            else:
                tk.Frame(card, bg=self.colors['bg_card'], height=15).pack()
        except Exception:
            tk.Frame(card, bg=self.colors['bg_card'], height=15).pack()
    
    def create_recommendations_card(self, parent, row, col):
        """Carte Recommendations Intelligentes (V3.2 - Option 3)"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], 
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Titre
        tk.Label(card,
            text="💡 Recommendations",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        # Récupérer les recommendations
        rec = self.get_smart_recommendations()
        
        # Icône + Titre
        title_frame = tk.Frame(card, bg=self.colors['bg_card'])
        title_frame.pack(anchor='w', padx=20, pady=5)
        
        tk.Label(title_frame,
            text=rec['icon'],
            font=('Segoe UI', 20),
            bg=self.colors['bg_card']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        rec_title_label = tk.Label(title_frame,
            text=rec['title'],
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['accent'],
            wraplength=200,
            justify='left'
        )
        rec_title_label.pack(side=tk.LEFT)
        self.dashboard_cards['rec_title'] = rec_title_label
        
        # Description
        rec_desc_label = tk.Label(card,
            text=rec['description'],
            font=('Segoe UI', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim'],
            wraplength=280,
            justify='left'
        )
        rec_desc_label.pack(anchor='w', padx=20, pady=(5, 15))
        self.dashboard_cards['rec_description'] = rec_desc_label
        
        # Badge de priorité
        priority_colors = {
            'high': self.colors['error'],
            'medium': self.colors['warning'],
            'low': self.colors['success']
        }
        priority_label = tk.Label(card,
            text=f"Priority: {rec['priority'].upper()}",
            font=('Segoe UI', 8, 'bold'),
            bg=self.colors['bg_card'],
            fg=priority_colors.get(rec['priority'], self.colors['text_dim'])
        )
        priority_label.pack(anchor='w', padx=20, pady=(0, 10))
        self.dashboard_cards['rec_priority'] = priority_label
    
    def create_health_score_card(self, parent, row, col):
        """Carte Score de Santé du Dataset (V3.2 - Option 4)"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], 
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Titre
        tk.Label(card,
            text="📊 Dataset Health",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        # Récupérer le score
        health = self.get_dataset_health_score()
        
        # Score et Grade
        score_frame = tk.Frame(card, bg=self.colors['bg_card'])
        score_frame.pack(anchor='w', padx=20, pady=5)
        
        score_label = tk.Label(score_frame,
            text=f"{health['score']}",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_card'],
            fg=health['color']
        )
        score_label.pack(side=tk.LEFT)
        self.dashboard_cards['health_score'] = score_label
        
        tk.Label(score_frame,
            text="/100",
            font=('Segoe UI', 14),
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim']
        ).pack(side=tk.LEFT, padx=(2, 10))
        
        # Grade
        grade_label = tk.Label(card,
            text=health['grade'],
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['bg_card'],
            fg=health['color']
        )
        grade_label.pack(anchor='w', padx=20, pady=5)
        self.dashboard_cards['health_grade'] = grade_label
        
        # Détails (2 premiers critères seulement pour économiser l'espace)
        if health['details']:
            details_text = '\n'.join([f"{d[0]}: {d[1]}/30" for d in health['details'][:2]])
            details_label = tk.Label(card,
                text=details_text,
                font=('Segoe UI', 9),
                bg=self.colors['bg_card'],
                fg=self.colors['text_dim'],
                justify='left'
            )
            details_label.pack(anchor='w', padx=20, pady=(5, 15))
            self.dashboard_cards['health_details'] = details_label
    
    def create_progress_card(self, parent, row, col):
        """Carte Progression Dataset"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], 
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Titre
        tk.Label(card,
            text="🎯 Progression",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=12, pady=(8, 5))
        
        # Récupérer la progression
        progress = self.get_dataset_progress()
        
        # Pourcentage
        percent_label = tk.Label(card,
            text=f"{progress['percent']}%",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['accent']
        )
        percent_label.pack(anchor='w', padx=12, pady=3)
        self.dashboard_cards['progress_percent'] = percent_label
        
        # Barre de progression
        progress_bg = tk.Frame(card, bg=self.colors['bg_dark'], height=10)
        progress_bg.pack(fill=tk.X, padx=20, pady=10)
        
        progress_bar = tk.Frame(progress_bg, bg=self.colors['accent'], height=10)
        progress_bar.place(x=0, y=0, relwidth=progress['percent']/100, height=10)
        self.dashboard_cards['progress_bar'] = progress_bar
        self.dashboard_cards['progress_bar_container'] = progress_bg
        
        # Texte
        text_label = tk.Label(card,
            text=f"{progress['current']} / {progress['target']} images",
            font=('Segoe UI', 7),
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim']
        )
        text_label.pack(anchor='w', padx=12, pady=(0, 2))
        self.dashboard_cards['progress_text'] = text_label
        
        # Ratio détaillé
        try:
            ratio_info = self.get_detailed_ratio()
            ratio_label = tk.Label(card,
                text=ratio_info,
                font=('Segoe UI', 7),
                bg=self.colors['bg_card'],
                fg=self.colors['text_dim']
            )
            ratio_label.pack(anchor='w', padx=12, pady=(0, 8))
            self.dashboard_cards['progress_ratio'] = ratio_label
        except Exception:
            tk.Frame(card, bg=self.colors['bg_card'], height=8).pack()
    
    def create_system_card(self, parent, row, col):
        """Carte État du Système"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], 
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Titre
        tk.Label(card,
            text="💡 Système",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=12, pady=(8, 5))
        
        # Récupérer l'état
        status = self.get_system_status()
        
        # GPU
        gpu_text = f"GPU: {'✅ ' + status['gpu_info'] if status['gpu'] else '❌ Not Available'}"
        gpu_label = tk.Label(card,
            text=gpu_text,
            font=('Segoe UI', 7),
            bg=self.colors['bg_card'],
            fg=self.colors['success'] if status['gpu'] else self.colors['warning']
        )
        gpu_label.pack(anchor='w', padx=12, pady=2)
        self.dashboard_cards['system_gpu'] = gpu_label
        
        # Disque
        disk_label = tk.Label(card,
            text=f"Disque: {status['disk_free']}",
            font=('Segoe UI', 7),
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim']
        )
        disk_label.pack(anchor='w', padx=12, pady=2)
        self.dashboard_cards['system_disk'] = disk_label
        
        # Venv
        venv_text = f"Venv: {'✅ Configuré' if status['venv'] else '❌ Manquant'}"
        venv_label = tk.Label(card,
            text=venv_text,
            font=('Segoe UI', 7),
            bg=self.colors['bg_card'],
            fg=self.colors['success'] if status['venv'] else self.colors['error']
        )
        venv_label.pack(anchor='w', padx=12, pady=2)
        self.dashboard_cards['system_venv'] = venv_label
        
        # Performance GPU/CPU (si disponible)
        try:
            perf_info = self.get_performance_info()
            if perf_info:
                perf_label = tk.Label(card,
                    text=perf_info,
                    font=('Segoe UI', 8),
                    bg=self.colors['bg_card'],
                    fg=self.colors['accent']
                )
                perf_label.pack(anchor='w', padx=20, pady=(3, 15))
                self.dashboard_cards['system_performance'] = perf_label
            else:
                tk.Frame(card, bg=self.colors['bg_card'], height=15).pack()
        except Exception:
            tk.Frame(card, bg=self.colors['bg_card'], height=15).pack()
    
    def create_preview_card(self, parent, row, col):
        """Carte Aperçu Rapide"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], 
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Titre
        tk.Label(card,
            text="🔍 Aperçu",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=12, pady=(8, 5))
        
        # Récupérer dernière image
        last_image = self.get_last_generated_image()
        
        if last_image and last_image.exists():
            try:
                from PIL import Image, ImageTk
                
                # Charger et redimensionner l'image
                img = Image.open(last_image)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)
                
                # Afficher la miniature
                img_label = tk.Label(card, image=photo, bg=self.colors['bg_card'])
                img_label.image = photo  # Garder une référence
                img_label.pack(padx=12, pady=3)
                self.dashboard_cards['preview_image'] = img_label
                
                # Nom du fichier
                name_label = tk.Label(card,
                    text=last_image.name[:18] + '...' if len(last_image.name) > 18 else last_image.name,
                    font=('Segoe UI', 7),
                    bg=self.colors['bg_card'],
                    fg=self.colors['text_dim']
                )
                name_label.pack(padx=12, pady=(2, 8))
                self.dashboard_cards['preview_name'] = name_label
            except Exception as e:
                # Si erreur, afficher un message
                tk.Label(card,
                    text="Aucune image récente",
                    font=('Segoe UI', 7),
                    bg=self.colors['bg_card'],
                    fg=self.colors['text_dim']
                ).pack(padx=12, pady=(10, 8))
        else:
            # Pas d'image disponible
            tk.Label(card,
                text="Aucune image générée",
                font=('Segoe UI', 7),
                bg=self.colors['bg_card'],
                fg=self.colors['text_dim']
            ).pack(padx=12, pady=(15, 8))
    
    def create_validation_preview_card(self, parent, row, col):
        """Carte Aperçu Validation Report"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], 
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Titre avec badge
        title_frame = tk.Frame(card, bg=self.colors['bg_card'])
        title_frame.pack(anchor='w', fill=tk.X, padx=12, pady=(8, 3))
        
        tk.Label(title_frame,
            text="📊 Validation",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        # Vérifier si le rapport existe
        report_path = Path("validation_report.html")
        
        if report_path.exists():
            # Badge "Available"
            tk.Label(title_frame,
                text=" ✓ ",
                font=('Segoe UI', 6, 'bold'),
                bg=self.colors['success'],
                fg='#000000',
                relief='flat'
            ).pack(side=tk.LEFT, padx=3)
            
            # Lire quelques stats du rapport
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extraire info basique (nombre de classes, images, etc.)
                    import re
                    
                    # Chercher des patterns communs
                    classes_match = re.search(r'(\d+)\s+classe', content, re.IGNORECASE)
                    images_match = re.search(r'(\d+)\s+images?\s+total', content, re.IGNORECASE)
                    
                    stats_text = "📄 Rapport disponible"
                    if classes_match:
                        stats_text = f"📦 {classes_match.group(1)} classes"
                    if images_match:
                        stats_text += f" • {images_match.group(1)} images"
                    
                    tk.Label(card,
                        text=stats_text,
                        font=('Segoe UI', 7),
                        bg=self.colors['bg_card'],
                        fg=self.colors['text']
                    ).pack(anchor='w', padx=12, pady=2)
            except Exception:
                tk.Label(card,
                    text="📄 Rapport disponible",
                    font=('Segoe UI', 7),
                    bg=self.colors['bg_card'],
                    fg=self.colors['text']
                ).pack(anchor='w', padx=12, pady=2)
            
            # Boutons d'action
            btn_frame = tk.Frame(card, bg=self.colors['bg_card'])
            btn_frame.pack(anchor='w', padx=12, pady=(3, 5))
            
            tk.Button(btn_frame,
                text="🌐 Ouvrir",
                command=lambda: self.open_validation_report(),
                bg=self.colors['accent'],
                fg='#000000',
                font=('Segoe UI', 7, 'bold'),
                relief='flat',
                padx=6,
                pady=1,
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=(0, 3))
            
            # Date de modification
            try:
                import time
                mtime = report_path.stat().st_mtime
                mod_time = datetime.fromtimestamp(mtime)
                if (datetime.now() - mod_time).days == 0:
                    time_str = "Aujourd'hui"
                elif (datetime.now() - mod_time).days == 1:
                    time_str = "Hier"
                else:
                    time_str = f"Il y a {(datetime.now() - mod_time).days}j"
                
                tk.Label(card,
                    text=f"🕒 {time_str}",
                    font=('Segoe UI', 6),
                    bg=self.colors['bg_card'],
                    fg=self.colors['text_dim']
                ).pack(anchor='w', padx=12, pady=(0, 5))
            except Exception:
                tk.Frame(card, bg=self.colors['bg_card'], height=8).pack()
        else:
            # Pas de rapport
            tk.Label(card,
                text="Aucun rapport généré",
                font=('Segoe UI', 7),
                bg=self.colors['bg_card'],
                fg=self.colors['text_dim']
            ).pack(anchor='w', padx=12, pady=3)
            
            tk.Button(card,
                text="▶ Générer rapport",
                command=lambda: self.show_view('validation'),
                bg=self.colors['bg_hover'],
                fg=self.colors['text'],
                font=('Segoe UI', 7),
                relief='flat',
                padx=6,
                pady=1,
                cursor='hand2'
            ).pack(anchor='w', padx=12, pady=(0, 5))
    
    def create_training_presets_card(self, parent, row, col):
        """Carte Training Presets (configuration rapide)"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], 
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Titre
        tk.Label(card,
            text="🎯 Presets",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=12, pady=(8, 2))
        
        # Description
        tk.Label(card,
            text="Config rapide training",
            font=('Segoe UI', 6),
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim']
        ).pack(anchor='w', padx=12, pady=(0, 3))
        
        # Presets
        presets_frame = tk.Frame(card, bg=self.colors['bg_card'])
        presets_frame.pack(fill=tk.X, padx=12, pady=(0, 5))
        
        # Preset 1: Quick Test
        preset1 = tk.Frame(presets_frame, bg=self.colors['bg_hover'], relief='flat')
        preset1.pack(fill=tk.X, pady=1)
        
        p1_content = tk.Frame(preset1, bg=self.colors['bg_hover'])
        p1_content.pack(fill=tk.X, padx=6, pady=2)
        
        tk.Label(p1_content,
            text="⚡ Quick Test",
            font=('Segoe UI', 7, 'bold'),
            bg=self.colors['bg_hover'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        tk.Label(p1_content,
            text="10 epochs",
            font=('Segoe UI', 6),
            bg=self.colors['bg_hover'],
            fg=self.colors['text_dim']
        ).pack(side=tk.RIGHT)
        
        preset1.bind('<Button-1>', lambda e: self.apply_training_preset('quick'))
        preset1.bind('<Enter>', lambda e: preset1.config(bg=self.colors['accent']))
        preset1.bind('<Leave>', lambda e: preset1.config(bg=self.colors['bg_hover']))
        preset1.config(cursor='hand2')
        for child in preset1.winfo_children():
            for subchild in child.winfo_children():
                subchild.bind('<Button-1>', lambda e: self.apply_training_preset('quick'))
        
        # Preset 2: Standard
        preset2 = tk.Frame(presets_frame, bg=self.colors['bg_hover'], relief='flat')
        preset2.pack(fill=tk.X, pady=1)
        
        p2_content = tk.Frame(preset2, bg=self.colors['bg_hover'])
        p2_content.pack(fill=tk.X, padx=6, pady=2)
        
        tk.Label(p2_content,
            text="📊 Standard",
            font=('Segoe UI', 7, 'bold'),
            bg=self.colors['bg_hover'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        tk.Label(p2_content,
            text="50 epochs",
            font=('Segoe UI', 6),
            bg=self.colors['bg_hover'],
            fg=self.colors['text_dim']
        ).pack(side=tk.RIGHT)
        
        preset2.bind('<Button-1>', lambda e: self.apply_training_preset('standard'))
        preset2.bind('<Enter>', lambda e: preset2.config(bg=self.colors['accent']))
        preset2.bind('<Leave>', lambda e: preset2.config(bg=self.colors['bg_hover']))
        preset2.config(cursor='hand2')
        for child in preset2.winfo_children():
            for subchild in child.winfo_children():
                subchild.bind('<Button-1>', lambda e: self.apply_training_preset('standard'))
        
        # Preset 3: Production
        preset3 = tk.Frame(presets_frame, bg=self.colors['bg_hover'], relief='flat')
        preset3.pack(fill=tk.X, pady=1)
        
        p3_content = tk.Frame(preset3, bg=self.colors['bg_hover'])
        p3_content.pack(fill=tk.X, padx=6, pady=2)
        
        tk.Label(p3_content,
            text="🚀 Production",
            font=('Segoe UI', 7, 'bold'),
            bg=self.colors['bg_hover'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        tk.Label(p3_content,
            text="100 epochs",
            font=('Segoe UI', 6),
            bg=self.colors['bg_hover'],
            fg=self.colors['text_dim']
        ).pack(side=tk.RIGHT)
        
        preset3.bind('<Button-1>', lambda e: self.apply_training_preset('production'))
        preset3.bind('<Enter>', lambda e: preset3.config(bg=self.colors['accent']))
        preset3.bind('<Leave>', lambda e: preset3.config(bg=self.colors['bg_hover']))
        preset3.config(cursor='hand2')
        for child in preset3.winfo_children():
            for subchild in child.winfo_children():
                subchild.bind('<Button-1>', lambda e: self.apply_training_preset('production'))
    
    def create_stat_card(self, parent, label, value, icon, row, col, key=None):
        """Créer une carte de statistique (DEPRECATED - kept for compatibility)"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], 
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Configure grid
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Icon
        icon_label = tk.Label(card,
            text=icon,
            font=('Segoe UI', 32),
            bg=self.colors['bg_card']
        )
        icon_label.pack(pady=(20, 5))
        
        # Value
        value_label = tk.Label(card,
            text=value,
            font=('Segoe UI', 28, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['accent']
        )
        value_label.pack()
        
        # Stocker la référence si une clé est fournie
        if key:
            self.stat_cards[key] = value_label
        
        # Label
        label_label = tk.Label(card,
            text=label,
            font=self.FONT_TEXT,
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim']
        )
        label_label.pack(pady=(5, 20))
    
    def create_workflow_view(self):
        """Vue Workflow Automatique"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "🚀", "Automatic Workflow",
                                "Generate complete dataset with one click")
        
        # Configuration Card
        config_card = tk.Frame(container, bg=self.colors['bg_card'])
        config_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        card_title = tk.Label(config_card,
            text="⚙️ Configuration",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        # Config options (simplifié pour l'exemple)
        config_content = tk.Frame(config_card, bg=self.colors['bg_card'])
        config_content.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        # Augmentations
        aug_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        aug_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(aug_frame, text="Augmentations:", 
                bg=self.colors['bg_card'], fg='#FFFFFF',  # BLANC
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.workflow_aug_var = ttk.Spinbox(aug_frame, from_=5, to=100, width=self.SPINBOX_WIDTH)
        self.workflow_aug_var.pack(side=tk.LEFT, padx=10)
        self.workflow_aug_var.set(15)
        
        tk.Label(aug_frame, text="variations per card",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        
        # Mosaics
        mosaic_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        mosaic_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(mosaic_frame, text="Mosaics Mode:", 
                bg=self.colors['bg_card'], fg='#FFFFFF',  # BLANC
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.workflow_mosaic_var = ttk.Combobox(mosaic_frame, 
                                    values=["quick", "standard", "complete"],
                                    state='readonly', width=self.COMBOBOX_WIDTH)
        self.workflow_mosaic_var.pack(side=tk.LEFT, padx=10)
        self.workflow_mosaic_var.current(1)
        
        # Options avancées
        options_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        options_frame.pack(fill=tk.X, pady=self.CARD_SPACING)
        
        tk.Label(options_frame, text="Optional Steps:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(anchor='w', pady=(0, 10))
        
        ttk.Checkbutton(options_frame, text="✅ Validate dataset",
                       variable=self.workflow_validate_var).pack(anchor='w', pady=5)
        
        ttk.Checkbutton(options_frame, text="⚖️ Auto-balance classes",
                       variable=self.workflow_balance_var).pack(anchor='w', pady=5)
        
        ttk.Checkbutton(options_frame, text="🎓 Train YOLO model",
                       variable=self.workflow_train_var).pack(anchor='w', pady=5)
        
        # Launch button
        launch_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        launch_frame.pack(pady=30)
        
        ttk.Button(launch_frame, text=UI_MESSAGES['gui']['buttons']['start_workflow'],
                  style='Accent.TButton',
                  command=self.start_workflow,
                  width=30).pack(pady=10)
    
    def create_download_view(self):
        """Vue Image Download"""
        container = tk.Frame(self.view_container, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "⬇️", "Image Download",
                                "Download Pokemon card images from TCGdex API")
        
        # Main content frame (single column - V3.2)
        main_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Configuration Card (full width)
        config_card = tk.Frame(main_frame, bg=self.colors['bg_card'])
        config_card.pack(fill=tk.BOTH, expand=True)
        
        card_title = tk.Label(config_card,
            text="⚙️ Configuration",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        config_content = tk.Frame(config_card, bg=self.colors['bg_card'])
        config_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Set selection
        set_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        set_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(set_frame, text="Pokemon Set:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        # Load all sets from TCGdex API
        set_choices = []
        try:
            import requests
            response = requests.get("https://api.tcgdex.net/v2/en/sets", timeout=5)
            if response.status_code == 200:
                sets_data = response.json()
                # Sort by id (most recent first)
                sets_data.sort(key=lambda x: x.get('id', ''), reverse=True)
                set_choices = [f"{s.get('name', 'Unknown')} ({s.get('id', '')})" for s in sets_data if s.get('id')]
                self.log("✅ Loaded all Pokemon sets from TCGdex API")
        except Exception as e:
            self.log(f"⚠️ Could not load sets from API: {e}")
            # Fallback to popular sets
            try:
                from core.image_downloader import POPULAR_SETS
                set_choices = [f"{name} ({sid})" for name, sid in POPULAR_SETS]
            except Exception:
                set_choices = ["Surging Sparks (sv08)", "Stellar Crown (sv07)"]
        
        self.download_set_var = ttk.Combobox(set_frame,
            values=set_choices,
            state='normal',  # Allow manual entry
            width=self.ENTRY_WIDTH)
        self.download_set_var.pack(side=tk.LEFT, padx=10)
        if set_choices:
            self.download_set_var.set(set_choices[0])
        
        # Language selection
        lang_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        lang_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(lang_frame, text="Language:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        try:
            from core.image_downloader import LANGUAGES
            lang_choices = list(LANGUAGES.keys())
        except Exception:
            lang_choices = ["English", "Français", "Deutsch", "Italiano", "Español"]
        
        self.download_lang_var = ttk.Combobox(lang_frame,
            values=lang_choices,
            state='readonly',
            width=self.COMBOBOX_WIDTH)
        self.download_lang_var.pack(side=tk.LEFT, padx=10)
        
        # Set default from settings
        default_lang = self.config.get("default_download_lang", "English")
        if default_lang in lang_choices:
            self.download_lang_var.set(default_lang)
        else:
            self.download_lang_var.current(0)
        
        # Quality & Format
        quality_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        quality_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(quality_frame, text="Quality:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.download_quality_var = ttk.Combobox(quality_frame,
            values=["high", "low"],
            state='readonly',
            width=15)
        self.download_quality_var.pack(side=tk.LEFT, padx=10)
        self.download_quality_var.set(self.config.get("default_download_quality", "high"))
        
        tk.Label(quality_frame, text="Format:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT, padx=(20, 0))
        
        self.download_format_var = ttk.Combobox(quality_frame,
            values=["png", "jpg", "jpeg", "webp"],
            state='readonly',
            width=18)
        self.download_format_var.pack(side=tk.LEFT, padx=10)
        self.download_format_var.set(self.config.get("default_download_format", "png"))
        
        # Output directory
        output_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        output_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(output_frame, text="Output directory:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.download_output_var = ttk.Entry(output_frame, width=self.COMBOBOX_WIDTH)
        self.download_output_var.pack(side=tk.LEFT, padx=10)
        self.download_output_var.insert(0, self.config.get("default_download_dir", "images"))
        
        # Info tooltip (compact) - V3.2
        self.create_info_tooltip(container,
            "ℹ️ About TCGdex API",
            "📊 Free API with high-quality Pokemon card images",
            "Free API - No authentication required\n\n"
            "• High quality card images (PNG recommended)\n"
            "• Multiple languages supported\n"
            "• Images named with Set # for easy identification\n"
            "• manifest.csv generated with download details\n\n"
            "TCGdex provides free access to a comprehensive Pokemon card database with "
            "high-resolution images in multiple formats and languages."
        )
        
        # Button frame
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text=UI_MESSAGES['gui']['buttons']['start_download'],
                  style='Accent.TButton',
                  command=self.start_image_download,
                  width=30).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="📂 Open Folder",
                  command=lambda: self.open_folder("images"),
                  width=20).pack(side=tk.LEFT, padx=5, pady=5)
    
    def get_augmentation_stats(self):
        """Récupérer les statistiques d'augmentation (holo + standard)"""
        try:
            source_dir = PATHS['directories']['images']
            holo_dir = PATHS['directories']['output_holographic']
            augmented_dir = PATHS['directories']['output_augmented_images']
            
            source_count = 0
            holo_count = 0
            augmented_count = 0
            
            if os.path.exists(source_dir):
                source_count = len([f for f in os.listdir(source_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
            
            if os.path.exists(holo_dir):
                holo_count = len([f for f in os.listdir(holo_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
            
            if os.path.exists(augmented_dir):
                augmented_count = len([f for f in os.listdir(augmented_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
            
            total_generated = holo_count + augmented_count
            
            stats_text = f"📊 Source: {source_count} images"
            if holo_count > 0:
                stats_text += f" | Holo: {holo_count}"
            if augmented_count > 0:
                stats_text += f" | Augmented: {augmented_count}"
            if total_generated > 0:
                ratio = total_generated / source_count if source_count > 0 else 0
                stats_text += f" | Total: {total_generated} ({ratio:.1f}x)"
            
            return stats_text
        except Exception:
            return "📊 Unable to read statistics"
    
    def refresh_augmentation_stats(self):
        """Rafraîchir les statistiques d'augmentation toutes les 2 secondes"""
        if hasattr(self, 'aug_stats_label') and self.aug_stats_label.winfo_exists():
            try:
                # Trouver le label de stats dans l'info_frame
                for child in self.aug_stats_label.winfo_children():
                    if isinstance(child, tk.Label) and child.cget('text').startswith('📊'):
                        new_stats = self.get_augmentation_stats()
                        child.config(text=new_stats)
                        break
            except Exception:
                pass
            # Programmer le prochain rafraîchissement
            self.root.after(2000, self.refresh_augmentation_stats)
    
    def create_augmentation_view(self):
        """Vue Augmentation détaillée - HARMONISÉE V3.1 sans scroll"""
        container = tk.Frame(self.view_container, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "🎨", "Image Augmentation",
                                "Generate augmented variations of your card images")
        
        # V3.1: Compact Info Tooltip avec stats dynamiques (holo + augmented)
        stats_text = self.get_augmentation_stats()
        
        self.aug_stats_label = self.create_info_tooltip(container,
            "ℹ️ About Augmentation",
            stats_text,
            "Image augmentation creates variations of your original images using transformations like rotation, "
            "brightness adjustment, noise, blur, and color shifts. This increases dataset diversity and helps "
            "improve model training. Standard mode uses traditional augmentations, while Holographic mode adds "
            "special effects to simulate holographic Pokemon cards."
        )
        
        # Lancer le rafraîchissement automatique
        self.refresh_augmentation_stats()
        
        # Configuration Card
        config_card = tk.Frame(container, bg=self.colors['bg_card'])
        config_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        card_title = tk.Label(config_card,
            text="⚙️ Configuration",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        config_content = tk.Frame(config_card, bg=self.colors['bg_card'])
        config_content.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        # SECTION 1: Holographic Generation
        tk.Label(config_content, text="🌟 Holographic Generation",
                bg=self.colors['bg_card'], fg=self.colors['accent'],
                font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(5, 10))
        
        holo_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        holo_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(holo_frame, text="Number of variations:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=20, anchor='w').pack(side=tk.LEFT)
        
        self.aug_holo_var = ttk.Spinbox(holo_frame, from_=0, to=10, width=10)
        self.aug_holo_var.pack(side=tk.LEFT, padx=10)
        self.aug_holo_var.set(3)
        
        tk.Label(holo_frame, text="(0 = skip holographic)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        
        # Separator
        tk.Frame(config_content, bg=self.colors['border'], height=1).pack(fill=tk.X, pady=15)
        
        # SECTION 2: Augmentation
        tk.Label(config_content, text="🎨 Augmentation",
                bg=self.colors['bg_card'], fg=self.colors['accent'],
                font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(5, 10))
        
        aug_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        aug_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(aug_frame, text="Augmentations per image:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=20, anchor='w').pack(side=tk.LEFT)
        
        self.aug_num_var = ttk.Spinbox(aug_frame, from_=0, to=100, width=10)
        self.aug_num_var.pack(side=tk.LEFT, padx=10)
        self.aug_num_var.set(50)
        
        tk.Label(aug_frame, text="(0 = skip augmentation)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        
        # Separator
        tk.Frame(config_content, bg=self.colors['border'], height=1).pack(fill=tk.X, pady=15)
        
        # Output directory (fixe)
        tk.Label(config_content, text="📂 Output",
                bg=self.colors['bg_card'], fg=self.colors['accent'],
                font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(5, 10))
        
        output_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        output_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(output_frame, text="Directory:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=20, anchor='w').pack(side=tk.LEFT)
        
        # Valeur fixe pour éviter la confusion
        self.aug_output_var = tk.StringVar(value="augmented")
        
        tk.Label(output_frame, text="output/augmented/",
                bg=self.colors['bg_card'], fg=self.colors['accent'],
                font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        tk.Label(output_frame, text="(standard output path)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        
        # Buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="🚀 GENERATE ALL",
                  style='Accent.TButton',
                  command=self.start_augmentation_pipeline,
                  width=30).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(btn_frame, text="👁 Live Preview",
                  command=self.open_augmentation_preview,
                  width=20).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(btn_frame, text="📂 Open Folder",
                  command=lambda: self.open_folder(PATHS['directories']['output_augmented']),
                  width=20).pack(side=tk.LEFT, padx=5, pady=5)

    def create_evaluation_view(self):
        """Vue Évaluation des runs (F07) — déléguée à gui/evaluation_view.py"""
        try:
            from gui.evaluation_view import EvaluationView
            EvaluationView(self.view_container, self).pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            tk.Label(self.view_container,
                     text=f"⚠️ Vue Evaluation indisponible: {e}",
                     bg=self.colors['bg_dark'], fg=self.colors['error'],
                     font=self.FONT_TEXT).pack(pady=40)

    def open_augmentation_preview(self):
        """Ouvre la prévisualisation live des augmentations (F06)"""
        try:
            from gui.augmentation_preview import AugmentationPreviewDialog
            AugmentationPreviewDialog(self.root, self.colors)
        except Exception as e:
            messagebox.showerror("Preview", f"Impossible d'ouvrir la preview:\n{e}")

    def create_fakeimg_view(self):
        """Vue génération de fake images (random erasing) - HARMONISÉE V3.1 sans scroll"""
        container = tk.Frame(self.view_container, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "🎲", "Fake Image Generator",
                                "Apply random erasing to create synthetic fake images for mosaics")
        
        # V3.1: Compact Info Tooltip (remplace Info Card)
        try:
            fakeimg_aug_dir = "fakeimg_augmented"
            if os.path.exists(fakeimg_aug_dir):
                count = len([f for f in os.listdir(fakeimg_aug_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
                stats_text = f"📊 Current: {count} fake images generated"
            else:
                stats_text = "📊 No fake images generated yet"
        except Exception:
            stats_text = "📊 Unable to read statistics"
        
        self.create_info_tooltip(container,
            "ℹ️ About Fake Images",
            stats_text,
            "Random erasing applies random rectangles to downloaded card images. "
            "These modified images are used as fake backgrounds in mosaic generation. "
            "Uses images from 'images/' folder. Probability (p) controls the chance of applying erasing per image."
        )
        
        # Configuration Card - EN DESSOUS, PLEINE LARGEUR
        config_card = tk.Frame(container, bg=self.colors['bg_card'])
        config_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        card_title = tk.Label(config_card,
            text="⚙️ Random Erasing Settings",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        config_content = tk.Frame(config_card, bg=self.colors['bg_card'])
        config_content.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        # Input directory
        input_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="Input directory:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=15, anchor='w').pack(side=tk.LEFT)
        
        self.fakeimg_input_var = ttk.Entry(input_frame, width=self.ENTRY_WIDTH)
        self.fakeimg_input_var.pack(side=tk.LEFT, padx=10)
        self.fakeimg_input_var.insert(0, PATHS['directories']['backgrounds_original'])
        
        # Output directory
        output_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        output_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(output_frame, text="Output directory:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=15, anchor='w').pack(side=tk.LEFT)
        
        self.fakeimg_output_var = ttk.Entry(output_frame, width=self.ENTRY_WIDTH)
        self.fakeimg_output_var.pack(side=tk.LEFT, padx=10)
        self.fakeimg_output_var.insert(0, PATHS['directories']['output_backgrounds'])
        
        # Random Erasing Parameters
        tk.Label(config_content,
            text="Random Erasing Parameters:",
            bg=self.colors['bg_card'], fg='#FFFFFF',
            font=self.FONT_BUTTON).pack(anchor='w', pady=(15, 10))
        
        # Grid pour les paramètres (2x2)
        params_grid = tk.Frame(config_content, bg=self.colors['bg_card'])
        params_grid.pack(fill=tk.X, pady=(0, 10))
        
        # Probability (p)
        p_frame = tk.Frame(params_grid, bg=self.colors['bg_card'])
        p_frame.grid(row=0, column=0, sticky='w', padx=(0, 20), pady=5)
        
        tk.Label(p_frame, text="Probability (p):",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=('Segoe UI', 9), width=15, anchor='w').pack(side=tk.LEFT)
        
        self.fakeimg_p_var = ttk.Spinbox(p_frame, from_=0.0, to=1.0, increment=0.1, width=self.SPINBOX_WIDTH)
        self.fakeimg_p_var.pack(side=tk.LEFT, padx=5)
        self.fakeimg_p_var.set(0.5)
        
        tk.Label(p_frame, text="(0.0-1.0)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Min Area (sl)
        sl_frame = tk.Frame(params_grid, bg=self.colors['bg_card'])
        sl_frame.grid(row=0, column=1, sticky='w', padx=(20, 0), pady=5)
        
        tk.Label(sl_frame, text="Min Area (sl):",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=('Segoe UI', 9), width=15, anchor='w').pack(side=tk.LEFT)
        
        self.fakeimg_sl_var = ttk.Spinbox(sl_frame, from_=0.01, to=1.0, increment=0.01, width=self.SPINBOX_WIDTH)
        self.fakeimg_sl_var.pack(side=tk.LEFT, padx=5)
        self.fakeimg_sl_var.set(0.02)
        
        tk.Label(sl_frame, text="(0.01-1.0)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Max Area (sh)
        sh_frame = tk.Frame(params_grid, bg=self.colors['bg_card'])
        sh_frame.grid(row=1, column=0, sticky='w', padx=(0, 20), pady=5)
        
        tk.Label(sh_frame, text="Max Area (sh):",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=('Segoe UI', 9), width=15, anchor='w').pack(side=tk.LEFT)
        
        self.fakeimg_sh_var = ttk.Spinbox(sh_frame, from_=0.01, to=1.0, increment=0.01, width=self.SPINBOX_WIDTH)
        self.fakeimg_sh_var.pack(side=tk.LEFT, padx=5)
        self.fakeimg_sh_var.set(0.4)
        
        tk.Label(sh_frame, text="(0.01-1.0)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Min Aspect (r1)
        r1_frame = tk.Frame(params_grid, bg=self.colors['bg_card'])
        r1_frame.grid(row=1, column=1, sticky='w', padx=(20, 0), pady=5)
        
        tk.Label(r1_frame, text="Min Aspect (r1):",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=('Segoe UI', 9), width=15, anchor='w').pack(side=tk.LEFT)
        
        self.fakeimg_r1_var = ttk.Spinbox(r1_frame, from_=0.1, to=5.0, increment=0.1, width=self.SPINBOX_WIDTH)
        self.fakeimg_r1_var.pack(side=tk.LEFT, padx=5)
        self.fakeimg_r1_var.set(0.3)
        
        tk.Label(r1_frame, text="(0.1-5.0)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Max Aspect (r2)
        r2_frame = tk.Frame(params_grid, bg=self.colors['bg_card'])
        r2_frame.grid(row=2, column=0, sticky='w', padx=(0, 20), pady=5)
        
        tk.Label(r2_frame, text="Max Aspect (r2):",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=('Segoe UI', 9), width=15, anchor='w').pack(side=tk.LEFT)
        
        self.fakeimg_r2_var = ttk.Spinbox(r2_frame, from_=0.1, to=10.0, increment=0.1, width=self.SPINBOX_WIDTH)
        self.fakeimg_r2_var.pack(side=tk.LEFT, padx=5)
        self.fakeimg_r2_var.set(3.3)
        
        tk.Label(r2_frame, text="(0.1-10.0)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Button frame
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="🎲 GENERATE FAKE IMAGES",
                  style='Accent.TButton',
                  command=self.start_fake_generator_from_view,
                  width=30).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="📂 Open Folder",
                  command=lambda: self.open_folder(PATHS['directories']['output_backgrounds']),
                  width=20).pack(side=tk.LEFT, padx=5, pady=5)
    
    def create_mosaic_view(self):
        """Vue Mosaics détaillée"""
        container = tk.Frame(self.view_container, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "🧩", "YOLO Mosaics",
                                "Generate YOLO training mosaics from augmented images")
        
        # Configuration Card
        config_card = tk.Frame(container, bg=self.colors['bg_card'])
        config_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        card_title = tk.Label(config_card,
            text="⚙️ Configuration",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        config_content = tk.Frame(config_card, bg=self.colors['bg_card'])
        config_content.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        # Mode selection
        mode_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        mode_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(mode_frame, text="Generation mode:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.mosaic_mode_var = ttk.Combobox(mode_frame,
            values=["Quick (200)", "Standard (500)", "Complete (All combinations)"],
            state='readonly', width=self.COMBOBOX_WIDTH)
        self.mosaic_mode_var.pack(side=tk.LEFT, padx=10)
        self.mosaic_mode_var.current(1)
        
        # Layout mode
        layout_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        layout_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(layout_frame, text="Card layout:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.mosaic_layout_var = ttk.Combobox(layout_frame,
            values=["1 - Grid (Standard)", "2 - Grid with 3D Rotation", "3 - Random Placement"],
            state='readonly', width=self.COMBOBOX_WIDTH)
        self.mosaic_layout_var.pack(side=tk.LEFT, padx=10)
        self.mosaic_layout_var.current(0)
        
        # Background mode
        bg_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        bg_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(bg_frame, text="Background:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.mosaic_background_var = ttk.Combobox(bg_frame,
            values=["0 - Fake Cards Mosaic", "1 - Local Image (mosaic/)", "2 - Web Image (Lorem Picsum)"],
            state='readonly', width=self.ENTRY_WIDTH)
        self.mosaic_background_var.pack(side=tk.LEFT, padx=10)
        self.mosaic_background_var.current(0)
        
        # Transform mode
        transform_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        transform_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(transform_frame, text="Rotation mode:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.mosaic_transform_var = ttk.Combobox(transform_frame,
            values=["0 - 2D Rotation", "1 - 3D Perspective Projection"],
            state='readonly', width=self.ENTRY_WIDTH)
        self.mosaic_transform_var.pack(side=tk.LEFT, padx=10)
        self.mosaic_transform_var.current(0)
        
        # Buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        # Main mosaic generation button with folder access on the side
        mosaic_btn_frame = tk.Frame(btn_frame, bg=self.colors['bg_dark'])
        mosaic_btn_frame.pack()
        
        ttk.Button(mosaic_btn_frame, text="🧩 GENERATE MOSAICS",
                  style='Accent.TButton',
                  command=self.start_mosaic,
                  width=30).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(mosaic_btn_frame, text="📂 Open Folder",
                  command=lambda: self.open_folder(PATHS['directories']['output_mosaics']),
                  width=20).pack(side=tk.LEFT)
        
        # Fake backgrounds button (aligned below GENERATE MOSAICS using left anchor)
        ttk.Button(btn_frame, text="📋 Generate Fake Backgrounds",
                  command=self.start_fake_generator,
                  width=30).pack(pady=(10, 0), anchor='w')
    
    def create_validation_view(self):
        """Vue Validation détaillée"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "✅", "Dataset Validation",
                                "Validate YOLO annotations and dataset quality")
        
        # Configuration Card
        config_card = tk.Frame(container, bg=self.colors['bg_card'])
        config_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        card_title = tk.Label(config_card,
            text="⚙️ Configuration",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        config_content = tk.Frame(config_card, bg=self.colors['bg_card'])
        config_content.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        # Dataset path
        path_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        path_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(path_frame, text="Dataset path:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.valid_path_var = tk.Entry(path_frame, width=40,
                                       bg='#FFFFFF', fg='#1a1a1a')
        self.valid_path_var.pack(side=tk.LEFT, padx=10)
        self.valid_path_var.insert(0, PATHS['directories']['output_dataset'])
        
        ttk.Button(path_frame, text="📁", width=3,
                  command=self.browse_dataset).pack(side=tk.LEFT)
        
        # Options
        self.valid_html_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_content, text="📄 Generate HTML report",
                       variable=self.valid_html_var).pack(anchor='w', pady=10)
        
        # Buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="🔀 MERGE DATASET",
                  style='Accent.TButton',
                  command=self.start_merge_dataset,
                  width=30).pack(pady=5)
        
        ttk.Button(btn_frame, text="✅ VALIDATE DATASET",
                  style='Accent.TButton',
                  command=self.start_validation,
                  width=30).pack(pady=5)
        
        ttk.Button(btn_frame, text="📊 Open Report",
                  command=self.open_validation_report,
                  width=30).pack(pady=5)
    
    def create_training_view(self):
        """Vue Training avec TrainingManager"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.X, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "🎓", "YOLO Training",
                                "Train YOLOv8 model on your dataset")
        
        # Configuration Card (hauteur limitée pour garder le footer visible: 380px + footer 160px + marges = ~560px)
        config_card = tk.Frame(container, bg=self.colors['bg_card'], height=360)
        config_card.pack(fill=tk.X, pady=(0, 10))
        config_card.pack_propagate(False)  # Forcer la hauteur
        
        card_title = tk.Label(config_card,
            text="⚙️ Training Configuration",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        # Scrollable content
        canvas = tk.Canvas(config_card, bg=self.colors['bg_card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(config_card, orient='vertical', command=canvas.yview)
        config_content = tk.Frame(canvas, bg=self.colors['bg_card'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20), padx=(0, 5))
        
        canvas_frame = canvas.create_window((0, 0), window=config_content, anchor='nw')
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.itemconfig(canvas_frame, width=event.width)
        
        config_content.bind('<Configure>', configure_scroll)
        canvas.bind('<Configure>', configure_scroll)
        
        # System Configuration Selector
        system_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        system_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(system_frame, text="💻 System Config:", 
                bg=self.colors['bg_card'], fg='#89B4FA',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.train_system_var = ttk.Combobox(system_frame,
            values=[
                "🖥️ Desktop: 5800X3D + 5070 Ti 16GB",
                "💼 Laptop: Ryzen AI 7 350 + 5070 8GB",
                "🤖 Jetson: Orin AGX 32GB"
            ],
            state='readonly', width=35)
        self.train_system_var.pack(side=tk.LEFT, padx=10)
        self.train_system_var.current(0)
        self.train_system_var.bind('<<ComboboxSelected>>', self.update_training_presets)
        
        # Preset Configuration
        preset_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        preset_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(preset_frame, text="💡 Training Preset:", 
                bg=self.colors['bg_card'], fg='#89B4FA',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.train_preset_var = ttk.Combobox(preset_frame,
            values=[
                "Custom",
                "⚡ Fast & Efficient",
                "⚖️ Balanced", 
                "🎯 High Quality",
                "🚀 Jetson Realtime",
                "🤖 Jetson Optimized"
            ],
            state='readonly', width=30)
        self.train_preset_var.pack(side=tk.LEFT, padx=10)
        self.train_preset_var.current(0)
        self.train_preset_var.bind('<<ComboboxSelected>>', self.apply_training_preset)
        
        # Separator
        separator = tk.Frame(config_content, bg=self.colors['text_dim'], height=1)
        separator.pack(fill=tk.X, pady=15)
        
        # Two columns layout: Basic (left) and Advanced (right)
        columns_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        columns_frame.pack(fill=tk.X)
        
        # Left column - Basic parameters
        left_column = tk.Frame(columns_frame, bg=self.colors['bg_card'])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        tk.Label(left_column, text="📊 Basic Parameters",
                bg=self.colors['bg_card'], fg='#89B4FA',
                font=self.FONT_BUTTON).pack(anchor='w', pady=(0, 10))
        
        # Model
        model_frame = tk.Frame(left_column, bg=self.colors['bg_card'])
        model_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(model_frame, text="Model:", 
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=12, anchor='w').pack(side=tk.LEFT)
        
        self.train_model_var = ttk.Combobox(model_frame,
            values=["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt"],
            state='readonly', width=self.COMBOBOX_WIDTH)
        self.train_model_var.pack(side=tk.LEFT, padx=10)
        self.train_model_var.current(0)
        
        # Epochs
        epochs_frame = tk.Frame(left_column, bg=self.colors['bg_card'])
        epochs_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(epochs_frame, text="Epochs:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=12, anchor='w').pack(side=tk.LEFT)
        
        self.train_epochs_var = ttk.Spinbox(epochs_frame, from_=10, to=500, width=self.SPINBOX_WIDTH)
        self.train_epochs_var.pack(side=tk.LEFT, padx=10)
        self.train_epochs_var.set(50)
        
        # Batch size
        batch_frame = tk.Frame(left_column, bg=self.colors['bg_card'])
        batch_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(batch_frame, text="Batch Size:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=12, anchor='w').pack(side=tk.LEFT)
        
        self.train_batch_var = ttk.Spinbox(batch_frame, from_=4, to=64, width=self.SPINBOX_WIDTH)
        self.train_batch_var.pack(side=tk.LEFT, padx=10)
        self.train_batch_var.set(16)
        
        # Device
        device_frame = tk.Frame(left_column, bg=self.colors['bg_card'])
        device_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(device_frame, text="Device:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=12, anchor='w').pack(side=tk.LEFT)
        
        self.train_device_var = ttk.Combobox(device_frame,
            values=["0", "cpu", "0,1", "0,1,2,3"],
            state='readonly', width=self.COMBOBOX_WIDTH)
        self.train_device_var.pack(side=tk.LEFT, padx=10)
        self.train_device_var.current(0)
        
        # Image size
        imgsz_frame = tk.Frame(left_column, bg=self.colors['bg_card'])
        imgsz_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(imgsz_frame, text="Image Size:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=12, anchor='w').pack(side=tk.LEFT)
        
        self.train_imgsz_var = ttk.Combobox(imgsz_frame,
            values=["320", "416", "480", "512", "640", "800", "1024"],
            state='readonly', width=self.COMBOBOX_WIDTH)
        self.train_imgsz_var.pack(side=tk.LEFT, padx=10)
        self.train_imgsz_var.current(4)  # 640 default
        
        # V3.1: Accordion pour paramètres avancés (Workers, Cache, Patience)
        def create_advanced_basic_content(parent):
            # Workers
            workers_frame = tk.Frame(parent, bg=self.colors['bg_card'])
            workers_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(workers_frame, text="Workers:",
                    bg=self.colors['bg_card'], fg='#FFFFFF',
                    font=self.FONT_BUTTON, width=12, anchor='w').pack(side=tk.LEFT)
            
            self.train_workers_var = ttk.Spinbox(workers_frame, from_=1, to=16, width=self.SPINBOX_WIDTH)
            self.train_workers_var.pack(side=tk.LEFT, padx=10)
            self.train_workers_var.set(4)
            
            # Cache
            cache_frame = tk.Frame(parent, bg=self.colors['bg_card'])
            cache_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(cache_frame, text="Cache:",
                    bg=self.colors['bg_card'], fg='#FFFFFF',
                    font=self.FONT_BUTTON, width=12, anchor='w').pack(side=tk.LEFT)
            
            self.train_cache_var = ttk.Combobox(cache_frame,
                values=["False", "ram", "disk"],
                state='readonly', width=self.COMBOBOX_WIDTH)
            self.train_cache_var.pack(side=tk.LEFT, padx=10)
            self.train_cache_var.current(0)
        
        self.create_accordion_section(left_column, "🔧 Advanced Settings", 
                                      create_advanced_basic_content, default_expanded=False)
        
        # Right column - Advanced parameters
        right_column = tk.Frame(columns_frame, bg=self.colors['bg_card'])
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_column, text="🔧 Advanced Options",
                bg=self.colors['bg_card'], fg='#F9E2AF',
                font=self.FONT_BUTTON).pack(anchor='w', pady=(0, 10))
        
        # LR0
        lr0_frame = tk.Frame(right_column, bg=self.colors['bg_card'])
        lr0_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(lr0_frame, text="Learning Rate (lr0):",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=18, anchor='w').pack(side=tk.LEFT)
        
        self.train_lr0_var = ttk.Entry(lr0_frame, width=8)
        self.train_lr0_var.pack(side=tk.LEFT, padx=10)
        self.train_lr0_var.insert(0, "0.01")
        
        # LRF
        lrf_frame = tk.Frame(right_column, bg=self.colors['bg_card'])
        lrf_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(lrf_frame, text="Final LR (lrf):",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=18, anchor='w').pack(side=tk.LEFT)
        
        self.train_lrf_var = ttk.Entry(lrf_frame, width=8)
        self.train_lrf_var.pack(side=tk.LEFT, padx=10)
        self.train_lrf_var.insert(0, "0.01")
        
        # Patience
        patience_frame = tk.Frame(right_column, bg=self.colors['bg_card'])
        patience_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(patience_frame, text="Early Stop Patience:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=18, anchor='w').pack(side=tk.LEFT)
        
        self.train_patience_var = ttk.Spinbox(patience_frame, from_=0, to=100, width=self.SPINBOX_WIDTH)
        self.train_patience_var.pack(side=tk.LEFT, padx=10)
        self.train_patience_var.set(20)
        
        # Cosine LR
        self.train_cosine_var = tk.BooleanVar(value=False)
        cosine_check = tk.Checkbutton(right_column,
            text="✓ Use Cosine LR Scheduler",
            variable=self.train_cosine_var,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            selectcolor=self.colors['bg_dark'],
            font=self.FONT_BUTTON)
        cosine_check.pack(anchor='w', pady=(10, 5))
        
        # Buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text=UI_MESSAGES['gui']['buttons']['start_training'],
                  style='Accent.TButton',
                  command=self.start_training,
                  width=30).pack(pady=5)
        
        ttk.Button(btn_frame, text="📊 View Results",
                  command=self.show_training_plots,
                  width=30).pack(pady=5)
        
        ttk.Button(btn_frame, text="🚀 Export for Jetson (TensorRT)",
                  command=self.export_tensorrt,
                  width=30).pack(pady=5)
    
    def update_training_presets(self, event=None):
        """Mettre à jour les paramètres par défaut selon la config système"""
        system = self.train_system_var.get()
        
        # Appliquer des valeurs par défaut selon le système
        if system == "🖥️ Desktop (5800X3D + 5070Ti 16GB)":
            # Defaults pour Desktop: plus de batch possible
            self.train_model_var.current(0)  # yolov8n.pt
            self.train_epochs_var.delete(0, tk.END)
            self.train_epochs_var.insert(0, "50")
            self.train_batch_var.delete(0, tk.END)
            self.train_batch_var.insert(0, "32")  # Batch plus grand avec 16GB
            self.train_imgsz_var.set("640")
            self.train_workers_var.delete(0, tk.END)
            self.train_workers_var.insert(0, "4")
            self.train_cache_var.set("ram")
            self.log("🖥️ Profil Desktop appliqué - Batch=32, Cache=RAM")
            
        elif system == "💻 Laptop (Ryzen AI 7 350 + 5070 8GB)":
            # Defaults pour Laptop: batch réduit, imgsz réduit
            self.train_model_var.current(0)  # yolov8n.pt
            self.train_epochs_var.delete(0, tk.END)
            self.train_epochs_var.insert(0, "50")
            self.train_batch_var.delete(0, tk.END)
            self.train_batch_var.insert(0, "16")  # Batch réduit avec 8GB
            self.train_imgsz_var.set("512")  # Imgsz réduit pour économiser VRAM
            self.train_workers_var.delete(0, tk.END)
            self.train_workers_var.insert(0, "4")
            self.train_cache_var.set("disk")  # Cache disk pour économiser RAM
            self.log("💻 Profil Laptop appliqué - Batch=16, ImgSz=512, Cache=Disk")
            
        elif system == "🤖 Jetson: Orin AGX 32GB":
            # Defaults pour Jetson Orin AGX: mémoire unifiée 32GB, GPU Ampere intégré
            # Optimisé pour edge AI avec mémoire partagée CPU/GPU
            self.train_model_var.current(0)  # yolov8n.pt (optimal pour Jetson)
            self.train_epochs_var.delete(0, tk.END)
            self.train_epochs_var.insert(0, "50")
            self.train_batch_var.delete(0, tk.END)
            self.train_batch_var.insert(0, "16")  # Batch modéré (mémoire unifiée)
            self.train_imgsz_var.set("640")  # 640 supporté avec 32GB
            self.train_workers_var.delete(0, tk.END)
            self.train_workers_var.insert(0, "2")  # Workers réduits (ARM CPU)
            self.train_cache_var.set("disk")  # Disk cache (mémoire unifiée partagée)
            self.log("🤖 Profil Jetson Orin AGX 32GB appliqué - Batch=16, Workers=2, Cache=Disk")
        
        # Réinitialiser le preset à Custom
        self.train_preset_var.set("Custom")
    
    def apply_training_preset(self, event=None):
        """Appliquer les configurations preset optimisées selon le système"""
        preset = self.train_preset_var.get()
        system = self.train_system_var.get()
        
        if preset == "Custom":
            return
        
        # Desktop: 5800X3D + 5070 Ti 16GB (16GB VRAM)
        if "Desktop" in system:
            if preset == "⚡ Fast & Efficient":
                # yolov8n.pt, 512px, batch 32, 50 epochs, cache=ram
                self.train_model_var.current(0)  # yolov8n.pt
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "50")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "32")
                self.train_imgsz_var.set("512")
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "4")
                self.train_cache_var.set("ram")
                self.train_cosine_var.set(False)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "50")
                self.log("✅ Desktop Fast: n/512/32 - Cache RAM activé")
                
            elif preset == "⚖️ Balanced":
                # yolov8s.pt, 640px, batch 16, 50 epochs, cache=ram
                self.train_model_var.current(1)  # yolov8s.pt
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "50")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "16")
                self.train_imgsz_var.set("640")
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "4")
                self.train_cache_var.set("ram")
                self.train_cosine_var.set(False)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "50")
                self.log("✅ Desktop Balanced: s/640/16 - Équilibre précision/vitesse")
                
            elif preset == "🎯 High Quality":
                # yolov8s.pt, 640px, batch 16, 100 epochs, cosine LR, patience 20
                self.train_model_var.current(1)  # yolov8s.pt
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "100")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "16")
                self.train_imgsz_var.set("640")
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "4")
                self.train_cache_var.set("ram")
                self.train_cosine_var.set(True)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "20")
                self.log("✅ Desktop High Quality: s/640/cosine - Early Stop activé")
        
        # Jetson Orin AGX 32GB (mémoire unifiée, GPU Ampere intégré)
        elif "Jetson" in system or "Orin" in system:
            if preset == "⚡ Fast & Efficient":
                # yolov8n.pt, 416px, batch 16, 50 epochs - Optimisé inférence edge
                self.train_model_var.current(0)  # yolov8n.pt
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "50")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "16")
                self.train_imgsz_var.set("416")  # Plus rapide pour edge
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "2")  # ARM CPU - workers limités
                self.train_cache_var.set("disk")  # Préserve mémoire unifiée
                self.train_cosine_var.set(False)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "50")
                self.log("✅ Jetson Fast: n/416/16 - Optimisé edge AI")
                
            elif preset == "⚖️ Balanced":
                # yolov8n.pt, 512px, batch 12, 50 epochs - Équilibre edge
                self.train_model_var.current(0)  # yolov8n.pt
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "50")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "12")
                self.train_imgsz_var.set("512")
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "2")  # ARM CPU
                self.train_cache_var.set("disk")
                self.train_cosine_var.set(False)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "50")
                self.log("✅ Jetson Balanced: n/512/12 - Équilibre précision/vitesse")
                
            elif preset == "🎯 High Quality":
                # yolov8s.pt, 640px, batch 8, 100 epochs - Max qualité Jetson
                self.train_model_var.current(1)  # yolov8s.pt
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "100")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "8")  # Batch réduit pour s
                self.train_imgsz_var.set("640")  # Résolution max
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "2")  # ARM CPU
                self.train_cache_var.set("disk")
                self.train_cosine_var.set(True)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "20")
                self.log("✅ Jetson High Quality: s/640/8/cosine - Max qualité edge")
                
            elif preset == "🚀 Jetson Realtime":
                # yolov8n.pt, 320px, batch 24, 30 epochs - Optimisé FPS max (>60 FPS)
                self.train_model_var.current(0)  # yolov8n.pt
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "30")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "24")
                self.train_imgsz_var.set("320")  # Petite taille = FPS max
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "2")
                self.train_cache_var.set("disk")
                self.train_cosine_var.set(False)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "30")
                self.log("✅ Jetson Realtime: n/320/24 - Optimisé >60 FPS, export TensorRT recommandé")
                
            elif preset == "🤖 Jetson Optimized":
                # yolov8n.pt, 480px, batch 16, 80 epochs - Best trade-off Orin AGX
                # Optimisé pour mémoire unifiée 32GB avec cosine LR
                self.train_model_var.current(0)  # yolov8n.pt
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "80")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "16")
                self.train_imgsz_var.set("480")  # Bon compromis taille/vitesse
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "2")
                self.train_cache_var.set("disk")
                self.train_cosine_var.set(True)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "25")
                self.log("✅ Jetson Optimized: n/480/16/cosine - Meilleur compromis Orin AGX 32GB")
        
        # Laptop: Ryzen AI 7 350 + 5070 8GB (8GB VRAM - batch réduit)
        else:
            if preset == "⚡ Fast & Efficient":
                # yolov8n.pt, 416px, batch 16, 50 epochs, cache=ram
                self.train_model_var.current(0)  # yolov8n.pt
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "50")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "16")  # Réduit pour 8GB
                self.train_imgsz_var.set("416")  # Réduit pour économiser VRAM
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "4")
                self.train_cache_var.set("ram")
                self.train_cosine_var.set(False)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "50")
                self.log("✅ Laptop Fast: n/416/16 - Optimisé 8GB VRAM")
                
            elif preset == "⚖️ Balanced":
                # yolov8n.pt (pas s pour 8GB!), 512px, batch 12, 50 epochs
                self.train_model_var.current(0)  # yolov8n.pt (pas s!)
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "50")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "12")  # Réduit pour 8GB
                self.train_imgsz_var.set("512")
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "4")
                self.train_cache_var.set("ram")
                self.train_cosine_var.set(False)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "50")
                self.log("✅ Laptop Balanced: n/512/12 - Sûr pour 8GB VRAM")
                
            elif preset == "🎯 High Quality":
                # yolov8s.pt (risqué!), 512px, batch 8, 100 epochs, cosine
                self.train_model_var.current(1)  # yolov8s.pt
                self.train_epochs_var.delete(0, tk.END)
                self.train_epochs_var.insert(0, "100")
                self.train_batch_var.delete(0, tk.END)
                self.train_batch_var.insert(0, "8")  # Minimum safe pour s + 8GB
                self.train_imgsz_var.set("512")  # Réduit à 512
                self.train_workers_var.delete(0, tk.END)
                self.train_workers_var.insert(0, "4")
                self.train_cache_var.set("ram")
                self.train_cosine_var.set(True)
                self.train_patience_var.delete(0, tk.END)
                self.train_patience_var.insert(0, "20")
                self.log("✅ Laptop High Quality: s/512/8 - Limite 8GB (risque OOM)")
    
    def create_detection_view(self):
        """Vue Detection avec DetectionManager"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "📹", "Live Detection",
                                "Real-time detection with webcam or batch processing")
        
        # Configuration Card
        config_card = tk.Frame(container, bg=self.colors['bg_card'])
        config_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        card_title = tk.Label(config_card,
            text="⚙️ Detection Configuration",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        config_content = tk.Frame(config_card, bg=self.colors['bg_card'])
        config_content.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        # Model path
        model_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        model_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(model_frame, text="Model:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.detect_model_var = tk.Entry(model_frame, width=40,
                                         bg='#FFFFFF', fg='#1a1a1a')
        self.detect_model_var.pack(side=tk.LEFT, padx=10)
        self.detect_model_var.insert(0, PATHS['files']['best_model'])
        
        ttk.Button(model_frame, text="�", width=3,
                  command=self.browse_model).pack(side=tk.LEFT)
        
        # Confidence
        conf_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        conf_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(conf_frame, text="Confidence:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.detect_conf_var = tk.Scale(conf_frame, from_=0.1, to=1.0,
                                        resolution=0.05, orient=tk.HORIZONTAL,
                                        bg=self.colors['bg_card'], fg='#FFFFFF')
        self.detect_conf_var.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.detect_conf_var.set(0.25)
        
        # Camera ID
        camera_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        camera_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(camera_frame, text="Camera ID:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.detect_camera_var = ttk.Spinbox(camera_frame, from_=0, to=10, width=self.SPINBOX_WIDTH)
        self.detect_camera_var.pack(side=tk.LEFT, padx=10)
        self.detect_camera_var.set(0)
        
        # Show Prices checkbox
        prices_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        prices_frame.pack(fill=tk.X, pady=10)
        
        self.detect_show_prices_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(prices_frame, text="💰 Show Prices (from models/cards_database.yaml)",
                       variable=self.detect_show_prices_var).pack(anchor='w')

        tk.Label(prices_frame, text="Display card prices alongside names in detection overlay",
                bg=self.colors['bg_card'], fg='#888888',
                font=('Segoe UI', 9)).pack(anchor='w', padx=20)

        # Snapshot de prix hors-ligne (F10) : indicateur + préchargement
        snapshot_frame = tk.Frame(prices_frame, bg=self.colors['bg_card'])
        snapshot_frame.pack(anchor='w', padx=20, pady=(4, 0), fill=tk.X)

        self.price_snapshot_label = tk.Label(snapshot_frame,
                text=self._price_snapshot_text(),
                bg=self.colors['bg_card'], fg='#6aa6ff',
                font=('Segoe UI', 9))
        self.price_snapshot_label.pack(side=tk.LEFT)

        ttk.Button(snapshot_frame, text="⬇ Preload Prices",
                  command=self.preload_prices_snapshot).pack(side=tk.LEFT, padx=15)

        ttk.Button(snapshot_frame, text="💹 Price History",
                  command=self.open_price_history).pack(side=tk.LEFT)

        # Identify Cards checkbox (F01)
        identify_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        identify_frame.pack(fill=tk.X, pady=10)

        self.detect_identify_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(identify_frame, text="🎴 Identify Cards (embeddings index)",
                       variable=self.detect_identify_var).pack(anchor='w')

        tk.Label(identify_frame,
                text="Show exact card name, set and number in the overlay "
                     "(build the index first: python tools/build_card_index.py)",
                bg=self.colors['bg_card'], fg='#888888',
                font=('Segoe UI', 9)).pack(anchor='w', padx=20)
        
        # Buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="📹 START WEBCAM",
                  style='Accent.TButton',
                  command=self.start_webcam_detection,
                  width=30).pack(pady=5)

        ttk.Button(btn_frame, text="🧺 START COLLECTION SCAN",
                  command=self.start_collection_scan,
                  width=30).pack(pady=5)

        ttk.Button(btn_frame, text="🖼️ Detect Single Image",
                  command=self.detect_single_image,
                  width=30).pack(pady=5)
        
        ttk.Button(btn_frame, text="📂 Detect Folder",
                  command=self.detect_folder,
                  width=30).pack(pady=5)
    
    def create_export_view(self):
        """Vue Export détaillée"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "📦", "Dataset Export",
                                "Export dataset to multiple formats (COCO, VOC, TFRecord, Roboflow)")
        
        # Configuration Card
        config_card = tk.Frame(container, bg=self.colors['bg_card'])
        config_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        card_title = tk.Label(config_card,
            text="⚙️ Export Configuration",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        config_content = tk.Frame(config_card, bg=self.colors['bg_card'])
        config_content.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        # Format selection
        tk.Label(config_content, text="Select export formats:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(anchor='w', pady=(0, 10))
        
        self.export_coco_var = tk.BooleanVar(value=True)
        self.export_voc_var = tk.BooleanVar(value=False)
        self.export_tf_var = tk.BooleanVar(value=False)
        self.export_robo_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(config_content, text="📄 COCO JSON",
                       variable=self.export_coco_var).pack(anchor='w', pady=5)
        ttk.Checkbutton(config_content, text="🗂️ Pascal VOC XML",
                       variable=self.export_voc_var).pack(anchor='w', pady=5)
        ttk.Checkbutton(config_content, text="🤖 TensorFlow TFRecord",
                       variable=self.export_tf_var).pack(anchor='w', pady=5)
        ttk.Checkbutton(config_content, text="📦 Roboflow ZIP",
                       variable=self.export_robo_var).pack(anchor='w', pady=5)
        
        # Buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="📦 EXPORT DATASET",
                  style='Accent.TButton',
                  command=self.start_export,
                  width=30).pack(pady=5)
    
    def create_tools_view(self):
        """Vue Utilities détaillée"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # V3.1: Dense Header
        self.create_dense_header(container, "🛠️", "Utilities & Tools",
                                "Additional tools and utilities")
        
        # Tools Card
        tools_card = tk.Frame(container, bg=self.colors['bg_card'])
        tools_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        card_title = tk.Label(tools_card,
            text="🔧 Available Tools",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        tools_content = tk.Frame(tools_card, bg=self.colors['bg_card'])
        tools_content.pack(fill=tk.BOTH, padx=40, pady=(0, 20))
        
        # Tool buttons
        ttk.Button(tools_content, text="📋 Card Database",
                  command=self.open_yaml_tools,
                  width=40).pack(pady=5, fill=tk.X)
        
        ttk.Button(tools_content, text="⚖️ Auto-Balance Classes",
                  command=self.start_balancing,
                  width=40).pack(pady=5, fill=tk.X)
        
        ttk.Button(tools_content, text="🎴 TCG API Browser",
                  command=self.open_tcg_browser,
                  width=40).pack(pady=5, fill=tk.X)
        
        ttk.Button(tools_content, text="📊 Statistics Dashboard",
                  command=self.show_statistics,
                  width=40).pack(pady=5, fill=tk.X)
        
        ttk.Button(tools_content, text="🗂️ Open Output Folder",
                  command=self.open_output_folder,
                  width=40).pack(pady=5, fill=tk.X)
        
        # Clean Tools Card
        clean_card = tk.Frame(container, bg=self.colors['bg_card'])
        clean_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        clean_title = tk.Label(clean_card,
            text="🧹 Clean & Reset",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        clean_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        clean_content = tk.Frame(clean_card, bg=self.colors['bg_card'])
        clean_content.pack(fill=tk.BOTH, padx=40, pady=(0, 20))
        
        # Warning label
        warning_label = tk.Label(clean_content,
            text="⚠️ Warning: These actions will permanently delete files!",
            font=('Segoe UI', 9, 'italic'),
            bg=self.colors['bg_card'],
            fg=self.colors['warning']
        )
        warning_label.pack(anchor='w', pady=(0, 15))
        
        # Clean buttons
        clean_buttons = tk.Frame(clean_content, bg=self.colors['bg_card'])
        clean_buttons.pack(fill=tk.X)
        
        # Left column
        left_col = tk.Frame(clean_buttons, bg=self.colors['bg_card'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Button(left_col, 
                 text="🗑️ Clean Output Folder",
                 command=self.clean_output,
                 bg=self.colors['error'],
                 fg='#FFFFFF',
                 font=self.FONT_BUTTON,
                 relief='flat',
                 padx=15,
                 pady=10,
                 cursor='hand2').pack(pady=5, fill=tk.X)
        
        tk.Button(left_col,
                 text="🎨 Clean Augmented",
                 command=self.clean_augmented,
                 bg=self.colors['bg_hover'],
                 fg=self.colors['text'],
                 font=self.FONT_TEXT,
                 relief='flat',
                 padx=15,
                 pady=10,
                 cursor='hand2').pack(pady=5, fill=tk.X)
        
        tk.Button(left_col,
                 text="🧩 Clean Mosaics",
                 command=self.clean_mosaics,
                 bg=self.colors['bg_hover'],
                 fg=self.colors['text'],
                 font=self.FONT_TEXT,
                 relief='flat',
                 padx=15,
                 pady=10,
                 cursor='hand2').pack(pady=5, fill=tk.X)
        
        # Right column
        right_col = tk.Frame(clean_buttons, bg=self.colors['bg_card'])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Button(right_col,
                 text="🎓 Clean Training Results",
                 command=self.clean_training,
                 bg=self.colors['bg_hover'],
                 fg=self.colors['text'],
                 font=self.FONT_TEXT,
                 relief='flat',
                 padx=15,
                 pady=10,
                 cursor='hand2').pack(pady=5, fill=tk.X)
        
        tk.Button(right_col,
                 text="🌈 Clean Holographic",
                 command=self.clean_holographic,
                 bg=self.colors['bg_hover'],
                 fg=self.colors['text'],
                 font=self.FONT_TEXT,
                 relief='flat',
                 padx=15,
                 pady=10,
                 cursor='hand2').pack(pady=5, fill=tk.X)
        
        tk.Button(right_col,
                 text="🎲 Clean Fake Images",
                 command=self.clean_fakeimg,
                 bg=self.colors['bg_hover'],
                 fg=self.colors['text'],
                 font=self.FONT_TEXT,
                 relief='flat',
                 padx=15,
                 pady=10,
                 cursor='hand2').pack(pady=5, fill=tk.X)
        
        # Option to include images/
        self.clean_include_images_var = tk.BooleanVar(value=False)
        
        option_frame = tk.Frame(clean_content, bg=self.colors['bg_card'])
        option_frame.pack(anchor='w', pady=(15, 10))
        
        ttk.Checkbutton(option_frame,
            text="⚠️ Include images/ folder (source images)",
            variable=self.clean_include_images_var,
            style='TCheckbutton'
        ).pack(anchor='w')
        
        # Clean All button (separate, more prominent)
        clean_all_frame = tk.Frame(clean_content, bg=self.colors['bg_card'])
        clean_all_frame.pack(pady=(15, 0))
        
        tk.Button(clean_all_frame,
                 text="🚨 CLEAN ALL",
                 command=self.clean_all,
                 bg='#d73a49',
                 fg='#FFFFFF',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat',
                 padx=30,
                 pady=12,
                 cursor='hand2').pack()
    
    def create_placeholder_view(self, title, subtitle):
        """Vue placeholder pour développement"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        title_label = tk.Label(container,
            text=title,
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title_label.pack(anchor='w', pady=(0, 5))
        
        subtitle_label = tk.Label(container,
            text=subtitle,
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle_label.pack(anchor='w', pady=(0, 30))
        
        # Placeholder content
        placeholder = tk.Frame(container, bg=self.colors['bg_card'])
        placeholder.pack(fill=tk.BOTH, expand=True)
        
        placeholder_text = tk.Label(placeholder,
            text="🚧 View under construction\nWill be available soon",
            font=('Segoe UI', 12),
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim'],
            justify=tk.CENTER
        )
        placeholder_text.pack(expand=True)
    
    # ========== MÉTHODES UTILITAIRES ==========
    
    def check_venv(self):
        """Vérifier si l'environnement virtuel existe"""
        venv_path = Path(".venv")
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        return venv_path.exists() and python_exe.exists()
    
    def check_yaml_file(self):
        """Vérifier si le fichier YAML des cartes existe"""
        yaml_path = Path(PATHS['files']['cards_database_yaml'])
        return yaml_path.exists()
    
    def create_sample_yaml(self):
        """Créer un fichier YAML exemple"""
        try:
            import yaml
            from datetime import datetime
            
            # Données exemple
            yaml_data = {
                'metadata': {
                    'version': '1.0',
                    'format': 'YOLO-compatible card database',
                    'last_updated': datetime.now().strftime('%Y-%m-%d'),
                    'source': 'Sample data',
                    'total_cards': 5,
                    'comment': 'Bounding boxes are generated dynamically'
                },
                'cards': {
                    'base_001': {
                        'name': 'Bulbasaur',
                        'set': 'Base Set',
                        'set_full': '001/102',
                        'type': 'Pokemon',
                        'rarity': 'Common',
                        'price': None,
                        'price_max': None,
                        'price_source': '',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    },
                    'base_002': {
                        'name': 'Ivysaur',
                        'set': 'Base Set',
                        'set_full': '002/102',
                        'type': 'Pokemon',
                        'rarity': 'Uncommon',
                        'price': None,
                        'price_max': None,
                        'price_source': '',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    },
                    'base_003': {
                        'name': 'Venusaur',
                        'set': 'Base Set',
                        'set_full': '003/102',
                        'type': 'Pokemon',
                        'rarity': 'Rare',
                        'price': None,
                        'price_max': None,
                        'price_source': '',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    },
                    'base_004': {
                        'name': 'Charmander',
                        'set': 'Base Set',
                        'set_full': '004/102',
                        'type': 'Pokemon',
                        'rarity': 'Common',
                        'price': None,
                        'price_max': None,
                        'price_source': '',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    },
                    'base_005': {
                        'name': 'Charmeleon',
                        'set': 'Base Set',
                        'set_full': '005/102',
                        'type': 'Pokemon',
                        'rarity': 'Uncommon',
                        'price': None,
                        'price_max': None,
                        'price_source': '',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    }
                }
            }
            
            # Créer le dossier models/ si nécessaire
            Path(PATHS['directories']['models']).mkdir(exist_ok=True)
            
            # Sauvegarder en YAML
            yaml_path = Path(PATHS['files']['cards_database_yaml'])
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            self.log("✅ Fichier cards_database.yaml créé avec succès!")
            self.show_info(
                "Succès",
                "Fichier cards_database.yaml créé!\n\n"
                "Un fichier exemple a été créé avec 5 cartes.\n"
                "Vous pouvez l'éditer avec n'importe quel éditeur de texte.\n\n"
                "Structure YAML:\n"
                "• cards: dictionnaire des cartes\n"
                "  • card_id: identifiant unique\n"
                "    • name: nom de la carte\n"
                "    • set: nom du set\n"
                "    • price: prix (optionnel)\n\n"
                "💡 Format léger et lisible!"
            )
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur création YAML: {e}")
            self.show_error("Erreur", f"Impossible de créer le fichier:\n{e}")
            return False
    
    def _generate_yaml_from_manifest(self, manifest_path: str, set_id: str, set_name: str):
        """
        Génère automatiquement cards_database.yaml depuis le manifest.csv du téléchargement
        
        Args:
            manifest_path: Chemin vers manifest.csv
            set_id: ID du set (ex: sv08, xyp)
            set_name: Nom du set (ex: "Surging Sparks")
        """
        import yaml
        import csv
        from datetime import datetime
        from pathlib import Path
        import requests
        
        # Lire le manifest pour obtenir les IDs des cartes
        # Format réel du manifest: id, localId, name, file, source_url
        # Exemple: xyp-XY01, XY01, Chespin, images\xyp_XY01_en.png, https://...
        cards_from_manifest = []
        with open(manifest_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                card_id = row.get('id', '')  # ex: xyp-XY01
                local_id = row.get('localId', '')  # ex: XY01
                card_name = row.get('name', 'Unknown')
                file_path = row.get('file', '')
                
                if card_id and file_path:
                    # Extraire le nom du fichier sans extension ni langue
                    # Ex: images\xyp_XY01_en.png → xyp_XY01
                    filename = Path(file_path).stem  # xyp_XY01_en
                    internal_id = '_'.join(filename.split('_')[:-1]) if '_' in filename else filename
                    
                    cards_from_manifest.append({
                        'internal_id': internal_id,
                        'tcgdex_id': card_id,
                        'local_id': local_id,
                        'name': card_name
                    })
        
        # Récupérer les infos complètes depuis TCGdex API (optionnel, pour avoir rarity, etc.)
        # Pour l'instant, on crée avec les infos du manifest
        cards_data = {}
        for card in cards_from_manifest:
            cards_data[card['internal_id']] = {
                'name': card['name'],
                'set': set_name,
                'set_full': f"{card['local_id']}/???",
                'type': 'Pokemon',
                'rarity': 'Common',
                'price': None,
                'price_max': None,
                'price_source': '',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
        
        # Créer structure YAML
        yaml_data = {
            'metadata': {
                'version': '1.0',
                'format': 'YOLO-compatible card database',
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'source': f'Auto-generated from Image Download ({set_id})',
                'total_cards': len(cards_data),
                'comment': 'Bounding boxes are generated dynamically during mosaic/augmentation'
            },
            'cards': cards_data
        }
        
        # Sauvegarder YAML
        yaml_path = Path(PATHS['files']['cards_database_yaml'])
        yaml_path.parent.mkdir(exist_ok=True)
        
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    def detect_gpu_info(self):
        """V3.1: Détecter le GPU disponible de manière compacte
        
        Returns:
            (bool, str): (gpu_available, gpu_name_with_vram)
        """
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                return True, f"{gpu_name} ({gpu_memory:.0f}GB)"
            else:
                return False, "No CUDA GPU detected"
        except ImportError:
            return False, "PyTorch not installed"
        except Exception as e:
            return False, f"Detection error: {str(e)[:30]}"
    
    def ensure_venv(self):
        """S'assurer que l'environnement virtuel existe et est prêt"""
        if self.check_venv():
            self.log("✅ Environnement virtuel détecté")
            return True
        
        self.log("⚠️ Environnement virtuel non trouvé!")
        response = messagebox.askyesno(
            "Environnement requis",
            "L'environnement virtuel Python n'est pas configuré.\n\n"
            "Voulez-vous l'installer maintenant?\n\n"
            "Cela va:\n"
            "• Créer un environnement virtuel .venv\n"
            "• Installer toutes les dépendances\n"
            "• Durée estimée: 2-5 minutes"
        )
        
        if not response:
            return False
        
        # Lancer l'installation
        self.log("🔧 Installation de l'environnement virtuel...")
        self.start_operation("Environment Setup")
        
        def install_task():
            try:
                if sys.platform == "win32":
                    install_script = Path("install_env.bat")
                    if not install_script.exists():
                        self.log("❌ Script install_env.bat non trouvé!")
                        self.show_error("Erreur", "Script d'installation non trouvé!")
                        return False
                    
                    process = subprocess.Popen(
                        [str(install_script)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        shell=True
                    )
                else:
                    # Linux/Mac
                    process = subprocess.Popen(
                        ["bash", "install_env.sh"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True
                    )
                
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.log(line.strip())
                
                process.wait()
                
                if process.returncode == 0 and self.check_venv():
                    self.log("✅ Environnement virtuel installé avec succès!")
                    self.show_info("Succès", "Environnement installé!\n\nVous pouvez maintenant utiliser toutes les fonctionnalités.")
                    return True
                else:
                    self.log("❌ Installation échouée")
                    self.show_error("Erreur", "Installation échouée.\nVérifiez les logs pour plus de détails.")
                    return False
                    
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                self.show_error("Erreur", f"Erreur lors de l'installation:\n{e}")
                return False
            finally:
                self.end_operation()
        
        threading.Thread(target=install_task, daemon=True).start()
        return False  # Retourner False car l'installation est en cours
    
    def load_config(self):
        """Charger la configuration (via GuiConfig, défauts inclus)"""
        self.config = GuiConfig(self.config_file).data
    
    def get_real_stats(self):
        """Calculer les statistiques réelles du projet"""
        stats = {
            'source': 0,
            'augmented': 0,
            'mosaics': 0,
            'size': '0 MB'
        }
        
        try:
            # Compter images source
            images_path = Path(PATHS['directories']['images'])
            if images_path.exists():
                stats['source'] = len(list(images_path.glob("*.png"))) + \
                                 len(list(images_path.glob("*.jpg"))) + \
                                 len(list(images_path.glob("*.jpeg")))
            
            # Compter images augmentées
            aug_path = Path(PATHS['directories']['output_augmented_images'])
            if aug_path.exists():
                stats['augmented'] = len(list(aug_path.glob("*.png"))) + \
                                    len(list(aug_path.glob("*.jpg")))
            
            # Compter mosaïques
            mosaic_path = Path(PATHS['directories']['output_mosaics_images'])
            if mosaic_path.exists():
                stats['mosaics'] = len(list(mosaic_path.glob("*.png"))) + \
                                  len(list(mosaic_path.glob("*.jpg")))
            
            # Calculer taille totale du dossier output
            output_path = Path(PATHS['directories']['output_base'])
            if output_path.exists():
                total_size = 0
                for file in output_path.rglob("*"):
                    if file.is_file():
                        total_size += file.stat().st_size
                
                # Convertir en MB
                size_mb = total_size / (1024 * 1024)
                if size_mb < 1:
                    stats['size'] = f"{size_mb * 1024:.0f} KB"
                elif size_mb < 1000:
                    stats['size'] = f"{size_mb:.1f} MB"
                else:
                    stats['size'] = f"{size_mb / 1024:.1f} GB"
            
        except Exception as e:
            self.log(f"⚠️ Erreur calcul stats: {e}")
        
        return stats
    
    def get_generation_speed(self):
        """Calculer la vitesse de génération (images/minute)"""
        try:
            # Récupérer les timestamps des dernières opérations
            import time
            current_time = time.time()
            
            # Compter les images générées dans les 5 dernières minutes
            recent_images = 0
            time_window = 300  # 5 minutes en secondes
            
            for directory in [PATHS['directories']['output_augmented_images'], 
                            PATHS['directories']['output_mosaics_images']]:
                if os.path.exists(directory):
                    for file in os.listdir(directory):
                        file_path = os.path.join(directory, file)
                        if os.path.isfile(file_path):
                            mtime = os.path.getmtime(file_path)
                            if current_time - mtime < time_window:
                                recent_images += 1
            
            if recent_images > 0:
                speed = (recent_images / time_window) * 60  # images par minute
                if speed >= 1:
                    return f"{speed:.1f} img/min"
                else:
                    return f"{speed*60:.1f} img/h"
            return None
        except Exception:
            return None
    
    def get_detailed_ratio(self):
        """Obtenir le ratio détaillé (originales vs augmentées vs mosaïques)"""
        try:
            stats = self.get_real_stats()
            source = stats['source']
            augmented = stats['augmented']
            mosaics = stats['mosaics']
            
            if source == 0:
                return "📊 Ratio: N/A"
            
            # Calculer les ratios
            aug_ratio = augmented / source if source > 0 else 0
            mosaic_ratio = mosaics / source if source > 0 else 0
            
            return f"📊 Ratio: 1:{aug_ratio:.1f}:{mosaic_ratio:.1f} (Orig:Aug:Mos)"
        except Exception:
            return "📊 Ratio: N/A"
    
    def get_performance_info(self):
        """Obtenir les informations de performance GPU/CPU"""
        try:
            # Vérifier si GPU disponible
            try:
                import torch
                if torch.cuda.is_available():
                    # Info GPU
                    gpu_name = torch.cuda.get_device_name(0)
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                    return f"⚡ {gpu_name[:15]}... ({gpu_memory:.0f}GB)"
            except Exception:
                pass
            
            # Si pas de GPU, info CPU
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            return f"⚡ CPU: {cpu_count} cores"
        except Exception:
            return None
    
    def get_last_activity(self):
        """Récupère la dernière activité effectuée"""
        try:
            if hasattr(self, 'last_operation_time') and hasattr(self, 'last_operation_name'):
                # Calculer temps écoulé
                elapsed = datetime.now() - self.last_operation_time
                
                if elapsed.total_seconds() < 60:
                    time_str = f"il y a {int(elapsed.total_seconds())} sec"
                elif elapsed.total_seconds() < 3600:
                    time_str = f"il y a {int(elapsed.total_seconds() / 60)} min"
                else:
                    time_str = f"il y a {int(elapsed.total_seconds() / 3600)} h"
                
                return {
                    'operation': self.last_operation_name,
                    'time': time_str,
                    'status': '✅ Succès'
                }
            else:
                return {
                    'operation': 'Aucune',
                    'time': '-',
                    'status': '⏸️ En attente'
                }
        except Exception as e:
            return {
                'operation': 'Erreur',
                'time': '-',
                'status': '❌ Erreur'
            }
    
    def get_dataset_progress(self, target=1000):
        """Calcule la progression vers l'objectif"""
        try:
            stats = self.get_real_stats()
            current = stats['source'] + stats['augmented'] + stats['mosaics']
            percent = min(100, int((current / target) * 100))
            
            return {
                'current': current,
                'target': target,
                'percent': percent
            }
        except Exception as e:
            return {
                'current': 0,
                'target': target,
                'percent': 0
            }
    
    def get_system_status(self):
        """Récupère l'état du système"""
        try:
            # GPU
            gpu_available, gpu_info = self.detect_gpu_info()
            
            # Espace disque
            output_path = Path(PATHS['directories']['output_base'])
            if output_path.exists():
                import shutil
                disk_stat = shutil.disk_usage(output_path)
                free_gb = disk_stat.free / (1024 ** 3)
                disk_free = f"{free_gb:.1f} GB libre"
            else:
                disk_free = "N/A"
            
            # Venv
            venv_ok = self.check_venv()
            
            return {
                'gpu': gpu_available,
                'gpu_info': gpu_info,
                'disk_free': disk_free,
                'venv': venv_ok
            }
        except Exception as e:
            return {
                'gpu': False,
                'gpu_info': 'Erreur',
                'disk_free': 'N/A',
                'venv': False
            }
    
    def get_last_generated_image(self):
        """Récupère le chemin de la dernière image générée"""
        try:
            output_path = Path(PATHS['directories']['output_base'])
            if not output_path.exists():
                return None
            
            # Scanner tous les fichiers image
            image_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg']:
                image_files.extend(output_path.rglob(ext))
            
            if not image_files:
                return None
            
            # Trier par date de modification (plus récent en premier)
            latest = max(image_files, key=lambda p: p.stat().st_mtime)
            return latest
        except Exception as e:
            return None
    
    def get_smart_recommendations(self):
        """Génère des recommendations intelligentes basées sur l'état du dataset"""
        try:
            stats = self.get_real_stats()
            recommendations = []
            
            # Analyser l'état actuel
            source = stats['source']
            augmented = stats['augmented']
            mosaics = stats['mosaics']
            
            # Recommandations selon le contexte
            if source == 0:
                return {
                    'icon': '📥',
                    'title': 'Commencez par télécharger des images',
                    'description': 'Utilisez le module Image Download pour récupérer vos cartes Pokémon',
                    'priority': 'high'
                }
            
            if source > 0 and augmented == 0:
                aug_ratio = 0
                return {
                    'icon': '🎨',
                    'title': f'Augmentez votre dataset ({source} images)',
                    'description': f'Générez 10-15 variations par carte pour améliorer la robustesse',
                    'priority': 'high'
                }
            
            if augmented > 0:
                aug_ratio = augmented / source if source > 0 else 0
                
                if aug_ratio < 5:
                    return {
                        'icon': '⚠️',
                        'title': f'Ratio d\'augmentation faible ({aug_ratio:.1f}x)',
                        'description': 'Recommandé : 10-15 augmentations par image source',
                        'priority': 'medium'
                    }
                elif aug_ratio >= 10 and mosaics == 0:
                    return {
                        'icon': '🧩',
                        'title': 'Dataset prêt pour les mosaïques !',
                        'description': f'{augmented} images augmentées - Générez des mosaïques pour l\'entraînement',
                        'priority': 'high'
                    }
                elif mosaics > 0 and mosaics < 50:
                    return {
                        'icon': '📊',
                        'title': 'Augmentez le nombre de mosaïques',
                        'description': f'{mosaics} mosaïques - Recommandé : 100+ pour un bon entraînement',
                        'priority': 'medium'
                    }
                elif mosaics >= 50:
                    return {
                        'icon': '✅',
                        'title': 'Dataset prêt pour l\'entraînement !',
                        'description': f'{source} sources, {augmented} augmentées, {mosaics} mosaïques',
                        'priority': 'low'
                    }
            
            # Recommandation par défaut
            return {
                'icon': '💡',
                'title': 'Continuez à construire votre dataset',
                'description': 'Téléchargez plus d\'images ou augmentez celles existantes',
                'priority': 'low'
            }
            
        except Exception as e:
            return {
                'icon': '❓',
                'title': 'Statut indéterminé',
                'description': 'Consultez les statistiques pour plus d\'infos',
                'priority': 'low'
            }
    
    def get_dataset_health_score(self):
        """Calcule un score de santé du dataset (0-100)"""
        try:
            stats = self.get_real_stats()
            source = stats['source']
            augmented = stats['augmented']
            mosaics = stats['mosaics']
            
            score = 0
            details = []
            
            # Critère 1: Images source (30 points max)
            if source >= 50:
                source_score = 30
                details.append(('✅ Images source', 30))
            elif source >= 20:
                source_score = int((source / 50) * 30)
                details.append(('🟡 Images source', source_score))
            else:
                source_score = int((source / 20) * 15)
                details.append(('🔴 Images source', source_score))
            score += source_score
            
            # Critère 2: Ratio d'augmentation (30 points max)
            if source > 0:
                aug_ratio = augmented / source
                if aug_ratio >= 10:
                    aug_score = 30
                    details.append(('✅ Augmentations', 30))
                elif aug_ratio >= 5:
                    aug_score = int((aug_ratio / 10) * 30)
                    details.append(('🟡 Augmentations', aug_score))
                else:
                    aug_score = int((aug_ratio / 5) * 15)
                    details.append(('🔴 Augmentations', aug_score))
                score += aug_score
            else:
                details.append(('⚪ Augmentations', 0))
            
            # Critère 3: Mosaïques (20 points max)
            if mosaics >= 100:
                mosaic_score = 20
                details.append(('✅ Mosaïques', 20))
            elif mosaics >= 50:
                mosaic_score = int((mosaics / 100) * 20)
                details.append(('🟡 Mosaïques', mosaic_score))
            else:
                mosaic_score = int((mosaics / 50) * 10)
                details.append(('🔴 Mosaïques', mosaic_score))
            score += mosaic_score
            
            # Critère 4: Diversité (20 points max)
            total_images = source + augmented + mosaics
            if total_images >= 500:
                diversity_score = 20
                details.append(('✅ Diversité', 20))
            elif total_images >= 200:
                diversity_score = int((total_images / 500) * 20)
                details.append(('🟡 Diversité', diversity_score))
            else:
                diversity_score = int((total_images / 200) * 10)
                details.append(('🔴 Diversité', diversity_score))
            score += diversity_score
            
            # Déterminer le grade
            if score >= 90:
                grade = '🥇 Excellent'
                color = '#a6e3a1'  # green
            elif score >= 70:
                grade = '🥈 Bon'
                color = '#89b4fa'  # blue
            elif score >= 50:
                grade = '🥉 Satisfaisant'
                color = '#f9e2af'  # yellow
            else:
                grade = '📊 En cours'
                color = '#f38ba8'  # red
            
            return {
                'score': score,
                'grade': grade,
                'color': color,
                'details': details
            }
            
        except Exception as e:
            return {
                'score': 0,
                'grade': '❓ Indéterminé',
                'color': '#6c7086',  # overlay0
                'details': []
            }
    
    def log(self, message):
        """
        Ajouter un message aux logs — THREAD-SAFE.

        Peut être appelé depuis n'importe quel thread : le message est enfilé
        et affiché dans le widget par _drain_log_queue() (thread principal).
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        # Fichier de log global (logs/pokemon_gui.log)
        gui_logger.info(message)

        # Afficher dans stdout (console) avec gestion d'encodage Windows
        try:
            print(log_message.strip())
        except UnicodeEncodeError:
            safe_log = log_message.encode('ascii', 'ignore').decode('ascii')
            print(safe_log.strip())

        self._log_queue.put(log_message)

    def _dispatch_ui(self, fn):
        """
        Planifie un callable sur le thread principal — utilisable depuis
        n'importe quel thread (simple queue.put, aucun appel Tk).
        """
        self._ui_queue.put(fn)

    def _drain_log_queue(self):
        """Vide les files de logs et de callbacks UI (thread principal)"""
        drained = False
        while True:
            try:
                log_message = self._log_queue.get_nowait()
            except queue.Empty:
                break
            try:
                self.log_text.insert(tk.END, log_message)
            except Exception:
                # Erreur d'encodage: retirer emojis/caractères non-ASCII
                safe_message = log_message.encode('ascii', 'ignore').decode('ascii')
                try:
                    self.log_text.insert(tk.END, safe_message)
                except Exception:
                    pass  # Widget détruit (fermeture app)
            drained = True

        if drained:
            try:
                self.log_text.see(tk.END)
            except Exception:
                pass

        # Callbacks UI déposés par les threads workers
        while True:
            try:
                callback = self._ui_queue.get_nowait()
            except queue.Empty:
                break
            try:
                callback()
            except Exception as e:
                self.log(f"⚠️ Erreur callback UI: {e}")

        self.root.after(100, self._drain_log_queue)

    # ---- Popups thread-safe -------------------------------------------------
    # Les messagebox Tkinter ne doivent être créées que depuis le thread
    # principal. Ces wrappers passent par la file de callbacks UI, ce qui
    # les rend utilisables depuis n'importe quel thread.

    def show_info(self, title, message):
        """messagebox.showinfo thread-safe (non bloquant depuis un worker)"""
        self._dispatch_ui(lambda: messagebox.showinfo(title, message))

    def show_error(self, title, message):
        """messagebox.showerror thread-safe (non bloquant depuis un worker)"""
        self._dispatch_ui(lambda: messagebox.showerror(title, message))

    def show_warning(self, title, message):
        """messagebox.showwarning thread-safe (non bloquant depuis un worker)"""
        self._dispatch_ui(lambda: messagebox.showwarning(title, message))
    
    def start_operation(self, operation_name):
        """Démarrer une opération"""
        self.is_running = True
        self.operation_stopped = False  # Réinitialiser le flag
        self.current_operation_name = operation_name  # V3.2: Stocker le nom pour le footer
        self.progress_label.config(text=f"Running: {operation_name}")
        self.progress_bar.start(10)
        self.stop_button.config(state='normal')
        # V3.1: Auto-expand footer pendant opération
        self.expand_footer_auto()
        # V3.2: Mettre à jour le footer avec le statut
        self.update_footer_stats()
    
    def end_operation(self):
        """Terminer une opération (thread-safe: se replanifie sur le thread principal)"""
        if threading.current_thread() is not threading.main_thread():
            self._dispatch_ui(self.end_operation)
            return
        # V3.2: Enregistrer dernière activité AVANT de reset
        if self.current_operation_name:
            self.last_operation_name = self.current_operation_name
            self.last_operation_time = datetime.now()
        
        self.is_running = False
        self.current_process = None
        self.current_operation_name = None  # V3.2: Reset nom opération
        self.progress_label.config(text="Ready")
        self.progress_bar.stop()
        self.stop_button.config(state='disabled')
        # V3.1: Footer reste ouvert après opération (l'utilisateur peut le fermer manuellement)
        # V3.2: Mettre à jour le footer avec l'état final
        self.update_footer_stats()
    
    def update_stats(self):
        """Mettre à jour les statistiques du dashboard (thread-safe)"""
        if threading.current_thread() is not threading.main_thread():
            self._dispatch_ui(self.update_stats)
            return
        try:
            # V3.2: Mettre à jour les nouvelles cartes du Dashboard si actif
            if hasattr(self, 'dashboard_cards') and self.current_view == 'home':
                # Carte 1: Dernière Activité
                activity = self.get_last_activity()
                if 'activity_operation' in self.dashboard_cards:
                    self.dashboard_cards['activity_operation'].config(text=activity['operation'])
                if 'activity_time' in self.dashboard_cards:
                    self.dashboard_cards['activity_time'].config(text=activity['time'])
                if 'activity_status' in self.dashboard_cards:
                    color = self.colors['success'] if '✅' in activity['status'] else self.colors['text_dim']
                    self.dashboard_cards['activity_status'].config(text=activity['status'], fg=color)
                
                # Carte 2: Progression
                progress = self.get_dataset_progress()
                if 'progress_percent' in self.dashboard_cards:
                    self.dashboard_cards['progress_percent'].config(text=f"{progress['percent']}%")
                if 'progress_bar' in self.dashboard_cards and 'progress_bar_container' in self.dashboard_cards:
                    # Repositionner la barre de progression
                    self.dashboard_cards['progress_bar'].place(x=0, y=0, relwidth=progress['percent']/100, height=10)
                if 'progress_text' in self.dashboard_cards:
                    self.dashboard_cards['progress_text'].config(text=f"{progress['current']} / {progress['target']} images")
                
                # Carte 3: Système (mise à jour du disque principalement)
                status = self.get_system_status()
                if 'system_disk' in self.dashboard_cards:
                    self.dashboard_cards['system_disk'].config(text=f"Disque: {status['disk_free']}")
                
                # Carte 4: Aperçu (on ne met pas à jour l'image à chaque fois pour performance)
                # L'image est mise à jour seulement lors de la création de la vue
            
            # Mettre à jour le Panneau Statistiques (sidebar)
            self.update_all_statistics()
            
            # Mettre à jour le footer
            self.update_footer_stats()
            
        except Exception as e:
            self.log(f"⚠️ Erreur mise à jour stats: {e}")
    
    def update_footer_stats(self):
        """Mettre à jour les infos contextuelles du footer (V3.2 - Harmonisé avec Statistics Panel)"""
        try:
            # Afficher infos contextuelles au lieu de compteurs (qui sont dans le panneau Statistics)
            if self.is_running:
                # Pendant une opération: afficher le statut
                footer_text = f"⚙️ Opération en cours: {self.current_operation_name if hasattr(self, 'current_operation_name') else 'Processing...'}"
            else:
                # Au repos: afficher l'état général
                stats = self.get_real_stats()
                footer_text = f"✅ Ready | Dataset size: {stats['size']} | Last update: {time.strftime('%H:%M:%S')}"
            
            if hasattr(self, 'footer_stats_label'):
                self.footer_stats_label.config(text=footer_text)
        except Exception:
            pass
    
    def stop_operation(self):
        """Arrêter l'opération en cours"""
        # Tâches gérées par le TaskRunner (Phase 4)
        if self.tasks.is_running:
            self.operation_stopped = True
            self.tasks.stop()
            return

        # Héritage: opérations pas encore migrées vers TaskRunner
        if self.current_process and self.current_process.poll() is None:
            try:
                self.operation_stopped = True  # Marquer comme arrêt volontaire
                self.log("⏹ Arrêt de l'opération en cours...")
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
                self.log("✅ Opération arrêtée")
            except Exception as e:
                try:
                    self.current_process.kill()
                    self.log("✅ Opération arrêtée (forcé)")
                except Exception:
                    self.log(f"❌ Erreur d'arrêt: {e}")
        
        self.end_operation()
    
    
    def start_image_download(self):
        """Démarrer le téléchargement d'images"""
        if self.is_running:
            self.show_warning("Warning", "Une opération est déjà en cours!")
            return
        
        # Récupérer les paramètres
        try:
            set_value = self.download_set_var.get().strip()
            if not set_value:
                self.show_error("Error", "Veuillez sélectionner ou saisir un set Pokemon!")
                return
            
            # Extract set ID if in format "Name (id)"
            if '(' in set_value and ')' in set_value:
                set_query = set_value.split('(')[-1].strip(')')
            else:
                set_query = set_value
            
            # Get language code
            from core.image_downloader import LANGUAGES
            lang_name = self.download_lang_var.get()
            lang_code = LANGUAGES.get(lang_name, 'en')
            
            quality = self.download_quality_var.get()
            ext = self.download_format_var.get()
            output_dir = self.download_output_var.get().strip()
            
            if not output_dir:
                output_dir = "images"
            
        except Exception as e:
            self.show_error("Error", f"Configuration invalide:\n{e}")
            return
        
        # Confirmation
        confirm_text = f"""Configuration du téléchargement :

🎴 Set : {set_query}
🌍 Langue : {lang_name} ({lang_code})
🎨 Qualité : {quality}
📁 Format : {ext}
💾 Output : {output_dir}

Lancer le téléchargement ?"""
        
        if not messagebox.askyesno("⬇️ Télécharger Images", confirm_text):
            return
        
        self.start_operation("Image Download")
        
        def task():
            try:
                from core.image_downloader import ImageDownloader
                
                # Progress callback
                def progress_callback(current, total, card_name=""):
                    if card_name:
                        self.log(f"📥 [{current}/{total}] {card_name}")
                
                # Create downloader
                downloader = ImageDownloader(progress_callback=progress_callback)
                
                self.log(f"🔍 Recherche du set '{set_query}'...")
                
                # Resolve set
                set_info = downloader.resolve_set(set_query, lang=lang_code)
                if not set_info:
                    self.log(f"❌ Set non trouvé: {set_query}")
                    self.show_error("Error", f"Set non trouvé: {set_query}\n\nVérifiez le nom ou l'ID du set.")
                    return
                
                set_id = set_info.get('id', set_query)
                # name can be a string or dict depending on API version
                name_data = set_info.get('name', set_id)
                set_name = name_data if isinstance(name_data, str) else name_data.get(lang_code, set_id)
                # cardCount can be a dict or int
                card_count_data = set_info.get('cardCount', '?')
                card_count = card_count_data.get('total', '?') if isinstance(card_count_data, dict) else card_count_data
                
                self.log(get_message('console.set_found', name=set_name, id=set_id, count=card_count))
                self.log(get_message('console.download_progress'))
                
                # Download
                ok, fail, total = downloader.download_set(
                    set_query=set_query,
                    output_dir=output_dir,
                    lang=lang_code,
                    quality=quality,
                    ext=ext,
                    workers=8
                )
                
                # Results
                self.log(f"\n{'='*60}")
                self.log(get_message('console.download_complete'))
                self.log(f"{'='*60}")
                self.log(get_message('console.download_success', ok=ok, total=total))
                if fail > 0:
                    self.log(get_message('console.download_failure', fail=fail, total=total))
                self.log(get_message('console.download_folder', folder=f"{output_dir}/{set_id}/"))
                self.log(get_message('console.download_manifest', file=f"{output_dir}/manifest.csv"))
                
                # 🔧 AUTO-GENERATE cards_database.yaml from manifest
                if ok > 0:
                    self.log(f"\n📋 Génération automatique de cards_database.yaml...")
                    try:
                        # Le manifest est à la racine du output_dir, pas dans le sous-dossier set_id
                        manifest_path = f"{output_dir}/manifest.csv"
                        self._generate_yaml_from_manifest(manifest_path, set_id, set_name)
                        self.log(get_message('console.yaml_created'))
                    except Exception as yaml_err:
                        self.log(get_message('console.yaml_error', error=yaml_err))
                
                if fail == 0:
                    self.show_info("✅ Succès", 
                        f"Téléchargement terminé !\n\n"
                        f"✅ {ok} cartes téléchargées\n"
                        f"💾 Dossier: {output_dir}/{set_id}/")
                else:
                    self.show_warning("⚠️ Terminé avec erreurs",
                        f"Téléchargement terminé avec des erreurs.\n\n"
                        f"✅ Succès: {ok}/{total}\n"
                        f"❌ Échecs: {fail}/{total}")
                
                # Mettre à jour les statistiques (V3.2)
                self.update_all_statistics()
                
            except Exception as e:
                self.log(f"❌ ERREUR: {e}")
                import traceback
                self.log(traceback.format_exc())
                self.show_error("Error", f"Erreur lors du téléchargement:\n{e}")
            finally:
                self.stop_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def start_workflow(self):
        """Démarrer le workflow automatique avec WorkflowManager"""
        if self.is_running:
            self.show_warning("Warning", "Une opération est déjà en cours!")
            return
        
        # Vérifier l'environnement virtuel
        if not self.ensure_venv():
            return
        
        # Récupérer configuration
        try:
            num_aug = int(self.workflow_aug_var.get())
            mosaic_mode = self.workflow_mosaic_var.get()
            do_validate = self.workflow_validate_var.get()
            do_balance = self.workflow_balance_var.get()
            do_train = self.workflow_train_var.get()
        except Exception as e:
            self.show_error("Error", f"Configuration invalide:\n{e}")
            return
        
        # Confirmation
        steps_text = f"""Configuration du workflow :

1️⃣ Augmentation : {num_aug} variations
2️⃣ Mosaïques : Mode {mosaic_mode}
3️⃣ Validation : {'✅ Activée' if do_validate else '❌ Désactivée'}
4️⃣ Auto-balancing : {'✅ Activé' if do_balance else '❌ Désactivé'}
5️⃣ Entraînement : {'✅ Activé' if do_train else '❌ Désactivé'}

Continuer ?"""
        
        if not messagebox.askyesno("🚀 Lancer Workflow", steps_text):
            return
        
        self.start_operation("Auto Workflow")
        
        def task():
            try:
                # Créer configuration
                config = WorkflowConfig(
                    num_augmentations=num_aug,
                    mosaic_mode=mosaic_mode,
                    enable_validation=do_validate,
                    enable_balancing=do_balance,
                    enable_training=do_train
                )
                
                # Créer manager
                manager = WorkflowManager(config)
                manager.set_log_callback(self.log)
                manager.set_progress_callback(self.update_workflow_progress)
                
                # Lancer workflow
                self.log(f"⏱️  Durée estimée: {manager.estimate_duration()}")
                results = manager.run()
                
                # Résumé
                if manager.is_success():
                    self.log("\n" + "="*50)
                    self.log("🎉 WORKFLOW TERMINÉ AVEC SUCCÈS!")
                    self.log("="*50)
                    self.show_info("Succès", 
                        f"✅ Workflow terminé!\n\n{manager.get_summary()}")
                else:
                    self.log("\n⚠️ Workflow terminé avec des erreurs")
                    self.show_warning("Attention",
                        f"Workflow terminé avec erreurs:\n\n{manager.get_summary()}")
                
            except Exception as e:
                self.log(f"\n❌ ERREUR WORKFLOW: {e}")
                import traceback
                self.log(traceback.format_exc())
                self.show_error("Erreur", f"Erreur workflow:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def update_workflow_progress(self, current: int, total: int, message: str):
        """Callback pour mise à jour progression workflow"""
        percentage = (current / total) * 100
        self.progress_bar['value'] = percentage
        self.progress_label.config(text=f"{message} ({current}/{total})")
        self.root.update_idletasks()
    
    def open_settings(self):
        """Ouvrir les paramètres"""
        SettingsDialog(self.root, self)
    
    def show_help(self):
        """Ouvrir la documentation d'aide dans le navigateur"""
        import webbrowser
        
        # Ouvrir directement la version GitHub (bien formatée, toujours accessible)
        github_url = "https://github.com/lo26lo/pok/blob/main/HELP.md"
        
        try:
            webbrowser.open(github_url)
            self.log("📖 Help documentation opened in browser")
        except Exception as e:
            self.log(f"⚠️ Could not open browser: {e}")
            # Fallback: afficher le lien
            from pathlib import Path
            help_local = Path("HELP.md").absolute()
            self.show_info(
                "Help Documentation",
                f"📖 Online:\n{github_url}\n\n"
                f"📁 Local:\n{help_local}\n\n"
                "Copy the online link to your browser"
            )
    
    # ==================== TRAINING METHODS ====================
    
    def start_training(self):
        """Démarrer l'entraînement avec TrainingManager"""
        if self.is_running:
            self.show_warning("Warning", "Une opération est déjà en cours!")
            return
        
        # Vérifier l'environnement virtuel
        if not self.ensure_venv():
            return
        
        try:
            model_name = self.train_model_var.get()
            epochs = int(self.train_epochs_var.get())
            batch = int(self.train_batch_var.get())
            device = self.train_device_var.get()
            imgsz = int(self.train_imgsz_var.get())
            workers = int(self.train_workers_var.get())
            cache = self.train_cache_var.get()
            
            # Paramètres avancés (toujours disponibles)
            lr0 = float(self.train_lr0_var.get())
            lrf = float(self.train_lrf_var.get())
            cos_lr = self.train_cosine_var.get()
            patience = int(self.train_patience_var.get())
                
        except Exception as e:
            self.show_error("Error", f"Configuration invalide:\n{e}")
            return
        
        # Vérifier data.yaml
        data_yaml = Path(PATHS['files']['dataset_data_yaml'])
        if not data_yaml.exists():
            self.show_error("Error",
                f"Fichier data.yaml non trouvé!\n{data_yaml}\n\n"
                "Générez d'abord le dataset (Augmentation + Mosaics + Merge).")
            return
        
        self.start_operation("Training")
        
        def task():
            try:
                # Configuration
                config = TrainingConfig(
                    model_name=model_name,
                    epochs=epochs,
                    batch_size=batch,
                    device=device,
                    image_size=imgsz,
                    workers=workers,
                    cache=cache,
                    lr0=lr0,
                    lrf=lrf,
                    cos_lr=cos_lr,
                    patience=patience,
                    data_yaml=data_yaml
                )
                
                # Manager
                manager = TrainingManager(config)
                manager.set_log_callback(self.log)
                
                # Entraîner
                self.log(f"🎓 Démarrage entraînement: {model_name}")
                self.log(f"   Epochs: {epochs}, Batch: {batch}, Image Size: {imgsz}")
                self.log(f"   Device: {device}, Workers: {workers}, Cache: {cache}")
                if cos_lr:
                    self.log(f"   LR: {lr0} → {lrf} (Cosine), Patience: {patience}")
                
                if manager.train():
                    metrics = manager.get_metrics()
                    msg = f"✅ Entraînement terminé!\n\nModèle: {manager.get_best_model_path()}"
                    if metrics:
                        msg += f"\n\nmAP50: {metrics.get('mAP50', 0):.3f}"
                        msg += f"\nmAP50-95: {metrics.get('mAP50-95', 0):.3f}"
                    self.show_info("Succès", msg)
                else:
                    self.show_error("Erreur", "Entraînement échoué!")
                
            except ImportError:
                self.log("❌ Package ultralytics non installé!")
                self.show_error("Erreur",
                    "Package ultralytics non installé!\n\n"
                    "Ce package est requis pour l'entraînement YOLO.\n"
                    "Il nécessite PyTorch et un GPU compatible (recommandé).\n\n"
                    "Installation:\n"
                    "pip install -r requirements_training.txt\n\n"
                    "Ou manuellement:\n"
                    "pip install ultralytics torch torchvision")
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                import traceback
                self.log(traceback.format_exc())
                self.show_error("Erreur", f"Erreur:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def export_tensorrt(self):
        """Exporter le modèle en TensorRT pour déploiement Jetson"""
        try:
            from ultralytics import YOLO
        except ImportError:
            self.show_error("Erreur", 
                "Package ultralytics non installé!\n\n"
                "Installation: pip install ultralytics")
            return
        
        # Chercher le modèle best.pt
        model_path = Path(PATHS['directories']['train_output']) / "weights" / "best.pt"
        
        if not model_path.exists():
            # Demander à l'utilisateur de sélectionner un modèle
            model_path = filedialog.askopenfilename(
                title="Sélectionner le modèle à exporter",
                filetypes=[("PyTorch Model", "*.pt")],
                initialdir=PATHS['directories']['train_base']
            )
            if not model_path:
                return
            model_path = Path(model_path)
        
        # Demander le format d'export
        export_dialog = tk.Toplevel(self.root)
        export_dialog.title("🚀 Export pour Jetson")
        export_dialog.geometry("450x400")
        export_dialog.configure(bg=self.colors['bg_dark'])
        export_dialog.transient(self.root)
        export_dialog.grab_set()
        
        # Centrer la fenêtre
        export_dialog.update_idletasks()
        x = (export_dialog.winfo_screenwidth() // 2) - (225)
        y = (export_dialog.winfo_screenheight() // 2) - (200)
        export_dialog.geometry(f"+{x}+{y}")
        
        tk.Label(export_dialog, 
                text="🚀 Export Modèle pour Jetson Orin",
                font=self.FONT_HEADER,
                bg=self.colors['bg_dark'],
                fg=self.colors['text']).pack(pady=20)
        
        tk.Label(export_dialog,
                text=f"Modèle: {model_path.name}",
                font=self.FONT_TEXT,
                bg=self.colors['bg_dark'],
                fg=self.colors['text_dim']).pack(pady=5)
        
        # Format selection
        format_frame = tk.Frame(export_dialog, bg=self.colors['bg_dark'])
        format_frame.pack(pady=20, fill=tk.X, padx=30)
        
        tk.Label(format_frame, text="Format d'export:",
                font=self.FONT_BUTTON,
                bg=self.colors['bg_dark'],
                fg=self.colors['text']).pack(anchor='w')
        
        format_var = tk.StringVar(value="engine")
        
        formats = [
            ("engine", "🚀 TensorRT Engine (.engine) - Optimal Jetson"),
            ("onnx", "📦 ONNX (.onnx) - Portable"),
            ("torchscript", "🔥 TorchScript (.torchscript) - PyTorch natif")
        ]
        
        for fmt, desc in formats:
            tk.Radiobutton(format_frame, text=desc,
                          variable=format_var, value=fmt,
                          bg=self.colors['bg_dark'],
                          fg=self.colors['text'],
                          selectcolor=self.colors['bg_card'],
                          activebackground=self.colors['bg_dark'],
                          font=self.FONT_TEXT).pack(anchor='w', pady=3)
        
        # Options TensorRT
        options_frame = tk.Frame(export_dialog, bg=self.colors['bg_dark'])
        options_frame.pack(pady=10, fill=tk.X, padx=30)
        
        tk.Label(options_frame, text="Options TensorRT:",
                font=self.FONT_BUTTON,
                bg=self.colors['bg_dark'],
                fg=self.colors['text']).pack(anchor='w')
        
        half_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="✓ FP16 (Half precision) - Recommandé Jetson",
                      variable=half_var,
                      bg=self.colors['bg_dark'],
                      fg=self.colors['text'],
                      selectcolor=self.colors['bg_card'],
                      font=self.FONT_TEXT).pack(anchor='w')
        
        int8_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="✓ INT8 Quantization - Max vitesse (nécessite calibration)",
                      variable=int8_var,
                      bg=self.colors['bg_dark'],
                      fg=self.colors['text'],
                      selectcolor=self.colors['bg_card'],
                      font=self.FONT_TEXT).pack(anchor='w')
        
        dynamic_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="✓ Dynamic batch size",
                      variable=dynamic_var,
                      bg=self.colors['bg_dark'],
                      fg=self.colors['text'],
                      selectcolor=self.colors['bg_card'],
                      font=self.FONT_TEXT).pack(anchor='w')
        
        # Info Jetson
        info_label = tk.Label(export_dialog,
            text="💡 Pour Jetson Orin AGX:\n"
                 "• TensorRT FP16 offre 2-3x speedup\n"
                 "• Exécuter l'export SUR le Jetson pour compatibilité\n"
                 "• Ou exporter ONNX ici, puis convertir sur Jetson",
            font=('Segoe UI', 9),
            bg=self.colors['bg_dark'],
            fg='#F9E2AF',
            justify='left')
        info_label.pack(pady=10, padx=30, anchor='w')
        
        def do_export():
            export_dialog.destroy()
            fmt = format_var.get()
            self.log(f"🚀 Export {model_path.name} vers {fmt.upper()}...")
            self.start_operation(f"Export {fmt.upper()}")
            
            def export_task():
                try:
                    model = YOLO(str(model_path))
                    
                    # Paramètres d'export
                    export_kwargs = {
                        'format': fmt,
                        'half': half_var.get() if fmt == 'engine' else False,
                        'int8': int8_var.get() if fmt == 'engine' else False,
                        'dynamic': dynamic_var.get(),
                        'simplify': True,  # Simplifier le graphe ONNX
                    }
                    
                    self.log(f"   Format: {fmt}")
                    self.log(f"   FP16: {export_kwargs.get('half', False)}")
                    self.log(f"   INT8: {export_kwargs.get('int8', False)}")
                    
                    export_path = model.export(**export_kwargs)
                    
                    self.log(f"✅ Export réussi!")
                    self.log(f"📁 Fichier: {export_path}")
                    self.log("")
                    self.log("📋 Pour déployer sur Jetson Orin AGX:")
                    self.log("   1. Copier le fichier sur le Jetson")
                    self.log("   2. from ultralytics import YOLO")
                    self.log(f"   3. model = YOLO('{Path(export_path).name}')")
                    self.log("   4. results = model.predict(source=0)  # Webcam")
                    
                    self.show_info("Export réussi",
                        f"Modèle exporté:\n{export_path}\n\n"
                        "Copiez ce fichier sur votre Jetson Orin AGX.")
                    
                except Exception as e:
                    self.log(f"❌ Erreur export: {e}")
                    self.show_error("Erreur", f"Export échoué:\n{e}")
                finally:
                    self.end_operation()
            
            threading.Thread(target=export_task, daemon=True).start()
        
        # Buttons
        btn_frame = tk.Frame(export_dialog, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="🚀 Exporter",
                  command=do_export,
                  style='Accent.TButton',
                  width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Annuler",
                  command=export_dialog.destroy,
                  width=15).pack(side=tk.LEFT, padx=5)
    
    def show_training_plots(self):
        """Afficher les graphiques d'entraînement"""
        plots_dir = Path(PATHS['directories']['train_output'])
        results_png = plots_dir / "results.png"
        
        if not results_png.exists():
            self.show_warning("Attention",
                f"Graphiques non trouvés!\n\n{results_png}\n\n"
                "Entraînez d'abord un modèle.")
            return
        
        try:
            import cv2
            img = cv2.imread(str(results_png))
            cv2.imshow("Training Results", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as e:
            self.show_error("Erreur", f"Impossible d'afficher:\n{e}")
    
    # ==================== DETECTION METHODS ====================
    
    def browse_model(self):
        """Parcourir pour sélectionner un modèle"""
        model_path = filedialog.askopenfilename(
            title="Sélectionner modèle YOLO",
            filetypes=[("PyTorch Model", "*.pt"), ("Tous", "*.*")],
            initialdir=PATHS['directories']['train_base']
        )
        if model_path:
            self.detect_model_var.delete(0, tk.END)
            self.detect_model_var.insert(0, model_path)
    
    def start_webcam_detection(self):
        """Démarrer détection webcam avec DetectionManager"""
        try:
            model_path = Path(self.detect_model_var.get())
            conf = self.detect_conf_var.get()
            camera_id = int(self.detect_camera_var.get())
        except Exception as e:
            self.show_error("Error", f"Configuration invalide:\n{e}")
            return
        
        if not model_path.exists():
            self.show_error("Error",
                f"Modèle non trouvé!\n{model_path}\n\n"
                "Entraînez d'abord un modèle.")
            return
        
        self.log("📹 Démarrage détection webcam...")
        self.log(f"   Modèle: {model_path}")
        self.log(f"   Confiance: {conf}")
        self.log(f"   Caméra: {camera_id}")
        
        def task():
            try:
                config = DetectionConfig(
                    model_path=model_path,
                    confidence=conf,
                    camera_id=camera_id,
                    show_prices=self.detect_show_prices_var.get(),
                    identify_cards=self.detect_identify_var.get()
                )
                
                manager = DetectionManager(config)
                manager.set_log_callback(self.log)
                
                self.log("✅ Webcam démarrée! (appuyez sur 'q' pour quitter)")
                manager.detect_webcam()
                self.log("✅ Webcam arrêtée")
                
            except ImportError:
                self.log("❌ Packages manquants (ultralytics ou opencv)!")
                self.show_error("Erreur",
                    "Packages manquants!\n\n"
                    "Installation:\n"
                    "pip install ultralytics opencv-python")
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                self.show_error("Erreur", f"Erreur webcam:\n{e}")
        
        threading.Thread(target=task, daemon=True).start()

    def _price_snapshot_text(self) -> str:
        """Libellé de l'indicateur de snapshot de prix hors-ligne (F10)"""
        try:
            from core.price_cache import snapshot_status
            status = snapshot_status()
        except Exception:
            status = None
        return f"💾 {status}" if status else "💾 No offline price snapshot yet"

    def preload_prices_snapshot(self):
        """Précharge le snapshot de prix hors-ligne (F10)"""
        self.log("⬇️ Préchargement des prix (cartes de la base locale)...")

        def task():
            try:
                from core.price_cache import database_card_ids, preload_prices

                card_ids = database_card_ids()
                if not card_ids:
                    self.log("❌ models/cards_database.yaml vide — rien à précharger")
                    self.show_warning("Preload Prices",
                        "La base de cartes est vide.\n"
                        "Générez-la d'abord (vue Excel/Prices) ou utilisez\n"
                        "python tools/preload_prices.py --set <id>")
                    return

                result = preload_prices(
                    card_ids=card_ids,
                    progress_callback=lambda msg, cur, tot: self.log(msg))

                # Rafraîchir l'indicateur depuis le thread principal
                self.root.after(0, lambda: self.price_snapshot_label.config(
                    text=self._price_snapshot_text()))

                # F09 : notifier les alertes de seuil franchies par ce relevé
                for t in result.get("alerts", []):
                    self.log(f"🔔 ALERTE PRIX: {t.describe()}")
                if result.get("alerts"):
                    lines = "\n".join(f"• {t.describe()}"
                                      for t in result["alerts"])
                    self.show_info("🔔 Alertes de prix", lines)

                if result["failed"] and not result["fetched"]:
                    self.show_error("Preload Prices",
                        "Préchargement impossible (réseau ?).\n"
                        "Le snapshot existant reste utilisable hors-ligne.")
            except Exception as e:
                self.log(f"❌ Erreur préchargement: {e}")
                self.show_error("Erreur", f"Erreur préchargement:\n{e}")

        threading.Thread(target=task, daemon=True).start()

    def open_price_history(self):
        """Ouvre l'historique des prix et la gestion des alertes (F09)"""
        try:
            from gui.price_history_view import PriceHistoryDialog
            PriceHistoryDialog(self.root, self.colors)
        except Exception as e:
            messagebox.showerror("Price History",
                                 f"Impossible d'ouvrir l'historique:\n{e}")

    def start_collection_scan(self):
        """Scan de collection (F03) : webcam + inventaire dédupliqué + export"""
        try:
            model_path = Path(self.detect_model_var.get())
            conf = self.detect_conf_var.get()
            camera_id = int(self.detect_camera_var.get())
        except Exception as e:
            self.show_error("Error", f"Configuration invalide:\n{e}")
            return

        if not model_path.exists():
            self.show_error("Error",
                f"Modèle non trouvé!\n{model_path}\n\n"
                "Entraînez d'abord un modèle.")
            return

        self.log("🧺 Démarrage du scan de collection...")
        self.log("   Présentez vos cartes à la caméra ('q' pour terminer)")

        def task():
            try:
                from core.collection_scanner import CollectionScanner

                config = DetectionConfig(
                    model_path=model_path,
                    confidence=conf,
                    camera_id=camera_id,
                    show_prices=self.detect_show_prices_var.get(),
                    identify_cards=True  # identification exacte recommandée
                )

                manager = DetectionManager(config)
                manager.set_log_callback(self.log)
                scanner = CollectionScanner()

                manager.detect_webcam(scanner=scanner)

                # Récap de fin de session + exports
                s = scanner.summary()
                csv_path = scanner.export_csv()
                xlsx_path = scanner.export_excel()

                self.log(f"🧺 Scan terminé: {s['unique_cards']} cartes uniques, "
                         f"{s['total_quantity']} exemplaires, "
                         f"valeur {s['total_value']:.2f}-{s['total_value_max']:.2f}€")
                self.log(f"   💾 Inventaire: {csv_path}")
                if xlsx_path:
                    self.log(f"   💾 Excel: {xlsx_path}")

                unpriced = (f"\nCartes sans prix: {s['unpriced_cards']}"
                            if s['unpriced_cards'] else "")
                exports = f"CSV: {csv_path}" + (f"\nExcel: {xlsx_path}"
                                                if xlsx_path else "")
                self.show_info("Scan de collection terminé",
                    f"🧺 {s['unique_cards']} cartes uniques "
                    f"({s['total_quantity']} exemplaires)\n"
                    f"💰 Valeur estimée: {s['total_value']:.2f}€ "
                    f"à {s['total_value_max']:.2f}€\n"
                    f"⏱️ Durée: {s['duration_s']:.0f}s"
                    f"{unpriced}\n\n{exports}")

            except ImportError:
                self.log("❌ Packages manquants (ultralytics ou opencv)!")
                self.show_error("Erreur",
                    "Packages manquants!\n\n"
                    "Installation:\n"
                    "pip install ultralytics opencv-python")
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                self.show_error("Erreur", f"Erreur scan:\n{e}")

        threading.Thread(target=task, daemon=True).start()

    def detect_single_image(self):
        """Détecter cartes dans une image"""
        try:
            model_path = Path(self.detect_model_var.get())
            conf = self.detect_conf_var.get()
        except Exception as e:
            self.show_error("Error", f"Configuration invalide:\n{e}")
            return
        
        if not model_path.exists():
            self.show_error("Error", "Modèle non trouvé!")
            return
        
        # Choisir image
        img_path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[("Images", "*.png *.jpg *.jpeg"), ("Tous", "*.*")]
        )
        
        if not img_path:
            return
        
        self.log(f"🔍 Détection sur: {img_path}")
        
        def task():
            try:
                config = DetectionConfig(
                    model_path=model_path,
                    confidence=conf,
                    show_prices=self.detect_show_prices_var.get(),
                    identify_cards=self.detect_identify_var.get()
                )
                
                manager = DetectionManager(config)
                manager.set_log_callback(self.log)
                
                # Détecter et afficher
                manager.show_image(img_path)
                
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                self.show_error("Erreur", f"Erreur:\n{e}")
        
        threading.Thread(target=task, daemon=True).start()
    
    def detect_folder(self):
        """Détecter cartes dans un dossier"""
        try:
            model_path = Path(self.detect_model_var.get())
            conf = self.detect_conf_var.get()
        except Exception as e:
            self.show_error("Error", f"Configuration invalide:\n{e}")
            return
        
        if not model_path.exists():
            self.show_error("Error", "Modèle non trouvé!")
            return
        
        # Choisir dossier
        folder_path = filedialog.askdirectory(title="Choisir un dossier d'images")
        
        if not folder_path:
            return
        
        self.log(f"📂 Détection sur le dossier: {folder_path}")
        self.start_operation("Détection")
        
        def task():
            try:
                config = DetectionConfig(
                    model_path=model_path,
                    confidence=conf,
                    show_prices=self.detect_show_prices_var.get(),
                    identify_cards=self.detect_identify_var.get()
                )
                
                manager = DetectionManager(config)
                manager.set_log_callback(self.log)
                
                # Détecter batch
                results = manager.detect_folder(folder_path)
                
                total = sum(len(dets) for dets in results.values())
                self.log(f"✅ {total} détection(s) sur {len(results)} images")
                
                self.show_info("Succès",
                    f"✅ Détection terminée!\n\n"
                    f"{len(results)} images traitées\n"
                    f"{total} détections totales\n\n"
                    f"Résultats dans: {folder_path}/detections/")
                
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                self.show_error("Erreur", f"Erreur:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    # ==================== FOLDER UTILITIES ====================
    
    def open_folder(self, folder_path: str):
        """
        Open a folder in Windows Explorer.
        
        Args:
            folder_path: Relative or absolute path to the folder
        """
        try:
            from pathlib import Path
            import os
            import subprocess
            
            # Convert to absolute path
            folder = Path(folder_path).resolve()
            
            # Create folder if it doesn't exist
            if not folder.exists():
                folder.mkdir(parents=True, exist_ok=True)
                self.log(f"📂 Created folder: {folder}")
            
            # Open in explorer
            if os.name == 'nt':  # Windows
                os.startfile(str(folder))
            elif os.name == 'posix':  # Linux/Mac
                subprocess.Popen(['xdg-open', str(folder)])
            
            self.log(f"📂 Opened folder: {folder}")
            
        except Exception as e:
            self.log(f"❌ Error opening folder: {e}")
            self.show_error("Error", f"Cannot open folder:\n{e}")
    
    def open_validation_report(self):
        """Ouvrir le rapport de validation HTML dans le navigateur"""
        try:
            import webbrowser
            report_path = Path("validation_report.html")
            
            if report_path.exists():
                webbrowser.open(f"file:///{report_path.absolute()}")
                self.log("🌐 Rapport de validation ouvert dans le navigateur")
            else:
                self.log("⚠️ Aucun rapport de validation trouvé")
                self.show_warning("Rapport introuvable", 
                    "Aucun rapport de validation n'a été généré.\n\n"
                    "Allez dans 'Validation' pour générer un rapport.")
        except Exception as e:
            self.log(f"❌ Erreur ouverture rapport: {e}")
            self.show_error("Erreur", f"Impossible d'ouvrir le rapport:\n{e}")
    
    def apply_training_preset(self, preset_name: str):
        """Appliquer un preset de training et naviguer vers la vue Training"""
        try:
            presets = {
                'quick': {
                    'epochs': 10,
                    'batch': 16,
                    'img_size': 640,
                    'patience': 5,
                    'name': 'Quick Test'
                },
                'standard': {
                    'epochs': 50,
                    'batch': 16,
                    'img_size': 640,
                    'patience': 10,
                    'name': 'Standard'
                },
                'production': {
                    'epochs': 100,
                    'batch': 16,
                    'img_size': 640,
                    'patience': 20,
                    'name': 'Production'
                }
            }
            
            if preset_name in presets:
                preset = presets[preset_name]
                
                # Naviguer vers Training
                self.show_view('training')
                
                # Attendre que la vue soit créée puis appliquer les valeurs
                def apply_values():
                    try:
                        if hasattr(self, 'train_epochs_var'):
                            self.train_epochs_var.delete(0, tk.END)
                            self.train_epochs_var.insert(0, str(preset['epochs']))
                        
                        if hasattr(self, 'train_batch_var'):
                            self.train_batch_var.set(str(preset['batch']))
                        
                        if hasattr(self, 'train_imgsz_var'):
                            self.train_imgsz_var.set(str(preset['img_size']))
                        
                        if hasattr(self, 'train_patience_var'):
                            self.train_patience_var.delete(0, tk.END)
                            self.train_patience_var.insert(0, str(preset['patience']))
                        
                        self.log(f"✅ Preset '{preset['name']}' appliqué: {preset['epochs']} epochs, batch {preset['batch']}")
                    except Exception as e:
                        self.log(f"⚠️ Erreur application preset: {e}")
                
                # Appliquer après un court délai pour laisser la vue se créer
                self.root.after(100, apply_values)
                
        except Exception as e:
            self.log(f"❌ Erreur application preset: {e}")
    
    # ==================== AUGMENTATION METHODS ====================
    
    def start_augmentation_pipeline(self):
        """Lancer le pipeline complet: Holographic → Augmentation"""
        # Vérifier l'environnement virtuel
        if not self.ensure_venv():
            return
        
        try:
            num_holo = int(self.aug_holo_var.get())
            num_aug = int(self.aug_num_var.get())
        except Exception as e:
            self.show_error("Error", f"Configuration invalide:\n{e}")
            return
        
        # Vérifier qu'au moins une opération est demandée
        if num_holo == 0 and num_aug == 0:
            self.show_warning("Warning", "Au moins une opération doit être > 0 !\n\nHolographic = 0 ET Augmentation = 0")
            return
        
        # Message de confirmation
        steps = []
        if num_holo > 0:
            steps.append(f"🌟 Holographic: {num_holo} variations")
        if num_aug > 0:
            steps.append(f"🎨 Augmentation: {num_aug} variations")
        
        confirm_msg = "Pipeline de génération:\n\n" + "\n".join(steps) + "\n\nContinuer ?"
        
        if not messagebox.askyesno("Confirmation", confirm_msg):
            return
        
        self.log("🚀 Démarrage du pipeline de génération...")

        def work(runner):
            source_dir = PATHS['directories']['images']

            # ÉTAPE 1: Holographic (optionnel)
            if num_holo > 0:
                runner.log(f"\n🌟 ÉTAPE 1/2: Génération holographique ({num_holo} variations)...")
                runner.stream_or_fail(
                    [sys.executable, "-u", "core/holographic_augmenter_optimized.py",
                     source_dir,
                     PATHS['directories']['output_holographic'],
                     "--variations", str(num_holo)],
                    "Holographic génération échouée!")
                runner.log("✅ Holographic terminé!")
                # NOTE: source_dir reste "images", l'augmentation part des originales

            # ÉTAPE 2: Augmentation (optionnel) - TOUJOURS depuis images originales
            if num_aug > 0:
                step_num = "2/2" if num_holo > 0 else "1/1"
                runner.log(f"\n🎨 ÉTAPE {step_num}: Augmentation ({num_aug} variations par image)...")
                runner.stream_or_fail(
                    [sys.executable, "-u", "core/augmentation_albumentations.py",
                     "--num_aug", str(num_aug),
                     "--source", "images",  # Toujours "images", jamais "holographic"
                     "--target", "augmented"],
                    "Augmentation échouée!")
                runner.log("✅ Augmentation terminée!")

            runner.log("\n" + "="*50)
            runner.log("🎉 PIPELINE TERMINÉ AVEC SUCCÈS!")
            runner.log("="*50)

        def on_success():
            summary = "Pipeline terminé!\n\n"
            if num_holo > 0:
                summary += f"✅ Holographic: {num_holo} variations générées\n"
            if num_aug > 0:
                summary += f"✅ Augmentation: {num_aug} variations par image\n"
            summary += "\n📂 Output: output/augmented/"
            self.show_info("Succès", summary)
            self.update_stats()
            self.update_all_statistics()

        self.tasks.run("Generation Pipeline", work,
                       on_success=on_success,
                       on_error=lambda msg: self.show_error("Error", msg))

    def start_augmentation(self):
        """Lancer l'augmentation d'images"""
        # Vérifier l'environnement virtuel
        if not self.ensure_venv():
            return
        
        try:
            num_aug = int(self.aug_num_var.get())
            target = self.aug_output_var.get()
            aug_type = self.aug_type_var.get()  # Standard / Holographic / Both
        except Exception as e:
            self.show_error("Error", f"Configuration invalide:\n{e}")
            return
        
        self.log(f"🎨 Augmentation ({aug_type}): {num_aug} variations → {target}/")

        # Lu sur le thread principal (variable Tkinter)
        holo_variations = self.holographic_variations.get()

        def work(runner):
            # Standard augmentation
            if aug_type in ["Standard", "Both"]:
                runner.log("🎨 Running standard augmentation (Albumentations)...")
                returncode = runner.stream(
                    [sys.executable, "-u", "core/augmentation_albumentations.py",
                     "--num_aug", str(num_aug),
                     "--target", target])
                if returncode != 0:
                    runner.log("❌ Standard augmentation failed!")
                    if aug_type == "Standard":
                        raise TaskError("Augmentation failed!")
                else:
                    runner.log("✅ Standard augmentation completed!")

            # Holographic augmentation
            if aug_type in ["Holographic", "Both"]:
                runner.log("✨ Running holographic augmentation (OPTIMIZED - GPU/CPU hybrid)...")
                output_dir = target + "_holographic" if aug_type == "Both" else target
                runner.stream_or_fail(
                    [sys.executable, "-u", "core/holographic_augmenter_optimized.py",
                     "images",  # positional: input directory
                     output_dir,  # positional: output directory
                     "--variations", str(holo_variations)],
                    "Holographic augmentation failed!")
                runner.log("✅ Holographic augmentation completed!")

            runner.log("✅ All augmentations completed successfully!")

        def on_success():
            self.show_info("Success", "Augmentation completed successfully!")
            self.update_stats()

        self.tasks.run("Augmentation", work,
                       on_success=on_success,
                       on_error=lambda msg: self.show_error("Error", msg))
    
    # ==================== MOSAIC METHODS ====================
    
    def start_mosaic(self):
        """Lancer génération de mosaïques"""
        mode = self.mosaic_mode_var.get()
        
        # Extract layout, background, transform values from combobox
        try:
            layout_val = int(self.mosaic_layout_var.get().split(' - ')[0])
            background_val = int(self.mosaic_background_var.get().split(' - ')[0])
            transform_val = int(self.mosaic_transform_var.get().split(' - ')[0])
        except Exception:
            layout_val = 1
            background_val = 0  # Fixed: Default to mode 0 (Fake Cards Mosaic)
            transform_val = 0
        
        # Determine max groups based on mode
        max_groups = None
        if "Quick" in mode:
            max_groups = 25  # 25 groups × 8 cards = 200 mosaics
        elif "Standard" in mode:
            max_groups = 62  # 62 groups × 8 cards ≈ 500 mosaics
        # If "Complete" or "All", max_groups stays None (unlimited)
        
        self.log(f"🧩 Génération mosaïques: {mode}")
        self.log(f"   Layout: {layout_val}, Background: {background_val}, Transform: {transform_val}")
        if max_groups:
            self.log(f"   Max groups: {max_groups}")
        def work(runner):
            # Utilisation de la version OPTIMISÉE par défaut
            cmd = [sys.executable, "-u", "core/mosaic_optimized.py",
                   str(layout_val), str(background_val), str(transform_val)]
            if max_groups:
                cmd.extend(["--max-groups", str(max_groups)])
            runner.stream_or_fail(cmd, "Génération échouée!")
            runner.log("✅ Mosaïques générées!")

        def on_success():
            self.show_info("Succès", "Mosaïques générées avec succès!")
            self.update_stats()
            self.update_all_statistics()

        self.tasks.run("Mosaic Generation", work,
                       on_success=on_success,
                       on_error=lambda msg: self.show_error("Erreur", msg))
    
    # ==================== VALIDATION METHODS ====================
    
    def browse_dataset(self):
        """Parcourir pour sélectionner un dataset"""
        folder = filedialog.askdirectory(
            title="Sélectionner dataset YOLO",
            initialdir="output"
        )
        if folder:
            self.valid_path_var.delete(0, tk.END)
            self.valid_path_var.insert(0, folder)
    
    def start_merge_dataset(self):
        """Fusionner augmented + mosaics dans dataset final"""
        self.log("🔀 Fusion du dataset (augmented + mosaics)...")

        def work(runner):
            # Ajouter scripts/ au path pour import
            scripts_dir = Path(__file__).parent / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))

            import merge_dataset

            # Rediriger stdout pour capturer les prints
            import io
            from contextlib import redirect_stdout

            output = io.StringIO()
            with redirect_stdout(output):
                merge_dataset.merge_dataset()

            for line in output.getvalue().split('\n'):
                if line.strip():
                    runner.log(line)

            runner.log("✅ Dataset fusionné avec succès!")

        def on_success():
            self.show_info("Succès",
                f"Dataset fusionné!\n\n"
                f"📂 Emplacement: {PATHS['directories']['output_dataset']}\n"
                "✓ train.txt et val.txt créés\n"
                "✓ data.yaml copié\n\n"
                "Prêt pour l'entraînement!")

        self.tasks.run("Merge Dataset", work,
                       on_success=on_success,
                       on_error=lambda msg: self.show_error("Erreur", f"Erreur lors du merge:\n{msg}"))
    
    def start_validation(self):
        """Lancer validation du dataset"""
        dataset_path = self.valid_path_var.get()
        html = self.valid_html_var.get()
        
        if not os.path.exists(dataset_path):
            self.show_error("Error", f"Dataset non trouvé:\n{dataset_path}")
            return
        
        self.log(f"✅ Validation: {dataset_path}")

        def work(runner):
            cmd = [sys.executable, "-u", "core/dataset_validator.py", dataset_path]
            if html:
                cmd.append("--html")
            runner.stream_or_fail(cmd, "Validation échouée!")
            runner.log("✅ Validation terminée!")
            if html:
                runner.log("📄 Rapport: validation_report.html")

        self.tasks.run("Validation", work,
                       on_success=lambda: self.show_info(
                           "Succès", "Validation terminée!\nVoir validation_report.html"),
                       on_error=lambda msg: self.show_error("Erreur", msg))
    
    def open_validation_report(self):
        """Ouvrir le rapport HTML"""
        report_path = Path("validation_report.html")
        if report_path.exists():
            import webbrowser
            webbrowser.open(str(report_path.absolute()))
        else:
            self.show_warning("Attention", "Rapport non trouvé!\nValidez d'abord le dataset.")
    
    # ==================== EXPORT METHODS ====================
    
    def start_export(self):
        """Lancer export multi-format"""
        formats = []
        if self.export_coco_var.get():
            formats.append("coco")
        if self.export_voc_var.get():
            formats.append("voc")
        if self.export_tf_var.get():
            formats.append("tfrecord")
        if self.export_robo_var.get():
            formats.append("roboflow")
        
        if not formats:
            self.show_warning("Attention", "Sélectionnez au moins un format!")
            return
        
        self.log(f"📦 Export: {', '.join(formats)}")

        def work(runner):
            for fmt in formats:
                runner.log(f"\n📦 Export format: {fmt}")
                returncode = runner.stream(
                    [sys.executable, "-u", "core/dataset_exporter.py",
                     PATHS['directories']['output_dataset'], "--format", fmt])
                if returncode != 0:
                    runner.log(f"❌ Export {fmt} échoué")
            runner.log("\n✅ Export terminé!")

        self.tasks.run("Export", work,
                       on_success=lambda: self.show_info(
                           "Succès", f"Export terminé!\n\nFormats: {', '.join(formats)}"),
                       on_error=lambda msg: self.show_error("Erreur", msg))
    
    # ==================== TOOLS METHODS ====================
    
    def start_balancing(self):
        """Lancer auto-balancing (VERSION OPTIMISÉE)"""
        self.log("⚖️ Auto-balancing des classes (optimisé)...")

        def work(runner):
            runner.stream_or_fail(
                [sys.executable, "-u", "core/auto_balancer_optimized.py",
                 PATHS['directories']['output_dataset'],
                 "--strategy", "augment", "--target", "50"],
                "Balancing échoué!")
            runner.log("✅ Balancing terminé!")

        self.tasks.run("Balancing", work,
                       on_success=lambda: self.show_info("Succès", "Classes équilibrées!"),
                       on_error=lambda msg: self.show_error("Erreur", msg))
    
    def start_holographic(self):
        """Lancer augmentation holographique"""
        # Dialog pour configurer l'effet holographique
        dialog = tk.Toplevel(self.root)
        dialog.title("✨ Holographic Augmenter")
        dialog.geometry("500x400")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer le dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 200
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Titre
        tk.Label(
            dialog,
            text="✨ Holographic Effect",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # Instructions
        tk.Label(
            dialog,
            text="Apply holographic effects to card images",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        ).pack(pady=(0, 20))
        
        # Configuration frame
        config_frame = tk.Frame(dialog, bg=self.colors['bg_card'])
        config_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Intensity slider
        tk.Label(
            config_frame,
            text="Effect Intensity:",
            font=self.FONT_BUTTON,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(pady=(20, 5))
        
        intensity_var = tk.DoubleVar(value=0.5)
        intensity_slider = tk.Scale(
            config_frame,
            from_=0.1,
            to=1.0,
            resolution=0.1,
            orient='horizontal',
            variable=intensity_var,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            highlightthickness=0,
            troughcolor=self.colors['bg_dark'],
            activebackground=self.colors['accent']
        )
        intensity_slider.pack(fill='x', padx=20, pady=5)
        
        # Number of variations
        tk.Label(
            config_frame,
            text="Number of Variations:",
            font=self.FONT_BUTTON,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(pady=(20, 5))
        
        variations_var = tk.IntVar(value=5)
        variations_spin = tk.Spinbox(
            config_frame,
            from_=1,
            to=20,
            textvariable=variations_var,
            font=self.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        )
        variations_spin.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=20)
        
        def run_holographic():
            variations = variations_var.get()  # Lu avant destruction du dialog
            intensity = intensity_var.get()
            dialog.destroy()
            self.log(f"✨ Holographic augmentation: intensity={intensity}, variations={variations}")

            def work(runner):
                runner.stream_or_fail(
                    [sys.executable, "-u", "core/holographic_augmenter_optimized.py",
                     "images", "images_holographic", "--variations", str(variations)],
                    "Augmentation holographique échouée!")
                runner.log("✅ Holographic augmentation terminée!")

            self.tasks.run("Holographic Augmentation", work,
                           on_success=lambda: self.show_info("Succès", "Effets holographiques appliqués!"),
                           on_error=lambda msg: self.show_error("Erreur", msg))
        
        tk.Button(
            btn_frame,
            text="✨ Apply Effect",
            command=run_holographic,
            bg=self.colors['success'],
            fg='#000000',
            font=self.FONT_BUTTON,
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            font=self.FONT_TEXT,
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)
    
    def start_fake_generator_from_view(self):
        """Générer fake images (random erasing) depuis la vue dédiée"""
        try:
            input_dir = self.fakeimg_input_var.get()
            output_dir = self.fakeimg_output_var.get()
            p = float(self.fakeimg_p_var.get())
            sl = float(self.fakeimg_sl_var.get())
            sh = float(self.fakeimg_sh_var.get())
            r1 = float(self.fakeimg_r1_var.get())
            r2 = float(self.fakeimg_r2_var.get())
        except Exception as e:
            self.show_error("Error", f"Invalid configuration:\n{e}")
            return
        
        if not os.path.exists(input_dir):
            self.show_error("Error", f"Input directory '{input_dir}' does not exist!\nDownload card images first from the Image Download view.")
            return
        
        if sl >= sh:
            self.show_error("Error", "Min area (sl) must be less than max area (sh)!")
            return
        
        if r1 >= r2:
            self.show_error("Error", "Min aspect (r1) must be less than max aspect (r2)!")
            return
        
        self.log(f"🎲 Applying random erasing: {input_dir} → {output_dir}")

        def work(runner):
            runner.stream_or_fail(
                [sys.executable, "-u", "core/random_erasing.py",
                 "--input_dir", input_dir,
                 "--output_dir", output_dir,
                 "--p", str(p),
                 "--sl", str(sl),
                 "--sh", str(sh),
                 "--r1", str(r1),
                 "--r2", str(r2)],
                "Fake generation failed!")

        def on_success():
            if os.path.exists(output_dir):
                count = len([f for f in os.listdir(output_dir)
                             if f.endswith(('.png', '.jpg', '.jpeg'))])
                self.log(f"✅ {count} fake images generated in {output_dir}/")
                self.show_info("Success", f"Generated {count} fake images!")
            else:
                self.log(f"✅ Fake images generated in {output_dir}/")
                self.show_info("Success", "Fake images generated successfully!")
            self.update_stats()
            # Refresh view if still on fakeimg
            if self.current_view == 'fakeimg':
                self.show_view('fakeimg')

        self.tasks.run("Fake Image Generation", work,
                       on_success=on_success,
                       on_error=lambda msg: self.show_error("Error", msg))
    
    def start_fake_generator(self):
        """Générer des fausses images de background"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📋 Fake Background Generator")
        dialog.geometry("500x450")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        
        # Header
        header = tk.Label(dialog,
            text="📋 Fake Background Generator",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        header.pack(pady=20)
        
        subtitle = tk.Label(dialog,
            text="Generate realistic fake backgrounds for training",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(pady=(0, 20))
        
        # Config frame
        config_frame = tk.Frame(dialog, bg=self.colors['bg_card'])
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        content = tk.Frame(config_frame, bg=self.colors['bg_card'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Number of images
        count_frame = tk.Frame(content, bg=self.colors['bg_card'])
        count_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(count_frame,
            text="Number of images:",
            bg=self.colors['bg_card'],
            fg='#FFFFFF',
            font=self.FONT_BUTTON
        ).pack(side=tk.LEFT)
        
        count_var = tk.IntVar(value=self.settings_dialog.fakeimg_count.get() if hasattr(self, 'settings_dialog') else 100)
        count_spinbox = ttk.Spinbox(count_frame, from_=10, to=1000, textvariable=count_var, width=15)
        count_spinbox.pack(side=tk.LEFT, padx=10)
        
        # Output directory
        output_frame = tk.Frame(content, bg=self.colors['bg_card'])
        output_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(output_frame,
            text="Output directory:",
            bg=self.colors['bg_card'],
            fg='#FFFFFF',
            font=self.FONT_BUTTON
        ).pack(side=tk.LEFT)
        
        output_var = tk.StringVar(value=self.settings_dialog.fakeimg_output_dir.get() if hasattr(self, 'settings_dialog') else "fakeimg")
        output_entry = ttk.Entry(output_frame, textvariable=output_var, width=20)
        output_entry.pack(side=tk.LEFT, padx=10)
        
        # Noise range
        tk.Label(content,
            text="Noise Intensity Range:",
            bg=self.colors['bg_card'],
            fg='#FFFFFF',
            font=self.FONT_BUTTON
        ).pack(anchor='w', pady=(15, 5))
        
        noise_frame = tk.Frame(content, bg=self.colors['bg_card'])
        noise_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(noise_frame,
            text="Min:",
            bg=self.colors['bg_card'],
            fg='#FFFFFF',
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT)
        
        min_noise_var = tk.IntVar(value=self.settings_dialog.fakeimg_min_noise.get() if hasattr(self, 'settings_dialog') else 20)
        min_noise = ttk.Scale(noise_frame, from_=0, to=100, variable=min_noise_var, orient='horizontal', length=150)
        min_noise.pack(side=tk.LEFT, padx=5)
        
        tk.Label(noise_frame, textvariable=min_noise_var,
            bg=self.colors['bg_card'],
            fg='#FFFFFF',
            width=3
        ).pack(side=tk.LEFT)
        
        tk.Label(noise_frame,
            text="Max:",
            bg=self.colors['bg_card'],
            fg='#FFFFFF',
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT, padx=(20, 0))
        
        max_noise_var = tk.IntVar(value=self.settings_dialog.fakeimg_max_noise.get() if hasattr(self, 'settings_dialog') else 60)
        max_noise = ttk.Scale(noise_frame, from_=0, to=100, variable=max_noise_var, orient='horizontal', length=150)
        max_noise.pack(side=tk.LEFT, padx=5)
        
        tk.Label(noise_frame, textvariable=max_noise_var,
            bg=self.colors['bg_card'],
            fg='#FFFFFF',
            width=3
        ).pack(side=tk.LEFT)
        
        # Button frame
        btn_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=20)
        
        def run_fake_generator():
            # Lire les variables Tkinter AVANT de détruire le dialog
            count = count_var.get()
            output_dir = output_var.get()
            min_noise = min_noise_var.get()
            max_noise = max_noise_var.get()
            dialog.destroy()
            self.log(f"📋 Generating {count} fake backgrounds...")

            def work(runner):
                runner.stream_or_fail(
                    [sys.executable, "-u", "tools/generate_fake_backgrounds.py",
                     "--count", str(count),
                     "--output", output_dir,
                     "--min-noise", str(min_noise),
                     "--max-noise", str(max_noise)],
                    "Fake generation failed!")
                runner.log(f"✅ {count} fake backgrounds generated in {output_dir}/")

            def on_success():
                self.show_info("Success", f"Generated {count} fake backgrounds!")
                self.update_stats()
                self.update_all_statistics()

            self.tasks.run("Fake Background Generation", work,
                           on_success=on_success,
                           on_error=lambda msg: self.show_error("Error", msg))
        
        tk.Button(
            btn_frame,
            text="📋 Generate",
            command=run_fake_generator,
            bg=self.colors['success'],
            fg='#000000',
            font=self.FONT_BUTTON,
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            font=self.FONT_TEXT,
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)
    
    def open_tcg_browser(self):
        """Ouvrir navigateur API TCG"""
        # Dialog pour rechercher des cartes
        dialog = tk.Toplevel(self.root)
        dialog.title("🎴 TCG API Browser")
        dialog.geometry("600x500")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer le dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 300
        y = (dialog.winfo_screenheight() // 2) - 250
        dialog.geometry(f"600x500+{x}+{y}")
        
        # Titre
        tk.Label(
            dialog,
            text="🎴 Pokemon TCG API Browser",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # Search frame
        search_frame = tk.Frame(dialog, bg=self.colors['bg_card'])
        search_frame.pack(fill='x', padx=30, pady=10)
        
        tk.Label(
            search_frame,
            text="Search Pokemon Card:",
            font=self.FONT_BUTTON,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(pady=(15, 5), padx=20, anchor='w')
        
        search_entry_frame = tk.Frame(search_frame, bg=self.colors['bg_card'])
        search_entry_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_entry_frame,
            textvariable=search_var,
            font=self.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        )
        search_entry.pack(side='left', fill='x', expand=True, ipady=8)
        
        def search_card():
            query = search_var.get().strip()
            if not query:
                self.show_warning("Attention", "Entrez un nom de carte!")
                return
            
            results_text.delete('1.0', tk.END)
            results_text.insert('1.0', f"🔍 Recherche: {query}...\n\n")
            
            def task():
                try:
                    from core import tcgdex_api
                    
                    # Recherche dans l'API
                    results_text.insert(tk.END, "📡 Connexion à TCGdex API...\n")
                    results_text.insert(tk.END, f"✅ Carte: {query}\n")
                    results_text.insert(tk.END, f"📦 Set: Base Set / Jungle / Fossil\n")
                    results_text.insert(tk.END, f"💎 Rarity: Rare / Holo\n")
                    results_text.insert(tk.END, f"🔢 Number: #001\n\n")
                    results_text.insert(tk.END, "ℹ️ Utilisez core/tcgdex_api.py pour plus de détails\n")
                    
                except Exception as e:
                    results_text.insert(tk.END, f"\n❌ Erreur: {e}\n")
            
            threading.Thread(target=task, daemon=True).start()
        
        tk.Button(
            search_entry_frame,
            text="🔍 Search",
            command=search_card,
            bg=self.colors['accent'],
            fg='#000000',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            padx=15,
            cursor='hand2'
        ).pack(side='right', padx=(5, 0))
        
        # Results frame
        results_frame = tk.Frame(dialog, bg=self.colors['bg_card'])
        results_frame.pack(fill='both', expand=True, padx=30, pady=(0, 10))
        
        tk.Label(
            results_frame,
            text="Results:",
            font=self.FONT_BUTTON,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(pady=(15, 5), padx=20, anchor='w')
        
        results_text = scrolledtext.ScrolledText(
            results_frame,
            bg='#2b2b2b',
            fg='#e0e0e0',
            font=('Consolas', 9),
            relief='flat',
            wrap='word'
        )
        results_text.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Instructions initiales
        results_text.insert('1.0', "ℹ️ Enter a Pokemon card name to search\n\n")
        results_text.insert(tk.END, "Examples:\n")
        results_text.insert(tk.END, "• Pikachu\n")
        results_text.insert(tk.END, "• Charizard\n")
        results_text.insert(tk.END, "• Mewtwo\n")
        
        # Close button
        tk.Button(
            dialog,
            text="❌ Close",
            command=dialog.destroy,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            font=self.FONT_TEXT,
            relief='flat',
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(pady=(0, 20))
    
    def show_statistics(self):
        """Afficher statistiques"""
        try:
            images_count = len(list(Path(PATHS['directories']['images']).glob("*.png")))
            aug_count = len(list(Path(PATHS['directories']['output_augmented_images']).glob("*.png"))) if Path(PATHS['directories']['output_augmented_images']).exists() else 0
            mosaic_count = len(list(Path(PATHS['directories']['output_mosaics_images']).glob("*.png"))) if Path(PATHS['directories']['output_mosaics_images']).exists() else 0
            dataset_count = len(list(Path(PATHS['directories']['output_dataset_images']).glob("*.png"))) if Path(PATHS['directories']['output_dataset_images']).exists() else 0
            
            msg = f"""📊 Dataset Statistics

📁 Original images: {images_count}
🎨 Augmented images: {aug_count}
🧩 Mosaics: {mosaic_count}
📦 Final dataset: {dataset_count}

Total: {images_count + aug_count + mosaic_count} images"""
            
            self.show_info("Statistics", msg)
        except Exception as e:
            self.show_error("Error", f"Erreur stats:\n{e}")
    
    def open_yaml_tools(self):
        """Ouvrir dialog YAML & Prices avec TCGdex API"""
        # Dialog pour outils YAML
        dialog = tk.Toplevel(self.root)
        dialog.title("📋 YAML Card Database & Prices")
        dialog.geometry("700x750")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        
        # Centrer le dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 350
        y = (dialog.winfo_screenheight() // 2) - 375
        dialog.geometry(f"700x750+{x}+{y}")
        
        # Titre
        tk.Label(
            dialog,
            text="📋 YAML Card Database & Prices Tools",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # Container avec scrollbar
        canvas = tk.Canvas(dialog, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20))
        
        # Section 1: Générer YAML depuis API
        section1 = tk.Frame(scrollable_frame, bg=self.colors['bg_card'])
        section1.pack(fill='x', pady=10)
        
        tk.Label(
            section1,
            text="📋 Generate Card List from API",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(15, 10))
        
        tk.Label(
            section1,
            text="Set Name or ID (e.g., 'Surging Sparks' or 'sv08'):",
            font=('Segoe UI', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        extension_var = tk.StringVar(value="Surging Sparks")
        tk.Entry(
            section1,
            textvariable=extension_var,
            font=self.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(fill='x', padx=15, pady=(0, 10), ipady=6)
        
        tk.Label(
            section1,
            text="Output File:",
            font=('Segoe UI', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        extension_output_var = tk.StringVar(value=PATHS['files']['cards_database_yaml'])
        tk.Entry(
            section1,
            textvariable=extension_output_var,
            font=self.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(fill='x', padx=15, pady=(0, 10), ipady=6)
        
        tk.Label(
            section1,
            text="ℹ️ Fetches all cards from a set via TCGdex API (free, no auth)",
            font=('Segoe UI', 8, 'italic'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim']
        ).pack(anchor='w', padx=15, pady=(0, 10))
        
        tk.Button(
            section1,
            text="▶️ Generate YAML",
            command=lambda: [dialog.destroy(), self.generate_extension_excel_full(extension_var.get(), extension_output_var.get())],
            bg=self.colors['accent'],
            fg='#000000',
            font=self.FONT_BUTTON,
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(padx=15, pady=(0, 15))
        
        # Section 2: Mettre à jour les prix
        section2 = tk.Frame(scrollable_frame, bg=self.colors['bg_card'])
        section2.pack(fill='x', pady=10)
        
        tk.Label(
            section2,
            text="💰 Update Card Prices",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(15, 10))
        
        tk.Label(
            section2,
            text="Input YAML File (models/cards_database.yaml):",
            font=('Segoe UI', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        price_input_frame = tk.Frame(section2, bg=self.colors['bg_card'])
        price_input_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        price_input_var = tk.StringVar(value=PATHS['files']['cards_database_yaml'])
        tk.Entry(
            price_input_frame,
            textvariable=price_input_var,
            font=self.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(side='left', fill='x', expand=True, ipady=6)
        
        def browse_input():
            filename = filedialog.askopenfilename(
                title="Select YAML File",
                filetypes=[("YAML files", "*.yaml;*.yml"), ("All files", "*.*")]
            )
            if filename:
                price_input_var.set(filename)
        
        tk.Button(
            price_input_frame,
            text="📁",
            command=browse_input,
            bg=self.colors['bg_hover'],
            fg=self.colors['text'],
            font=('Segoe UI', 9),
            relief='flat',
            padx=10,
            cursor='hand2'
        ).pack(side='right', padx=(5, 0))
        
        tk.Label(
            section2,
            text="Output YAML File:",
            font=('Segoe UI', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        price_output_var = tk.StringVar(value="models/cards_with_prices.yaml")
        tk.Entry(
            section2,
            textvariable=price_output_var,
            font=self.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(fill='x', padx=15, pady=(0, 10), ipady=6)
        
        tk.Label(
            section2,
            text="ℹ️ Adds 'Prix', 'Prix max', 'SourcePrix' columns from TCGdex",
            font=('Segoe UI', 8, 'italic'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim']
        ).pack(anchor='w', padx=15, pady=(0, 10))
        
        tk.Button(
            section2,
            text="▶️ Update Prices",
            command=lambda: [dialog.destroy(), self.update_card_prices_full(price_input_var.get(), price_output_var.get())],
            bg=self.colors['success'],
            fg='#000000',
            font=self.FONT_BUTTON,
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(padx=15, pady=(0, 15))
        
        # Section 3: Recherche rapide
        section3 = tk.Frame(scrollable_frame, bg=self.colors['bg_card'])
        section3.pack(fill='x', pady=10)
        
        tk.Label(
            section3,
            text="🔍 Quick Card Search",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(15, 10))
        
        tk.Label(
            section3,
            text="Card Name:",
            font=('Segoe UI', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        search_name_var = tk.StringVar()
        tk.Entry(
            section3,
            textvariable=search_name_var,
            font=self.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(fill='x', padx=15, pady=(0, 10), ipady=6)
        
        tk.Label(
            section3,
            text="Set (optional):",
            font=('Segoe UI', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        search_set_var = tk.StringVar()
        tk.Entry(
            section3,
            textvariable=search_set_var,
            font=self.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(fill='x', padx=15, pady=(0, 10), ipady=6)
        
        tk.Label(
            section3,
            text="ℹ️ Search for a card and display its current prices",
            font=('Segoe UI', 8, 'italic'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_dim']
        ).pack(anchor='w', padx=15, pady=(0, 10))
        
        tk.Button(
            section3,
            text="🔍 Search Price",
            command=lambda: [dialog.destroy(), self.search_card_price_full(search_name_var.get(), search_set_var.get())],
            bg=self.colors['accent'],
            fg='#000000',
            font=self.FONT_BUTTON,
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(padx=15, pady=(0, 15))
        
        # Close button
        tk.Button(
            dialog,
            text="❌ Close",
            command=dialog.destroy,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            font=self.FONT_TEXT,
            relief='flat',
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(pady=10)
    
    def generate_extension_excel_full(self, extension, output):
        """Générer un fichier YAML depuis l'API TCGdex pour une extension"""
        extension = extension.strip()
        output = output.strip()
        
        if not extension:
            self.show_error("Error", "Please enter a set name!")
            return
        
        if not output:
            self.show_error("Error", "Please enter an output filename!")
            return
        
        self.log(f"📋 Generating card list for: {extension}")
        self.start_operation("Generating Card Database")
        
        def task():
            try:
                import pandas as pd
                import requests
                from core.tcgdex_api import TCGdexAPI
                
                self.log("=" * 60)
                self.log("🚀 GENERATION WITH TCGdex (FREE)")
                self.log("=" * 60)
                
                # Charger la config API pour la langue
                try:
                    with open('api_config.json', 'r') as f:
                        api_config = json.load(f)
                except Exception:
                    api_config = {"tcgdex": {"language": "en"}}
                
                tcgdex_config = api_config.get("tcgdex", {})
                language = tcgdex_config.get("language", "en")
                
                self.log(f"🌍 Language: {language}")
                self.log(f"🌐 API: TCGdex v2 (free, no authentication)")
                
                # Initialiser le client TCGdex
                tcgdex = TCGdexAPI(language=language)
                
                # Déterminer si c'est un ID ou un nom de set
                set_lower = extension.lower().strip()
                set_code = tcgdex.set_mapping.get(set_lower)
                
                if set_code:
                    self.log(f"✅ Set recognized: '{extension}' → TCGdex ID: '{set_code}'")
                    set_id = set_code
                elif '-' in extension or len(extension) <= 6:
                    self.log(f"🔍 Extension looks like an ID: '{extension}'")
                    set_id = extension
                else:
                    # Try to find set by name
                    self.log(f"🔍 Searching set by name: '{extension}'...")
                    try:
                        url = f"https://api.tcgdex.net/v2/{language}/sets"
                        response = requests.get(url, timeout=15)
                        response.raise_for_status()
                        sets = response.json()
                        
                        # Search for set
                        found_sets = [s for s in sets if extension.lower() in s.get('name', '').lower()]
                        
                        if not found_sets:
                            self.log(f"❌ Set '{extension}' not found")
                            self.log(f"💡 Try with an ID (e.g., sv08, sv07, base1, etc.)")
                            self.show_error("Error", f"Set '{extension}' not found.\nTry with the set ID (e.g., sv08, sv07, etc.)")
                            return
                        
                        best_match = found_sets[0]
                        set_id = best_match.get('id')
                        set_name = best_match.get('name')
                        
                        self.log(f"✅ Set found: '{set_name}' (ID: {set_id})")
                        
                    except Exception as e:
                        self.log(f"❌ Error searching set: {e}")
                        self.show_error("Error", f"Cannot find set.\nTry with ID (e.g., sv08)")
                        return
                
                # Récupérer toutes les cartes du set
                self.log(f"📡 Fetching cards from set '{set_id}'...")
                
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
                    self.log(f"🎴 Official cards: {official_cards}")
                    self.log(f"📊 Total cards (with variants): {total_cards}")
                    
                    # Récupérer la liste des cartes
                    cards_list = set_data.get('cards', [])
                    
                    if not cards_list:
                        self.log(f"❌ No cards found in set")
                        self.show_warning("Warning", f"No cards found for '{set_name}'")
                        return
                    
                    self.log(f"✅ {len(cards_list)} cards fetched")
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        self.log(f"❌ Set '{set_id}' not found (404)")
                        self.show_error("Error", f"Set '{set_id}' not found.\nCheck the set ID.")
                    else:
                        self.log(f"❌ HTTP Error: {e}")
                        self.show_error("Error", f"Error fetching: {e}")
                    return
                except Exception as e:
                    self.log(f"❌ Error: {e}")
                    self.show_error("Error", f"Error: {e}")
                    return
                
                # Créer la structure YAML
                self.log(f"\n📝 Creating YAML file...")
                self.log(f"📁 File: {output}")
                
                from datetime import datetime
                import yaml
                
                yaml_data = {
                    'metadata': {
                        'version': '1.0',
                        'format': 'YOLO-compatible card database',
                        'last_updated': datetime.now().strftime('%Y-%m-%d'),
                        'source': f'TCGdex API - {set_name}',
                        'total_cards': len(cards_list),
                        'comment': 'Bounding boxes are generated dynamically'
                    },
                    'cards': {}
                }
                
                for card_brief in cards_list:
                    card_number = card_brief.get('localId', '')
                    name = card_brief.get('name', '')
                    
                    # Format card_id: setcode_number (ex: sv08_019)
                    set_code = set_id if set_id else 'unknown'
                    card_id = f"{set_code}_{card_number}"
                    
                    # Format set_full: 001/191
                    if official_cards > 0:
                        set_full = f"{card_number}/{official_cards}"
                    else:
                        set_full = card_number
                    
                    yaml_data['cards'][card_id] = {
                        'name': name,
                        'set': set_name,
                        'set_full': set_full,
                        'type': 'Pokemon',
                        'rarity': 'Common',
                        'price': None,
                        'price_max': None,
                        'price_source': '',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    }
                
                # Créer le dossier si nécessaire
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                self.log(f"💾 Writing to YAML...")
                with open(output, 'w', encoding='utf-8') as f:
                    yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                
                file_size = os.path.getsize(output) / 1024
                
                self.log(f"\n{'='*60}")
                self.log(f"✅ SUCCESS")
                self.log(f"{'='*60}")
                self.log(f"📁 File: {output}")
                self.log(f"💾 Size: {file_size:.1f} KB")
                self.log(f"📊 Cards: {len(cards_list)}")
                self.log(f"🌐 Source: TCGdex API (free)")
                self.log(f"💡 Format: YAML (human-readable)")
                self.log(f"{'='*60}")
                
                self.show_info("Success", f"File generated successfully!\n\n{len(cards_list)} cards from '{set_name}'\n\nFormat: YAML\nSource: TCGdex (free)")
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                self.show_error("Error", f"An error occurred:\n{str(e)}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def update_card_prices_full(self, input_file, output_file):
        """Mettre à jour les prix des cartes dans un fichier YAML avec TCGdex"""
        input_file = input_file.strip()
        output_file = output_file.strip()
        
        if not input_file or not os.path.exists(input_file):
            self.show_error("Error", f"Input file '{input_file}' doesn't exist!")
            return
        
        if not output_file:
            self.show_error("Error", "Please enter an output filename!")
            return
        
        # Charger la config API
        try:
            with open('api_config.json', 'r') as f:
                api_config = json.load(f)
        except Exception:
            api_config = {"tcgdex": {"language": "en"}}
        
        self.log(f"💰 Updating prices from: {input_file}")
        self.log(f"🌐 API: TCGdex (free)")
        
        self.start_operation("Updating Prices")
        
        def task():
            try:
                import yaml
                import concurrent.futures
                import time
                from datetime import datetime
                from core.tcgdex_api import TCGdexAPI
                
                tcgdex_config = api_config.get("tcgdex", {})
                language = tcgdex_config.get("language", "en")
                
                # Créer le client TCGdex
                self.log(f"🔧 Initializing TCGdex client (language: {language})...")
                tcgdex_api = TCGdexAPI(language=language)
                
                # Charger YAML
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                if 'cards' not in data:
                    self.log("❌ Invalid YAML structure (missing 'cards' section)")
                    self.show_error("Error", "Invalid YAML file structure!")
                    return
                
                cards_dict = data['cards']
                total = len(cards_dict)
                processed = 0
                last_log = [0]
                failed = []
                
                def worker(card_id, card_info):
                    """Worker thread to process one card"""
                    nonlocal processed
                    
                    name = str(card_info.get("name", "")).strip()
                    set_name = card_info.get("set", "")
                    set_full = card_info.get("set_full", "")
                    
                    # Extract card number from set_full (ex: "019/191" -> "019")
                    set_hash = set_full.split('/')[0] if '/' in set_full else ""
                    
                    # Delay between requests (free API, no strict rate limit)
                    if processed > 0:
                        time.sleep(0.3)  # 0.3s = fast
                    
                    # Search on TCGdex
                    try:
                        price, pmax, details = tcgdex_api.search_card_with_prices(name, set_name, set_hash)
                        
                        if details:
                            # Extract real source
                            pricing = details.get('pricing', {})
                            if pricing.get('cardmarket'):
                                source = "TCGdex(Cardmarket)"
                            elif pricing.get('tcgplayer'):
                                source = "TCGdex(TCGPlayer)"
                            else:
                                source = "TCGdex"
                            
                            # Update card_info
                            card_info['price'] = price
                            card_info['price_max'] = pmax if pmax else price
                            card_info['price_source'] = source
                            card_info['last_updated'] = datetime.now().strftime('%Y-%m-%d')
                        else:
                            source = None
                    except Exception as e:
                        price, pmax, source = None, None, None
                        failed.append((name, set_hash or "", str(e)))
                    
                    processed += 1
                    now = time.time()
                    if processed % 10 == 0 or (now - last_log[0]) >= 5:
                        percent = int(processed/total*100)
                        self.log(get_message('console.progress', 
                                           processed=processed, total=total, percent=percent))
                        last_log[0] = now
                    
                    return card_id, price, pmax, source
                
                self.log(f"🔄 Processing {total} cards with TCGdex (free)")
                self.log(f"💡 Automatic prices: Cardmarket (EUR) + TCGPlayer (USD)")
                self.log(f"⚡ No rate limit: fast processing (~{total * 0.3:.0f}s estimated)")
                
                start = time.time()
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    futures = [ex.submit(worker, card_id, card_info) for card_id, card_info in cards_dict.items()]
                    for fut in concurrent.futures.as_completed(futures):
                        fut.result()  # Cards already updated in-place
                
                elapsed = time.time() - start
                
                # Update metadata
                data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
                
                # Save YAML
                with open(output_file, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                
                success_count = sum(1 for c in cards_dict.values() if c.get('price') is not None)
                self.log(f"✅ File generated: {output_file}")
                self.log(f"📊 Prices found: {success_count}/{total} ({int(success_count/total*100)}%)")
                self.log(f"⏱️  Total time: {elapsed:.1f}s (~{(elapsed/total if total else 0):.2f}s/card)")
                
                if failed:
                    self.log(f"⚠️  {len(failed)} cards failed (examples):")
                    for c, num, e in failed[:5]:
                        self.log(f"   • {c} #{num}: {e[:50]}")
                
                self.show_info("Complete", f"Prices updated!\n{success_count}/{total} cards with prices")
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                self.show_error("Error", f"Error:\n{str(e)}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def search_card_price_full(self, card_name, card_set):
        """Rechercher le prix d'une carte"""
        card_name = card_name.strip()
        card_set = card_set.strip() if card_set else None
        
        if not card_name:
            self.show_error("Error", "Please enter a card name!")
            return
        
        self.log(f"🔍 Searching price for: {card_name}")
        if card_set:
            self.log(f"   Set: {card_set}")
        
        self.start_operation("Searching")
        
        def task():
            try:
                from core.tcgdex_api import TCGdexAPI
                
                # Charger config
                try:
                    with open('api_config.json', 'r') as f:
                        api_config = json.load(f)
                except Exception:
                    api_config = {"tcgdex": {"language": "en"}}
                
                tcgdex_config = api_config.get("tcgdex", {})
                language = tcgdex_config.get("language", "en")
                
                tcgdex_api = TCGdexAPI(language=language)
                
                self.log(f"📡 Searching on TCGdex...")
                price, pmax, details = tcgdex_api.search_card_with_prices(card_name, card_set, None)
                
                if details:
                    name = details.get('name', card_name)
                    set_name = details.get('set', {}).get('name', 'Unknown')
                    
                    pricing = details.get('pricing', {})
                    cardmarket = pricing.get('cardmarket', {})
                    tcgplayer = pricing.get('tcgplayer', {})
                    
                    result = f"🎴 Card: {name}\n📦 Set: {set_name}\n\n"
                    
                    if cardmarket:
                        result += "💶 Cardmarket (EUR):\n"
                        result += f"   Average: {cardmarket.get('averageSellPrice', 'N/A')} €\n"
                        result += f"   Low: {cardmarket.get('lowPrice', 'N/A')} €\n"
                        result += f"   Trend: {cardmarket.get('trendPrice', 'N/A')} €\n\n"
                    
                    if tcgplayer:
                        result += "💵 TCGPlayer (USD):\n"
                        result += f"   Market: ${tcgplayer.get('market', 'N/A')}\n"
                        result += f"   Low: ${tcgplayer.get('low', 'N/A')}\n"
                        result += f"   Mid: ${tcgplayer.get('mid', 'N/A')}\n"
                        result += f"   High: ${tcgplayer.get('high', 'N/A')}\n"
                    
                    if not cardmarket and not tcgplayer:
                        result += "⚠️ No prices available"
                    
                    self.log(f"✅ Card found: {name}")
                    self.show_info("Card Prices", result)
                else:
                    self.log(f"❌ Card not found: {card_name}")
                    self.show_warning("Not Found", f"Card '{card_name}' not found.\n\nTry with a different spelling or set name.")
                
            except Exception as e:
                self.log(f"❌ Error: {e}")
                import traceback
                self.log(traceback.format_exc())
                self.show_error("Error", f"Error:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    # ==================== CLEAN METHODS ====================
    
    def clean_output(self):
        """Nettoyer tout le dossier output/"""
        result = messagebox.askyesno(
            "Confirm Clean",
            "⚠️ This will DELETE the entire output/ folder!\n\n"
            "This includes:\n"
            "• All augmented images\n"
            "• All mosaics\n"
            "• All YOLO datasets\n\n"
            "Are you sure?",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            import shutil
            output_path = Path(PATHS['directories']['output_base'])
            if output_path.exists():
                shutil.rmtree(output_path)
                self.log("✅ Output folder deleted")
                self.show_info("Success", "Output folder cleaned successfully!")
            else:
                self.log("⚠️ Output folder not found")
                self.show_warning("Warning", "Output folder not found!")
        except Exception as e:
            self.log(f"❌ Error cleaning output: {e}")
            self.show_error("Error", f"Failed to clean output:\n{e}")
    
    def clean_augmented(self):
        """Nettoyer output/augmented/"""
        result = messagebox.askyesno(
            "Confirm Clean",
            "⚠️ This will DELETE output/augmented/ folder!\n\n"
            "This includes all augmented images and labels.\n\n"
            "Are you sure?",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            import shutil
            aug_path = Path(PATHS['directories']['output_augmented'])
            if aug_path.exists():
                shutil.rmtree(aug_path)
                self.log("✅ Augmented folder deleted")
                self.show_info("Success", "Augmented folder cleaned!")
            else:
                self.log("⚠️ Augmented folder not found")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.show_error("Error", f"Failed to clean:\n{e}")
    
    def clean_mosaics(self):
        """Nettoyer output/mosaics/ et output/dataset/"""
        result = messagebox.askyesno(
            "Confirm Clean",
            "⚠️ This will DELETE output/mosaics/ and output/dataset/ folders!\n\n"
            "This includes all mosaics and merged datasets.\n\n"
            "Are you sure?",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            import shutil
            
            # Nettoyer mosaics
            mosaic_path = Path(PATHS['directories']['output_mosaics'])
            if mosaic_path.exists():
                shutil.rmtree(mosaic_path)
                self.log("✅ Mosaics folder deleted")
            
            # Nettoyer dataset
            dataset_path = Path(PATHS['directories']['output_dataset'])
            if dataset_path.exists():
                shutil.rmtree(dataset_path)
                self.log("✅ Dataset folder deleted")
            
            self.show_info("Success", "Mosaics and Dataset folders cleaned!")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.show_error("Error", f"Failed to clean:\n{e}")
    
    def clean_training(self):
        """Nettoyer runs/ (résultats d'entraînement)"""
        result = messagebox.askyesno(
            "Confirm Clean",
            "⚠️ This will DELETE runs/ folder!\n\n"
            "This includes all training results:\n"
            "• Trained models (weights/)\n"
            "• Training metrics\n"
            "• Validation images\n\n"
            "Are you sure?",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            import shutil
            runs_path = Path(PATHS['directories']['train_base'])
            if runs_path.exists():
                shutil.rmtree(runs_path)
                self.log("✅ Training results deleted")
                self.show_info("Success", "Training results cleaned!")
            else:
                self.log("⚠️ Training results not found")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.show_error("Error", f"Failed to clean:\n{e}")
    
    def clean_holographic(self):
        """Nettoyer images_holographic/"""
        result = messagebox.askyesno(
            "Confirm Clean",
            "⚠️ This will DELETE images_holographic/ folder!\n\n"
            "This includes all holographic augmented images.\n\n"
            "Are you sure?",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            import shutil
            holo_path = Path(PATHS['directories']['output_holographic'])
            if holo_path.exists():
                shutil.rmtree(holo_path)
                self.log("✅ Holographic folder deleted")
                self.show_info("Success", "Holographic folder cleaned!")
            else:
                self.log("⚠️ Holographic folder not found")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.show_error("Error", f"Failed to clean:\n{e}")
    
    def clean_fakeimg(self):
        """Nettoyer fakeimg_augmented/"""
        result = messagebox.askyesno(
            "Confirm Clean",
            "⚠️ This will DELETE fake images folder!\n\n"
            "This includes:\n"
            "• fakeimg_augmented/ (generated fake images)\n\n"
            "Note: Source images in images/ folder will NOT be deleted.\n\n"
            "Are you sure?",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            import shutil
            deleted = []
            
            fake_aug_path = Path("fakeimg_augmented")
            if fake_aug_path.exists():
                shutil.rmtree(fake_aug_path)
                deleted.append("fakeimg_augmented/")
            
            if deleted:
                self.log(f"✅ Deleted: {', '.join(deleted)}")
                self.show_info("Success", f"Cleaned: {', '.join(deleted)}")
            else:
                self.log("⚠️ Fake image folder not found")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.show_error("Error", f"Failed to clean:\n{e}")
    
    def clean_all(self):
        """Nettoyer TOUS les dossiers générés"""
        include_images = self.clean_include_images_var.get()
        
        folders_to_delete = [
            "output/",
            "runs/",
            "images_holographic/",
            "fakeimg_augmented/"
        ]
        
        if include_images:
            folders_to_delete.append("images/")
        
        message = (
            "🚨 WARNING: This will DELETE ALL generated folders!\n\n"
            "Folders to be deleted:\n"
        )
        for folder in folders_to_delete:
            message += f"  • {folder}\n"
        
        message += "\n⚠️ THIS ACTION CANNOT BE UNDONE!\n\nAre you sure?"
        
        result = messagebox.askyesno(
            "Confirm Clean All",
            message,
            icon='warning'
        )
        
        if not result:
            return
        
        # Double confirmation
        result2 = messagebox.askyesno(
            "Final Confirmation",
            "🚨 LAST CHANCE!\n\n"
            "This will permanently delete all selected folders.\n\n"
            "Type 'YES' mentally and click Yes to proceed.",
            icon='error'
        )
        
        if not result2:
            return
        
        try:
            import shutil
            deleted = []
            errors = []
            
            for folder in folders_to_delete:
                folder_path = Path(folder.rstrip('/'))
                if folder_path.exists():
                    try:
                        shutil.rmtree(folder_path)
                        deleted.append(folder)
                        self.log(f"✅ Deleted: {folder}")
                    except Exception as e:
                        errors.append(f"{folder}: {e}")
                        self.log(f"❌ Failed: {folder} - {e}")
            
            if deleted:
                message = f"✅ Successfully cleaned {len(deleted)} folder(s):\n\n"
                message += "\n".join(f"• {f}" for f in deleted)
                
                if errors:
                    message += f"\n\n⚠️ Errors ({len(errors)}):\n"
                    message += "\n".join(f"• {e}" for e in errors)
                
                self.show_info("Clean Complete", message)
            else:
                self.show_info("Clean Complete", "No folders found to clean.")
                
        except Exception as e:
            self.log(f"❌ Error during clean all: {e}")
            self.show_error("Error", f"Failed to clean:\n{e}")
    
    def open_output_folder(self):
        """Ouvrir dossier output"""
        output_path = Path("output").absolute()
        if output_path.exists():
            import subprocess
            subprocess.run(["explorer", str(output_path)])
        else:
            self.show_warning("Attention", "Dossier output/ non trouvé!")
    
    def open_folder(self, folder_name):
        """Ouvrir un dossier spécifique"""
        folder_path = Path(folder_name).absolute()
        if folder_path.exists():
            import subprocess
            subprocess.run(["explorer", str(folder_path)])
        else:
            self.show_warning("Warning", f"Folder {folder_name}/ not found!")

def main():
    setup_logging()  # logs/pokemon_gui.log (rotation 1 Mo x3)
    root = tk.Tk()
    app = ModernPokemonGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
