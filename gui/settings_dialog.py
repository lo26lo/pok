"""
SettingsDialog — dialogue de configuration global (8 onglets).

Extrait de GUI_v3.1_modern.py lors du refactoring Phase 4.
"""
import json
import time
import traceback
import multiprocessing
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from core.utils import PATHS, UI_MESSAGES
from gui.config import GuiConfig


class SettingsDialog:
    """Dialog de configuration des paramètres globaux"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Settings")
        self.dialog.geometry("800x700")
        self.dialog.configure(bg='#1e1e2e')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"800x700+{x}+{y}")
        
        # Variables de configuration
        self.load_settings()
        
        try:
            self.create_ui()
            print("✅ Settings dialog created successfully")
        except Exception as e:
            print(f"❌ Error creating Settings dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def load_settings(self):
        """Charger les paramètres depuis gui_config.json (via GuiConfig)"""
        config = GuiConfig().data
        
        # Paramètres par défaut (from paths.json)
        self.default_images_dir = tk.StringVar(value=config.get("default_images_dir", PATHS['directories']['images']))
        self.default_output_dir = tk.StringVar(value=config.get("default_output_dir", PATHS['directories']['output_base']))
        self.default_augmented_dir = tk.StringVar(value=config.get("default_augmented_dir", PATHS['directories']['output_augmented']))
        self.default_mosaic_dir = tk.StringVar(value=config.get("default_mosaic_dir", PATHS['directories']['output_mosaics']))
        self.default_dataset_dir = tk.StringVar(value=config.get("default_dataset_dir", PATHS['directories']['output_dataset']))
        self.default_fakeimg_dir = tk.StringVar(value=config.get("default_fakeimg_dir", PATHS['directories']['output_backgrounds']))
        self.default_holographic_dir = tk.StringVar(value=config.get("default_holographic_dir", PATHS['directories']['output_holographic']))
        
        self.default_augmentations = tk.IntVar(value=config.get("default_augmentations", 50))
        self.holographic_intensity = tk.DoubleVar(value=config.get("holographic_intensity", 0.7))
        self.holographic_variations = tk.IntVar(value=config.get("holographic_variations", 3))
        self.default_mosaic_mode = tk.StringVar(value=config.get("default_mosaic_mode", "standard"))
        self.default_mosaic_layout = tk.IntVar(value=config.get("default_mosaic_layout", 1))
        self.default_mosaic_background = tk.IntVar(value=config.get("default_mosaic_background", 1))
        self.default_mosaic_transform = tk.IntVar(value=config.get("default_mosaic_transform", 0))
        self.default_model = tk.StringVar(value=config.get("default_model", "yolov8n.pt"))
        self.default_epochs = tk.IntVar(value=config.get("default_epochs", 50))
        self.default_batch = tk.IntVar(value=config.get("default_batch", 16))
        self.default_device = tk.StringVar(value=config.get("default_device", "0"))
        self.tcgdex_api_key = tk.StringVar(value=config.get("tcgdex_api_key", ""))
        self.auto_save_logs = tk.BooleanVar(value=config.get("auto_save_logs", True))
        self.enable_notifications = tk.BooleanVar(value=config.get("enable_notifications", True))
        
        # Fake image generation settings (random erasing) - from paths.json
        self.fakeimg_input_dir = tk.StringVar(value=config.get("fakeimg_input_dir", PATHS['directories']['backgrounds_original']))
        self.fakeimg_output_dir = tk.StringVar(value=config.get("fakeimg_output_dir", PATHS['directories']['output_backgrounds']))
        self.fakeimg_p = tk.DoubleVar(value=config.get("fakeimg_p", 0.5))
        self.fakeimg_sl = tk.DoubleVar(value=config.get("fakeimg_sl", 0.02))
        self.fakeimg_sh = tk.DoubleVar(value=config.get("fakeimg_sh", 0.4))
        self.fakeimg_r1 = tk.DoubleVar(value=config.get("fakeimg_r1", 0.3))
        self.fakeimg_r2 = tk.DoubleVar(value=config.get("fakeimg_r2", 3.3))
        
        # Image download settings - from paths.json
        self.default_download_dir = tk.StringVar(value=config.get("default_download_dir", PATHS['directories']['images']))
        self.default_download_lang = tk.StringVar(value=config.get("default_download_lang", "English"))
        self.default_download_quality = tk.StringVar(value=config.get("default_download_quality", "high"))
        self.default_download_format = tk.StringVar(value=config.get("default_download_format", "png"))
        self.default_download_workers = tk.IntVar(value=config.get("default_download_workers", 8))
        
        # Debug settings
        self.debug_device = tk.StringVar(value=config.get("debug_device", "auto"))  # auto, cpu, gpu, 0, 1, etc.
        self.debug_workers = tk.IntVar(value=config.get("debug_workers", multiprocessing.cpu_count()))
        self.debug_log_level = tk.StringVar(value=config.get("debug_log_level", "INFO"))  # ERROR, WARNING, INFO, DEBUG, TRACE
        self.debug_cache_mode = tk.StringVar(value=config.get("debug_cache_mode", "ram"))  # ram, disk, disabled
        self.debug_profiling = tk.BooleanVar(value=config.get("debug_profiling", False))
        self.debug_benchmark = tk.BooleanVar(value=config.get("debug_benchmark", False))
        self.debug_save_logs = tk.BooleanVar(value=config.get("debug_save_logs", False))
        self.debug_multiprocessing = tk.BooleanVar(value=config.get("debug_multiprocessing", False))
        self.debug_memory_profiling = tk.BooleanVar(value=config.get("debug_memory_profiling", False))
    
    def create_ui(self):
        """Créer l'interface du dialog"""
        colors = self.app.colors
        
        # Header
        header = tk.Frame(self.dialog, bg=colors['bg_sidebar'], height=60)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        # Container pour titre + bouton save
        header_content = tk.Frame(header, bg=colors['bg_sidebar'])
        header_content.pack(fill='both', expand=True, padx=20)
        
        title = tk.Label(
            header_content,
            text="⚙️ Configuration",
            font=('Segoe UI', 18, 'bold'),
            bg=colors['bg_sidebar'],
            fg=colors['text']
        )
        title.pack(side='left', pady=15)
        
        # Bouton Save dans le header (à droite)
        save_header_btn = tk.Button(
            header_content,
            text="💾 Save",
            command=self.save_settings,
            bg=colors['success'],
            fg='#000000',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        save_header_btn.pack(side='right', pady=15)
        
        # Notebook avec catégories
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Onglet Général
        general_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(general_frame, text=f"  {UI_MESSAGES['gui']['tabs']['general']}  ")
        self.create_general_tab(general_frame)
        
        # Onglet Augmentation
        aug_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(aug_frame, text=f"  {UI_MESSAGES['gui']['tabs']['augmentation']}  ")
        self.create_augmentation_tab(aug_frame)
        
        # Onglet Mosaic
        mosaic_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(mosaic_frame, text=f"  {UI_MESSAGES['gui']['tabs']['mosaic']}  ")
        self.create_mosaic_tab(mosaic_frame)
        
        # Onglet Fake Images
        fake_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(fake_frame, text=f"  {UI_MESSAGES['gui']['tabs']['fake_images']}  ")
        self.create_fakebackgrounds_tab(fake_frame)
        
        # Onglet Image Download
        download_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(download_frame, text=f"  {UI_MESSAGES['gui']['tabs']['download']}  ")
        self.create_download_tab(download_frame)
        
        # Onglet Training
        train_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(train_frame, text=f"  {UI_MESSAGES['gui']['tabs']['training']}  ")
        self.create_training_tab(train_frame)
        
        # Onglet Advanced
        advanced_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(advanced_frame, text=f"  {UI_MESSAGES['gui']['tabs']['advanced']}  ")
        self.create_advanced_tab(advanced_frame)
        
        # Onglet Debug
        debug_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(debug_frame, text="  🐛 Debug  ")
        self.create_debug_tab(debug_frame)
        
        # Footer avec boutons
        footer = tk.Frame(self.dialog, bg=colors['bg_sidebar'], height=70)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        
        btn_frame = tk.Frame(footer, bg=colors['bg_sidebar'])
        btn_frame.pack(expand=True)
        
        # Bouton Save
        save_btn = tk.Button(
            btn_frame,
            text="💾 Save",
            command=self.save_settings,
            bg=colors['success'],
            fg='#000000',
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            padx=30,
            pady=10,
            cursor='hand2'
        )
        save_btn.pack(side='left', padx=5)
        
        # Bouton Cancel
        cancel_btn = tk.Button(
            btn_frame,
            text="❌ Cancel",
            command=self.dialog.destroy,
            bg=colors['bg_card'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            relief='flat',
            padx=30,
            pady=10,
            cursor='hand2'
        )
        cancel_btn.pack(side='left', padx=5)
    
    def create_general_tab(self, parent):
        """Onglet paramètres généraux"""
        colors = self.app.colors
        
        container = tk.Frame(parent, bg=colors['bg_dark'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Images directory
        tk.Label(
            container,
            text="📁 Default Images Directory:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        frame1 = tk.Frame(container, bg=colors['bg_dark'])
        frame1.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        tk.Entry(
            frame1,
            textvariable=self.default_images_dir,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(side='left', fill='x', expand=True, ipady=8)
        
        tk.Button(
            frame1,
            text="📂",
            command=lambda: self.browse_dir(self.default_images_dir),
            bg=colors['accent'],
            fg='#000000',
            font=self.app.FONT_TEXT,
            relief='flat',
            padx=15,
            cursor='hand2'
        ).pack(side='right', padx=(5, 0))
        
        # Output directory
        tk.Label(
            container,
            text="📤 Default Output Directory:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        frame2 = tk.Frame(container, bg=colors['bg_dark'])
        frame2.grid(row=3, column=0, sticky='ew', pady=(0, 20))
        
        tk.Entry(
            frame2,
            textvariable=self.default_output_dir,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(side='left', fill='x', expand=True, ipady=8)
        
        tk.Button(
            frame2,
            text="📂",
            command=lambda: self.browse_dir(self.default_output_dir),
            bg=colors['accent'],
            fg='#000000',
            font=self.app.FONT_TEXT,
            relief='flat',
            padx=15,
            cursor='hand2'
        ).pack(side='right', padx=(5, 0))
        
        # Augmented directory
        tk.Label(
            container,
            text="🎨 Augmented Output Directory:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        frame3 = tk.Frame(container, bg=colors['bg_dark'])
        frame3.grid(row=5, column=0, sticky='ew', pady=(0, 15))
        
        tk.Entry(
            frame3,
            textvariable=self.default_augmented_dir,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(side='left', fill='x', expand=True, ipady=8)
        
        tk.Button(
            frame3,
            text="📂",
            command=lambda: self.browse_dir(self.default_augmented_dir),
            bg=colors['accent'],
            fg='#000000',
            font=self.app.FONT_TEXT,
            relief='flat',
            padx=15,
            cursor='hand2'
        ).pack(side='right', padx=(5, 0))
        
        # Mosaic directory
        tk.Label(
            container,
            text="🧩 Mosaic Output Directory:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        frame4 = tk.Frame(container, bg=colors['bg_dark'])
        frame4.grid(row=7, column=0, sticky='ew', pady=(0, 15))
        
        tk.Entry(
            frame4,
            textvariable=self.default_mosaic_dir,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(side='left', fill='x', expand=True, ipady=8)
        
        tk.Button(
            frame4,
            text="📂",
            command=lambda: self.browse_dir(self.default_mosaic_dir),
            bg=colors['accent'],
            fg='#000000',
            font=self.app.FONT_TEXT,
            relief='flat',
            padx=15,
            cursor='hand2'
        ).pack(side='right', padx=(5, 0))
        
        # Fake images output directory
        tk.Label(
            container,
            text="🎲 Fake Images Output Directory:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=8, column=0, sticky='w', pady=(0, 5))
        
        frame5 = tk.Frame(container, bg=colors['bg_dark'])
        frame5.grid(row=9, column=0, sticky='ew', pady=(0, 15))
        
        tk.Entry(
            frame5,
            textvariable=self.default_fakeimg_dir,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(side='left', fill='x', expand=True, ipady=8)
        
        tk.Button(
            frame5,
            text="📂",
            command=lambda: self.browse_dir(self.default_fakeimg_dir),
            bg=colors['accent'],
            fg='#000000',
            font=self.app.FONT_TEXT,
            relief='flat',
            padx=15,
            cursor='hand2'
        ).pack(side='right', padx=(5, 0))
        
        # Holographic directory
        tk.Label(
            container,
            text="✨ Holographic Output Directory:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=10, column=0, sticky='w', pady=(0, 5))
        
        frame6 = tk.Frame(container, bg=colors['bg_dark'])
        frame6.grid(row=11, column=0, sticky='ew', pady=(0, 20))
        
        tk.Entry(
            frame6,
            textvariable=self.default_holographic_dir,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        ).pack(side='left', fill='x', expand=True, ipady=8)
        
        tk.Button(
            frame6,
            text="📂",
            command=lambda: self.browse_dir(self.default_holographic_dir),
            bg=colors['accent'],
            fg='#000000',
            font=self.app.FONT_TEXT,
            relief='flat',
            padx=15,
            cursor='hand2'
        ).pack(side='right', padx=(5, 0))
        
        # Auto-save logs
        tk.Checkbutton(
            container,
            text="💾 Auto-save logs to file",
            variable=self.auto_save_logs,
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text']
        ).grid(row=12, column=0, sticky='w', pady=10)
        
        # Enable notifications
        tk.Checkbutton(
            container,
            text="🔔 Enable notifications",
            variable=self.enable_notifications,
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text']
        ).grid(row=13, column=0, sticky='w', pady=10)
        
        container.grid_columnconfigure(0, weight=1)
    
    def create_augmentation_tab(self, parent):
        """Onglet paramètres d'augmentation"""
        colors = self.app.colors
        
        container = tk.Frame(parent, bg=colors['bg_dark'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Info message
        tk.Label(
            container,
            text="ℹ️ Configuration du Pipeline Augmentation Unifié",
            bg=colors['bg_dark'],
            fg=colors['accent'],
            font=('Segoe UI', 12, 'bold')
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="Ces paramètres définissent les valeurs par défaut du pipeline 'Holographic → Augmentation'.",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=1, column=0, sticky='w', pady=(0, 20))
        
        # Séparateur
        tk.Frame(container, bg=colors['border'], height=1).grid(row=2, column=0, sticky='ew', pady=(0, 20))
        
        # Section 1: Holographic
        tk.Label(
            container,
            text="🌟 Holographic Generation Defaults:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=3, column=0, sticky='w', pady=(0, 10))
        
        holo_frame = tk.Frame(container, bg=colors['bg_dark'])
        holo_frame.grid(row=4, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(
            holo_frame,
            text="Number of variations:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            holo_frame,
            from_=0,
            to=10,
            textvariable=self.holographic_variations,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=10
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            holo_frame,
            text="(0 = skip holographic)",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT, padx=5)
        
        # Intensity
        intensity_frame = tk.Frame(container, bg=colors['bg_dark'])
        intensity_frame.grid(row=5, column=0, sticky='w', pady=(0, 20))
        
        tk.Label(
            intensity_frame,
            text="Effect intensity:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        intensity_scale = ttk.Scale(
            intensity_frame,
            from_=0.1,
            to=1.0,
            variable=self.holographic_intensity,
            orient='horizontal',
            length=200
        )
        intensity_scale.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            intensity_frame,
            textvariable=self.holographic_intensity,
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=('Segoe UI', 9, 'bold'),
            width=5
        ).pack(side=tk.LEFT)
        
        # Séparateur
        tk.Frame(container, bg=colors['border'], height=1).grid(row=6, column=0, sticky='ew', pady=(0, 20))
        
        # Section 2: Augmentation
        tk.Label(
            container,
            text="🎨 Augmentation Defaults:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=7, column=0, sticky='w', pady=(0, 10))
        
        aug_frame = tk.Frame(container, bg=colors['bg_dark'])
        aug_frame.grid(row=8, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(
            aug_frame,
            text="Augmentations per image:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            aug_frame,
            from_=0,
            to=100,
            textvariable=self.default_augmentations,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=10
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            aug_frame,
            text="(0 = skip augmentation)",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT, padx=5)
        
        # Info résultat attendu
        tk.Label(
            container,
            text="💡 Résultat attendu avec 8 cartes sources:",
            bg=colors['bg_dark'],
            fg=colors['accent'],
            font=('Segoe UI', 10, 'bold')
        ).grid(row=9, column=0, sticky='w', pady=(20, 5))
        
        result_text = tk.Text(
            container,
            height=4,
            bg=colors['bg_card'],
            fg=colors['text'],
            font=('Consolas', 9),
            relief='flat',
            bd=0,
            wrap='word'
        )
        result_text.grid(row=10, column=0, sticky='ew', pady=(0, 10))
        
        result_info = f"""• Holographic: 8 cartes × {self.holographic_variations.get()} = {8 * self.holographic_variations.get()} images
• Augmentation: {8 * self.holographic_variations.get()} × {self.default_augmentations.get()} = {8 * self.holographic_variations.get() * self.default_augmentations.get()} images
• Mosaics possibles: {8 * self.holographic_variations.get() * self.default_augmentations.get()} ÷ 8 = {(8 * self.holographic_variations.get() * self.default_augmentations.get()) // 8} groupes"""
        
        result_text.insert('1.0', result_info)
        result_text.config(state='disabled')
        
        container.grid_columnconfigure(0, weight=1)
    
    def create_mosaic_tab(self, parent):
        """Onglet paramètres de mosaïque"""
        colors = self.app.colors
        
        container = tk.Frame(parent, bg=colors['bg_dark'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Default mosaic mode
        tk.Label(
            container,
            text="🧩 Default Mosaic Generation Mode:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        mosaic_combo = ttk.Combobox(
            container,
            textvariable=self.default_mosaic_mode,
            values=["quick", "standard", "complete"],
            state='readonly',
            font=self.app.FONT_TEXT,
            width=18
        )
        mosaic_combo.grid(row=1, column=0, sticky='w', pady=(0, 5))
        
        # Info text
        tk.Label(
            container,
            text="• Quick: 200 mosaics  • Standard: 500 mosaics  • Complete: All combinations",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9),
            justify='left'
        ).grid(row=2, column=0, sticky='w', pady=(0, 20))
        
        # Layout mode
        tk.Label(
            container,
            text="📐 Card Layout Mode:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=3, column=0, sticky='w', pady=(0, 5))
        
        layout_combo = ttk.Combobox(
            container,
            textvariable=self.default_mosaic_layout,
            values=["1 - Grid (Standard)", "2 - Grid with 3D Rotation", "3 - Random Placement"],
            state='readonly',
            font=self.app.FONT_TEXT,
            width=30
        )
        layout_combo.grid(row=4, column=0, sticky='w', pady=(0, 5))
        layout_combo.current(0)
        
        tk.Label(
            container,
            text="Controls how cards are arranged on the mosaic",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=5, column=0, sticky='w', pady=(0, 20))
        
        # Background mode
        tk.Label(
            container,
            text="🎨 Background Mode:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        bg_combo = ttk.Combobox(
            container,
            textvariable=self.default_mosaic_background,
            values=["0 - Fake Cards Mosaic", "1 - Local Image (mosaic/)", "2 - Web Image (Lorem Picsum)"],
            state='readonly',
            font=self.app.FONT_TEXT,
            width=40
        )
        bg_combo.grid(row=7, column=0, sticky='w', pady=(0, 5))
        bg_combo.current(0)
        
        tk.Label(
            container,
            text="Type of background to use for mosaics",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=8, column=0, sticky='w', pady=(0, 20))
        
        # Transform mode
        tk.Label(
            container,
            text="🔄 Transform Mode:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=9, column=0, sticky='w', pady=(0, 5))
        
        transform_combo = ttk.Combobox(
            container,
            textvariable=self.default_mosaic_transform,
            values=["0 - 2D Rotation", "1 - 3D Perspective Projection"],
            state='readonly',
            font=self.app.FONT_TEXT,
            width=40
        )
        transform_combo.grid(row=10, column=0, sticky='w', pady=(0, 5))
        transform_combo.current(0)
        
        tk.Label(
            container,
            text="Controls rotation intensity for cards",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=11, column=0, sticky='w', pady=(0, 10))
        
        container.grid_columnconfigure(0, weight=1)
    
    def create_fakebackgrounds_tab(self, parent):
        """Onglet paramètres fake images (random erasing)"""
        colors = self.app.colors
        
        container = tk.Frame(parent, bg=colors['bg_dark'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Input/Output directories
        tk.Label(
            container,
            text="� Input Directory (source backgrounds):",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        tk.Entry(
            container,
            textvariable=self.fakeimg_input_dir,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=30
        ).grid(row=1, column=0, sticky='w', pady=(0, 15))
        
        tk.Label(
            container,
            text="📁 Output Directory (augmented images):",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        tk.Entry(
            container,
            textvariable=self.fakeimg_output_dir,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=30
        ).grid(row=3, column=0, sticky='w', pady=(0, 20))
        
        # Random Erasing Parameters
        tk.Label(
            container,
            text="🎛️ Random Erasing Parameters:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=4, column=0, sticky='w', pady=(0, 10))
        
        # Probability (p)
        p_frame = tk.Frame(container, bg=colors['bg_dark'])
        p_frame.grid(row=5, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(
            p_frame,
            text="Probability (p):",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            p_frame,
            from_=0.0,
            to=1.0,
            increment=0.1,
            textvariable=self.fakeimg_p,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Area range (sl, sh)
        sl_frame = tk.Frame(container, bg=colors['bg_dark'])
        sl_frame.grid(row=6, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(
            sl_frame,
            text="Min Area (sl):",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            sl_frame,
            from_=0.01,
            to=1.0,
            increment=0.01,
            textvariable=self.fakeimg_sl,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        sh_frame = tk.Frame(container, bg=colors['bg_dark'])
        sh_frame.grid(row=7, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(
            sh_frame,
            text="Max Area (sh):",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            sh_frame,
            from_=0.01,
            to=1.0,
            increment=0.01,
            textvariable=self.fakeimg_sh,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Aspect ratio range (r1, r2)
        r1_frame = tk.Frame(container, bg=colors['bg_dark'])
        r1_frame.grid(row=8, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(
            r1_frame,
            text="Min Aspect (r1):",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            r1_frame,
            from_=0.1,
            to=5.0,
            increment=0.1,
            textvariable=self.fakeimg_r1,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        r2_frame = tk.Frame(container, bg=colors['bg_dark'])
        r2_frame.grid(row=9, column=0, sticky='w', pady=(0, 20))
        
        tk.Label(
            r2_frame,
            text="Max Aspect (r2):",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            r2_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.fakeimg_r2,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Info text
        tk.Label(
            container,
            text="💡 Lower values (20-40) create subtle textures\n   Higher values (60-80) create more varied patterns",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9),
            justify='left'
        ).grid(row=5, column=0, sticky='w', pady=(0, 10))
        
        container.grid_columnconfigure(0, weight=1)
    
    def create_training_tab(self, parent):
        """Onglet paramètres d'entraînement"""
        colors = self.app.colors
        
        container = tk.Frame(parent, bg=colors['bg_dark'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Default model
        tk.Label(
            container,
            text="🤖 Default YOLO Model:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        model_combo = ttk.Combobox(
            container,
            textvariable=self.default_model,
            values=["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"],
            state='readonly',
            font=self.app.FONT_TEXT,
            width=18
        )
        model_combo.grid(row=1, column=0, sticky='w', pady=(0, 20))
        
        # Default epochs
        tk.Label(
            container,
            text="📊 Default Epochs:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        tk.Spinbox(
            container,
            from_=1,
            to=1000,
            textvariable=self.default_epochs,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=10
        ).grid(row=3, column=0, sticky='w', pady=(0, 20))
        
        # Default batch size
        tk.Label(
            container,
            text="📦 Default Batch Size:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        tk.Spinbox(
            container,
            from_=1,
            to=128,
            textvariable=self.default_batch,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=10
        ).grid(row=5, column=0, sticky='w', pady=(0, 20))
        
        # Default device
        tk.Label(
            container,
            text="💻 Default Device:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        device_combo = ttk.Combobox(
            container,
            textvariable=self.default_device,
            values=["0", "cpu", "0,1", "0,1,2,3"],
            font=self.app.FONT_TEXT,
            width=18
        )
        device_combo.grid(row=7, column=0, sticky='w', pady=(0, 20))
        
        container.grid_columnconfigure(0, weight=1)
    
    def create_advanced_tab(self, parent):
        """Onglet paramètres avancés"""
        colors = self.app.colors
        
        container = tk.Frame(parent, bg=colors['bg_dark'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # TCGdex API Key
        tk.Label(
            container,
            text="🔑 TCGdex API Key (optional):",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        tk.Entry(
            container,
            textvariable=self.tcgdex_api_key,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            show='*'
        ).grid(row=1, column=0, sticky='ew', pady=(0, 20), ipady=8)
        
        tk.Label(
            container,
            text="ℹ️ Optional: for enhanced TCG API features",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=2, column=0, sticky='w', pady=(0, 20))
        
        container.grid_columnconfigure(0, weight=1)
    
    def create_debug_tab(self, parent):
        """Onglet paramètres Debug"""
        colors = self.app.colors
        
        # Container avec scrollbar
        canvas = tk.Canvas(parent, bg=colors['bg_dark'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        container = tk.Frame(scrollable_frame, bg=colors['bg_dark'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Section: Device Configuration
        tk.Label(
            container,
            text="🎮 Device Configuration",
            bg=colors['bg_dark'],
            fg=colors['accent'],
            font=('Segoe UI', 12, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        tk.Label(
            container,
            text="Device:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=1, column=0, sticky='w', pady=(0, 5))
        
        device_frame = tk.Frame(container, bg=colors['bg_dark'])
        device_frame.grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        # Radio buttons pour device
        tk.Radiobutton(
            device_frame,
            text="Auto (recommended)",
            variable=self.debug_device,
            value="auto",
            bg=colors['bg_dark'],
            fg=colors['text'],
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text'],
            font=self.app.FONT_TEXT
        ).pack(anchor='w', pady=2)
        
        tk.Radiobutton(
            device_frame,
            text="CPU Only",
            variable=self.debug_device,
            value="cpu",
            bg=colors['bg_dark'],
            fg=colors['text'],
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text'],
            font=self.app.FONT_TEXT
        ).pack(anchor='w', pady=2)
        
        tk.Radiobutton(
            device_frame,
            text="GPU 0 (Primary)",
            variable=self.debug_device,
            value="0",
            bg=colors['bg_dark'],
            fg=colors['text'],
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text'],
            font=self.app.FONT_TEXT
        ).pack(anchor='w', pady=2)
        
        tk.Radiobutton(
            device_frame,
            text="GPU 1 (Secondary)",
            variable=self.debug_device,
            value="1",
            bg=colors['bg_dark'],
            fg=colors['text'],
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text'],
            font=self.app.FONT_TEXT
        ).pack(anchor='w', pady=2)
        
        tk.Label(
            container,
            text="ℹ️ Auto: Detects best device (GPU if available, else CPU)",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=3, column=0, columnspan=2, sticky='w', pady=(0, 20))
        
        # Section: Performance
        tk.Label(
            container,
            text="⚡ Performance Settings",
            bg=colors['bg_dark'],
            fg=colors['accent'],
            font=('Segoe UI', 12, 'bold')
        ).grid(row=4, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        tk.Label(
            container,
            text="Worker Processes:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=5, column=0, sticky='w', pady=(0, 5))
        
        workers_spinbox = tk.Spinbox(
            container,
            from_=1,
            to=32,
            textvariable=self.debug_workers,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=10
        )
        workers_spinbox.grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text=f"ℹ️ CPU cores detected: {multiprocessing.cpu_count()} (recommended: {max(1, multiprocessing.cpu_count() // 2)})",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=7, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="⚠️ More workers = faster processing but higher RAM usage",
            bg=colors['bg_dark'],
            fg=colors['warning'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=8, column=0, columnspan=2, sticky='w', pady=(0, 20))
        
        # Cache mode
        tk.Label(
            container,
            text="Cache Mode:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=9, column=0, sticky='w', pady=(0, 5))
        
        cache_combo = ttk.Combobox(
            container,
            textvariable=self.debug_cache_mode,
            values=["ram", "disk", "disabled"],
            state='readonly',
            font=self.app.FONT_TEXT,
            width=15
        )
        cache_combo.grid(row=10, column=0, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="ℹ️ RAM: Fastest but uses more memory | Disk: Slower but saves RAM | Disabled: No caching",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=11, column=0, columnspan=2, sticky='w', pady=(0, 20))
        
        # Section: Logging
        tk.Label(
            container,
            text="📋 Logging Configuration",
            bg=colors['bg_dark'],
            fg=colors['accent'],
            font=('Segoe UI', 12, 'bold')
        ).grid(row=12, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        tk.Label(
            container,
            text="Log Level:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=13, column=0, sticky='w', pady=(0, 5))
        
        log_combo = ttk.Combobox(
            container,
            textvariable=self.debug_log_level,
            values=["ERROR", "WARNING", "INFO", "DEBUG", "TRACE"],
            state='readonly',
            font=self.app.FONT_TEXT,
            width=15
        )
        log_combo.grid(row=14, column=0, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="ERROR: Critical errors only | WARNING: Warnings + errors | INFO: General info (recommended)",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=15, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="DEBUG: Detailed debugging | TRACE: Maximum verbosity (very detailed)",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=16, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        # Save logs to file
        tk.Checkbutton(
            container,
            text="💾 Save debug logs to file",
            variable=self.debug_save_logs,
            bg=colors['bg_dark'],
            fg=colors['text'],
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text'],
            font=self.app.FONT_TEXT
        ).grid(row=17, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="ℹ️ Logs saved to: debug_logs/<timestamp>.log",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=18, column=0, columnspan=2, sticky='w', pady=(0, 20))
        
        # Section: Advanced Debug
        tk.Label(
            container,
            text="🔧 Advanced Debug Options",
            bg=colors['bg_dark'],
            fg=colors['accent'],
            font=('Segoe UI', 12, 'bold')
        ).grid(row=19, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        # Profiling
        tk.Checkbutton(
            container,
            text="📊 Enable performance profiling",
            variable=self.debug_profiling,
            bg=colors['bg_dark'],
            fg=colors['text'],
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text'],
            font=self.app.FONT_TEXT
        ).grid(row=20, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="ℹ️ Measures execution time of functions (slight performance impact)",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=21, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # Benchmark
        tk.Checkbutton(
            container,
            text="⏱️ Enable benchmark logging",
            variable=self.debug_benchmark,
            bg=colors['bg_dark'],
            fg=colors['text'],
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text'],
            font=self.app.FONT_TEXT
        ).grid(row=22, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="ℹ️ Logs detailed performance metrics for benchmarking",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=23, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # Multiprocessing debug
        tk.Checkbutton(
            container,
            text="🔍 Multiprocessing debug mode",
            variable=self.debug_multiprocessing,
            bg=colors['bg_dark'],
            fg=colors['text'],
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text'],
            font=self.app.FONT_TEXT
        ).grid(row=24, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="ℹ️ Enables detailed logging for parallel processing (useful for debugging crashes)",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=25, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # Memory profiling
        tk.Checkbutton(
            container,
            text="🧠 Memory profiling",
            variable=self.debug_memory_profiling,
            bg=colors['bg_dark'],
            fg=colors['text'],
            selectcolor=colors['bg_card'],
            activebackground=colors['bg_dark'],
            activeforeground=colors['text'],
            font=self.app.FONT_TEXT
        ).grid(row=26, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="ℹ️ Tracks memory usage (significant performance impact, use only when debugging memory issues)",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=27, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # Warning banner
        warning_frame = tk.Frame(container, bg=colors['warning'], relief='solid', bd=1)
        warning_frame.grid(row=28, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        
        tk.Label(
            warning_frame,
            text="⚠️ WARNING: Advanced debug options may impact performance. Enable only when debugging.",
            bg=colors['warning'],
            fg='#000000',
            font=('Segoe UI', 9, 'bold'),
            wraplength=550,
            justify='left'
        ).pack(padx=10, pady=10)
        
        container.grid_columnconfigure(0, weight=1)
    
    def create_download_tab(self, parent):
        """Onglet paramètres Image Download"""
        colors = self.app.colors
        
        container = tk.Frame(parent, bg=colors['bg_dark'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Default output directory
        tk.Label(
            container,
            text="💾 Default Output Directory:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        dir_frame = tk.Frame(container, bg=colors['bg_dark'])
        dir_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        download_dir_entry = tk.Entry(
            dir_frame,
            textvariable=self.default_download_dir,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2
        )
        download_dir_entry.pack(side=tk.LEFT, fill='x', expand=True, ipady=8)
        
        tk.Button(
            dir_frame,
            text="📁",
            command=lambda: self.browse_dir(self.default_download_dir),
            bg=colors['accent'],
            fg='#000000',
            font=self.app.FONT_BUTTON,
            relief='flat',
            padx=10,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Default language
        tk.Label(
            container,
            text="🌍 Default Language:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        try:
            from core.image_downloader import LANGUAGES
            lang_choices = list(LANGUAGES.keys())
        except Exception:
            lang_choices = ["English", "Français", "Deutsch", "Italiano", "Español"]
        
        lang_combo = ttk.Combobox(
            container,
            textvariable=self.default_download_lang,
            values=lang_choices,
            state='readonly',
            font=self.app.FONT_TEXT,
            width=20
        )
        lang_combo.grid(row=3, column=0, sticky='w', pady=(0, 20))
        
        # Default quality
        tk.Label(
            container,
            text="🎨 Default Quality:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        quality_combo = ttk.Combobox(
            container,
            textvariable=self.default_download_quality,
            values=["high", "low"],
            state='readonly',
            font=self.app.FONT_TEXT,
            width=15
        )
        quality_combo.grid(row=5, column=0, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="High quality recommended for training datasets",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=6, column=0, sticky='w', pady=(0, 20))
        
        # Default format
        tk.Label(
            container,
            text="📁 Default Format:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=7, column=0, sticky='w', pady=(0, 5))
        
        format_combo = ttk.Combobox(
            container,
            textvariable=self.default_download_format,
            values=["png", "jpg", "jpeg", "webp"],
            state='readonly',
            font=self.app.FONT_TEXT,
            width=18
        )
        format_combo.grid(row=8, column=0, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="PNG recommended for lossless quality",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=9, column=0, sticky='w', pady=(0, 20))
        
        # Default workers
        tk.Label(
            container,
            text="⚡ Default Parallel Workers:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.app.FONT_BUTTON
        ).grid(row=10, column=0, sticky='w', pady=(0, 5))
        
        workers_spinbox = tk.Spinbox(
            container,
            from_=1,
            to=16,
            textvariable=self.default_download_workers,
            font=self.app.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=10
        )
        workers_spinbox.grid(row=11, column=0, sticky='w', pady=(0, 5))
        
        tk.Label(
            container,
            text="More workers = faster download (4-8 recommended)",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=12, column=0, sticky='w', pady=(0, 10))
        
        container.grid_columnconfigure(0, weight=1)
    
    def browse_dir(self, var):
        """Parcourir pour choisir un dossier"""
        directory = filedialog.askdirectory(title="Select Directory")
        if directory:
            var.set(directory)
    
    def save_settings(self):
        """Sauvegarder les paramètres"""
        config = {
            "default_images_dir": self.default_images_dir.get(),
            "default_output_dir": self.default_output_dir.get(),
            "default_augmented_dir": self.default_augmented_dir.get(),
            "default_mosaic_dir": self.default_mosaic_dir.get(),
            "default_fakeimg_dir": self.default_fakeimg_dir.get(),
            "default_holographic_dir": self.default_holographic_dir.get(),
            "default_augmentations": self.default_augmentations.get(),
            "holographic_intensity": self.holographic_intensity.get(),
            "holographic_variations": self.holographic_variations.get(),
            "default_mosaic_mode": self.default_mosaic_mode.get(),
            "default_mosaic_layout": self.default_mosaic_layout.get(),
            "default_mosaic_background": self.default_mosaic_background.get(),
            "default_mosaic_transform": self.default_mosaic_transform.get(),
            "default_model": self.default_model.get(),
            "default_epochs": self.default_epochs.get(),
            "default_batch": self.default_batch.get(),
            "default_device": self.default_device.get(),
            "tcgdex_api_key": self.tcgdex_api_key.get(),
            "auto_save_logs": self.auto_save_logs.get(),
            "enable_notifications": self.enable_notifications.get(),
            "fakeimg_input_dir": self.fakeimg_input_dir.get(),
            "fakeimg_output_dir": self.fakeimg_output_dir.get(),
            "fakeimg_p": self.fakeimg_p.get(),
            "fakeimg_sl": self.fakeimg_sl.get(),
            "fakeimg_sh": self.fakeimg_sh.get(),
            "fakeimg_r1": self.fakeimg_r1.get(),
            "fakeimg_r2": self.fakeimg_r2.get(),
            "default_download_dir": self.default_download_dir.get(),
            "default_download_lang": self.default_download_lang.get(),
            "default_download_quality": self.default_download_quality.get(),
            "default_download_format": self.default_download_format.get(),
            "default_download_workers": self.default_download_workers.get(),
            "debug_device": self.debug_device.get(),
            "debug_workers": self.debug_workers.get(),
            "debug_log_level": self.debug_log_level.get(),
            "debug_cache_mode": self.debug_cache_mode.get(),
            "debug_profiling": self.debug_profiling.get(),
            "debug_benchmark": self.debug_benchmark.get(),
            "debug_save_logs": self.debug_save_logs.get(),
            "debug_multiprocessing": self.debug_multiprocessing.get(),
            "debug_memory_profiling": self.debug_memory_profiling.get()
        }
        
        try:
            # GuiConfig préserve les clés existantes (paths, last_used, ...)
            # au lieu d'écraser tout le fichier avec les seules clés du dialog
            cfg = GuiConfig()
            cfg.update(config)
            if not cfg.save():
                raise OSError(f"écriture impossible: {cfg.path}")

            messagebox.showinfo("Success", "✅ Settings saved successfully!")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")
            traceback.print_exc()
