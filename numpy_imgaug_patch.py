#!/usr/bin/env python3
"""
Patch de compatibilité NumPy pour imgaug
Ajoute les alias dépréciés manquants pour que imgaug fonctionne
"""
import numpy as np

# Restaurer les alias NumPy dépréciés pour imgaug
if not hasattr(np, 'bool'):
    np.bool = np.bool_
if not hasattr(np, 'int'):
    np.int = np.int_
if not hasattr(np, 'float'):
    np.float = np.float_
if not hasattr(np, 'complex'):
    np.complex = np.complex_
if not hasattr(np, 'object'):
    np.object = np.object_
if not hasattr(np, 'str'):
    np.str = np.str_
if not hasattr(np, 'long'):
    np.long = np.int_
if not hasattr(np, 'unicode'):
    np.unicode = np.str_

print("✓ Patch NumPy appliqué pour imgaug")
