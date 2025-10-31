#!/usr/bin/env python3
"""
Patch de compatibilité NumPy pour imgaug
Ajoute les alias dépréciés manquants pour que imgaug fonctionne
"""
import numpy as np

# Restaurer les alias NumPy dépréciés pour imgaug
# NumPy 2.0 a supprimé ces alias, on les recrée
if not hasattr(np, 'bool'):
    np.bool = bool
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float
if not hasattr(np, 'complex'):
    np.complex = complex
if not hasattr(np, 'object'):
    np.object = object
if not hasattr(np, 'str'):
    np.str = str
if not hasattr(np, 'long'):
    np.long = int
if not hasattr(np, 'unicode'):
    np.unicode = str

# Types spécifiques NumPy
if not hasattr(np, 'float_'):
    np.float_ = np.float64
if not hasattr(np, 'int_'):
    np.int_ = np.int64
if not hasattr(np, 'bool_'):
    np.bool_ = np.bool8

print("✓ Patch NumPy appliqué pour imgaug")
