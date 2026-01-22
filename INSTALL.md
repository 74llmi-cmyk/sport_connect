# 🚀 Guide d'Installation - Sport Connect

Ce guide vous aidera à installer et démarrer l'application Sport Connect sur votre machine après avoir cloné le dépôt.

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :
- **Python 3.7 ou supérieur** installé sur votre machine
  - Vérifiez avec : `python --version`
- **Git** (pour cloner le dépôt)
- Un navigateur web moderne (Chrome, Firefox, Edge, Safari)

---

## 🔧 Installation Étape par Étape

### Étape 1 : Cloner le dépôt (déjà fait ✓)

```bash
git clone https://github.com/jedeth/sport_connect.git
cd sport_connect
```

### Étape 2 : Créer un environnement virtuel Python

**Sur Windows :**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Sur macOS/Linux :**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

✅ **Vous devriez voir** `(.venv)` apparaître au début de votre ligne de commande.

### Étape 3 : Installer les dépendances Python

```bash
pip install -r requirements.txt
```

Cette commande installe automatiquement :
- Flask 3.1.2
- Flask-Login 0.6.3
- Werkzeug
- Jinja2
- Et toutes les autres dépendances

⏱️ **Temps estimé :** 1-2 minutes

### Étape 4 : Initialiser la base de données

**A. Créer la structure de base :**
```bash
python migrations/init_db.py
```

**B. Ajouter la géolocalisation (pour la carte) :**
```bash
python migrations/add_geolocation.py
```

✅ **Vous devriez voir** des messages de confirmation :
```
✓ Table 'users' créée avec succès
✓ Table 'participations' créée avec succès
✓ Colonne 'latitude' ajoutée
✓ Colonne 'longitude' ajoutée
```

### Étape 5 : Lancer l'application

```bash
python app.py
```

✅ **Vous devriez voir** :
```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
```

### Étape 6 : Accéder à l'application

Ouvrez votre navigateur et allez à :
```
http://127.0.0.1:5000
```
ou
```
http://localhost:5000
```

---

## 🎯 Premiers Pas

### 1. Créer un compte

- Sur la page d'accueil, cliquez sur **"Inscrivez-vous ici"**
- Remplissez le formulaire (username, mot de passe)
- Vous serez automatiquement connecté après l'inscription

### 2. Explorer l'application

- **🏃 Activités** : Liste de tous les événements sportifs
- **🗺️ Carte** : Visualisation géographique des événements
- **➕ Proposer** : Créer un nouvel événement sportif
- **👤 Profil** : Voir vos statistiques et historique

### 3. Créer votre premier événement

1. Cliquez sur **"+ Proposer une activité"**
2. Remplissez le formulaire :
   - Choisissez un sport
   - Définissez le niveau
   - Indiquez le lieu
   - Ajoutez la date et l'heure
   - **Optionnel** : Géolocalisez l'événement (cliquez sur 📍 ou choisissez une ville)
3. Validez : vous gagnez **+20 points** !

---

## ⚙️ Configuration Avancée (Optionnel)

### Changer le port de l'application

Éditez `app.py` ligne 441 :
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

Changez `5000` par le port désiré.

### Changer la clé secrète

Éditez `app.py` ligne 11 :
```python
app.config['SECRET_KEY'] = 'votre-cle-secrete-a-changer-en-production-sft2026'
```

⚠️ **Important** : Changez cette clé en production !

### Mode Debug

Pour désactiver le mode debug (en production), éditez `app.py` ligne 441 :
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

---

## 🛑 Arrêter l'application

Dans le terminal où l'application tourne, appuyez sur :
```
Ctrl + C
```

---

## 🔄 Mettre à jour l'application

Si des modifications ont été faites sur le dépôt :

```bash
# 1. Récupérer les dernières modifications
git pull

# 2. Mettre à jour les dépendances (si requirements.txt a changé)
pip install -r requirements.txt

# 3. Exécuter les nouvelles migrations (si nécessaire)
python migrations/[nouvelle_migration].py

# 4. Relancer l'application
python app.py
```

---

## ❓ Résolution de Problèmes

### Problème : "python n'est pas reconnu"

**Solution :** Ajoutez Python au PATH de votre système ou utilisez `py` au lieu de `python` sur Windows.

### Problème : "Module 'flask' introuvable"

**Solution :**
1. Vérifiez que l'environnement virtuel est activé (vous devez voir `.venv` dans le terminal)
2. Réinstallez les dépendances : `pip install -r requirements.txt`

### Problème : "Address already in use" (port 5000 occupé)

**Solutions :**
1. Arrêtez l'autre application qui utilise le port 5000
2. Ou changez le port dans `app.py` (voir Configuration Avancée)

### Problème : "Database is locked"

**Solution :**
1. Fermez toutes les instances de l'application
2. Si nécessaire, supprimez `database.db` et relancez les migrations

### Problème : La carte ne s'affiche pas

**Solution :**
1. Vérifiez votre connexion Internet (OpenStreetMap nécessite Internet)
2. Désactivez les bloqueurs de publicités qui pourraient bloquer Leaflet.js
3. Videz le cache de votre navigateur

---

## 📦 Structure du Projet

```
sport_connect/
├── app.py                      # Application Flask principale
├── models.py                   # Modèles de données (User, gamification)
├── requirements.txt            # Dépendances Python
├── database.db                 # Base de données SQLite (créée automatiquement)
├── INSTALL.md                  # Ce fichier
├── README.md                   # Documentation générale
│
├── migrations/                 # Scripts de migration de base de données
│   ├── init_db.py             # Migration initiale
│   └── add_geolocation.py     # Ajout de la géolocalisation
│
├── static/                     # Fichiers statiques
│   ├── logo.png               # Logo de l'application
│   ├── style.css              # Styles CSS personnalisés
│   └── main.js                # Scripts JavaScript
│
└── templates/                  # Templates HTML
    ├── base.html              # Template de base
    ├── index.html             # Page d'accueil (liste des activités)
    ├── add.html               # Formulaire de création d'événement
    ├── login.html             # Page de connexion
    ├── register.html          # Page d'inscription
    ├── profile.html           # Page de profil utilisateur
    └── map.html               # Carte interactive
```

---

## 🎓 Fonctionnalités Principales

### ✅ Déjà Implémentées

- **Authentification** : Inscription, connexion, déconnexion
- **Gamification** : Points, niveaux, barres de progression
- **Événements** : Créer, rejoindre, quitter, annuler
- **Filtres** : Par sport, niveau, lieu
- **Carte interactive** : Visualisation géographique avec OpenStreetMap
- **Profil utilisateur** : Statistiques, historique
- **Design responsive** : Compatible mobile et desktop

### 🚧 En Développement (Roadmap)

- Notifications en temps réel
- Messagerie intégrée (chat de groupe)
- Calendrier interactif
- Upload d'avatar personnalisé
- Système d'amis
- API REST pour application mobile

---

## 💡 Conseils pour le Développement

### Variables d'environnement

Pour une meilleure sécurité, créez un fichier `.env` :
```
SECRET_KEY=votre-cle-tres-securisee
DEBUG=True
DATABASE_URL=sqlite:///database.db
```

### Tests

Pour tester rapidement sans créer de compte à chaque fois :
1. Créez un utilisateur de test : `testuser` / `test123`
2. Créez quelques événements géolocalisés
3. Testez les différentes fonctionnalités

### Base de données de démonstration

Si vous voulez repartir de zéro :
```bash
# Supprimer la base de données
rm database.db  # Linux/Mac
del database.db  # Windows

# Recréer
python migrations/init_db.py
python migrations/add_geolocation.py
```

---

## 📞 Support

**Problème technique ?**
- Consultez la section "Résolution de Problèmes" ci-dessus
- Vérifiez les logs dans le terminal où l'application tourne
- Ouvrez une issue sur le dépôt GitHub

**Questions sur les fonctionnalités ?**
- Consultez le README.md
- Consultez la maquette dans `doc_de_travail/Doc3.pdf`

---

## ✨ Bon développement !

N'hésitez pas à contribuer au projet. Pour toute question, contactez l'équipe SFT 2026.

**Version du guide :** 1.0 (Janvier 2026)
