# 🚀 Guide de Déploiement sur Render

## ✅ Prérequis pour le Déploiement

- ✅ Compte GitHub avec accès au dépôt
- ✅ Compte Render.com (inscription gratuite)
- ✅ Tous les fichiers pushés vers GitHub (`main` branch)

---

## 📋 Fichiers de Configuration Inclus

| Fichier | Fonction |
|---------|----------|
| `render.yaml` | Configuration Render (auto-détection) |
| `requirements.txt` | Dépendances Python |
| `app.py` | Application Streamlit principale |
| `README.md` | Documentation complète |

---

## 🌐 Étapes de Déploiement sur Render

### Étape 1 : Vérifier le statut GitHub
```bash
git status
git log --oneline  # Vérifier les commits
```
✅ Les 3 commits doivent être pushés :
- "Add deployment config and update README..."
- "Add .gitignore for clean repository"

### Étape 2 : Connexion à Render

1. Aller sur [render.com](https://render.com)
2. Cliquer **"Sign up"** (GitHub OAuth recommandé)
3. Autoriser Render à accéder à vos dépôts GitHub

### Étape 3 : Créer un nouveau Web Service

1. Dashboard Render → **"New +"** → **"Web Service"**
2. Sélectionner le dépôt : `Projet-de-Modèles-Équations-Simultanées-et-Correction-d-Erreur`
3. Connecter le dépôt à Render (autoriser accès)

### Étape 4 : Configuration Automatique

Les paramètres suivants seront **auto-détectés** depuis `render.yaml` :

| Paramètre | Valeur |
|-----------|--------|
| **Name** | ProjetMES-Dashboard |
| **Environment** | Python |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0` |
| **Python Version** | 3.11 |
| **Plan** | Free |

### Étape 5 : Déployer

1. Cliquer **"Create Web Service"**
2. ⏳ Attendre 2-3 minutes (logs affichés en temps réel)
3. 🎉 Une URL publique sera générée : `https://votre-app.onrender.com`

---

## 🔗 URL de Déploiement

Une fois déployé, votre dashboard sera accessible à :
```
https://projet-mes-[random].onrender.com
```

---

## ⚙️ Variables d'Environnement (Optionnelles)

Pour plus de contrôle, vous pouvez ajouter dans Render :

```
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=$PORT
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

Ces variables sont déjà configurées dans `render.yaml` ✅

---

## 📁 Gestion des Données sur Render

### Option 1 : Utiliser base.xlsx du dépôt (RECOMMANDÉE)
- Ajouter `base.xlsx` au dépôt Git
- L'app le chargera automatiquement au démarrage
- ✅ Données versionnées et persistantes

### Option 2 : Upload via interface Streamlit
- Laisser `base.xlsx` absent
- Les utilisateurs uploadent un fichier Excel
- ⚠️ Les données ne sont pas persistantes (rechargement à chaque visite)

### Option 3 : Base de données externe
- Connecter PostgreSQL/MongoDB
- Plus complexe mais recommandé pour production

---

## 🐛 Dépannage

### ❌ Erreur : "render.yaml not found"
**Solution** : Vérifier que `render.yaml` est à la racine du dépôt et pushé

```bash
git ls-files | grep render.yaml  # Doit afficher render.yaml
```

### ❌ Erreur : "ModuleNotFoundError: No module named 'streamlit'"
**Solution** : `requirements.txt` mal formé ou pas pushé

```bash
cat requirements.txt  # Vérifier le contenu
git log --follow -p requirements.txt | head -20  # Vérifier historique
```

### ❌ App démarre mais affiche une erreur
1. Vérifier les **Logs** dans Render (Dashboard → Logs)
2. Chercher `Traceback` ou `ImportError`
3. Ajouter le package manquant à `requirements.txt` et repush

### ❌ App charge mais pas de données
**Solution** : Ajouter `base.xlsx` au dépôt :
```bash
git add base.xlsx
git commit -m "Add data file for deployment"
git push origin main
```

### ❌ Render service "Spinning down"
- **Cause** : Inactivité > 15 minutes (plan free)
- **Solution** : Upgrade vers plan Paid ou redémarrer manuellement
- **URL** : Dashboard Render → Web Service → Manual Deploy

---

## 📊 Monitoring et Logs

Une fois déployé :

1. **Logs en temps réel** : Dashboard Render → Logs (voir requêtes utilisateurs)
2. **Health Check** : Render teste automatiquement `/` de l'app
3. **Auto-restart** : En cas de crash, Render relance le service

---

## 🔄 Mises à Jour et Redéploiement

Pour mettre à jour l'app :

```bash
# Faire des modifications locales
# ...

# Commit et push
git add .
git commit -m "Update: description du changement"
git push origin main
```

**Render redéploiera automatiquement** en quelques minutes ✅

Pour forcer un redéploiement sans changements :
- Dashboard Render → Web Service → "Manual Deploy" → "Latest"

---

## 💰 Coûts

| Plan | Prix | Limite |
|------|------|--------|
| **Free** | $0/mois | Spins down après 15 min inactivité |
| **Starter** | $7/mois | Toujours actif, 400h/mois |
| **Pro** | $12+/mois | Illimité, priorité support |

---

## ✨ Checklist Avant Déploiement

- ✅ `git push origin main` fait ?
- ✅ `requirements.txt` au niveau racine ?
- ✅ `render.yaml` au niveau racine ?
- ✅ `app.py` sans chemins absolus en dur ?
- ✅ Aucune clé API sensible en dur dans le code ?
- ✅ `base.xlsx` versionné (ou utilisateurs uploadent) ?
- ✅ Tous les imports testés localement ?

---

## 🆘 Support

**Problèmes Render** :
- Docs : [render.com/docs](https://render.com/docs)
- Support : help@render.com

**Problèmes Streamlit** :
- Docs : [docs.streamlit.io](https://docs.streamlit.io)
- Community : [discuss.streamlit.io](https://discuss.streamlit.io)

**Problèmes Projet** :
- GitHub Issues : [ProjetMES Repository](https://github.com/AssaAllo/Projet-de-Modèles-Équations-Simultanées-et-Correction-d-Erreur)

---

## 🎉 Succès !

Une fois votre app en ligne, partagez l'URL :
```
Tableau de bord ARDL/ECM + 3SLS : https://votre-app.onrender.com
```

Bonne chance ! 🚀
