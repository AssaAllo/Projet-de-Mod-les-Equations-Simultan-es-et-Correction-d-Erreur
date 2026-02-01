# 📊 Dashboard Professionnel ARDL/ECM + Système 3SLS

## Vue d'ensemble

Ce projet propose un **dashboard analytique complet et interactif** pour l'étude des **transferts de fonds et de la croissance économique au Tchad (1995–2022)**. Il combine deux approches économétriques avancées :

- **ARDL/ECM** : Analyse dynamique court et long terme
- **3SLS (Système d'Équations Simultanées)** : Relations multivariées endogènes
- **Causalité de Granger** : Tests de causalité économique

---

## 🎯 Objectifs

1. **Modéliser les déterminants des transferts de fonds** de migrants vers le Tchad
2. **Analyser l'impact sur la croissance économique** via plusieurs canaux
3. **Tester les relations long terme** via cointégration (Pesaran Bounds)
4. **Quantifier les effets dynamiques** court et long terme
5. **Fournir un outil d'aide à la décision** avec simulations interactives

---

## 📁 Contenu du Projet

```
ProjetMES/
├── app.py                      # Application Streamlit principale
├── base.xlsx                   # Données (si présent)
├── README.md                   # Documentation complète
└── PUSH_TO_GITHUB.md          # Guide pour déployer sur GitHub
```

---

## 🚀 Installation et Configuration

### Prérequis

- **Python 3.8+**
- **pip** (gestionnaire de paquets Python)
- **Git** (pour le contrôle de version)

### Installation des dépendances

```bash
pip install streamlit pandas numpy plotly openpyxl
```

### Lancer l'application

```bash
streamlit run app.py
```

L'application se lancera sur `http://localhost:8501`

---

## 📊 Structure de l'Application

Le dashboard est organisé en **7 onglets principaux** :

### 1. 📁 **Données**
- **Aperçu** : Visualisation des données brutes (premier 25 lignes)
- **Statistiques descriptives** : Moyennes, écarts-types, min/max
- **Distributions** : Histogrammes et matrice de corrélations
- **Téléchargement** : Export en CSV/Excel

**Variables principales :**
- `year` : Année (1995–2022)
- `GROWTH` : Croissance du PIB (%)
- `REM` : Remittances (USD, niveau)
- `TC` : Taux de change (FCFA/USD)
- `FDI` : Investissement direct étrangement (USD)
- `OPEN` : Ouverture commerciale (ratio X+M/PIB)
- `CREDIT` : Crédit intérieur privé (% PIB)
- `INV` : Investissement total
- `INF` : Inflation (IPC, %)
- `MIGSTOCK` : Stock de migrants
- `HOSTGDP` : PIB des pays hôtes

---

### 2. 📈 **Séries Temporelles & KPIs**
- **Graphiques interactifs** : Sélection de variables à analyser
- **KPIs** : Moyenne, écart-type, min, max par variable
- **Comparaisons multiples** : Variables normalisées (0-1)
- **Analyse de corrélations** : Matrice de corrélations colorée

**Utilité** : Comprendre les tendances et mouvements conjoints des variables

---

### 3. 🧩 **ARDL/ECM – Résultats Complets**

Modèle spécifié : **ARDL(1,2,2,1,3,3,1,3)**

#### 📊 Sous-onglet : Modèle Général
- Coefficients du modèle ARDL complet
- Significativité statistique (p-values colorées)
- Graphique en barres des coefficients

#### 📈 Sous-onglet : Long Terme
- **Relation d'équilibre structurel** entre variables
- Effets permanents sur la variable dépendante
- Interprétation économique des élasticités

**Résultats clés :**
- `logREM` : -5.10 (diminution long terme du PIB si augmentation des transferts, effet indirect)
- `logOPEN` : +27.75 (fortement positif - ouverture commerciale crucial)
- `logTC` : -36.45 (dépréciation du FCFA affecte négativement)

#### 📉 Sous-onglet : Court Terme (ECM)
- **Dynamique d'ajustement** vers l'équilibre long terme
- Vitesse de correction d'erreur (ECT)
- Effets immédiats des chocs (Δ variables)

**Interprétation :** ECT < 0 indique convergence vers l'équilibre

#### 🔬 Sous-onglet : Test de Pesaran Bounds
- **F-statistic** : 5.3808
- **Seuil critique 5% I(1)** : 4.163
- **Résultat** : ✅ **Cointégration détectée** (F > I(1))

**Implication** : Relation long terme stable et exploitable

#### 📋 Sous-onglet : Diagnostics
- Wilcoxon & t-test : Moyenne des résidus = 0 ✓
- ARCH LM : Pas d'hétéroscédasticité ✓
- Box-Pierce & Ljung-Box : Pas d'autocorrélation ✓
- Lilliefors & Shapiro-Wilk : Normalité ✓

**Conclusion** : Modèle bien spécifié

---

### 4. 🔁 **Causalité de Granger**

Test d'ordre 3 sur chaque variable exogène vers GROWTH

**Résultats au seuil 5% :**
- ✅ **logOPEN** (p = 0.01461) → Causalité significative
- ⚠️ **logINV, logTC** (p < 0.1) → Causalité marginale

**Interprétation** : L'ouverture commerciale cause-t-elle Granger la croissance ?

---

### 5. 🧠 **Système 3SLS (4 Équations Simultanées)**

**Méthode** : Three-Stage Least Squares (endogénéité traitée)

#### Équation 1: Remittances (logREM)
```
logREM ~ GROWTH + MIGSTOCK + HOSTGDP + logTC
```
**Résultat clé** : 🔴 **GROWTH = -0.0497*** (très significatif)
- Transferts contracycliques (motif d'assurance)
- Familles envoient plus en temps de crise économique

#### Équation 2: Croissance (GROWTH)
```
GROWTH ~ logREM + logINV + OPEN + logFDI + logTC
```
**Résultat clé** : 🟢 **OPEN = 0.4264*** (très significatif)
- **Variable la plus importante** pour la croissance
- Ouverture commerciale stimule 0.43 points de croissance/pt

#### Équation 3: Investissement (logINV)
```
logINV ~ logREM + CREDIT + GROWTH + INF
```
**Résultat clé** : 🟢 **CREDIT = 0.1364** (significatif, p=0.033)
- Accès au crédit stimule l'investissement
- Canal financier actif

#### Équation 4: Ouverture (OPEN)
```
OPEN ~ logREM + GROWTH + logINV + HOSTGDP
```
**Résultat clé** : 🟢 **GROWTH = 2.3959** (significatif, p=0.006)
- Croissance élargit naturellement le commerce

---

### 6. 🎛️ **Scénarios & Simulation**

**Simulez l'impact sur GROWTH** en utilisant les coefficients 3SLS équation (2)

**Formule** :
```
ΔGrowth = β₁·ΔOPEN + β₂·Δ(logREM) + β₃·Δ(logINV) + β₄·Δ(logFDI) + β₅·Δ(logTC)
```

**Paramètres interactifs** :
- OPEN : +/- 30 points
- REM, INV, FDI : +/- 50 à 80%
- TC : +/- 30%

**Exemple** : 
- Si OPEN +10pts → GROWTH +4.26 points
- Si REM +10% → GROWTH +0.69 points (limité)

---

### 7. ⬇️ **Export des Résultats**

Télécharge **tous les tableaux en Excel** :
- Équations 3SLS (4 feuilles)
- Résultats ARDL
- Tests de diagnostics
- Résultats Granger

Fichier : `ARDL_3SLS_Resultats_YYYYMMDD.xlsx`

---

## 🎨 Caractéristiques de l'Interface

### Styling Professionnel
- ✨ **Palette de couleurs cohérente** : Bleu, Orange, Vert, Mauve
- 📊 **Tables color-codées** :
  - 🟢 Vert = Coefficient positif
  - 🔴 Rouge = Coefficient négatif
  - Intensité = Magnitude
- 📈 **Graphiques interactifs** Plotly avec zoom/pan
- 🔍 **Hover pour détails** sur tous les graphiques

### Expérience Utilisateur
- ⚡ **Chargement rapide** (cache streamlit)
- 📱 **Responsive design** (desktop/mobile)
- 🎯 **Navigation intuitive** (onglets clairs)
- 📥 **Import de données** facile (upload ou base.xlsx)

---

## 📈 Interprétations Économiques

### Remittances (Équation 1)
- **Contracycliques** (GROWTH < 0) → Fonction d'assurance
- Diminuent si économie locale s'améliore
- Affectées par conditions pays hôtes (HOSTGDP < 0)
- Sensibles au taux de change (logTC < 0)

### Croissance (Équation 2)
- **Ouverture commerciale est CLEF** (OPEN >> autres)
- Transferts pas d'effet direct (canal indirect probable)
- Compétitivité (TC) aide légèrement

### Investissement (Équation 3)
- **Crédit crucial** pour former capital
- Croissance renforce confiance (GROWTH > 0)
- Transferts → consommation, pas investissement

### Ouverture (Équation 4)
- **Croissance → Échanges** (feedback positif)
- Boucle d'expansion économique

---

## 🔬 Méthodologie Statistique

### ARDL/ECM
- **Avantage** : Flexibilité sur ordres de retard
- **Test** : Pesaran Bounds pour cointégration
- **Résultat** : F = 5.38 > I(1) → Cointégration ✓

### 3SLS
- **Avantage** : Traite endogénéité simultanée
- **Système** : 4 équations interconnectées
- **Efficacité** : Meilleur que OLS/2SLS

### Diagnostics
- ✓ Résidus ~ bruit blanc
- ✓ Pas d'autocorrélation (Ljung-Box)
- ✓ Pas d'hétéroscédasticité (ARCH)
- ✓ Normalité acceptable (Shapiro-Wilk)

---

## 💻 Données Requises

**Format Excel** : Une feuille avec colonnes :
```
year, GROWTH, REM, TC, FDI, OPEN, CREDIT, INV, INF, MIGSTOCK, HOSTGDP
```

**Placement** :
- Même dossier que `app.py` → nommé `base.xlsx` (auto-charge)
- Ou téléverser via interface

---

## 🛠️ Dépannage

| Problème | Solution |
|----------|----------|
| App ne démarre pas | `pip install -r requirements.txt` ou réinstaller dépendances |
| Données non trouvées | Placer `base.xlsx` au même niveau que `app.py` |
| Tables mal affichées | Actualiser navigateur (F5) |
| Export Excel échoue | Vérifier droits d'écriture du dossier |

---

## 📚 Références

**Méthodes** :
- Pesaran, M.H., Shin, Y., & Smith, R.J. (2001). ARDL bounds testing
- Zellner, A. (1962). Three-stage least squares

**Économie des migrations** :
- Rapoport & Docquier (2006). Transferts de fonds et développement

---

## 📝 Licence & Auteur

**Projet** : Étude des Modèles ARDL/ECM et Systèmes d'Équations Simultanées (3SLS)  
**Données** : Tchad 1995–2022  
**Année** : 2026

---

## 📧 Support

Pour questions/améliorations :
- GitHub Issues : [Projet-de-Modèles-Équations-Simultanées](https://github.com/AssaAllo/Projet-de-Modèles-Équations-Simultanées-et-Correction-d-Erreur)
- Dashboard : `streamlit run app.py`

---

## ✨ Dernières Améliorations (v3.0)

- ✅ Interface professionnelle avec couleurs cohérentes
- ✅ Tables color-codées par significativité
- ✅ Graphiques en barres pour coefficients
- ✅ Sous-onglets ARDL pour clarté
- ✅ Scénarios interactifs dynamiques
- ✅ Export Excel complet
- ✅ Diagnostics automatisés
- ✅ Causalité Granger intégrée