"""
Modèles de données pour Sport Connect
Contient la classe User et les fonctions utilitaires
"""

from flask_login import UserMixin
import sqlite3


class User(UserMixin):
    """Classe utilisateur pour Flask-Login"""

    def __init__(self, id, username, email, points, avatar_color):
        self.id = id
        self.username = username
        self.email = email
        self.points = points
        self.avatar_color = avatar_color

    def get_level_info(self):
        """Retourne les informations de niveau basées sur les points"""
        return get_level_info(self.points)

    def get_initials(self):
        """Retourne les initiales de l'utilisateur pour l'avatar"""
        if not self.username:
            return "?"
        parts = self.username.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return self.username[:2].upper()


def get_level_info(points):
    """
    Calcule le niveau et les informations de progression
    basés sur le nombre de points

    Returns:
        dict: {
            'name': nom du niveau,
            'color': couleur Bootstrap,
            'progress': pourcentage de progression (0-100),
            'points': points actuels,
            'next_level': points requis pour le niveau suivant
        }
    """
    levels = [
        {
            "name": "Débutant Sportif",
            "min": 0,
            "max": 100,
            "color": "secondary"
        },
        {
            "name": "Explorateur Sportif",
            "min": 100,
            "max": 200,
            "color": "info"
        },
        {
            "name": "Athlète Confirmé",
            "min": 200,
            "max": 500,
            "color": "warning"
        },
        {
            "name": "Champion Olympique",
            "min": 500,
            "max": 1000,
            "color": "success"
        },
        {
            "name": "Légende du Sport",
            "min": 1000,
            "max": float('inf'),
            "color": "danger"
        }
    ]

    for level in levels:
        if level['min'] <= points < level['max']:
            # Calcul du pourcentage de progression
            if level['max'] == float('inf'):
                progress = 100
            else:
                progress = ((points - level['min']) / (level['max'] - level['min'])) * 100

            return {
                'name': level['name'],
                'color': level['color'],
                'progress': int(progress),
                'points': points,
                'next_level': level['max'] if level['max'] != float('inf') else points
            }

    # Par défaut (ne devrait jamais arriver)
    return {
        'name': 'Débutant Sportif',
        'color': 'secondary',
        'progress': 0,
        'points': 0,
        'next_level': 100
    }


def get_user_by_id(user_id):
    """
    Récupère un utilisateur par son ID

    Args:
        user_id (int): ID de l'utilisateur

    Returns:
        User: Instance de User ou None si non trouvé
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    conn.close()

    if user_data:
        return User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            points=user_data['points'],
            avatar_color=user_data['avatar_color']
        )
    return None


def get_user_by_username(username):
    """
    Récupère un utilisateur par son nom d'utilisateur

    Args:
        username (str): Nom d'utilisateur

    Returns:
        dict: Données de l'utilisateur ou None si non trouvé
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_data = c.fetchone()
    conn.close()

    return dict(user_data) if user_data else None


def create_user(username, password_hash, email=None, avatar_color='#6c757d'):
    """
    Crée un nouvel utilisateur dans la base de données

    Args:
        username (str): Nom d'utilisateur (unique)
        password_hash (str): Hash du mot de passe
        email (str, optional): Email de l'utilisateur
        avatar_color (str): Couleur de l'avatar en hexadécimal

    Returns:
        int: ID du nouvel utilisateur
        None: Si erreur (username déjà existant)
    """
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, password_hash, email, avatar_color) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, avatar_color)
        )
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        # Username déjà existant
        return None


def update_user_points(user_id, points_change):
    """
    Met à jour les points d'un utilisateur

    Args:
        user_id (int): ID de l'utilisateur
        points_change (int): Nombre de points à ajouter (peut être négatif)

    Returns:
        int: Nouveau total de points
    """
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Mise à jour avec MAX pour éviter les points négatifs
    c.execute(
        "UPDATE users SET points = MAX(0, points + ?) WHERE id = ?",
        (points_change, user_id)
    )

    # Récupérer le nouveau total
    c.execute("SELECT points FROM users WHERE id = ?", (user_id,))
    new_points = c.fetchone()[0]

    conn.commit()
    conn.close()

    return new_points
