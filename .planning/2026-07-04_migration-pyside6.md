# 📋 Planification : Migration GUI Tkinter → PySide6 (Qt)

**Date de création** : 2026-07-04
**Statut** : ✅ Q0-Q4 implémentés (2026-07-04) — Tkinter conservé en secours jusqu'à validation sur poste Windows
**Priorité** : Moyenne (confort/pérennité, pas un correctif)

---

## 🎯 Vue d'ensemble

### Description de la demande
> Suite à la question « on aurait pu refactoriser en Rust ou Avalonia ? » :
> Rust/Avalonia écartés (voir décision ci-dessous), chiffrage d'une migration
> PySide6 demandé (« go »).

### Objectif
Remplacer la couche d'affichage Tkinter par PySide6 (Qt 6) **sans toucher au
pipeline** : UI moderne (thème sombre natif, widgets riches, HiDPI), vrai
modèle de signaux/slots thread-safe, et tests UI exécutables en CI
(`QT_QPA_PLATFORM=offscreen` — gros avantage vs Tkinter).

### Pourquoi c'est devenu raisonnable
La Phase 4 (v3.6.0) a découplé la logique de l'UI :
- `gui/task_runner.py` et `gui/config.py` sont **déjà indépendants de Tkinter**
- les managers core communiquent par callbacks (`BaseManager`)
- le thème est centralisé (`gui/theme.py` → transposable en QSS)
Seule la couche widgets est à réécrire (~7 100 lignes Tkinter + le
SettingsDialog de 1 650 lignes).

### Décision d'architecture (rappel)
| Option | Verdict | Raison |
|---|---|---|
| Rust (pipeline) | ❌ | OpenCV/PyTorch déjà en C++/CUDA ; perte d'Albumentations/ultralytics ; gain ~nul |
| Avalonia (C#) | ❌ | IPC UI C# ↔ backend Python = double toolchain pour un mono-dev |
| **PySide6** | ✅ | Reste en Python, migration incrémentale, tests headless en CI |
| NiceGUI / Tauri | 💤 backlog | Si un jour l'UI doit être web/distribuée |

---

## 📐 Principes de migration

1. **Coexistence** : le GUI Tkinter reste fonctionnel pendant TOUTE la
   migration. Nouveau package `gui_qt/` + point d'entrée `GUI_qt.py`.
   Tkinter n'est retiré qu'à parité fonctionnelle constatée.
2. **Zéro changement dans `core/`** : les managers et le TaskRunner sont
   consommés tels quels. Le `ui_dispatch` du TaskRunner devient un signal Qt
   (thread-safe nativement — plus besoin de la file manuelle).
3. **Une vue = un module** : pas de nouveau monolithe. `gui_qt/views/*.py`.
4. **Testable en CI** : chaque vue a un test `pytest-qt` offscreen (le job CI
   actuel peut les exécuter sur Ubuntu ET Windows sans display).

---

## 📝 Planification par étapes

### Étape Q0 : Socle applicatif
**Statut** : ✅ Terminé — **Effort : ~½ journée**

- [x] Dépendance `pyside6` (extra `[gui-qt]` dans pyproject) + `pytest-qt` en dev
- [x] `gui_qt/app.py` : QMainWindow, sidebar de navigation (QListWidget),
  `QStackedWidget` pour les vues, panneau de log dockable (QPlainTextEdit),
  barre de statut avec progression + bouton Stop
- [x] `gui_qt/theme.py` : feuille QSS générée depuis `gui/theme.COLORS`
  (palette Catppuccin conservée)
- [x] `gui_qt/bridge.py` : `QtTaskBridge` — adapte TaskRunner à Qt
  (log → signal `logged(str)`, ui_dispatch → signal `dispatched(object)`)
- [x] Test pytest-qt : lancement offscreen, navigation, log streamé

**Validation** : fenêtre vide navigable + logs TaskRunner visibles, test CI vert

### Étape Q1 : Vues « simples » (peu de logique)
**Statut** : ✅ Terminé — **Effort : ~1 journée**

- [ ] Home/Dashboard (stats + dernière activité)
- [ ] Validation, Export, Tools (boutons → TaskRunner, déjà générique)
- [ ] Fake images (formulaire paramètres → TaskRunner)

**Validation** : chaque vue déclenche sa commande réelle (test sur mini-dataset)

### Étape Q2 : Vues de génération
**Statut** : ✅ Terminé — **Effort : ~1 journée**

- [ ] Download (liste des sets TCGdex, progression par image)
- [ ] Augmentation (+ pipeline holographic), Mosaïques (mode/layout/etc.)
- [ ] Workflow automatique (progression par étape via `set_progress_callback`)

**Validation** : pipeline complet Download → Augment → Mosaic → Merge depuis
le GUI Qt sur le mini-dataset de test

### Étape Q3 : Training, Détection, Settings
**Statut** : ✅ Terminé — **Effort : ~1-1,5 journée**

- [ ] Training (presets système/Jetson, métriques, export TensorRT)
- [ ] Détection (webcam/image/dossier — la fenêtre OpenCV reste inchangée)
- [ ] Settings : QDialog à onglets (remplace les 1 650 lignes du
  SettingsDialog Tkinter ; lecture/écriture via `GuiConfig` déjà en place)

**Validation** : parité écran par écran avec la checklist
`docs/archive/migration/CHECKLIST_TEST_GUI.md` (adaptée)

### Étape Q4 : Bascule et retrait de Tkinter
**Statut** : 🟡 Bascule faite — retrait Tkinter EN ATTENTE de validation Windows — **Effort : ~½ journée** — ⚠️ seulement après validation utilisateur sur Windows

- [ ] START.bat / start.sh pointent vers `GUI_qt.py`
- [ ] Suppression de `GUI_v3.1_modern.py` + `gui/settings_dialog.py`
  (les modules agnostiques `task_runner`/`config`/`theme` restent)
- [ ] Doc (README, USER_GUIDE, CHANGELOG) + captures d'écran

---

## 📊 Estimation globale

- **Total : ~4-5 journées** de travail effectif, découpables en 5 livraisons
  indépendantes (chaque étape laisse le projet fonctionnel, Tkinter en secours)
- Taille attendue de `gui_qt/` : ~2 500-3 500 lignes (Qt est plus déclaratif
  que le Tkinter manuel actuel : layouts, styles QSS, signaux)

## ⚠️ Risques & parades

| Risque | Parade |
|---|---|
| Perte de parité fonctionnelle (11 vues, beaucoup de petits comportements) | Migration vue par vue + checklist de parité + Tkinter conservé jusqu'à la fin |
| PySide6 ≈ 200 Mo installés | extra optionnel `[gui-qt]`, Tkinter reste le défaut jusqu'à Q4 |
| Licence | PySide6 est LGPL (usage libre, pas de contamination du code) — OK |
| Webcam OpenCV + boucle Qt | inchangé : cv2.imshow tourne déjà dans son propre thread/process |

## ❓ Questions avant lancement

1. **Périmètre** : les 11 vues sont-elles toutes utilisées ? Si certaines ne
   servent jamais (ex. Export VOC/TFRecord), on les migre en dernier ou pas
   du tout → gain de temps direct.
2. **Look** : conserver la palette Catppuccin actuelle à l'identique, ou en
   profiter pour un rafraîchissement (thème clair/sombre commutable) ?
3. **Rythme** : tout d'un trait, ou étape par étape avec validation sur votre
   poste Windows entre chaque (recommandé — comme pour les Phases 1-4) ?

---

## ✅ Checklist finale
- [ ] Parité fonctionnelle validée sur Windows (checklist complète)
- [ ] Tests pytest-qt verts en CI (Ubuntu + Windows, offscreen)
- [ ] Doc et lanceurs à jour
- [ ] Retrait Tkinter (Q4) validé explicitement par l'utilisateur


---

## 📊 Journal d'exécution (2026-07-04)

- Décisions utilisateur : périmètre complet (11 vues), thèmes clair+sombre, tout d'un trait
- Q0-Q3 : package gui_qt/ complet (~2 300 lignes), 11 vues, 2 thèmes commutables persistés
- `core/manifest_tools.py` extrait du GUI Tkinter (partagé par les 2 interfaces)
- Q4 partiel : START.bat/start.sh → GUI_qt.py ; Tkinter conservé (START_LEGACY.bat / start.sh --legacy).
  ⚠️ La SUPPRESSION de GUI_v3.1_modern.py attend un passage visuel sur poste Windows —
  seule dérogation au « tout d'un trait » (irréversible sans validation sur display réel).
- Validation : 7 tests pytest-qt offscreen + smoke test complet (11 vues, thèmes,
  bridge succès/échec) + 3 captures d'écran générées sous offscreen ; suite complète verte
