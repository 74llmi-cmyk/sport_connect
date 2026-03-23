# Sport Connect

Application web de mise en relation entre personnes souhaitant pratiquer des activités sportives ensemble.

## 🚀 Installation Rapide

### Option 1 : Installation Automatique (Recommandée - Windows)

```bash
# 1. Cloner le projet
git clone https://github.com/jedeth/sport_connect.git
cd sport_connect

# 2. Double-cliquer sur setup.bat
# (ou exécuter dans le terminal : setup.bat)

# 3. Double-cliquer sur start.bat pour lancer l'application
```

### Option 2 : Installation Manuelle

```bash
# 1. Cloner le projet
git clone https://github.com/jedeth/sport_connect.git
cd sport_connect

# 2. Créer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Initialiser la base de données
python migrations/init_db.py
python migrations/add_geolocation.py

# 5. Lancer l'application
python app.py
```

**📖 Pour plus de détails, consultez [INSTALL.md](INSTALL.md)**

---

## Description

Sport Connect est une plateforme web permettant aux utilisateurs de proposer et de rejoindre des activités sportives. L'application facilite la création de groupes sportifs et encourage l'engagement à travers un système de gamification complet.

## ✨ Fonctionnalités

### 🔐 Authentification & Profil
- **Inscription / Connexion** : Système d'authentification sécurisé avec Flask-Login
- **Profil utilisateur** : Avatar avec initiales colorées, statistiques détaillées
- **Historique** : Suivi des événements organisés et participations

### 🎮 Système de Gamification
- **Points** : Gagnez des points en créant et rejoignant des événements
  - +50 pts : Rejoindre un événement
  - +20 pts : Créer un événement
  - -50 pts : Quitter un événement
- **Niveaux** : Progression à travers 5 niveaux (Débutant → Légende du Sport)
- **Barre de progression** : Visualisation en temps réel de votre avancement

### 🏃 Gestion des Événements
- **Créer des activités** : Formulaire complet avec géolocalisation
- **Consulter les activités** : Liste filtrée et carte interactive
- **Rejoindre un groupe** : Participation en un clic avec AJAX
- **Annuler des événements** : Les organisateurs peuvent annuler leurs événements
- **Filtres intelligents** : Par sport, niveau, lieu

### 🗺️ Carte Interactive
- **Visualisation géographique** : Tous les événements sur une carte OpenStreetMap
- **Marqueurs colorés** :
  - 🔵 Événements disponibles
  - 🟢 Événements auxquels vous participez
  - 🟡 Vos événements organisés
- **Géolocalisation** : Localisez-vous et trouvez les événements à proximité
- **Filtres en temps réel** : Filtrez les marqueurs par sport et niveau
- **Lieux préconfigurés** : Paris, Lyon, Marseille, Nantes, Bordeaux, etc.

### ♿ Accessibilité
- Indication des lieux accessibles PMR (Personnes à Mobilité Réduite)
- Interface responsive pour mobile et desktop
- Design moderne et ergonomique

## 🛠️ Technologies utilisées

### Backend
- **Flask 3.1.2** : Framework web Python
- **Flask-Login 0.6.3** : Gestion des sessions utilisateur
- **SQLite** : Base de données légère et portable
- **Werkzeug** : Sécurité (hashage des mots de passe)

### Frontend
- **Bootstrap 5.3.0** : Framework CSS responsive
- **Leaflet.js 1.9.4** : Bibliothèque de cartographie interactive
- **OpenStreetMap** : Fonds de carte open source
- **JavaScript (Vanilla)** : Interactions AJAX et dynamiques

### Outils
- **Git** : Contrôle de version
- **Python venv** : Environnement virtuel

## 📁 Structure du projet

```
sport_connect/
├── app.py                      # Application Flask principale (441 lignes)
├── models.py                   # Modèles de données et gamification
├── requirements.txt            # Dépendances Python
├── database.db                 # Base de données SQLite (auto-généré)
├── INSTALL.md                  # Guide d'installation détaillé
├── README.md                   # Ce fichier
├── setup.bat                   # Script d'installation automatique (Windows)
├── start.bat                   # Script de démarrage rapide (Windows)
│
├── migrations/                 # Scripts de migration de base de données
│   ├── init_db.py             # Migration initiale (tables users, participations, events)
│   └── add_geolocation.py     # Ajout de la géolocalisation (latitude, longitude)
│
├── static/                     # Fichiers statiques
│   ├── logo.png               # Logo de l'application
│   ├── style.css              # Styles CSS personnalisés (200+ lignes)
│   └── main.js                # Scripts JavaScript (AJAX, filtres)
│
├── templates/                  # Templates HTML (Jinja2)
│   ├── base.html              # Template de base avec navbar et gamification
│   ├── index.html             # Page d'accueil (liste des activités avec filtres)
│   ├── add.html               # Formulaire de création d'événement
│   ├── login.html             # Page de connexion
│   ├── register.html          # Page d'inscription
│   ├── profile.html           # Page de profil utilisateur
│   └── map.html               # Carte interactive avec Leaflet.js
│
└── doc_de_travail/            # Documentation de travail
    └── Doc3.pdf               # Maquette de l'interface utilisateur
```

## 🗄️ Base de données

### Schéma

**Table `users`**
- `id` : Identifiant unique (PRIMARY KEY)
- `username` : Nom d'utilisateur (UNIQUE)
- `password_hash` : Mot de passe hashé
- `email` : Email (optionnel)
- `points` : Total de points gamification
- `avatar_color` : Couleur de l'avatar
- `created_at` : Date de création

**Table `events`**
- `id` : Identifiant unique
- `organisateur` : Nom de l'organisateur (legacy)
- `organizer_id` : ID de l'organisateur (FK vers users)
- `sport` : Type de sport
- `niveau` : Niveau requis (Débutant, Intermédiaire, Expert)
- `lieu` : Lieu textuel
- `latitude` / `longitude` : Coordonnées GPS (optionnelles)
- `date_heure` : Date et heure de l'événement
- `accessibilite` : Accessible PMR (Oui/Non)
- `is_cancelled` : Événement annulé (0/1)
- `created_at` : Date de création

**Table `participations`**
- `id` : Identifiant unique
- `user_id` : ID de l'utilisateur (FK vers users)
- `event_id` : ID de l'événement (FK vers events)
- `joined_at` : Date d'inscription
- `points_awarded` : Points attribués (50 par défaut)
- UNIQUE(user_id, event_id) : Empêche les doublons

**5 Index** pour optimiser les requêtes de filtrage.

## 📸 Captures d'écran

### Page d'accueil
- Liste des activités avec filtres intelligents
- Badges de niveau colorés
- Compteur de participants
- Boutons d'action (Rejoindre/Quitter/Annuler)

### Carte Interactive
- Visualisation géographique des événements
- Filtres en temps réel
- Géolocalisation de l'utilisateur
- Popups avec détails des événements

### Profil Utilisateur
- Statistiques (points, événements organisés, participations)
- Barre de progression vers le niveau suivant
- Historique des activités

## 🎓 Utilisation

### Créer un compte

1. Accédez à http://127.0.0.1:5000
2. Cliquez sur **"Inscrivez-vous ici"**
3. Remplissez le formulaire (username, mot de passe)
4. Vous êtes automatiquement connecté

### Proposer une activité

1. Cliquez sur **"+ Proposer une activité"** (navbar ou page d'accueil)
2. Choisissez un sport dans la liste
3. Définissez le niveau requis
4. Indiquez le lieu et la date/heure
5. **Optionnel** : Géolocalisez l'événement
   - Cliquez sur 📍 pour utiliser votre position
   - Ou choisissez une ville dans la liste déroulante
6. Cochez "Accessible PMR" si applicable
7. Validez : **+20 points !**

### Rejoindre une activité

1. Parcourez les activités sur la page d'accueil ou la carte
2. Utilisez les filtres pour affiner votre recherche
3. Cliquez sur **"Rejoindre le groupe"**
4. **+50 points !**
5. Un badge "✓ Vous participez" apparaît

### Consulter son profil

1. Cliquez sur votre avatar (coin supérieur droit)
2. Sélectionnez **"Mon Profil"**
3. Consultez vos statistiques :
   - Total de points
   - Nombre d'événements organisés
   - Nombre de participations
4. Visualisez votre historique dans les onglets

### Utiliser la carte

1. Cliquez sur **"🗺️ Carte"** dans la navbar
2. Explorez les événements géolocalisés
3. Cliquez sur un marqueur pour voir les détails
4. Utilisez les filtres (sport, niveau)
5. Cliquez sur **"📍 Me localiser"** pour vous centrer sur la carte

## 🎯 Système de Niveaux

| Points | Niveau | Couleur |
|--------|--------|---------|
| 0-99 | Débutant Sportif | Gris |
| 100-199 | Explorateur Sportif | Bleu |
| 200-499 | Athlète Confirmé | Jaune |
| 500-999 | Champion Olympique | Vert |
| 1000+ | Légende du Sport | Rouge |

## 🔧 Développement futur

### Fonctionnalités envisagées

**Phase 2 (Court terme) :**
- 🔔 Notifications en temps réel (WebSockets)
- 💬 Messagerie intégrée (chat de groupe par événement)
- 📅 Calendrier interactif (vue mensuelle)
- 🖼️ Upload d'avatar personnalisé
- ✉️ Vérification email

**Phase 3 (Moyen terme) :**
- 👥 Système d'amis/followers
- ⭐ Évaluations et avis sur les événements
- 🏆 Badges et achievements
- 📊 Statistiques avancées (graphiques)
- 🔍 Recherche avancée full-text

**Phase 4 (Long terme) :**
- 📱 Application mobile (React Native / Flutter)
- 🌐 API REST publique
- 💳 Paiements intégrés (événements payants)
- 🤖 Recommandations ML basées sur l'historique
- 📧 Export iCal/Google Calendar

## 🐛 Résolution de problèmes

### L'application ne démarre pas

**Vérifiez :**
1. Python est installé (`python --version`)
2. L'environnement virtuel est activé (vous voyez `.venv` dans le terminal)
3. Les dépendances sont installées (`pip list`)
4. Les migrations ont été exécutées

**Solution :** Relancez `setup.bat` ou consultez [INSTALL.md](INSTALL.md)

### Port 5000 déjà utilisé

**Solution :**
1. Arrêtez l'autre application sur le port 5000
2. Ou changez le port dans `app.py` ligne 441

### La carte ne s'affiche pas

**Causes possibles :**
- Pas de connexion Internet (OpenStreetMap nécessite Internet)
- Bloqueur de publicités actif
- Cache du navigateur

**Solution :** Désactivez temporairement les bloqueurs, videz le cache

### Erreur "Database is locked"

**Solution :**
```bash
# Arrêtez toutes les instances de l'app
# Puis relancez
python app.py
```

## 🤝 Contribution

Ce projet est développé dans le cadre de l'initiative **Sove For Tomorrow (SFT) 2026**. Les contributions sont les bienvenues !

### Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est un MVP (Minimum Viable Product) développé à des fins éducatives et de démonstration dans le cadre du projet Sove For Tomorrow.

## 👥 Auteurs

Développé dans le cadre du projet **Sove For Tomorrow - MVP 2026**

## 📞 Support

- **Documentation** : Consultez [INSTALL.md](INSTALL.md) pour l'installation
- **Issues** : Ouvrez une issue sur GitHub pour signaler un bug
- **Maquette** : Voir `doc_de_travail/Doc3.pdf`

---

**Version :** 2.0 (Janvier 2026)

**Technologies :** Flask + SQLite + Bootstrap + Leaflet.js

**Licence :** Projet éducatif SFT 2026
