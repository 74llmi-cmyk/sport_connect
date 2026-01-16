# Sport Connect

Application web de mise en relation entre personnes souhaitant pratiquer des activités sportives ensemble.

## Description

Sport Connect est une plateforme web permettant aux utilisateurs de proposer et de rejoindre des activités sportives. L'application facilite la création de groupes sportifs et encourage l'engagement à travers un système de gamification.

## Fonctionnalités

- **Proposer une activité sportive** : Les utilisateurs peuvent créer des annonces pour organiser des activités
- **Consulter les activités disponibles** : Affichage de toutes les activités proposées avec leurs détails
- **Rejoindre un groupe** : Mise en relation instantanée avec les organisateurs
- **Système de gamification** : Points, niveaux et progression pour encourager la participation
- **Accessibilité** : Filtrage des activités accessibles aux personnes à mobilité réduite

## Technologies utilisées

- **Backend** : Flask (Python)
- **Base de données** : SQLite
- **Frontend** : Bootstrap 5, HTML5, JavaScript
- **Design** : Interface responsive et moderne

## Structure du projet

```
sport_connect/
├── app.py                 # Application Flask principale
├── database.db            # Base de données SQLite
├── static/
│   └── logo.png          # Logo de l'application
├── templates/
│   ├── index.html        # Page d'accueil avec liste des activités
│   └── add.html          # Formulaire d'ajout d'activité
└── venv/                 # Environnement virtuel Python
```

## Installation

### Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Cloner le projet :
```bash
git clone <url-du-repo>
cd sport_connect
```

2. Créer et activer un environnement virtuel :
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install flask
```

4. Lancer l'application :
```bash
python app.py
```

5. Accéder à l'application :
Ouvrir un navigateur et aller à l'adresse : `http://localhost:5000`

## Utilisation

### Proposer une activité

1. Cliquer sur le bouton "Proposer une activité" sur la page d'accueil
2. Remplir le formulaire avec les informations suivantes :
   - Votre prénom (organisateur)
   - Sport proposé (Running, Tennis, Yoga, Football)
   - Niveau attendu (Débutant, Intermédiaire, Expert)
   - Lieu et horaire
   - Option d'accessibilité PMR/Handicap
3. Cliquer sur "Publier l'annonce"

### Rejoindre une activité

1. Parcourir les activités disponibles sur la page d'accueil
2. Cliquer sur "Rejoindre le groupe" sur l'activité souhaitée
3. Un système de chat de groupe sera ouvert pour communiquer avec l'organisateur
4. Gagner des points de gamification pour chaque participation

## Base de données

La base de données SQLite contient une table `events` avec les champs suivants :

| Champ | Type | Description |
|-------|------|-------------|
| id | INTEGER | Identifiant unique (clé primaire auto-incrémentée) |
| organisateur | TEXT | Nom de l'organisateur |
| sport | TEXT | Type de sport |
| niveau | TEXT | Niveau requis |
| lieu | TEXT | Lieu de l'activité |
| date_heure | TEXT | Date et heure de l'activité |
| accessibilite | TEXT | Indicateur d'accessibilité PMR |

## Système de gamification

L'application intègre un système de gamification simulé comprenant :
- **Points** : Gagner 50 points en rejoignant une activité
- **Niveaux** : Progression de "Explorateur Sportif" à "Athlète confirmé"
- **Barre de progression** : Visualisation de l'avancement vers le niveau suivant

## Développement futur

Fonctionnalités envisagées :
- Authentification utilisateur
- Système de messagerie intégré
- Notifications en temps réel
- Géolocalisation des activités
- Système de notation et avis
- Application mobile
- Intégration d'API de paiement pour activités payantes

## Contexte du projet

Ce projet a été développé dans le cadre de l'initiative **Sove For Tomorrow (SFT) 2026**, visant à promouvoir l'activité physique et la création de liens sociaux à travers le sport.

## Licence

Ce projet est un MVP (Minimum Viable Product) développé à des fins éducatives et de démonstration.

## Auteur

Développé dans le cadre du projet Sove For Tomorrow - MVP 2026
