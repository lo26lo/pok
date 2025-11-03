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
import time
from pathlib import Path
from datetime import datetime

# Import des managers du core
from core.workflow_manager import WorkflowManager, WorkflowConfig
from core.training_manager import TrainingManager, TrainingConfig
from core.detection_manager import DetectionManager, DetectionConfig


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
        
        self.create_ui()
    
    def load_settings(self):
        """Charger les paramètres depuis gui_config.json"""
        try:
            if Path("gui_config.json").exists():
                with open("gui_config.json", "r") as f:
                    config = json.load(f)
            else:
                config = {}
        except Exception:
            config = {}
        
        # Paramètres par défaut
        self.default_images_dir = tk.StringVar(value=config.get("default_images_dir", "images"))
        self.default_output_dir = tk.StringVar(value=config.get("default_output_dir", "output"))
        self.default_augmented_dir = tk.StringVar(value=config.get("default_augmented_dir", "augmented"))
        self.default_mosaic_dir = tk.StringVar(value=config.get("default_mosaic_dir", "output/yolov8"))
        self.default_fakeimg_dir = tk.StringVar(value=config.get("default_fakeimg_dir", "fakeimg_augmented"))
        self.default_holographic_dir = tk.StringVar(value=config.get("default_holographic_dir", "images_holographic"))
        
        self.default_augmentations = tk.IntVar(value=config.get("default_augmentations", 15))
        self.default_augmentation_type = tk.StringVar(value=config.get("default_augmentation_type", "standard"))
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
        
        # Fake image generation settings (random erasing)
        self.fakeimg_input_dir = tk.StringVar(value=config.get("fakeimg_input_dir", "images"))
        self.fakeimg_output_dir = tk.StringVar(value=config.get("fakeimg_output_dir", "fakeimg_augmented"))
        self.fakeimg_p = tk.DoubleVar(value=config.get("fakeimg_p", 0.5))
        self.fakeimg_sl = tk.DoubleVar(value=config.get("fakeimg_sl", 0.02))
        self.fakeimg_sh = tk.DoubleVar(value=config.get("fakeimg_sh", 0.4))
        self.fakeimg_r1 = tk.DoubleVar(value=config.get("fakeimg_r1", 0.3))
        self.fakeimg_r2 = tk.DoubleVar(value=config.get("fakeimg_r2", 3.3))
        
        # Image download settings
        self.default_download_dir = tk.StringVar(value=config.get("default_download_dir", "images"))
        self.default_download_lang = tk.StringVar(value=config.get("default_download_lang", "English"))
        self.default_download_quality = tk.StringVar(value=config.get("default_download_quality", "high"))
        self.default_download_format = tk.StringVar(value=config.get("default_download_format", "png"))
        self.default_download_workers = tk.IntVar(value=config.get("default_download_workers", 8))
    
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
            font=self.FONT_BUTTON,
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
        notebook.add(general_frame, text="  General  ")
        self.create_general_tab(general_frame)
        
        # Onglet Augmentation
        aug_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(aug_frame, text="  Augmentation  ")
        self.create_augmentation_tab(aug_frame)
        
        # Onglet Mosaic
        mosaic_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(mosaic_frame, text="  Mosaic  ")
        self.create_mosaic_tab(mosaic_frame)
        
        # Onglet Fake Images
        fake_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(fake_frame, text="  Fake Images  ")
        self.create_fakebackgrounds_tab(fake_frame)
        
        # Onglet Image Download
        download_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(download_frame, text="  Image Download  ")
        self.create_download_tab(download_frame)
        
        # Onglet Training
        train_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(train_frame, text="  Training  ")
        self.create_training_tab(train_frame)
        
        # Onglet Advanced
        advanced_frame = tk.Frame(notebook, bg=colors['bg_dark'])
        notebook.add(advanced_frame, text="  Advanced  ")
        self.create_advanced_tab(advanced_frame)
        
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
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        frame1 = tk.Frame(container, bg=colors['bg_dark'])
        frame1.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        tk.Entry(
            frame1,
            textvariable=self.default_images_dir,
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        frame2 = tk.Frame(container, bg=colors['bg_dark'])
        frame2.grid(row=3, column=0, sticky='ew', pady=(0, 20))
        
        tk.Entry(
            frame2,
            textvariable=self.default_output_dir,
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        frame3 = tk.Frame(container, bg=colors['bg_dark'])
        frame3.grid(row=5, column=0, sticky='ew', pady=(0, 15))
        
        tk.Entry(
            frame3,
            textvariable=self.default_augmented_dir,
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        frame4 = tk.Frame(container, bg=colors['bg_dark'])
        frame4.grid(row=7, column=0, sticky='ew', pady=(0, 15))
        
        tk.Entry(
            frame4,
            textvariable=self.default_mosaic_dir,
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=8, column=0, sticky='w', pady=(0, 5))
        
        frame5 = tk.Frame(container, bg=colors['bg_dark'])
        frame5.grid(row=9, column=0, sticky='ew', pady=(0, 15))
        
        tk.Entry(
            frame5,
            textvariable=self.default_fakeimg_dir,
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=10, column=0, sticky='w', pady=(0, 5))
        
        frame6 = tk.Frame(container, bg=colors['bg_dark'])
        frame6.grid(row=11, column=0, sticky='ew', pady=(0, 20))
        
        tk.Entry(
            frame6,
            textvariable=self.default_holographic_dir,
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
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
        
        # Default augmentations
        tk.Label(
            container,
            text="🎨 Default Number of Augmentations:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        tk.Spinbox(
            container,
            from_=1,
            to=100,
            textvariable=self.default_augmentations,
            font=self.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=10
        ).grid(row=1, column=0, sticky='w', pady=(0, 20))
        
        # Default augmentation type
        tk.Label(
            container,
            text="✨ Default Augmentation Type:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.FONT_BUTTON
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        aug_type_combo = ttk.Combobox(
            container,
            textvariable=self.default_augmentation_type,
            values=["standard", "holographic", "both"],
            state='readonly',
            font=self.FONT_TEXT,
            width=18
        )
        aug_type_combo.grid(row=3, column=0, sticky='w', pady=(0, 20))
        
        # Holographic settings section
        tk.Label(
            container,
            text="✨ Holographic Effect Settings:",
            bg=colors['bg_dark'],
            fg=colors['accent'],
            font=('Segoe UI', 11, 'bold')
        ).grid(row=4, column=0, sticky='w', pady=(10, 10))
        
        tk.Label(
            container,
            text="These settings apply when 'Holographic' or 'Both' type is selected.",
            bg=colors['bg_dark'],
            fg=colors['text_dim'],
            font=('Segoe UI', 9, 'italic')
        ).grid(row=5, column=0, sticky='w', pady=(0, 15))
        
        # Holographic intensity
        intensity_frame = tk.Frame(container, bg=colors['bg_dark'])
        intensity_frame.grid(row=6, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(
            intensity_frame,
            text="Effect intensity:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.FONT_TEXT,
            width=15,
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
        
        # Holographic variations
        variations_frame = tk.Frame(container, bg=colors['bg_dark'])
        variations_frame.grid(row=7, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(
            variations_frame,
            text="Number of variations:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            variations_frame,
            from_=1,
            to=10,
            textvariable=self.holographic_variations,
            font=self.FONT_TEXT,
            bg='#FFFFFF',
            fg='#1a1a1a',
            relief='flat',
            bd=2,
            width=8
        ).pack(side=tk.LEFT, padx=10)
        
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
            font=self.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        mosaic_combo = ttk.Combobox(
            container,
            textvariable=self.default_mosaic_mode,
            values=["quick", "standard", "complete"],
            state='readonly',
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=3, column=0, sticky='w', pady=(0, 5))
        
        layout_combo = ttk.Combobox(
            container,
            textvariable=self.default_mosaic_layout,
            values=["1 - Grid (Standard)", "2 - Grid with 3D Rotation", "3 - Random Placement"],
            state='readonly',
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        bg_combo = ttk.Combobox(
            container,
            textvariable=self.default_mosaic_background,
            values=["0 - Fake Cards Mosaic", "1 - Local Image (mosaic/)", "2 - Web Image (Lorem Picsum)"],
            state='readonly',
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=9, column=0, sticky='w', pady=(0, 5))
        
        transform_combo = ttk.Combobox(
            container,
            textvariable=self.default_mosaic_transform,
            values=["0 - 2D Rotation", "1 - 3D Perspective Projection"],
            state='readonly',
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        tk.Entry(
            container,
            textvariable=self.fakeimg_input_dir,
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        tk.Entry(
            container,
            textvariable=self.fakeimg_output_dir,
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=4, column=0, sticky='w', pady=(0, 10))
        
        # Probability (p)
        p_frame = tk.Frame(container, bg=colors['bg_dark'])
        p_frame.grid(row=5, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(
            p_frame,
            text="Probability (p):",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            p_frame,
            from_=0.0,
            to=1.0,
            increment=0.1,
            textvariable=self.fakeimg_p,
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            sl_frame,
            from_=0.01,
            to=1.0,
            increment=0.01,
            textvariable=self.fakeimg_sl,
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            sh_frame,
            from_=0.01,
            to=1.0,
            increment=0.01,
            textvariable=self.fakeimg_sh,
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            r1_frame,
            from_=0.1,
            to=5.0,
            increment=0.1,
            textvariable=self.fakeimg_r1,
            font=self.FONT_TEXT,
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
            font=self.FONT_TEXT,
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Spinbox(
            r2_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.fakeimg_r2,
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        model_combo = ttk.Combobox(
            container,
            textvariable=self.default_model,
            values=["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"],
            state='readonly',
            font=self.FONT_TEXT,
            width=18
        )
        model_combo.grid(row=1, column=0, sticky='w', pady=(0, 20))
        
        # Default epochs
        tk.Label(
            container,
            text="📊 Default Epochs:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.FONT_BUTTON
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        tk.Spinbox(
            container,
            from_=1,
            to=1000,
            textvariable=self.default_epochs,
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        tk.Spinbox(
            container,
            from_=1,
            to=128,
            textvariable=self.default_batch,
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        device_combo = ttk.Combobox(
            container,
            textvariable=self.default_device,
            values=["0", "cpu", "0,1", "0,1,2,3"],
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        tk.Entry(
            container,
            textvariable=self.tcgdex_api_key,
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        dir_frame = tk.Frame(container, bg=colors['bg_dark'])
        dir_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        download_dir_entry = tk.Entry(
            dir_frame,
            textvariable=self.default_download_dir,
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON,
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
            font=self.FONT_BUTTON
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        try:
            from core.image_downloader import LANGUAGES
            lang_choices = list(LANGUAGES.keys())
        except:
            lang_choices = ["English", "Français", "Deutsch", "Italiano", "Español"]
        
        lang_combo = ttk.Combobox(
            container,
            textvariable=self.default_download_lang,
            values=lang_choices,
            state='readonly',
            font=self.FONT_TEXT,
            width=20
        )
        lang_combo.grid(row=3, column=0, sticky='w', pady=(0, 20))
        
        # Default quality
        tk.Label(
            container,
            text="🎨 Default Quality:",
            bg=colors['bg_dark'],
            fg=colors['text'],
            font=self.FONT_BUTTON
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        quality_combo = ttk.Combobox(
            container,
            textvariable=self.default_download_quality,
            values=["high", "low"],
            state='readonly',
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=7, column=0, sticky='w', pady=(0, 5))
        
        format_combo = ttk.Combobox(
            container,
            textvariable=self.default_download_format,
            values=["png", "jpg", "jpeg", "webp"],
            state='readonly',
            font=self.FONT_TEXT,
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
            font=self.FONT_BUTTON
        ).grid(row=10, column=0, sticky='w', pady=(0, 5))
        
        workers_spinbox = tk.Spinbox(
            container,
            from_=1,
            to=16,
            textvariable=self.default_download_workers,
            font=self.FONT_TEXT,
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
            "default_augmentation_type": self.default_augmentation_type.get(),
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
            "default_download_workers": self.default_download_workers.get()
        }
        
        try:
            with open("gui_config.json", "w") as f:
                json.dump(config, f, indent=4)
            
            messagebox.showinfo("Success", "✅ Settings saved successfully!")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")


class ModernPokemonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokemon Dataset Generator v3.0 - Professional")
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
        self.train_device_var = None
        
        # Variables pour detection
        self.detect_model_var = None
        self.detect_conf_var = None
        self.detect_camera_var = None
        
        # Variables pour augmentation
        self.aug_num_var = None
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
        
        # Chargement config
        self.load_config()
        
        # Palette de couleurs moderne (Catppuccin Mocha inspired)
        self.colors = {
            'bg_dark': '#1e1e2e',       # Background principal
            'bg_sidebar': '#181825',     # Sidebar
            'bg_card': '#313244',        # Cartes/Panels
            'bg_hover': '#45475a',       # Hover
            'accent': '#89b4fa',         # Bleu accent
            'accent_hover': '#74c7ec',   # Bleu hover
            'success': '#a6e3a1',        # Vert success
            'warning': '#f9e2af',        # Jaune warning
            'error': '#f38ba8',          # Rouge error
            'text': '#cdd6f4',           # Texte principal
            'text_dim': '#9399b2',       # Texte secondaire
            'border': '#45475a'          # Bordures
        }
        
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
            text="🎮 Pokemon Dataset Generator",
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
    
    def create_footer(self, parent):
        """Créer le footer avec progress bar et logs - COMPACTÉ V3.1"""
        self.footer = tk.Frame(parent, bg=self.colors['bg_sidebar'], height=160)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.footer.pack_propagate(False)
        
        # Progress section
        progress_frame = tk.Frame(self.footer, bg=self.colors['bg_sidebar'])
        progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Frame pour label et bouton stop sur la même ligne
        progress_header = tk.Frame(progress_frame, bg=self.colors['bg_sidebar'])
        progress_header.pack(fill=tk.X)
        
        self.progress_label = tk.Label(progress_header,
            text="Ready",
            font=('Segoe UI', 9),
            bg=self.colors['bg_sidebar'],
            fg=self.colors['text_dim'],
            anchor='w'
        )
        self.progress_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bouton Stop
        self.stop_button = tk.Button(progress_header,
            text="⏹ Stop",
            command=self.stop_operation,
            bg=self.colors['error'],
            fg='#FFFFFF',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            padx=15,
            pady=3,
            cursor='hand2',
            state='disabled'
        )
        self.stop_button.pack(side=tk.RIGHT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Logs section
        logs_label = tk.Label(self.footer,
            text="📜 Logs",
            font=self.FONT_BUTTON,
            bg=self.colors['bg_sidebar'],
            fg=self.colors['text'],
            anchor='w'
        )
        logs_label.pack(fill=tk.X, padx=20)
        
        # ScrolledText pour logs - 4 lignes V3.1 (augmenté pour meilleure lisibilité)
        self.log_text = scrolledtext.ScrolledText(self.footer,
            height=4,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='flat',
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))
    
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
        elif view_id == 'detection':
            self.create_detection_view()
        elif view_id == 'export':
            self.create_export_view()
        elif view_id == 'tools':
            self.create_tools_view()
    
    def create_home_view(self):
        """Vue Home / Dashboard - HARMONISÉ V3.1"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # Header
        title = tk.Label(container,
            text="Dashboard",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 5))
        
        subtitle = tk.Label(container,
            text="Overview of your Pokemon dataset project",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
        # Calculer les statistiques réelles
        stats = self.get_real_stats()
        
        # Initialiser le dictionnaire pour stocker les labels de stats
        self.stat_cards = {}
        
        # Stats Cards (grid 2x2)
        stats_grid = tk.Frame(container, bg=self.colors['bg_dark'])
        stats_grid.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        self.create_stat_card(stats_grid, "Source Images", str(stats['source']), "📸", 0, 0, 'source')
        self.create_stat_card(stats_grid, "Augmented", str(stats['augmented']), "🎨", 0, 1, 'augmented')
        self.create_stat_card(stats_grid, "Mosaics", str(stats['mosaics']), "🧩", 1, 0, 'mosaic')
        self.create_stat_card(stats_grid, "Dataset Size", stats['size'], "💾", 1, 1, 'size')
        
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
        
        # Avertissement si fichier Excel manquant
        if not self.check_excel_file():
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
                text="File 'cards_info.xlsx' not found. This file is needed for some features.\nClick below to generate a card list from the TCGdex API.",
                font=('Segoe UI', 9),
                bg=self.colors['warning'],
                fg='#000000'
            ).pack(anchor='w', pady=(5, 10))
            
            tk.Button(warning_content2,
                text="� Generate Card List",
                command=self.open_excel_tools,
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
    
    def create_stat_card(self, parent, label, value, icon, row, col, key=None):
        """Créer une carte de statistique"""
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
        
        title = tk.Label(container,
            text="🚀 Automatic Workflow",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 5))
        
        subtitle = tk.Label(container,
            text="Generate complete dataset with one click",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
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
        
        ttk.Button(launch_frame, text="🚀 START WORKFLOW",
                  style='Accent.TButton',
                  command=self.start_workflow,
                  width=30).pack(pady=10)
    
    def create_download_view(self):
        """Vue Image Download"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # Header
        title = tk.Label(container,
            text="⬇️ Image Download",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 10))
        
        subtitle = tk.Label(container,
            text="Download Pokemon card images from TCGdex API",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
        # Main content frame (2 colonnes)
        main_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Left column: Configuration Card
        config_card = tk.Frame(main_frame, bg=self.colors['bg_card'])
        config_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
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
            except:
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
        except:
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
        
        # Right column: Info Card
        info_card = tk.Frame(main_frame, bg=self.colors['bg_card'])
        info_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        info_title = tk.Label(info_card,
            text="ℹ️ About TCGdex API",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        info_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        info_content = tk.Frame(info_card, bg=self.colors['bg_card'])
        info_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tk.Label(info_content,
            text="• Free API - No authentication required\n"
                 "• High quality card images (PNG recommended)\n"
                 "• Multiple languages supported\n"
                 "• Images named with Set # for easy identification\n"
                 "• manifest.csv generated with download details",
            font=self.FONT_TEXT,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            justify='left'
        ).pack(anchor='w')
        
        # Button frame
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="⬇️ START DOWNLOAD",
                  style='Accent.TButton',
                  command=self.start_image_download,
                  width=30).pack(pady=5)
    
    def create_augmentation_view(self):
        """Vue Augmentation détaillée - ENRICHIE V3.1 avec scroll"""
        # Canvas avec scrollbar pour contenu défilant
        canvas = tk.Canvas(self.content_area, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_area, orient="vertical", command=canvas.yview)
        
        container = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenu avec padding
        content_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # Header
        title = tk.Label(content_frame,
            text="🎨 Image Augmentation",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 10))
        
        subtitle = tk.Label(content_frame,
            text="Generate augmented variations of your card images",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
        # Info Card - NOUVEAU
        info_card = tk.Frame(content_frame, bg=self.colors['bg_card'])
        info_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        info_content = tk.Frame(info_card, bg=self.colors['bg_card'])
        info_content.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(info_content,
            text="ℹ️ About Augmentation",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['accent']
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(info_content,
            text="Image augmentation creates variations of your original images using transformations like rotation, "
                 "brightness adjustment, noise, blur, and color shifts. This increases dataset diversity and helps "
                 "improve model training. Standard mode uses traditional augmentations, while Holographic mode adds "
                 "special effects to simulate holographic Pokemon cards.",
            font=self.FONT_TEXT,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            justify='left',
            wraplength=1300
        ).pack(anchor='w', pady=(0, 10))
        
        # Stats
        try:
            source_dir = "images"
            augmented_dir = "augmented"
            source_count = 0
            augmented_count = 0
            
            if os.path.exists(source_dir):
                source_count = len([f for f in os.listdir(source_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
            
            if os.path.exists(augmented_dir):
                augmented_count = len([f for f in os.listdir(augmented_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
            
            stats_text = f"📊 Source: {source_count} images | Augmented: {augmented_count} images"
            if augmented_count > 0:
                ratio = augmented_count / source_count if source_count > 0 else 0
                stats_text += f" | Ratio: {ratio:.1f}x"
            stats_color = self.colors['success'] if augmented_count > 0 else self.colors['warning']
        except:
            stats_text = "📊 Unable to read statistics"
            stats_color = self.colors['text_dim']
        
        tk.Label(info_content,
            text=stats_text,
            font=self.FONT_BUTTON,
            bg=self.colors['bg_card'],
            fg=stats_color
        ).pack(anchor='w')
        
        # Configuration Card
        config_card = tk.Frame(content_frame, bg=self.colors['bg_card'])
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
        
        # Number of augmentations
        aug_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        aug_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(aug_frame, text="Augmentations per image:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.aug_num_var = ttk.Spinbox(aug_frame, from_=1, to=100, width=self.SPINBOX_WIDTH)
        self.aug_num_var.pack(side=tk.LEFT, padx=10)
        self.aug_num_var.set(15)
        
        tk.Label(aug_frame, text="(number of variations per source image)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        
        # Augmentation type
        type_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        type_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(type_frame, text="Augmentation type:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.aug_type_var = ttk.Combobox(type_frame,
            values=["Standard", "Holographic", "Both"],
            state='readonly', width=self.COMBOBOX_WIDTH)
        self.aug_type_var.pack(side=tk.LEFT, padx=10)
        self.aug_type_var.current(0)
        
        tk.Label(type_frame, text="(Standard: classic | Holographic: special effects)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        
        # Output directory
        output_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        output_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(output_frame, text="Output directory:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.aug_output_var = ttk.Combobox(output_frame,
            values=["augmented", "images_aug", "output/augmented"],
            state='readonly', width=self.COMBOBOX_WIDTH)
        self.aug_output_var.pack(side=tk.LEFT, padx=10)
        self.aug_output_var.current(0)
        
        tk.Label(output_frame, text="(where augmented images will be saved)",
                bg=self.colors['bg_card'], fg=self.colors['text_dim'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        
        # Buttons
        btn_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="🎨 START AUGMENTATION",
                  style='Accent.TButton',
                  command=self.start_augmentation,
                  width=30).pack(pady=5)
    
    def create_fakeimg_view(self):
        """Vue génération de fake images (random erasing) - HARMONISÉE V3.1 avec scroll"""
        # Canvas avec scrollbar pour contenu défilant
        canvas = tk.Canvas(self.content_area, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_area, orient="vertical", command=canvas.yview)
        
        container = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenu avec padding
        content_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # Header
        title = tk.Label(content_frame,
            text="🎲 Fake Image Generator",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 10))
        
        subtitle = tk.Label(content_frame,
            text="Apply random erasing to create synthetic fake images for mosaics",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
        # Info Card - EN HAUT, PLEINE LARGEUR
        info_card = tk.Frame(content_frame, bg=self.colors['bg_card'])
        info_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        info_content = tk.Frame(info_card, bg=self.colors['bg_card'])
        info_content.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(info_content,
            text="ℹ️ About Fake Images",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['accent']
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(info_content,
            text="Random erasing applies random rectangles to downloaded card images. "
                 "These modified images are used as fake backgrounds in mosaic generation. "
                 "Uses images from 'images/' folder. Probability (p) controls the chance of applying erasing per image.",
            font=self.FONT_TEXT,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            justify='left',
            wraplength=1300
        ).pack(anchor='w', pady=(0, 10))
        
        # Stats
        try:
            fakeimg_aug_dir = "fakeimg_augmented"
            if os.path.exists(fakeimg_aug_dir):
                count = len([f for f in os.listdir(fakeimg_aug_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
                stats_text = f"📊 Current: {count} fake images generated"
                stats_color = self.colors['success'] if count > 0 else self.colors['warning']
            else:
                stats_text = "📊 No fake images generated yet"
                stats_color = self.colors['warning']
        except:
            stats_text = "📊 Unable to read statistics"
            stats_color = self.colors['text_dim']
        
        tk.Label(info_content,
            text=stats_text,
            font=self.FONT_BUTTON,
            bg=self.colors['bg_card'],
            fg=stats_color
        ).pack(anchor='w')
        
        # Configuration Card - EN DESSOUS, PLEINE LARGEUR
        config_card = tk.Frame(content_frame, bg=self.colors['bg_card'])
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
        self.fakeimg_input_var.insert(0, "images")
        
        # Output directory
        output_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        output_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(output_frame, text="Output directory:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON, width=15, anchor='w').pack(side=tk.LEFT)
        
        self.fakeimg_output_var = ttk.Entry(output_frame, width=self.ENTRY_WIDTH)
        self.fakeimg_output_var.pack(side=tk.LEFT, padx=10)
        self.fakeimg_output_var.insert(0, "fakeimg_augmented")
        
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
        btn_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="🎲 GENERATE FAKE IMAGES",
                  style='Accent.TButton',
                  command=self.start_fake_generator_from_view,
                  width=30).pack(pady=5)
    
    def create_mosaic_view(self):
        """Vue Mosaics détaillée"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # Header
        title = tk.Label(container,
            text="🧩 YOLO Mosaics",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 10))
        
        subtitle = tk.Label(container,
            text="Generate YOLO training mosaics from augmented images",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
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
        
        ttk.Button(btn_frame, text="🧩 GENERATE MOSAICS",
                  style='Accent.TButton',
                  command=self.start_mosaic,
                  width=30).pack(pady=5)
        
        ttk.Button(btn_frame, text="📋 Generate Fake Backgrounds",
                  command=self.start_fake_generator,
                  width=30).pack(pady=5)
    
    def create_validation_view(self):
        """Vue Validation détaillée"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # Header
        title = tk.Label(container,
            text="✅ Dataset Validation",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 10))
        
        subtitle = tk.Label(container,
            text="Validate YOLO annotations and dataset quality",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
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
        self.valid_path_var.insert(0, "output/yolov8")
        
        ttk.Button(path_frame, text="📁", width=3,
                  command=self.browse_dataset).pack(side=tk.LEFT)
        
        # Options
        self.valid_html_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_content, text="📄 Generate HTML report",
                       variable=self.valid_html_var).pack(anchor='w', pady=10)
        
        # Buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
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
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # Header
        title = tk.Label(container,
            text="🎓 YOLO Training",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 10))
        
        subtitle = tk.Label(container,
            text="Train YOLOv8 model on your dataset",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
        # Configuration Card
        config_card = tk.Frame(container, bg=self.colors['bg_card'])
        config_card.pack(fill=tk.X, pady=(0, self.CARD_SPACING))
        
        card_title = tk.Label(config_card,
            text="⚙️ Training Configuration",
            font=self.FONT_CARD_TITLE,
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        )
        card_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        config_content = tk.Frame(config_card, bg=self.colors['bg_card'])
        config_content.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        # Model
        model_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        model_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(model_frame, text="Model:", 
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.train_model_var = ttk.Combobox(model_frame,
            values=["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt"],
            state='readonly', width=self.COMBOBOX_WIDTH)
        self.train_model_var.pack(side=tk.LEFT, padx=10)
        self.train_model_var.current(0)
        
        # Epochs
        epochs_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        epochs_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(epochs_frame, text="Epochs:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.train_epochs_var = ttk.Spinbox(epochs_frame, from_=10, to=500, width=self.SPINBOX_WIDTH)
        self.train_epochs_var.pack(side=tk.LEFT, padx=10)
        self.train_epochs_var.set(50)
        
        # Batch size
        batch_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        batch_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(batch_frame, text="Batch Size:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.train_batch_var = ttk.Spinbox(batch_frame, from_=4, to=64, width=self.SPINBOX_WIDTH)
        self.train_batch_var.pack(side=tk.LEFT, padx=10)
        self.train_batch_var.set(16)
        
        # Device
        device_frame = tk.Frame(config_content, bg=self.colors['bg_card'])
        device_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(device_frame, text="Device:",
                bg=self.colors['bg_card'], fg='#FFFFFF',
                font=self.FONT_BUTTON).pack(side=tk.LEFT)
        
        self.train_device_var = ttk.Combobox(device_frame,
            values=["0", "cpu", "0,1", "0,1,2,3"],
            state='readonly', width=self.COMBOBOX_WIDTH)
        self.train_device_var.pack(side=tk.LEFT, padx=10)
        self.train_device_var.current(0)
        
        # Buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="🎓 START TRAINING",
                  style='Accent.TButton',
                  command=self.start_training,
                  width=30).pack(pady=5)
        
        ttk.Button(btn_frame, text="📊 View Results",
                  command=self.show_training_plots,
                  width=30).pack(pady=5)
    
    def create_detection_view(self):
        """Vue Detection avec DetectionManager"""
        container = tk.Frame(self.content_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)
        
        # Header
        title = tk.Label(container,
            text="📹 Live Detection",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 10))
        
        subtitle = tk.Label(container,
            text="Real-time detection with webcam or batch processing",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
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
        self.detect_model_var.insert(0, "runs/train/pokemon_detector/weights/best.pt")
        
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
        
        # Buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="📹 START WEBCAM",
                  style='Accent.TButton',
                  command=self.start_webcam_detection,
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
        
        # Header
        title = tk.Label(container,
            text="📦 Dataset Export",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 10))
        
        subtitle = tk.Label(container,
            text="Export dataset to multiple formats (COCO, VOC, TFRecord, Roboflow)",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
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
        
        # Header
        title = tk.Label(container,
            text="🛠️ Utilities & Tools",
            font=self.FONT_TITLE,
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 10))
        
        subtitle = tk.Label(container,
            text="Additional tools and utilities",
            font=self.FONT_TEXT,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor='w', pady=(0, self.CARD_SPACING))
        
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
        ttk.Button(tools_content, text="📋 Excel & Prices",
                  command=self.open_excel_tools,
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
    
    def check_excel_file(self):
        """Vérifier si le fichier Excel des cartes existe"""
        excel_path = Path("cards_info.xlsx")
        return excel_path.exists()
    
    def create_sample_excel(self):
        """Créer un fichier Excel exemple"""
        try:
            import pandas as pd
            
            # Données exemple
            sample_data = {
                "Set #": ["001/191", "002/191", "003/191", "004/191", "005/191"],
                "Name": ["Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon"],
                "Set": ["Base Set", "Base Set", "Base Set", "Base Set", "Base Set"]
            }
            
            df = pd.DataFrame(sample_data)
            df.to_excel("cards_info.xlsx", index=False)
            
            self.log("✅ Fichier cards_info.xlsx créé avec succès!")
            messagebox.showinfo(
                "Succès",
                "Fichier cards_info.xlsx créé!\n\n"
                "Un fichier exemple a été créé avec 5 cartes.\n"
                "Vous pouvez le modifier pour ajouter vos propres cartes.\n\n"
                "Colonnes requises:\n"
                "• Set # : Numéro de carte (ex: 001/191)\n"
                "• Name : Nom de la carte\n"
                "• Set : Nom du set (optionnel)"
            )
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur création Excel: {e}")
            messagebox.showerror("Erreur", f"Impossible de créer le fichier:\n{e}")
            return False
    
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
                        messagebox.showerror("Erreur", "Script d'installation non trouvé!")
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
                    messagebox.showinfo("Succès", "Environnement installé!\n\nVous pouvez maintenant utiliser toutes les fonctionnalités.")
                    return True
                else:
                    self.log("❌ Installation échouée")
                    messagebox.showerror("Erreur", "Installation échouée.\nVérifiez les logs pour plus de détails.")
                    return False
                    
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                messagebox.showerror("Erreur", f"Erreur lors de l'installation:\n{e}")
                return False
            finally:
                self.end_operation()
        
        threading.Thread(target=install_task, daemon=True).start()
        return False  # Retourner False car l'installation est en cours
    
    def load_config(self):
        """Charger la configuration"""
        default_config = {
            "paths": {
                "images_source": "images",
                "fakeimg": "fakeimg",
                "output": "output"
            },
            "last_used": {
                "num_aug": 15
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
    
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
            images_path = Path("images")
            if images_path.exists():
                stats['source'] = len(list(images_path.glob("*.png"))) + \
                                 len(list(images_path.glob("*.jpg"))) + \
                                 len(list(images_path.glob("*.jpeg")))
            
            # Compter images augmentées
            aug_path = Path("output/augmented/images")
            if aug_path.exists():
                stats['augmented'] = len(list(aug_path.glob("*.png"))) + \
                                    len(list(aug_path.glob("*.jpg")))
            
            # Compter mosaïques
            mosaic_path = Path("output/yolov8/images")
            if mosaic_path.exists():
                stats['mosaics'] = len(list(mosaic_path.glob("*.png"))) + \
                                  len(list(mosaic_path.glob("*.jpg")))
            
            # Calculer taille totale du dossier output
            output_path = Path("output")
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
    
    def log(self, message):
        """Ajouter un message aux logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Gérer les emojis pour éviter les erreurs d'encodage Windows
        try:
            # Essayer d'afficher le message tel quel
            log_message = f"[{timestamp}] {message}\n"
            self.log_text.insert(tk.END, log_message)
        except Exception:
            # Si erreur d'encodage, remplacer les emojis problématiques
            safe_message = message.encode('ascii', 'ignore').decode('ascii')
            log_message = f"[{timestamp}] {safe_message}\n"
            self.log_text.insert(tk.END, log_message)
        
        self.log_text.see(tk.END)
        self.log_text.update()
        
        # Afficher aussi dans stdout (console) avec gestion d'encodage
        try:
            print(log_message.strip())
        except UnicodeEncodeError:
            # Fallback pour console Windows avec encodage limité
            safe_log = log_message.encode('ascii', 'ignore').decode('ascii')
            print(safe_log.strip())
    
    def start_operation(self, operation_name):
        """Démarrer une opération"""
        self.is_running = True
        self.operation_stopped = False  # Réinitialiser le flag
        self.progress_label.config(text=f"Running: {operation_name}")
        self.progress_bar.start(10)
        self.stop_button.config(state='normal')
    
    def end_operation(self):
        """Terminer une opération"""
        self.is_running = False
        self.current_process = None
        self.progress_label.config(text="Ready")
        self.progress_bar.stop()
        self.stop_button.config(state='disabled')
    
    def update_stats(self):
        """Mettre à jour les statistiques du dashboard"""
        try:
            # Recalculer les stats
            stats = self.get_real_stats()
            
            # Mettre à jour les cartes de stats si on est sur la vue home
            if hasattr(self, 'stat_cards') and self.current_view == 'home':
                # Mettre à jour les valeurs dans les cartes
                if 'source' in self.stat_cards:
                    self.stat_cards['source'].config(text=f"{stats['source']:,}")
                if 'augmented' in self.stat_cards:
                    self.stat_cards['augmented'].config(text=f"{stats['augmented']:,}")
                if 'mosaic' in self.stat_cards:
                    self.stat_cards['mosaic'].config(text=f"{stats['mosaic']:,}")
                if 'size' in self.stat_cards:
                    self.stat_cards['size'].config(text=stats['size'])
            
            # Mettre à jour le footer
            self.update_footer_stats()
            
        except Exception as e:
            self.log(f"⚠️ Erreur mise à jour stats: {e}")
    
    def update_footer_stats(self):
        """Mettre à jour les stats du footer"""
        try:
            stats = self.get_real_stats()
            footer_text = f"📊 Source: {stats['source']:,} | Augmented: {stats['augmented']:,} | Mosaic: {stats['mosaic']:,} | Size: {stats['size']}"
            if hasattr(self, 'footer_stats_label'):
                self.footer_stats_label.config(text=footer_text)
        except Exception:
            pass
    
    def stop_operation(self):
        """Arrêter l'opération en cours"""
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
            messagebox.showwarning("Warning", "Une opération est déjà en cours!")
            return
        
        # Récupérer les paramètres
        try:
            set_value = self.download_set_var.get().strip()
            if not set_value:
                messagebox.showerror("Error", "Veuillez sélectionner ou saisir un set Pokemon!")
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
            messagebox.showerror("Error", f"Configuration invalide:\n{e}")
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
                    messagebox.showerror("Error", f"Set non trouvé: {set_query}\n\nVérifiez le nom ou l'ID du set.")
                    return
                
                set_id = set_info.get('id', set_query)
                # name can be a string or dict depending on API version
                name_data = set_info.get('name', set_id)
                set_name = name_data if isinstance(name_data, str) else name_data.get(lang_code, set_id)
                # cardCount can be a dict or int
                card_count_data = set_info.get('cardCount', '?')
                card_count = card_count_data.get('total', '?') if isinstance(card_count_data, dict) else card_count_data
                
                self.log(f"✅ Set trouvé: {set_name} ({set_id}) - {card_count} cartes")
                self.log(f"⬇️ Téléchargement en cours...")
                
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
                self.log(f"✅ TÉLÉCHARGEMENT TERMINÉ")
                self.log(f"{'='*60}")
                self.log(f"✅ Succès : {ok}/{total} cartes")
                if fail > 0:
                    self.log(f"❌ Échecs : {fail}/{total} cartes")
                self.log(f"💾 Dossier : {output_dir}/{set_id}/")
                self.log(f"📄 Manifest : {output_dir}/{set_id}/manifest.csv")
                
                if fail == 0:
                    messagebox.showinfo("✅ Succès", 
                        f"Téléchargement terminé !\n\n"
                        f"✅ {ok} cartes téléchargées\n"
                        f"💾 Dossier: {output_dir}/{set_id}/")
                else:
                    messagebox.showwarning("⚠️ Terminé avec erreurs",
                        f"Téléchargement terminé avec des erreurs.\n\n"
                        f"✅ Succès: {ok}/{total}\n"
                        f"❌ Échecs: {fail}/{total}")
                
            except Exception as e:
                self.log(f"❌ ERREUR: {e}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Error", f"Erreur lors du téléchargement:\n{e}")
            finally:
                self.stop_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def start_workflow(self):
        """Démarrer le workflow automatique avec WorkflowManager"""
        if self.is_running:
            messagebox.showwarning("Warning", "Une opération est déjà en cours!")
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
            messagebox.showerror("Error", f"Configuration invalide:\n{e}")
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
                    messagebox.showinfo("Succès", 
                        f"✅ Workflow terminé!\n\n{manager.get_summary()}")
                else:
                    self.log("\n⚠️ Workflow terminé avec des erreurs")
                    messagebox.showwarning("Attention",
                        f"Workflow terminé avec erreurs:\n\n{manager.get_summary()}")
                
            except Exception as e:
                self.log(f"\n❌ ERREUR WORKFLOW: {e}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Erreur", f"Erreur workflow:\n{e}")
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
            messagebox.showinfo(
                "Help Documentation",
                f"📖 Online:\n{github_url}\n\n"
                f"📁 Local:\n{help_local}\n\n"
                "Copy the online link to your browser"
            )
    
    # ==================== TRAINING METHODS ====================
    
    def start_training(self):
        """Démarrer l'entraînement avec TrainingManager"""
        if self.is_running:
            messagebox.showwarning("Warning", "Une opération est déjà en cours!")
            return
        
        # Vérifier l'environnement virtuel
        if not self.ensure_venv():
            return
        
        try:
            model_name = self.train_model_var.get()
            epochs = int(self.train_epochs_var.get())
            batch = int(self.train_batch_var.get())
            device = self.train_device_var.get()
        except Exception as e:
            messagebox.showerror("Error", f"Configuration invalide:\n{e}")
            return
        
        # Vérifier data.yaml
        data_yaml = Path("output/yolov8/data.yaml")
        if not data_yaml.exists():
            messagebox.showerror("Error",
                f"Fichier data.yaml non trouvé!\n{data_yaml}\n\n"
                "Générez d'abord les mosaïques.")
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
                    data_yaml=data_yaml
                )
                
                # Manager
                manager = TrainingManager(config)
                manager.set_log_callback(self.log)
                
                # Entraîner
                self.log(f"🎓 Démarrage entraînement: {model_name}")
                self.log(f"   Epochs: {epochs}, Batch: {batch}, Device: {device}")
                
                if manager.train():
                    metrics = manager.get_metrics()
                    msg = f"✅ Entraînement terminé!\n\nModèle: {manager.get_best_model_path()}"
                    if metrics:
                        msg += f"\n\nmAP50: {metrics.get('mAP50', 0):.3f}"
                        msg += f"\nmAP50-95: {metrics.get('mAP50-95', 0):.3f}"
                    messagebox.showinfo("Succès", msg)
                else:
                    messagebox.showerror("Erreur", "Entraînement échoué!")
                
            except ImportError:
                self.log("❌ Package ultralytics non installé!")
                messagebox.showerror("Erreur",
                    "Package ultralytics non installé!\n\n"
                    "Installation:\npip install ultralytics")
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Erreur", f"Erreur:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def show_training_plots(self):
        """Afficher les graphiques d'entraînement"""
        plots_dir = Path("runs/train/pokemon_detector")
        results_png = plots_dir / "results.png"
        
        if not results_png.exists():
            messagebox.showwarning("Attention",
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
            messagebox.showerror("Erreur", f"Impossible d'afficher:\n{e}")
    
    # ==================== DETECTION METHODS ====================
    
    def browse_model(self):
        """Parcourir pour sélectionner un modèle"""
        model_path = filedialog.askopenfilename(
            title="Sélectionner modèle YOLO",
            filetypes=[("PyTorch Model", "*.pt"), ("Tous", "*.*")],
            initialdir="runs/train"
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
            messagebox.showerror("Error", f"Configuration invalide:\n{e}")
            return
        
        if not model_path.exists():
            messagebox.showerror("Error",
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
                    camera_id=camera_id
                )
                
                manager = DetectionManager(config)
                manager.set_log_callback(self.log)
                
                self.log("✅ Webcam démarrée! (appuyez sur 'q' pour quitter)")
                manager.detect_webcam()
                self.log("✅ Webcam arrêtée")
                
            except ImportError:
                self.log("❌ Packages manquants (ultralytics ou opencv)!")
                messagebox.showerror("Erreur",
                    "Packages manquants!\n\n"
                    "Installation:\n"
                    "pip install ultralytics opencv-python")
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                messagebox.showerror("Erreur", f"Erreur webcam:\n{e}")
        
        threading.Thread(target=task, daemon=True).start()
    
    def detect_single_image(self):
        """Détecter cartes dans une image"""
        try:
            model_path = Path(self.detect_model_var.get())
            conf = self.detect_conf_var.get()
        except Exception as e:
            messagebox.showerror("Error", f"Configuration invalide:\n{e}")
            return
        
        if not model_path.exists():
            messagebox.showerror("Error", "Modèle non trouvé!")
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
                    confidence=conf
                )
                
                manager = DetectionManager(config)
                manager.set_log_callback(self.log)
                
                # Détecter et afficher
                manager.show_image(img_path)
                
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                messagebox.showerror("Erreur", f"Erreur:\n{e}")
        
        threading.Thread(target=task, daemon=True).start()
    
    def detect_folder(self):
        """Détecter cartes dans un dossier"""
        try:
            model_path = Path(self.detect_model_var.get())
            conf = self.detect_conf_var.get()
        except Exception as e:
            messagebox.showerror("Error", f"Configuration invalide:\n{e}")
            return
        
        if not model_path.exists():
            messagebox.showerror("Error", "Modèle non trouvé!")
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
                    confidence=conf
                )
                
                manager = DetectionManager(config)
                manager.set_log_callback(self.log)
                
                # Détecter batch
                results = manager.detect_folder(folder_path)
                
                total = sum(len(dets) for dets in results.values())
                self.log(f"✅ {total} détection(s) sur {len(results)} images")
                
                messagebox.showinfo("Succès",
                    f"✅ Détection terminée!\n\n"
                    f"{len(results)} images traitées\n"
                    f"{total} détections totales\n\n"
                    f"Résultats dans: {folder_path}/detections/")
                
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                messagebox.showerror("Erreur", f"Erreur:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    # ==================== AUGMENTATION METHODS ====================
    
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
            messagebox.showerror("Error", f"Configuration invalide:\n{e}")
            return
        
        self.log(f"🎨 Augmentation ({aug_type}): {num_aug} variations → {target}/")
        self.start_operation("Augmentation")
        
        def task():
            try:
                # Standard augmentation
                if aug_type in ["Standard", "Both"]:
                    self.log("🎨 Running standard augmentation...")
                    cmd = [sys.executable, "-u", "core/augmentation.py",
                          "--num_aug", str(num_aug),
                          "--target", target]
                    
                    self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT, text=True,
                                              encoding='utf-8', errors='replace', bufsize=1)
                    
                    for line in iter(self.current_process.stdout.readline, ''):
                        if line and self.current_process:
                            self.log(line.strip())
                    
                    if self.current_process:
                        self.current_process.wait()
                        if self.current_process.returncode != 0:
                            self.log("❌ Standard augmentation failed!")
                            if aug_type == "Standard":
                                messagebox.showerror("Error", "Augmentation failed!")
                                return
                        else:
                            self.log("✅ Standard augmentation completed!")
                
                # Holographic augmentation
                if aug_type in ["Holographic", "Both"]:
                    self.log("✨ Running holographic augmentation...")
                    output_dir = target + "_holographic" if aug_type == "Both" else target
                    
                    # Get holographic parameters from settings
                    intensity = self.holographic_intensity.get()
                    variations = self.holographic_variations.get()
                    
                    cmd = [sys.executable, "-u", "core/holographic_augmenter.py",
                           "--input", "images",
                           "--output", output_dir,
                           "--intensity", str(intensity),
                           "--variations", str(variations)]
                    
                    self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT, text=True,
                                              encoding='utf-8', errors='replace', bufsize=1)
                    
                    for line in iter(self.current_process.stdout.readline, ''):
                        if line and self.current_process:
                            self.log(line.strip())
                    
                    if self.current_process:
                        self.current_process.wait()
                        if self.current_process.returncode != 0:
                            self.log("❌ Holographic augmentation failed!")
                            messagebox.showerror("Error", "Holographic augmentation failed!")
                            return
                        else:
                            self.log("✅ Holographic augmentation completed!")
                
                # Success message
                self.log("✅ All augmentations completed successfully!")
                messagebox.showinfo("Success", "Augmentation completed successfully!")
                self.update_stats()
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", f"Error:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    # ==================== MOSAIC METHODS ====================
    
    def start_mosaic(self):
        """Lancer génération de mosaïques"""
        mode = self.mosaic_mode_var.get()
        
        # Extract layout, background, transform values from combobox
        try:
            layout_val = int(self.mosaic_layout_var.get().split(' - ')[0])
            background_val = int(self.mosaic_background_var.get().split(' - ')[0])
            transform_val = int(self.mosaic_transform_var.get().split(' - ')[0])
        except:
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
        self.start_operation("Mosaic Generation")
        
        def task():
            try:
                if "All" in mode:
                    cmd = [sys.executable, "-u", "core/mosaic.py", "all"]
                else:
                    # Pass layout, background, transform parameters, and optionally max_groups
                    cmd = [sys.executable, "-u", "core/mosaic.py", 
                           str(layout_val), str(background_val), str(transform_val)]
                    if max_groups:
                        cmd.append(str(max_groups))
                
                self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, text=True,
                                          encoding='utf-8', errors='replace', bufsize=1)
                
                for line in iter(self.current_process.stdout.readline, ''):
                    if line and self.current_process:
                        self.log(line.strip())
                
                if self.current_process:
                    self.current_process.wait()
                    
                    if self.current_process.returncode == 0:
                        self.log("✅ Mosaïques générées!")
                        messagebox.showinfo("Succès", "Mosaïques générées avec succès!")
                        self.update_stats()
                    elif self.current_process.returncode is not None:
                        self.log("❌ Génération échouée")
                        messagebox.showerror("Erreur", "Génération échouée!")
                    
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                messagebox.showerror("Erreur", f"Erreur:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
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
    
    def start_validation(self):
        """Lancer validation du dataset"""
        dataset_path = self.valid_path_var.get()
        html = self.valid_html_var.get()
        
        if not os.path.exists(dataset_path):
            messagebox.showerror("Error", f"Dataset non trouvé:\n{dataset_path}")
            return
        
        self.log(f"✅ Validation: {dataset_path}")
        self.start_operation("Validation")
        
        def task():
            try:
                cmd = [sys.executable, "-u", "core/dataset_validator.py", dataset_path]
                if html:
                    cmd.append("--html")
                
                self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, text=True,
                                          encoding='utf-8', errors='replace', bufsize=1)
                
                for line in iter(self.current_process.stdout.readline, ''):
                    if line and self.current_process:
                        self.log(line.strip())
                
                if self.current_process:
                    self.current_process.wait()
                    
                    if self.current_process.returncode == 0:
                        self.log("✅ Validation terminée!")
                        if html:
                            self.log("📄 Rapport: validation_report.html")
                        messagebox.showinfo("Succès", "Validation terminée!\nVoir validation_report.html")
                    elif self.current_process.returncode is not None:
                        self.log("❌ Validation échouée")
                        messagebox.showerror("Erreur", "Validation échouée!")
                    
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                messagebox.showerror("Erreur", f"Erreur:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def open_validation_report(self):
        """Ouvrir le rapport HTML"""
        report_path = Path("validation_report.html")
        if report_path.exists():
            import webbrowser
            webbrowser.open(str(report_path.absolute()))
        else:
            messagebox.showwarning("Attention", "Rapport non trouvé!\nValidez d'abord le dataset.")
    
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
            messagebox.showwarning("Attention", "Sélectionnez au moins un format!")
            return
        
        self.log(f"📦 Export: {', '.join(formats)}")
        self.start_operation("Export")
        
        def task():
            try:
                for fmt in formats:
                    self.log(f"\n📦 Export format: {fmt}")
                    cmd = [sys.executable, "-u", "core/dataset_exporter.py",
                          "output/yolov8", "--format", fmt]
                    
                    self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT, text=True,
                                              encoding='utf-8', errors='replace', bufsize=1)
                    
                    for line in iter(self.current_process.stdout.readline, ''):
                        if line and self.current_process:
                            self.log(line.strip())
                    
                    if self.current_process:
                        self.current_process.wait()
                        
                        if self.current_process.returncode != 0:
                            self.log(f"❌ Export {fmt} échoué")
                
                self.log("\n✅ Export terminé!")
                messagebox.showinfo("Succès", f"Export terminé!\n\nFormats: {', '.join(formats)}")
                
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
                messagebox.showerror("Erreur", f"Erreur:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    # ==================== TOOLS METHODS ====================
    
    def start_balancing(self):
        """Lancer auto-balancing"""
        self.log("⚖️ Auto-balancing des classes...")
        self.start_operation("Balancing")
        
        def task():
            try:
                # -u pour unbuffered output (logs en temps réel)
                cmd = [sys.executable, "-u", "core/auto_balancer.py", "output/yolov8",
                      "--strategy", "augment", "--target", "50"]
                
                self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, text=True,
                                          encoding='utf-8', errors='replace', bufsize=1)
                
                for line in iter(self.current_process.stdout.readline, ''):
                    if line and self.current_process:
                        self.log(line.strip())
                
                if self.current_process:
                    self.current_process.wait()
                    
                    # Vérifier si c'est un arrêt volontaire
                    if self.operation_stopped:
                        pass  # Déjà logué dans stop_operation()
                    elif self.current_process.returncode == 0:
                        self.log("✅ Balancing terminé!")
                        messagebox.showinfo("Succès", "Classes équilibrées!")
                    elif self.current_process.returncode is not None:
                        self.log("❌ Balancing échoué!")
                        messagebox.showerror("Erreur", "Balancing échoué!")
                    
            except Exception as e:
                if not self.operation_stopped:
                    self.log(f"❌ Erreur: {e}")
                    messagebox.showerror("Erreur", f"Erreur:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
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
            dialog.destroy()
            self.log(f"✨ Holographic augmentation: intensity={intensity_var.get()}, variations={variations_var.get()}")
            self.start_operation("Holographic Augmentation")
            
            def task():
                try:
                    output_dir = "images_holographic"
                    # -u pour unbuffered output (logs en temps réel)
                    cmd = [sys.executable, "-u", "core/holographic_augmenter.py",
                          "images", output_dir, "--variations", str(variations_var.get())]
                    
                    self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT, text=True, 
                                              encoding='utf-8', errors='replace', bufsize=1)
                    
                    for line in iter(self.current_process.stdout.readline, ''):
                        if line and self.current_process:
                            self.log(line.strip())
                    
                    if self.current_process:
                        self.current_process.wait()
                        
                        # Vérifier si c'est un arrêt volontaire
                        if self.operation_stopped:
                            pass  # Déjà logué dans stop_operation()
                        elif self.current_process.returncode == 0:
                            self.log("✅ Holographic augmentation terminée!")
                            messagebox.showinfo("Succès", "Effets holographiques appliqués!")
                        elif self.current_process.returncode is not None:
                            self.log("❌ Augmentation holographique échouée!")
                            messagebox.showerror("Erreur", "Augmentation holographique échouée!")
                        
                except Exception as e:
                    if not self.operation_stopped:
                        self.log(f"❌ Erreur: {e}")
                        messagebox.showerror("Erreur", f"Erreur:\n{e}")
                finally:
                    self.end_operation()
            
            threading.Thread(target=task, daemon=True).start()
        
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
            messagebox.showerror("Error", f"Invalid configuration:\n{e}")
            return
        
        if not os.path.exists(input_dir):
            messagebox.showerror("Error", f"Input directory '{input_dir}' does not exist!\nDownload card images first from the Image Download view.")
            return
        
        if sl >= sh:
            messagebox.showerror("Error", "Min area (sl) must be less than max area (sh)!")
            return
        
        if r1 >= r2:
            messagebox.showerror("Error", "Min aspect (r1) must be less than max aspect (r2)!")
            return
        
        self.log(f"🎲 Applying random erasing: {input_dir} → {output_dir}")
        self.start_operation("Fake Image Generation")
        
        def task():
            try:
                cmd = [sys.executable, "-u", "core/random_erasing.py",
                       "--input_dir", input_dir,
                       "--output_dir", output_dir,
                       "--p", str(p),
                       "--sl", str(sl),
                       "--sh", str(sh),
                       "--r1", str(r1),
                       "--r2", str(r2)]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        self.log(line)
                
                process.wait()
                
                if process.returncode == 0:
                    # Count generated files
                    if os.path.exists(output_dir):
                        count = len([f for f in os.listdir(output_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
                        self.log(f"✅ {count} fake images generated in {output_dir}/")
                        messagebox.showinfo("Success", f"Generated {count} fake images!")
                    else:
                        self.log(f"✅ Fake images generated in {output_dir}/")
                        messagebox.showinfo("Success", "Fake images generated successfully!")
                    
                    self.update_stats()
                    # Refresh view if still on fakeimg
                    if self.current_view == 'fakeimg':
                        self.show_view('fakeimg')
                else:
                    self.log(f"❌ Fake generation failed (exit code: {process.returncode})")
                    messagebox.showerror("Error", "Fake generation failed!")
            
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", f"Error:\n{e}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
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
            dialog.destroy()
            self.log(f"📋 Generating {count_var.get()} fake backgrounds...")
            self.start_operation("Fake Background Generation")
            
            def task():
                try:
                    output_dir = output_var.get()
                    cmd = [sys.executable, "-u", "tools/generate_fake_backgrounds.py",
                           "--count", str(count_var.get()),
                           "--output", output_dir,
                           "--min-noise", str(min_noise_var.get()),
                           "--max-noise", str(max_noise_var.get())]
                    
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    for line in process.stdout:
                        line = line.strip()
                        if line:
                            self.log(line)
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        self.log(f"✅ {count_var.get()} fake backgrounds generated in {output_dir}/")
                        messagebox.showinfo("Success", f"Generated {count_var.get()} fake backgrounds!")
                        self.update_stats()
                    else:
                        self.log(f"❌ Fake generation failed (exit code: {process.returncode})")
                        messagebox.showerror("Error", "Fake generation failed!")
                
                except Exception as e:
                    self.log(f"❌ Error: {e}")
                    messagebox.showerror("Error", f"Error:\n{e}")
                finally:
                    self.end_operation()
            
            threading.Thread(target=task, daemon=True).start()
        
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
                messagebox.showwarning("Attention", "Entrez un nom de carte!")
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
            images_count = len(list(Path("images").glob("*.png")))
            aug_count = len(list(Path("output/augmented/images").glob("*.png"))) if Path("output/augmented/images").exists() else 0
            yolo_count = len(list(Path("output/yolov8/images").glob("*.png"))) if Path("output/yolov8/images").exists() else 0
            
            msg = f"""📊 Dataset Statistics

📁 Original images: {images_count}
🎨 Augmented images: {aug_count}
🧩 YOLO mosaics: {yolo_count}

Total: {images_count + aug_count + yolo_count} images"""
            
            messagebox.showinfo("Statistics", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Erreur stats:\n{e}")
    
    def open_excel_tools(self):
        """Ouvrir dialog Excel & Prices avec TCGdex API"""
        # Dialog pour outils Excel
        dialog = tk.Toplevel(self.root)
        dialog.title("📋 Excel & Card Prices")
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
            text="📋 Excel & Card Prices Tools",
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
        
        # Section 1: Générer Excel depuis API
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
        
        extension_output_var = tk.StringVar(value="cards_list.xlsx")
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
            text="▶️ Generate Excel",
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
            text="Input Excel File (must have: Set #, Name, Set columns):",
            font=('Segoe UI', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        price_input_frame = tk.Frame(section2, bg=self.colors['bg_card'])
        price_input_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        price_input_var = tk.StringVar(value="cards_info.xlsx")
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
                title="Select Excel File",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
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
            text="Output Excel File:",
            font=('Segoe UI', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        price_output_var = tk.StringVar(value="cards_with_prices.xlsx")
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
        """Générer un fichier Excel depuis l'API TCGdex pour une extension"""
        extension = extension.strip()
        output = output.strip()
        
        if not extension:
            messagebox.showerror("Error", "Please enter a set name!")
            return
        
        if not output:
            messagebox.showerror("Error", "Please enter an output filename!")
            return
        
        self.log(f"📋 Generating card list for: {extension}")
        self.start_operation("Generating Excel")
        
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
                except:
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
                            messagebox.showerror("Error", f"Set '{extension}' not found.\nTry with the set ID (e.g., sv08, sv07, etc.)")
                            return
                        
                        best_match = found_sets[0]
                        set_id = best_match.get('id')
                        set_name = best_match.get('name')
                        
                        self.log(f"✅ Set found: '{set_name}' (ID: {set_id})")
                        
                    except Exception as e:
                        self.log(f"❌ Error searching set: {e}")
                        messagebox.showerror("Error", f"Cannot find set.\nTry with ID (e.g., sv08)")
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
                        messagebox.showwarning("Warning", f"No cards found for '{set_name}'")
                        return
                    
                    self.log(f"✅ {len(cards_list)} cards fetched")
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        self.log(f"❌ Set '{set_id}' not found (404)")
                        messagebox.showerror("Error", f"Set '{set_id}' not found.\nCheck the set ID.")
                    else:
                        self.log(f"❌ HTTP Error: {e}")
                        messagebox.showerror("Error", f"Error fetching: {e}")
                    return
                except Exception as e:
                    self.log(f"❌ Error: {e}")
                    messagebox.showerror("Error", f"Error: {e}")
                    return
                
                # Créer le DataFrame
                self.log(f"\n📝 Creating Excel file...")
                self.log(f"📁 File: {output}")
                
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
                
                # Sort by card number
                df['_sort'] = df['Set #'].str.extract(r'(\d+)').astype(int)
                df = df.sort_values('_sort').drop(columns=['_sort'])
                
                self.log(f"💾 Writing to Excel...")
                df.to_excel(output, index=False)
                
                file_size = os.path.getsize(output) / 1024
                
                self.log(f"\n{'='*60}")
                self.log(f"✅ SUCCESS")
                self.log(f"{'='*60}")
                self.log(f"📁 File: {output}")
                self.log(f"💾 Size: {file_size:.1f} KB")
                self.log(f"📊 Cards: {len(rows)}")
                self.log(f"🌐 Source: TCGdex API (free)")
                self.log(f"{'='*60}")
                
                messagebox.showinfo("Success", f"File generated successfully!\n\n{len(rows)} cards from '{set_name}'\n\nSource: TCGdex (free)")
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def update_card_prices_full(self, input_file, output_file):
        """Mettre à jour les prix des cartes dans un fichier Excel avec TCGdex"""
        input_file = input_file.strip()
        output_file = output_file.strip()
        
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", f"Input file '{input_file}' doesn't exist!")
            return
        
        if not output_file:
            messagebox.showerror("Error", "Please enter an output filename!")
            return
        
        # Charger la config API
        try:
            with open('api_config.json', 'r') as f:
                api_config = json.load(f)
        except:
            api_config = {"tcgdex": {"language": "en"}}
        
        self.log(f"💰 Updating prices from: {input_file}")
        self.log(f"🌐 API: TCGdex (free)")
        
        self.start_operation("Updating Prices")
        
        def task():
            try:
                import pandas as pd
                import concurrent.futures
                import time
                from core.tcgdex_api import TCGdexAPI
                
                tcgdex_config = api_config.get("tcgdex", {})
                language = tcgdex_config.get("language", "en")
                
                # Créer le client TCGdex
                self.log(f"🔧 Initializing TCGdex client (language: {language})...")
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
                    """Worker thread to process one card"""
                    nonlocal processed
                    
                    name = str(row.get("Name", "")).strip()
                    set_name = str(row.get("Set", "")).strip() if "Set" in row else None
                    set_hash = str(row.get("Set #", "")).strip() if "Set #" in row else None
                    
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
                        else:
                            source = None
                    except Exception as e:
                        price, pmax, source = None, None, None
                        failed.append((name, set_hash or "", str(e)))
                    
                    processed += 1
                    now = time.time()
                    if processed % 10 == 0 or (now - last_log[0]) >= 5:
                        self.log(f"📊 Progress: {processed}/{total} ({int(processed/total*100)}%)")
                        last_log[0] = now
                    
                    return idx, price, pmax, source
                
                self.log(f"🔄 Processing {total} cards with TCGdex (free)")
                self.log(f"💡 Automatic prices: Cardmarket (EUR) + TCGPlayer (USD)")
                self.log(f"⚡ No rate limit: fast processing (~{total * 0.3:.0f}s estimated)")
                
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
                
                # Save
                df.to_excel(output_file, index=False)
                
                success_count = df["Prix"].notna().sum()
                self.log(f"✅ File generated: {output_file}")
                self.log(f"📊 Prices found: {success_count}/{total} ({int(success_count/total*100)}%)")
                self.log(f"⏱️  Total time: {elapsed:.1f}s (~{(elapsed/total if total else 0):.2f}s/card)")
                
                if failed:
                    self.log(f"⚠️  {len(failed)} cards failed (examples):")
                    for c, num, e in failed[:5]:
                        self.log(f"   • {c} #{num}: {e[:50]}")
                
                messagebox.showinfo("Complete", f"Prices updated!\n{success_count}/{total} cards with prices")
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Error", f"Error:\n{str(e)}")
            finally:
                self.end_operation()
        
        threading.Thread(target=task, daemon=True).start()
    
    def search_card_price_full(self, card_name, card_set):
        """Rechercher le prix d'une carte"""
        card_name = card_name.strip()
        card_set = card_set.strip() if card_set else None
        
        if not card_name:
            messagebox.showerror("Error", "Please enter a card name!")
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
                except:
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
                    messagebox.showinfo("Card Prices", result)
                else:
                    self.log(f"❌ Card not found: {card_name}")
                    messagebox.showwarning("Not Found", f"Card '{card_name}' not found.\n\nTry with a different spelling or set name.")
                
            except Exception as e:
                self.log(f"❌ Error: {e}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Error", f"Error:\n{e}")
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
            output_path = Path("output")
            if output_path.exists():
                shutil.rmtree(output_path)
                self.log("✅ Output folder deleted")
                messagebox.showinfo("Success", "Output folder cleaned successfully!")
            else:
                self.log("⚠️ Output folder not found")
                messagebox.showwarning("Warning", "Output folder not found!")
        except Exception as e:
            self.log(f"❌ Error cleaning output: {e}")
            messagebox.showerror("Error", f"Failed to clean output:\n{e}")
    
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
            aug_path = Path("output/augmented")
            if aug_path.exists():
                shutil.rmtree(aug_path)
                self.log("✅ Augmented folder deleted")
                messagebox.showinfo("Success", "Augmented folder cleaned!")
            else:
                self.log("⚠️ Augmented folder not found")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Failed to clean:\n{e}")
    
    def clean_mosaics(self):
        """Nettoyer output/yolov8/"""
        result = messagebox.askyesno(
            "Confirm Clean",
            "⚠️ This will DELETE output/yolov8/ folder!\n\n"
            "This includes all mosaics and YOLO datasets.\n\n"
            "Are you sure?",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            import shutil
            mosaic_path = Path("output/yolov8")
            if mosaic_path.exists():
                shutil.rmtree(mosaic_path)
                self.log("✅ Mosaics folder deleted")
                messagebox.showinfo("Success", "Mosaics folder cleaned!")
            else:
                self.log("⚠️ Mosaics folder not found")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Failed to clean:\n{e}")
    
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
            runs_path = Path("runs")
            if runs_path.exists():
                shutil.rmtree(runs_path)
                self.log("✅ Training results deleted")
                messagebox.showinfo("Success", "Training results cleaned!")
            else:
                self.log("⚠️ Training results not found")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Failed to clean:\n{e}")
    
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
            holo_path = Path("images_holographic")
            if holo_path.exists():
                shutil.rmtree(holo_path)
                self.log("✅ Holographic folder deleted")
                messagebox.showinfo("Success", "Holographic folder cleaned!")
            else:
                self.log("⚠️ Holographic folder not found")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Failed to clean:\n{e}")
    
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
                messagebox.showinfo("Success", f"Cleaned: {', '.join(deleted)}")
            else:
                self.log("⚠️ Fake image folder not found")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Failed to clean:\n{e}")
    
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
                
                messagebox.showinfo("Clean Complete", message)
            else:
                messagebox.showinfo("Clean Complete", "No folders found to clean.")
                
        except Exception as e:
            self.log(f"❌ Error during clean all: {e}")
            messagebox.showerror("Error", f"Failed to clean:\n{e}")
    
    def open_output_folder(self):
        """Ouvrir dossier output"""
        output_path = Path("output").absolute()
        if output_path.exists():
            import subprocess
            subprocess.run(["explorer", str(output_path)])
        else:
            messagebox.showwarning("Attention", "Dossier output/ non trouvé!")
    
    def open_folder(self, folder_name):
        """Ouvrir un dossier spécifique"""
        folder_path = Path(folder_name).absolute()
        if folder_path.exists():
            import subprocess
            subprocess.run(["explorer", str(folder_path)])
        else:
            messagebox.showwarning("Warning", f"Folder {folder_name}/ not found!")

def main():
    root = tk.Tk()
    app = ModernPokemonGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
