# 📋 Dossier de Planification

Ce dossier contient les **documents de planification** pour les fonctionnalités majeures en cours de développement.

## 🎯 Objectif

Documenter la planification par étapes de chaque nouvelle fonctionnalité importante pour :
- ✅ Améliorer la communication entre développeur et Copilot
- ✅ Suivre la progression en temps réel
- ✅ Tracer les décisions importantes
- ✅ Clarifier les points bloquants
- ✅ Servir de base pour la documentation finale

## 📁 Structure

### Fichiers types
```
.planning/
├── README.md                              # Ce fichier (documentation du dossier)
├── TEMPLATE.md                            # Template à copier pour nouveaux documents
├── 2025-11-11_systeme-planification.md    # Exemple : Mise en place du système
├── 2025-11-15_integration-api-externe.md  # Exemple : Intégration d'API
└── 2025-11-20_refonte-module-core.md      # Exemple : Refactorisation majeure
```

### Nommage des fichiers
**Format** : `YYYY-MM-DD_description-courte.md`

**Exemples** :
- `2025-11-11_systeme-planification.md`
- `2025-11-15_integration-tcgdex-api.md`
- `2025-11-20_refonte-augmentation.md`
- `2025-12-01_support-multi-gpu.md`

## 📝 Sections obligatoires

Chaque document doit contenir :

1. **🎯 Vue d'ensemble**
   - Description demande originale
   - Objectif mesurable
   - Impact attendu

2. **📝 Planification par étapes**
   - Étapes numérotées avec actions
   - Fichiers concernés
   - Critères de validation

3. **📊 Suivi des progrès**
   - Timeline visuelle
   - Progression (X/Y étapes, %)
   - Journal des modifications

4. **❓ Questions de clarification**
   - Questions ouvertes
   - Décisions prises
   - Points d'attention

5. **🔧 Détails techniques**
   - Dépendances
   - Modifications structure
   - Tests requis

6. **📚 Documentation à mettre à jour**
   - Liste des docs concernées

7. **✅ Checklist finale**
   - Validation avant commit

## 🔄 Workflow

```
1. Nouvelle demande majeure arrive
         ↓
2. ⚠️ CRÉER document .planning/ AVANT tout code
         ↓
3. Copier TEMPLATE.md et renommer
         ↓
4. Remplir vue d'ensemble + étapes
         ↓
5. Proposer plan à l'utilisateur
         ↓
6. Obtenir validation/clarifications
         ↓
7. Pour chaque étape :
   - Marquer "En cours"
   - Exécuter actions
   - Mettre à jour progression
   - Logger décisions
   - Marquer "Terminé"
         ↓
8. Finalisation + checklist
         ↓
9. Commit (document reste en .planning/)
```

## ⚠️ Important

### Ce dossier est gitignored
- Ces documents sont des **work-in-progress**
- Ils ne doivent **pas être versionnés** dans Git
- Exception : `TEMPLATE.md` et `README.md` (références)

### Quand créer un document ?

**✅ OBLIGATOIRE pour** :
- Nouvelle fonctionnalité majeure
- Refactorisation d'architecture
- Ajout de plusieurs modules interconnectés
- Intégration d'API externe
- Modification workflow utilisateur

**❌ NON NÉCESSAIRE pour** :
- Simple bug fix ponctuel
- Correction de typo
- Mise à jour mineure de doc
- Ajout d'un seul petit script

## 🔗 Références

- Voir `.github/copilot-instructions.md` → Section "Système de Planification par Étapes"
- Exemple concret : `2025-11-11_systeme-planification.md`

## 📊 Avantages du système

| Aspect | Bénéfice |
|--------|----------|
| **Communication** | Plan visible avant exécution |
| **Traçabilité** | Historique complet des décisions |
| **Clarification** | Questions documentées avec contexte |
| **Progression** | Suivi visuel en temps réel |
| **Documentation** | Base pour CHANGELOG et docs finales |
| **Reproductibilité** | Plans réutilisables pour projets futurs |

---

**Créé le** : 11 novembre 2025  
**Par** : Système de planification v2.1
