# Sport Connect

Application web de mise en relation entre personnes souhaitant pratiquer des activités sportives ensemble, propulsée par l'IA.

## Description

Sport Connect est une plateforme web innovante permettant aux utilisateurs de proposer et de rejoindre des activités sportives. L'application facilite la création de groupes sportifs, encourage l'engagement à travers un système de gamification complet, et intègre un **chatbot IA coach sportif** propulsé par l'API Albert (IA de l'État français).

## ⭐ Fonctionnalités principales

### 👤 Authentification & Profils
- **Inscription/Connexion sécurisée** : Système de comptes utilisateurs avec hashage des mots de passe
- **Profil personnalisé** : Avatar avec initiales et couleur unique, statistiques personnelles
- **Tableau de bord** : Vue d'ensemble de vos activités organisées et participations

### 🏃 Gestion des Événements Sportifs
- **Créer une activité** : Formulaire complet avec sport, niveau, lieu, date, genre, accessibilité PMR
- **Lieux prédéfinis** : Base de données de lieux sportifs avec coordonnées GPS et informations transport
- **Géolocalisation** : Affichage des activités sur une carte interactive (Leaflet)
- **Filtres avancés** : Par sport, niveau, lieu, genre
- **Transport en commun** : Informations sur les stations et lignes de métro/RER/tramway à proximité

### 💬 Communication
- **Chat de groupe** : Messagerie en temps réel pour chaque événement
- **Notifications** : Indicateurs de nouveaux messages

### 🎮 Gamification
- **Système de points** :
  - +20 points pour créer un événement
  - +50 points pour rejoindre une activité
  - -10 points pour annuler un événement
- **Niveaux progressifs** : De "Débutant Motivé" (0-99 pts) à "Légende Sportive" (1000+ pts)
- **Barre de progression** : Visualisation en temps réel dans la navbar

### 🤖 **NOUVEAU : Chatbot IA Coach Sport+**
- **Assistant virtuel intelligent** : Expert en activités sportives pour enfants
- **Propulsé par Albert API** : IA de l'État français (modèle openai/gpt-oss-120b - 120 milliards de paramètres)
- **Conseils personnalisés** :
  - Recommandations d'activités adaptées à l'âge et au niveau
  - Conseils nutrition, hydratation, sécurité
  - Explications des règles de sport
  - Motivation et encouragements
- **Interface moderne** : Fenêtre de chat élégante avec animations fluides
- **Accessible depuis la navbar** : Bouton "⚽ Coach" toujours disponible

### 🔧 Administration
- **Panel admin** : Gestion des utilisateurs, événements et lieux
- **Modération** : Annulation d'événements, gestion des permissions
- **Statistiques** : Nombre de participants par événement

## 🛠️ Technologies utilisées

### Backend
- **Flask 3.1.2** : Framework web Python
- **Flask-Login 0.6.3** : Gestion des sessions utilisateurs
- **SQLite** : Base de données relationnelle
- **Requests** : Communication avec l'API Albert
- **Werkzeug** : Sécurité (hashage des mots de passe)

### Frontend
- **Bootstrap 5** : Framework CSS responsive
- **JavaScript ES6** : Interactions dynamiques et AJAX
- **Leaflet** : Cartes interactives
- **HTML5/CSS3** : Interface moderne

### IA & APIs
- **Albert API** : API IA de l'État français (Etalab)
- **Modèle LLM** : openai/gpt-oss-120b (120B paramètres)

## 📁 Structure du projet

```
sport_connect/
├── app.py                          # Application Flask principale
├── models.py                       # Modèles de données (User, Events, Places)
├── config.py                       # Configuration API & secrets (non versionné)
├── config.example.py               # Template de configuration
├── requirements.txt                # Dépendances Python
├── database.db                     # Base de données SQLite
├── .gitignore                      # Fichiers à ignorer (dont config.py)
│
├── static/
│   ├── style.css                   # Styles personnalisés
│   ├── main.js                     # JavaScript (événements, chatbot)
│   └── logo.png                    # Logo de l'application
│
├── templates/
│   ├── base.html                   # Template de base (navbar, chatbot)
│   ├── index.html                  # Dashboard principal
│   ├── login.html                  # Page de connexion
│   ├── register.html               # Page d'inscription
│   ├── profile.html                # Profil utilisateur
│   ├── add.html                    # Formulaire création événement
│   ├── map.html                    # Carte interactive
│   └── admin/
│       ├── places_list.html        # Gestion des lieux
│       ├── place_form.html         # Formulaire lieu
│       ├── events_list.html        # Gestion des événements
│       └── users_list.html         # Gestion des utilisateurs
│
├── migrations/
│   ├── init_db.py                  # Migration initiale
│   ├── add_admin_and_places.py     # Ajout admin et lieux
│   ├── add_geolocation.py          # Ajout géolocalisation
│   └── add_transport.py            # Ajout informations transport
│
├── docs/
│   ├── CHATBOT_README.md           # Documentation du chatbot
│   ├── architecture_sport_connect.drawio    # Schéma d'architecture
│   └── algorigramme_sport_connect.drawio    # Algorigrammes détaillés
│
└── .venv/                          # Environnement virtuel (non versionné)
```

## 🚀 Installation

### Prérequis

- **Python 3.7+** : [Télécharger Python](https://www.python.org/downloads/)
- **pip** : Gestionnaire de paquets Python (inclus avec Python)
- **Compte Albert API** : [S'inscrire sur Albert](https://albert.api.etalab.gouv.fr)

### Étapes d'installation

#### 1. Cloner le projet
```bash
git clone <url-du-repo>
cd sport_connect
```

#### 2. Créer et activer l'environnement virtuel
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

**Dépendances installées** :
- Flask 3.1.2
- Flask-Login 0.6.3
- Werkzeug 3.1.5
- Requests 2.31.0
- Jinja2, MarkupSafe, etc.

#### 4. Configurer l'API Albert

**a) Créer un compte Albert API** :
- Rendez-vous sur https://albert.playground.etalab.gouv.fr/
- Créez un compte
- Générez une clé API dans https://albert.playground.etalab.gouv.fr/keys

**b) Configurer les credentials** :
```bash
# Copier le fichier exemple
cp config.example.py config.py

# Éditer config.py et remplir :
# - ALBERT_API_KEY avec votre clé API
# - Personnaliser CHATBOT_SYSTEM_PROMPT si souhaité
```

**⚠️ IMPORTANT** : Ne versionnez JAMAIS le fichier `config.py` (déjà dans .gitignore)

#### 5. Initialiser la base de données
```bash
# Exécuter les migrations dans l'ordre
python migrations/init_db.py
python migrations/add_admin_and_places.py
python migrations/add_geolocation.py
python migrations/add_transport.py
```

**Compte admin par défaut** :
- Username : `admin`
- Password : `admin123`
- ⚠️ **Changez ce mot de passe en production !**

#### 6. Lancer l'application
```bash
python app.py
```

L'application sera accessible sur **http://localhost:5000**

## 📖 Guide d'utilisation

### Pour les utilisateurs

#### 1. Créer un compte
1. Cliquez sur **"S'inscrire"**
2. Remplissez le formulaire (username, email optionnel, mot de passe)
3. Vous êtes automatiquement connecté

#### 2. Créer une activité sportive
1. Cliquez sur **"➕ Proposer"** dans la navbar
2. Remplissez le formulaire :
   - Sport (Running, Tennis, Football, etc.)
   - Niveau (Débutant, Intermédiaire, Expert)
   - Genre (Mixte, Homme, Femme)
   - Lieu (prédéfini ou personnalisé)
   - Date et heure
   - Accessibilité PMR
   - Géolocalisation (optionnel)
   - Transport en commun (optionnel)
3. Cliquez sur **"Créer l'événement"**
4. **+20 points** sont automatiquement ajoutés à votre compte

#### 3. Rejoindre une activité
1. Sur le **Dashboard**, parcourez les activités disponibles
2. Utilisez les **filtres** pour affiner votre recherche
3. Cliquez sur **"Rejoindre"** sur l'activité souhaitée
4. **+50 points** sont ajoutés à votre compte
5. Accédez au **chat de groupe** pour communiquer avec les participants

#### 4. Utiliser le Chatbot Coach Sport+
1. Cliquez sur le bouton **"⚽ Coach"** dans la navbar
2. Une fenêtre de chat s'ouvre
3. Posez vos questions, exemples :
   - "Quel sport recommandes-tu pour un enfant de 8 ans ?"
   - "Comment bien s'échauffer avant de courir ?"
   - "Quels sont les bienfaits du yoga ?"
   - "Comment rester motivé pour faire du sport ?"
4. Le coach répond avec des conseils personnalisés et encourageants

#### 5. Consulter votre profil
1. Cliquez sur votre **avatar** dans la navbar
2. Sélectionnez **"Mon Profil"**
3. Consultez vos statistiques :
   - Événements organisés
   - Participations
   - Points et niveau
   - Progression

### Pour les administrateurs

#### Accéder au panel admin
1. Connectez-vous avec un compte admin
2. Cliquez sur **"Admin"** dans la navbar
3. Choisissez parmi :
   - **Lieux** : Gérer les lieux de pratique sportive
   - **Activités** : Modérer les événements
   - **Utilisateurs** : Gérer les comptes

#### Gérer les lieux
- **Créer** : Ajoutez des gymnases, stades, parcs avec coordonnées GPS
- **Modifier** : Mettez à jour les informations (transport, PMR, etc.)
- **Activer/Désactiver** : Contrôlez la visibilité des lieux
- **Supprimer** : Supprimez les lieux obsolètes

## 🗄️ Base de données

### Tables principales

#### `users`
| Champ | Type | Description |
|-------|------|-------------|
| id | INTEGER | Identifiant unique (PK) |
| username | TEXT | Nom d'utilisateur (unique) |
| email | TEXT | Email (optionnel) |
| password_hash | TEXT | Mot de passe hashé |
| points | INTEGER | Points de gamification |
| avatar_color | TEXT | Couleur d'avatar (hex) |
| is_admin | INTEGER | Statut admin (0 ou 1) |
| created_at | TIMESTAMP | Date de création |

#### `events`
| Champ | Type | Description |
|-------|------|-------------|
| id | INTEGER | Identifiant unique (PK) |
| organisateur | TEXT | Nom de l'organisateur |
| organizer_id | INTEGER | ID utilisateur organisateur (FK) |
| sport | TEXT | Type de sport |
| niveau | TEXT | Niveau requis |
| genre | TEXT | Genre (Mixte/Homme/Femme) |
| lieu | TEXT | Nom du lieu |
| place_id | INTEGER | ID lieu prédéfini (FK, optionnel) |
| date_heure | TEXT | Date et heure |
| accessibilite | TEXT | PMR (Oui/Non) |
| latitude | REAL | Coordonnée GPS (optionnel) |
| longitude | REAL | Coordonnée GPS (optionnel) |
| transport_station | TEXT | Station de transport (optionnel) |
| transport_lines | TEXT | Lignes de transport (optionnel) |
| is_cancelled | INTEGER | Événement annulé (0 ou 1) |

#### `places`
| Champ | Type | Description |
|-------|------|-------------|
| id | INTEGER | Identifiant unique (PK) |
| name | TEXT | Nom du lieu |
| city | TEXT | Ville |
| address | TEXT | Adresse complète |
| latitude | REAL | Coordonnée GPS |
| longitude | REAL | Coordonnée GPS |
| sports | TEXT | Sports disponibles |
| is_pmr_accessible | INTEGER | Accessible PMR (0 ou 1) |
| is_active | INTEGER | Lieu actif (0 ou 1) |
| transport_station | TEXT | Station proche |
| transport_lines | TEXT | Lignes de transport |
| image_url | TEXT | URL image (optionnel) |

#### `participations`
| Champ | Type | Description |
|-------|------|-------------|
| id | INTEGER | Identifiant unique (PK) |
| user_id | INTEGER | ID utilisateur (FK) |
| event_id | INTEGER | ID événement (FK) |
| points_awarded | INTEGER | Points attribués (50) |
| joined_at | TIMESTAMP | Date d'inscription |

#### `messages`
| Champ | Type | Description |
|-------|------|-------------|
| id | INTEGER | Identifiant unique (PK) |
| event_id | INTEGER | ID événement (FK) |
| user_id | INTEGER | ID utilisateur (FK) |
| username | TEXT | Nom utilisateur |
| content | TEXT | Contenu du message |
| created_at | TIMESTAMP | Date d'envoi |

## 🤖 Chatbot Coach Sport+

### Modèles LLM disponibles (API Albert)

| Modèle | Paramètres | Contexte Max | Usage |
|--------|-----------|--------------|-------|
| **openai/gpt-oss-120b** ⭐ | 120B | 131k tokens | **Utilisé** - Le plus puissant |
| meta-llama/Llama-3.1-8B-Instruct | 8B | 64k tokens | Rapide et léger |
| mistralai/Mistral-Small-3.2-24B-Instruct-2506 | 24B | 128k tokens | Bon compromis |
| Qwen/Qwen2.5-Coder-32B-Instruct-AWQ | 32B | 131k tokens | Expert code |

**Modèle actuel** : `openai/gpt-oss-120b` (120 milliards de paramètres)

### Configuration du chatbot

Le comportement du chatbot peut être personnalisé dans `config.py` :

```python
CHATBOT_SYSTEM_PROMPT = """Tu es Coach Sport+, un assistant virtuel expert en activités sportives pour enfants.

Ton rôle :
- Conseiller les enfants et leurs parents sur les activités sportives
- Encourager la pratique sportive avec un ton positif
- Donner des conseils sur nutrition, hydratation, sécurité
- Expliquer les règles des sports de manière simple

Ton style :
- Langage simple, positif et encourageant
- Enthousiaste et dynamique
- Émojis occasionnels pour rendre la conversation fun
- Concis (3-4 phrases maximum)
"""
```

### Documentation complète
Consultez `CHATBOT_README.md` pour :
- Guide d'utilisation détaillé
- Architecture technique
- Personnalisation du prompt
- Dépannage

## 🎨 Design & UX

- **Responsive** : Optimisé pour desktop, tablette et mobile
- **Couleurs** : Palette moderne avec dégradés violets/bleus
- **Animations** : Transitions fluides, indicateurs de chargement
- **Accessibilité** : Support des lecteurs d'écran, contrastes WCAG

## 🔐 Sécurité

- **Mots de passe hashés** : Werkzeug (generate_password_hash)
- **Sessions sécurisées** : Flask-Login avec secret key
- **Protection CSRF** : Tokens pour les formulaires
- **SQL Injection** : Requêtes paramétrées
- **XSS** : Échappement automatique avec Jinja2
- **Clés API protégées** : Fichier `config.py` dans .gitignore

## 📊 Documentation technique

### Schémas disponibles

- **architecture_sport_connect.drawio** : Architecture complète du système
  - Frontend / Backend / Base de données
  - API externe (Albert)
  - Flux de données

- **algorigramme_sport_connect.drawio** : 5 algorigrammes détaillés
  1. Authentification
  2. Création d'événement
  3. Participation événement
  4. Chatbot Coach Sport+
  5. Vue d'ensemble

Ouvrez ces fichiers avec [draw.io](https://app.diagrams.net/)

## 🐛 Dépannage

### Le chatbot ne répond pas
1. Vérifiez que `config.py` existe et contient votre clé API Albert
2. Vérifiez les logs Flask pour voir les erreurs
3. Testez la clé API :
   ```bash
   curl -H "Authorization: Bearer VOTRE_CLE" https://albert.api.etalab.gouv.fr/v1/models
   ```

### Erreur "Model not found"
- Vérifiez que le modèle dans `app.py` existe (ligne ~857)
- Modèles disponibles : voir section "Modèles LLM disponibles"

### Base de données corrompue
```bash
# Supprimer et recréer
rm database.db
python migrations/init_db.py
python migrations/add_admin_and_places.py
```

### Problèmes d'installation
```bash
# Réinstaller les dépendances
pip install --force-reinstall -r requirements.txt
```

## 🚀 Déploiement en production

### Checklist avant déploiement

- [ ] Changer `SECRET_KEY` dans `config.py`
- [ ] Changer le mot de passe admin par défaut
- [ ] Configurer un serveur WSGI (Gunicorn, uWSGI)
- [ ] Utiliser une vraie base de données (PostgreSQL, MySQL)
- [ ] Configurer HTTPS
- [ ] Mettre en place des sauvegardes
- [ ] Activer les logs de production
- [ ] Rate limiting sur l'API

### Exemple de déploiement avec Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 📈 Évolution future

### Fonctionnalités prévues
- [ ] Notifications push en temps réel (WebSockets)
- [ ] Système de notation des événements
- [ ] Export calendrier (iCal)
- [ ] Application mobile (React Native)
- [ ] Paiements en ligne pour événements payants
- [ ] Statistiques avancées pour les utilisateurs
- [ ] Chatbot multilingue
- [ ] Recommandations IA d'événements personnalisées

### Améliorations techniques
- [ ] Migration vers PostgreSQL
- [ ] Cache avec Redis
- [ ] API REST complète
- [ ] Tests unitaires et d'intégration
- [ ] CI/CD avec GitHub Actions
- [ ] Containerisation avec Docker

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📞 Contact & Support

- **Email** : etalab@modernisation.gouv.fr (pour questions sur Albert API)
- **Issues GitHub** : [Créer un ticket](https://github.com/votre-repo/issues)
- **Documentation Albert** : https://albert.api.etalab.gouv.fr/reference

## 📜 Licence

Ce projet est un MVP (Minimum Viable Product) développé à des fins éducatives et de démonstration dans le cadre de l'initiative **Sove For Tomorrow (SFT) 2026**.

## 🏆 Remerciements

- **Etalab** pour l'API Albert
- **Bootstrap** pour le framework CSS
- **Leaflet** pour les cartes interactives
- **Flask** pour le framework web Python
- L'équipe **Sove For Tomorrow 2026**

---

**Développé avec ❤️ pour encourager le sport chez les jeunes**

*Sport Connect - Sove For Tomorrow 2026*
