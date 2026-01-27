"""
Modèles de données pour Sport Connect
Contient la classe User et les fonctions utilitaires
"""

from flask_login import UserMixin
import sqlite3


class User(UserMixin):
    """Classe utilisateur pour Flask-Login"""

    def __init__(self, id, username, email, points, avatar_color, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.points = points
        self.avatar_color = avatar_color
        self.is_admin = is_admin

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
            avatar_color=user_data['avatar_color'],
            is_admin=bool(user_data['is_admin']) if 'is_admin' in user_data.keys() else False
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


# ===========================
# FONCTIONS CRUD POUR PLACES
# ===========================

def get_all_places(active_only=True):
    """
    Récupère tous les lieux de pratique sportive

    Args:
        active_only (bool): Si True, ne retourne que les lieux actifs

    Returns:
        list: Liste de dictionnaires représentant les lieux
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if active_only:
        c.execute("SELECT * FROM places WHERE is_active = 1 ORDER BY city, name")
    else:
        c.execute("SELECT * FROM places ORDER BY city, name")

    places = [dict(row) for row in c.fetchall()]
    conn.close()

    return places


def get_place_by_id(place_id):
    """
    Récupère un lieu par son ID

    Args:
        place_id (int): ID du lieu

    Returns:
        dict: Données du lieu ou None si non trouvé
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM places WHERE id = ?", (place_id,))
    place = c.fetchone()
    conn.close()

    return dict(place) if place else None


def create_place(name, city, address=None, latitude=None, longitude=None,
                 sports=None, is_pmr_accessible=False, transport_station=None,
                 transport_lines=None, image_url=None):
    """
    Crée un nouveau lieu de pratique sportive

    Args:
        name (str): Nom du lieu
        city (str): Ville
        address (str, optional): Adresse complète
        latitude (float, optional): Latitude
        longitude (float, optional): Longitude
        sports (str, optional): Sports disponibles (séparés par virgules)
        is_pmr_accessible (bool): Accessibilité PMR
        transport_station (str, optional): Station de transport la plus proche
        transport_lines (str, optional): Lignes de transport disponibles
        image_url (str, optional): URL de l'image du lieu

    Returns:
        int: ID du nouveau lieu
    """
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO places (name, city, address, latitude, longitude, sports,
                           is_pmr_accessible, transport_station, transport_lines, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, city, address, latitude, longitude, sports,
          1 if is_pmr_accessible else 0, transport_station, transport_lines, image_url))

    place_id = c.lastrowid
    conn.commit()
    conn.close()

    return place_id


def update_place(place_id, name=None, city=None, address=None, latitude=None,
                 longitude=None, sports=None, is_pmr_accessible=None,
                 transport_station=None, transport_lines=None, is_active=None,
                 image_url=None):
    """
    Met à jour un lieu existant

    Args:
        place_id (int): ID du lieu à modifier
        ... (autres args): Champs à mettre à jour

    Returns:
        bool: True si la mise à jour a réussi
    """
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Construire la requête dynamiquement
    updates = []
    params = []

    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if city is not None:
        updates.append("city = ?")
        params.append(city)
    if address is not None:
        updates.append("address = ?")
        params.append(address)
    if latitude is not None:
        updates.append("latitude = ?")
        params.append(latitude)
    if longitude is not None:
        updates.append("longitude = ?")
        params.append(longitude)
    if sports is not None:
        updates.append("sports = ?")
        params.append(sports)
    if is_pmr_accessible is not None:
        updates.append("is_pmr_accessible = ?")
        params.append(1 if is_pmr_accessible else 0)
    if transport_station is not None:
        updates.append("transport_station = ?")
        params.append(transport_station)
    if transport_lines is not None:
        updates.append("transport_lines = ?")
        params.append(transport_lines)
    if is_active is not None:
        updates.append("is_active = ?")
        params.append(1 if is_active else 0)
    if image_url is not None:
        updates.append("image_url = ?")
        params.append(image_url)

    if not updates:
        conn.close()
        return False

    params.append(place_id)
    query = f"UPDATE places SET {', '.join(updates)} WHERE id = ?"

    c.execute(query, params)
    success = c.rowcount > 0

    conn.commit()
    conn.close()

    return success


def delete_place(place_id):
    """
    Supprime un lieu (le désactive plutôt que de le supprimer réellement)

    Args:
        place_id (int): ID du lieu à supprimer

    Returns:
        bool: True si la suppression a réussi
    """
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Désactiver plutôt que supprimer pour préserver les références
    c.execute("UPDATE places SET is_active = 0 WHERE id = ?", (place_id,))
    success = c.rowcount > 0

    conn.commit()
    conn.close()

    return success


def toggle_place_active(place_id):
    """
    Active/désactive un lieu

    Args:
        place_id (int): ID du lieu

    Returns:
        bool: Nouveau statut is_active
    """
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("UPDATE places SET is_active = NOT is_active WHERE id = ?", (place_id,))
    c.execute("SELECT is_active FROM places WHERE id = ?", (place_id,))
    result = c.fetchone()

    conn.commit()
    conn.close()

    return bool(result[0]) if result else None
