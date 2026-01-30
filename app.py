from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import random
import requests

# Import du modèle User et des fonctions places
from models import (User, get_user_by_id, get_user_by_username, create_user, update_user_points,
                    get_all_places, get_place_by_id, create_place, update_place, delete_place,
                    toggle_place_active)

# Import de la configuration
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Configuration Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Charge un utilisateur depuis la base de données par son ID"""
    return get_user_by_id(user_id)


def admin_required(f):
    """Décorateur pour protéger les routes admin"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Accès réservé aux administrateurs.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def init_db():
    """Initialise la base de données avec les tables nécessaires"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  organisateur TEXT,
                  sport TEXT,
                  niveau TEXT,
                  lieu TEXT,
                  date_heure TEXT,
                  accessibilite TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  event_id INTEGER NOT NULL,
                  user_id INTEGER NOT NULL,
                  username TEXT NOT NULL,
                  content TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    conn.commit()
    conn.close()


# ===========================
# ROUTES D'AUTHENTIFICATION
# ===========================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip() or None
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Validation
        if not username or len(username) < 3:
            flash('Le nom d\'utilisateur doit contenir au moins 3 caractères.', 'error')
            return render_template('register.html')

        if not password or len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'error')
            return render_template('register.html')

        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('register.html')

        # Vérifier si le username existe déjà
        if get_user_by_username(username):
            flash('Ce nom d\'utilisateur est déjà pris.', 'error')
            return render_template('register.html')

        # Génération d'une couleur d'avatar aléatoire
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                  '#F06292', '#64B5F6', '#81C784', '#FFB74D', '#BA68C8']
        avatar_color = random.choice(colors)

        # Hachage du mot de passe
        password_hash = generate_password_hash(password)

        # Créer l'utilisateur
        user_id = create_user(username, password_hash, email, avatar_color)

        if user_id:
            # Auto-connexion après inscription
            user = get_user_by_id(user_id)
            login_user(user)
            flash(f'Bienvenue sur Sport Connect, {username} !', 'success')
            return redirect(url_for('index'))
        else:
            flash('Une erreur s\'est produite lors de l\'inscription.', 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'yes'

        # Récupérer l'utilisateur
        user_data = get_user_by_username(username)

        if user_data and check_password_hash(user_data['password_hash'], password):
            # Créer l'objet User et connecter
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                points=user_data['points'],
                avatar_color=user_data['avatar_color'],
                is_admin=bool(user_data.get('is_admin', 0))
            )
            login_user(user, remember=remember)

            # Redirection vers la page demandée ou index
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous êtes maintenant déconnecté.', 'info')
    return redirect(url_for('login'))


# ===========================
# ROUTE PROFIL
# ===========================

@app.route('/profile')
@login_required
def profile():
    """Page de profil utilisateur"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Récupérer les événements organisés par l'utilisateur
    c.execute("""
        SELECT * FROM events
        WHERE organizer_id = ?
        ORDER BY id DESC
    """, (current_user.id,))
    organized_events = c.fetchall()

    # Récupérer les participations
    c.execute("""
        SELECT e.*, p.joined_at, p.points_awarded
        FROM participations p
        JOIN events e ON p.event_id = e.id
        WHERE p.user_id = ?
        ORDER BY p.joined_at DESC
    """, (current_user.id,))
    participated_events = c.fetchall()

    conn.close()

    return render_template('profile.html',
                         organized_events=organized_events,
                         participated_events=participated_events)


# ===========================
# ROUTE PRINCIPALE (INDEX)
# ===========================

@app.route('/')
@login_required
def index():
    """Page d'accueil avec liste des événements et filtres"""
    # Récupérer les filtres depuis l'URL
    sport_filter = request.args.get('sport', '').strip()
    niveau_filter = request.args.get('niveau', '').strip()
    lieu_filter = request.args.get('lieu', '').strip()
    genre_filter = request.args.get('genre', '').strip()

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Construire la requête SQL dynamique
    query = "SELECT * FROM events WHERE is_cancelled = 0"
    params = []

    if sport_filter:
        query += " AND sport = ?"
        params.append(sport_filter)

    if niveau_filter:
        query += " AND niveau = ?"
        params.append(niveau_filter)

    if lieu_filter:
        query += " AND lieu LIKE ?"
        params.append(f'%{lieu_filter}%')

    if genre_filter:
        query += " AND genre = ?"
        params.append(genre_filter)

    query += " ORDER BY id DESC"

    c.execute(query, params)
    events = c.fetchall()

    # Enrichir chaque événement avec des infos supplémentaires
    event_list = []
    for event in events:
        # Compter le nombre de participants
        c.execute("SELECT COUNT(*) as count FROM participations WHERE event_id = ?",
                 (event['id'],))
        participant_count = c.fetchone()['count']

        # Vérifier si l'utilisateur actuel a rejoint
        c.execute("SELECT id FROM participations WHERE event_id = ? AND user_id = ?",
                 (event['id'], current_user.id))
        user_joined = c.fetchone() is not None

        # Récupérer le nom de l'organisateur
        organizer_name = event['organisateur']  # Valeur par défaut
        if event['organizer_id']:
            c.execute("SELECT username FROM users WHERE id = ?", (event['organizer_id'],))
            org = c.fetchone()
            if org:
                organizer_name = org['username']

        event_list.append({
            'event': event,
            'participant_count': participant_count,
            'user_joined': user_joined,
            'organizer_name': organizer_name,
            'is_organizer': event['organizer_id'] == current_user.id
        })

    conn.close()

    # Liste des sports disponibles (hardcodé pour MVP)
    sports_list = ['Running', 'Tennis', 'Yoga', 'Football', 'Natation', 'Basketball', 'Cyclisme']
    niveaux_list = ['Débutant', 'Intermédiaire', 'Expert']
    genres_list = ['Mixte', 'Homme', 'Femme']

    return render_template('index.html',
                         events=event_list,
                         sports_list=sports_list,
                         niveaux_list=niveaux_list,
                         genres_list=genres_list,
                         filters={
                             'sport': sport_filter,
                             'niveau': niveau_filter,
                             'lieu': lieu_filter,
                             'genre': genre_filter
                         })


# ===========================
# ROUTE CARTE INTERACTIVE
# ===========================

@app.route('/map')
@login_required
def map_view():
    """Page de carte interactive avec les événements géolocalisés"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Récupérer tous les événements non annulés avec géolocalisation
    c.execute("SELECT * FROM events WHERE is_cancelled = 0 ORDER BY id DESC")
    events = c.fetchall()

    # Enrichir les événements avec les infos de participation
    event_list = []
    for event in events:
        # Compter les participants
        c.execute("SELECT COUNT(*) as count FROM participations WHERE event_id = ?",
                 (event['id'],))
        participant_count = c.fetchone()['count']

        # Vérifier si l'utilisateur actuel a rejoint
        c.execute("SELECT id FROM participations WHERE event_id = ? AND user_id = ?",
                 (event['id'], current_user.id))
        user_joined = c.fetchone() is not None

        # Récupérer le nom de l'organisateur
        organizer_name = event['organisateur']
        if event['organizer_id']:
            c.execute("SELECT username FROM users WHERE id = ?", (event['organizer_id'],))
            org = c.fetchone()
            if org:
                organizer_name = org['username']

        event_list.append({
            'event': dict(event),
            'participant_count': participant_count,
            'user_joined': user_joined,
            'organizer_name': organizer_name,
            'is_organizer': event['organizer_id'] == current_user.id
        })

    conn.close()

    # Liste des sports pour les filtres
    sports_list = ['Running', 'Tennis', 'Yoga', 'Football', 'Natation', 'Basketball', 'Cyclisme']

    # Convertir en JSON pour JavaScript
    import json
    events_json = json.dumps(event_list)

    return render_template('map.html',
                         events=event_list,
                         events_json=events_json,
                         sports_list=sports_list)


# ===========================
# ROUTE AJOUT D'ÉVÉNEMENT
# ===========================

@app.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    """Créer un nouvel événement"""
    # Récupérer les lieux pour le menu déroulant
    places = get_all_places(active_only=True)

    if request.method == 'POST':
        sport = request.form['sport']
        niveau = request.form['niveau']
        date_heure = request.form['date_heure']
        accessibilite = request.form.get('accessibilite')
        genre = request.form.get('genre', 'Mixte')

        # Gestion du lieu (prédéfini ou personnalisé)
        place_id = request.form.get('place_id')
        lieu_custom = request.form.get('lieu_custom', '').strip()

        # Récupérer les coordonnées et transports
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        transport_station = request.form.get('transport_station', '').strip() or None
        transport_lines = request.form.get('transport_lines', '').strip() or None

        # Si un lieu prédéfini est sélectionné
        if place_id and place_id != 'other':
            place = get_place_by_id(int(place_id))
            if place:
                lieu = place['name'] + (f", {place['city']}" if place['city'] else "")
                # Utiliser les coordonnées et transports du lieu si non renseignés
                if not latitude and place['latitude']:
                    latitude = place['latitude']
                if not longitude and place['longitude']:
                    longitude = place['longitude']
                if not transport_station and place['transport_station']:
                    transport_station = place['transport_station']
                if not transport_lines and place['transport_lines']:
                    transport_lines = place['transport_lines']
                if not accessibilite and place['is_pmr_accessible']:
                    accessibilite = 'Oui'
            else:
                lieu = lieu_custom
                place_id = None
        else:
            lieu = lieu_custom
            place_id = None

        # Convertir en float ou None si vide
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except (ValueError, TypeError):
            latitude = None
            longitude = None

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("""INSERT INTO events
                     (organisateur, sport, niveau, lieu, date_heure, accessibilite, organizer_id, latitude, longitude, transport_station, transport_lines, place_id, genre)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (current_user.username, sport, niveau, lieu, date_heure, accessibilite, current_user.id, latitude, longitude, transport_station, transport_lines, place_id, genre))
        conn.commit()
        conn.close()

        # Ajouter des points pour la création d'événement
        update_user_points(current_user.id, 20)

        flash(f'Événement "{sport}" créé avec succès ! +20 points', 'success')
        return redirect(url_for('index'))

    return render_template('add.html', places=places)


# ===========================
# ROUTES DE PARTICIPATION (AJAX)
# ===========================

@app.route('/event/<int:event_id>/join', methods=['POST'])
@login_required
def join_event(event_id):
    """Rejoindre un événement (API JSON)"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    try:
        # Vérifier que l'événement existe et n'est pas annulé
        c.execute("SELECT is_cancelled, sport FROM events WHERE id = ?", (event_id,))
        event = c.fetchone()

        if not event:
            return jsonify({'success': False, 'message': 'Événement introuvable'}), 404

        if event[0] == 1:  # is_cancelled
            return jsonify({'success': False, 'message': 'Cet événement a été annulé'}), 400

        # Vérifier si déjà inscrit
        c.execute("SELECT id FROM participations WHERE user_id = ? AND event_id = ?",
                 (current_user.id, event_id))
        if c.fetchone():
            return jsonify({'success': False, 'message': 'Vous êtes déjà inscrit à cet événement'}), 400

        # Créer la participation
        points_awarded = 50
        c.execute("INSERT INTO participations (user_id, event_id, points_awarded) VALUES (?, ?, ?)",
                 (current_user.id, event_id, points_awarded))

        conn.commit()

        # Mettre à jour les points de l'utilisateur
        new_points = update_user_points(current_user.id, points_awarded)

        conn.close()

        return jsonify({
            'success': True,
            'message': f'+{points_awarded} points ! Vous avez rejoint {event[1]}',
            'new_points': new_points
        })

    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': 'Vous êtes déjà inscrit'}), 400

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/event/<int:event_id>/leave', methods=['POST'])
@login_required
def leave_event(event_id):
    """Quitter un événement (API JSON)"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    try:
        # Récupérer les points attribués
        c.execute("SELECT points_awarded FROM participations WHERE user_id = ? AND event_id = ?",
                 (current_user.id, event_id))
        participation = c.fetchone()

        if not participation:
            return jsonify({'success': False, 'message': 'Vous n\'êtes pas inscrit à cet événement'}), 400

        points_to_deduct = participation[0]

        # Supprimer la participation
        c.execute("DELETE FROM participations WHERE user_id = ? AND event_id = ?",
                 (current_user.id, event_id))

        conn.commit()

        # Déduire les points
        new_points = update_user_points(current_user.id, -points_to_deduct)

        conn.close()

        return jsonify({
            'success': True,
            'message': f'Participation annulée (-{points_to_deduct} points)',
            'new_points': new_points
        })

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_event(event_id):
    """Annuler un événement (organisateur uniquement) (API JSON)"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    try:
        # Vérifier que l'utilisateur est l'organisateur
        c.execute("SELECT organizer_id, sport FROM events WHERE id = ?", (event_id,))
        event = c.fetchone()

        if not event:
            return jsonify({'success': False, 'message': 'Événement introuvable'}), 404

        if event[0] != current_user.id:
            return jsonify({'success': False, 'message': 'Vous n\'êtes pas l\'organisateur de cet événement'}), 403

        # Marquer comme annulé
        c.execute("UPDATE events SET is_cancelled = 1 WHERE id = ?", (event_id,))

        conn.commit()
        conn.close()

        # Pénalité de points pour annulation
        update_user_points(current_user.id, -10)

        return jsonify({
            'success': True,
            'message': 'Événement annulé (-10 points)'
        })

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500


# ===========================
# ROUTES ADMINISTRATION
# ===========================

@app.route('/admin/places')
@admin_required
def admin_places():
    """Liste des lieux de pratique sportive (admin)"""
    places = get_all_places(active_only=False)
    return render_template('admin/places_list.html', places=places)


@app.route('/admin/places/add', methods=['GET', 'POST'])
@admin_required
def admin_add_place():
    """Ajouter un nouveau lieu (admin)"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city = request.form.get('city', '').strip()
        address = request.form.get('address', '').strip() or None
        sports = request.form.get('sports', '').strip() or None
        is_pmr = request.form.get('is_pmr_accessible') == 'on'
        transport_station = request.form.get('transport_station', '').strip() or None
        transport_lines = request.form.get('transport_lines', '').strip() or None
        image_url = request.form.get('image_url', '').strip() or None

        # Coordonnées
        try:
            latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
            longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
        except (ValueError, TypeError):
            latitude = None
            longitude = None

        if not name or not city:
            flash('Le nom et la ville sont obligatoires.', 'error')
            return render_template('admin/place_form.html', place=None)

        place_id = create_place(
            name=name, city=city, address=address,
            latitude=latitude, longitude=longitude,
            sports=sports, is_pmr_accessible=is_pmr,
            transport_station=transport_station, transport_lines=transport_lines,
            image_url=image_url
        )

        flash(f'Lieu "{name}" créé avec succès !', 'success')
        return redirect(url_for('admin_places'))

    return render_template('admin/place_form.html', place=None)


@app.route('/admin/places/<int:place_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_place(place_id):
    """Modifier un lieu existant (admin)"""
    place = get_place_by_id(place_id)

    if not place:
        flash('Lieu introuvable.', 'error')
        return redirect(url_for('admin_places'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city = request.form.get('city', '').strip()
        address = request.form.get('address', '').strip() or None
        sports = request.form.get('sports', '').strip() or None
        is_pmr = request.form.get('is_pmr_accessible') == 'on'
        transport_station = request.form.get('transport_station', '').strip() or None
        transport_lines = request.form.get('transport_lines', '').strip() or None
        image_url = request.form.get('image_url', '').strip() or None

        # Coordonnées
        try:
            latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
            longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
        except (ValueError, TypeError):
            latitude = None
            longitude = None

        if not name or not city:
            flash('Le nom et la ville sont obligatoires.', 'error')
            return render_template('admin/place_form.html', place=place)

        update_place(
            place_id=place_id, name=name, city=city, address=address,
            latitude=latitude, longitude=longitude,
            sports=sports, is_pmr_accessible=is_pmr,
            transport_station=transport_station, transport_lines=transport_lines,
            image_url=image_url
        )

        flash(f'Lieu "{name}" modifié avec succès !', 'success')
        return redirect(url_for('admin_places'))

    return render_template('admin/place_form.html', place=place)


@app.route('/admin/places/<int:place_id>/toggle', methods=['POST'])
@admin_required
def admin_toggle_place(place_id):
    """Activer/désactiver un lieu (admin)"""
    new_status = toggle_place_active(place_id)

    if new_status is not None:
        status_text = 'activé' if new_status else 'désactivé'
        flash(f'Lieu {status_text} avec succès.', 'success')
    else:
        flash('Lieu introuvable.', 'error')

    return redirect(url_for('admin_places'))


@app.route('/admin/places/<int:place_id>/delete', methods=['POST'])
@admin_required
def admin_delete_place(place_id):
    """Supprimer un lieu (admin)"""
    place = get_place_by_id(place_id)

    if place:
        delete_place(place_id)
        flash(f'Lieu "{place["name"]}" supprimé.', 'success')
    else:
        flash('Lieu introuvable.', 'error')

    return redirect(url_for('admin_places'))


@app.route('/api/places')
@login_required
def api_places():
    """API pour récupérer les lieux actifs (pour le formulaire d'ajout)"""
    places = get_all_places(active_only=True)
    return jsonify(places)


# ===========================
# API CHAT
# ===========================

@app.route('/api/event/<int:event_id>/messages')
@login_required
def get_event_messages(event_id):
    """Récupérer les messages d'un événement"""
    # Vérifier que l'utilisateur participe à l'événement
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT id FROM participations WHERE event_id = ? AND user_id = ?",
              (event_id, current_user.id))
    if not c.fetchone():
        # Vérifier si l'utilisateur est l'organisateur
        c.execute("SELECT organizer_id FROM events WHERE id = ?", (event_id,))
        event = c.fetchone()
        if not event or event['organizer_id'] != current_user.id:
            conn.close()
            return jsonify({'error': 'Non autorisé'}), 403

    # Récupérer les messages (paramètre since pour polling)
    since_id = request.args.get('since', 0, type=int)

    c.execute("""
        SELECT m.*, u.avatar_color
        FROM messages m
        LEFT JOIN users u ON m.user_id = u.id
        WHERE m.event_id = ? AND m.id > ?
        ORDER BY m.created_at ASC
    """, (event_id, since_id))

    messages = []
    for row in c.fetchall():
        messages.append({
            'id': row['id'],
            'user_id': row['user_id'],
            'username': row['username'],
            'content': row['content'],
            'created_at': row['created_at'],
            'avatar_color': row['avatar_color'] or '#6c757d',
            'is_mine': row['user_id'] == current_user.id
        })

    conn.close()
    return jsonify({'messages': messages})


@app.route('/api/event/<int:event_id>/messages', methods=['POST'])
@login_required
def send_event_message(event_id):
    """Envoyer un message dans un événement"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Vérifier que l'utilisateur participe ou est organisateur
    c.execute("SELECT id FROM participations WHERE event_id = ? AND user_id = ?",
              (event_id, current_user.id))
    is_participant = c.fetchone() is not None

    c.execute("SELECT organizer_id FROM events WHERE id = ?", (event_id,))
    event = c.fetchone()
    is_organizer = event and event['organizer_id'] == current_user.id

    if not is_participant and not is_organizer:
        conn.close()
        return jsonify({'error': 'Non autorisé'}), 403

    content = request.json.get('content', '').strip()
    if not content:
        conn.close()
        return jsonify({'error': 'Message vide'}), 400

    # Insérer le message
    c.execute("""
        INSERT INTO messages (event_id, user_id, username, content)
        VALUES (?, ?, ?, ?)
    """, (event_id, current_user.id, current_user.username, content))

    message_id = c.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': {
            'id': message_id,
            'user_id': current_user.id,
            'username': current_user.username,
            'content': content,
            'avatar_color': current_user.avatar_color,
            'is_mine': True
        }
    })


# ===========================
# API CHATBOT COACH SPORTIF
# ===========================

@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot():
    """
    API pour le chatbot coach sportif utilisant l'API Albert
    """
    print("=" * 50)
    print("[CHATBOT] Route appelée")
    print("=" * 50)

    try:
        data = request.json
        print(f"[CHATBOT] Data reçue: {data}")

        user_message = data.get('message', '').strip()
        conversation_history = data.get('history', [])

        print(f"[CHATBOT] Message utilisateur: {user_message}")
        print(f"[CHATBOT] Historique: {len(conversation_history)} messages")

        if not user_message:
            return jsonify({'error': 'Message vide'}), 400

        # Construire l'historique pour l'API Albert
        messages = [
            {
                "role": "system",
                "content": config.CHATBOT_SYSTEM_PROMPT
            }
        ]

        # Ajouter l'historique de conversation
        for msg in conversation_history[-10:]:  # Garder les 10 derniers messages
            messages.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })

        # Ajouter le message actuel
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Appeler l'API Albert
        headers = {
            'Authorization': f'Bearer {config.ALBERT_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }

        response = requests.post(
            f"{config.ALBERT_API_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"[CHATBOT] Status Code: {response.status_code}")
        print(f"[CHATBOT] Response: {response.text[:500]}")

        if response.status_code == 200:
            result = response.json()
            assistant_message = result.get('choices', [{}])[0].get('message', {}).get('content', '')

            if not assistant_message:
                assistant_message = "Désolé, je n'ai pas pu générer une réponse. Peux-tu reformuler ta question ?"

            return jsonify({
                'success': True,
                'message': assistant_message
            })
        else:
            # En cas d'erreur de l'API, afficher les détails
            print(f"[CHATBOT ERROR] Status: {response.status_code}")
            print(f"[CHATBOT ERROR] Body: {response.text}")
            return jsonify({
                'success': False,
                'message': "Je suis désolé, je rencontre un petit problème technique. Réessaie dans quelques instants !"
            }), 500

    except requests.exceptions.Timeout:
        print("[CHATBOT ERROR] Timeout")
        return jsonify({
            'success': False,
            'message': "La réponse prend trop de temps. Peux-tu réessayer ?"
        }), 504

    except Exception as e:
        print(f"[CHATBOT ERROR] Exception: {str(e)}")
        print(f"[CHATBOT ERROR] Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': "Une erreur est survenue. N'hésite pas à réessayer !"
        }), 500


# ===========================
# ADMIN - GESTION DES ACTIVITÉS
# ===========================

@app.route('/admin/events')
@admin_required
def admin_events():
    """Liste des événements (admin)"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT e.*, u.username as organizer_name
        FROM events e
        LEFT JOIN users u ON e.organizer_id = u.id
        ORDER BY e.id DESC
    """)
    events = c.fetchall()

    # Compter les participants pour chaque événement
    events_list = []
    for event in events:
        c.execute("SELECT COUNT(*) as count FROM participations WHERE event_id = ?", (event['id'],))
        participant_count = c.fetchone()['count']
        events_list.append({
            'event': dict(event),
            'participant_count': participant_count
        })

    conn.close()
    return render_template('admin/events_list.html', events=events_list)


@app.route('/admin/events/<int:event_id>/delete', methods=['POST'])
@admin_required
def admin_delete_event(event_id):
    """Supprimer un événement (admin)"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Récupérer l'événement
    c.execute("SELECT sport FROM events WHERE id = ?", (event_id,))
    event = c.fetchone()

    if event:
        # Supprimer les participations associées
        c.execute("DELETE FROM participations WHERE event_id = ?", (event_id,))
        # Supprimer l'événement
        c.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()
        flash(f'Événement supprimé avec succès.', 'success')
    else:
        flash('Événement introuvable.', 'error')

    conn.close()
    return redirect(url_for('admin_events'))


@app.route('/admin/events/<int:event_id>/toggle-cancel', methods=['POST'])
@admin_required
def admin_toggle_cancel_event(event_id):
    """Annuler/réactiver un événement (admin)"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("UPDATE events SET is_cancelled = NOT is_cancelled WHERE id = ?", (event_id,))
    c.execute("SELECT is_cancelled FROM events WHERE id = ?", (event_id,))
    result = c.fetchone()

    conn.commit()
    conn.close()

    if result:
        status = 'annulé' if result[0] else 'réactivé'
        flash(f'Événement {status}.', 'success')
    else:
        flash('Événement introuvable.', 'error')

    return redirect(url_for('admin_events'))


# ===========================
# ADMIN - GESTION DES UTILISATEURS
# ===========================

@app.route('/admin/users')
@admin_required
def admin_users():
    """Liste des utilisateurs (admin)"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT u.*,
               (SELECT COUNT(*) FROM events WHERE organizer_id = u.id) as events_count,
               (SELECT COUNT(*) FROM participations WHERE user_id = u.id) as participations_count
        FROM users u
        ORDER BY u.id DESC
    """)
    users = c.fetchall()

    conn.close()
    return render_template('admin/users_list.html', users=users)


@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def admin_toggle_admin(user_id):
    """Promouvoir/rétrograder un utilisateur admin (admin)"""
    # Empêcher de se rétrograder soi-même
    if user_id == current_user.id:
        flash('Vous ne pouvez pas modifier votre propre statut admin.', 'error')
        return redirect(url_for('admin_users'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("UPDATE users SET is_admin = NOT is_admin WHERE id = ?", (user_id,))
    c.execute("SELECT username, is_admin FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()

    conn.commit()
    conn.close()

    if result:
        status = 'promu administrateur' if result[1] else 'rétrogradé utilisateur'
        flash(f'{result[0]} a été {status}.', 'success')
    else:
        flash('Utilisateur introuvable.', 'error')

    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Supprimer un utilisateur (admin)"""
    # Empêcher de se supprimer soi-même
    if user_id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'error')
        return redirect(url_for('admin_users'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()

    if user:
        # Supprimer les participations
        c.execute("DELETE FROM participations WHERE user_id = ?", (user_id,))
        # Annuler les événements organisés (plutôt que supprimer)
        c.execute("UPDATE events SET is_cancelled = 1 WHERE organizer_id = ?", (user_id,))
        # Supprimer l'utilisateur
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        flash(f'Utilisateur "{user[0]}" supprimé.', 'success')
    else:
        flash('Utilisateur introuvable.', 'error')

    conn.close()
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/reset-points', methods=['POST'])
@admin_required
def admin_reset_points(user_id):
    """Remettre les points à zéro (admin)"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("UPDATE users SET points = 0 WHERE id = ?", (user_id,))
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()

    conn.commit()
    conn.close()

    if result:
        flash(f'Points de {result[0]} remis à zéro.', 'success')
    else:
        flash('Utilisateur introuvable.', 'error')

    return redirect(url_for('admin_users'))


# ===========================
# LANCEMENT DE L'APPLICATION
# ===========================

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
