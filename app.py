from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps
import sqlite3
import random
import re
import os
import json
import calendar as cal_module
import requests
from datetime import datetime, date

# Charger les variables d'environnement depuis .env
load_dotenv()

# Import du modèle User et des fonctions places
from models import (User, get_user_by_id, get_user_by_username, create_user, update_user_points,
                    get_all_places, get_place_by_id, create_place, update_place, delete_place,
                    toggle_place_active)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-fallback-key')

# Chemin de la base de données
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database.db')

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


@app.context_processor
def inject_logo():
    """Injecte le logo dynamique dans tous les templates"""
    logo_path = get_setting('logo_path', 'logo.png')
    return {'logo_url': url_for('static', filename=logo_path)}


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
    conn = sqlite3.connect(DATABASE_PATH)
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
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY,
                  value TEXT)''')
    conn.commit()
    conn.close()


def get_setting(key, default=''):
    """Récupérer un paramètre depuis la base de données"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default


def set_setting(key, value):
    """Enregistrer un paramètre dans la base de données"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


# ===========================
# IMAGES DES SPORTS (défauts)
# ===========================

DEFAULT_SPORT_IMAGES = {
    'Running':          'https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=400&h=200&fit=crop',
    'Tennis':           'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=400&h=200&fit=crop',
    'Yoga':             'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=200&fit=crop',
    'Football':         'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=400&h=200&fit=crop',
    'Natation':         'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=400&h=200&fit=crop',
    'Basketball':       'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=200&fit=crop',
    'Cyclisme':         'https://images.unsplash.com/photo-1541625602330-2277a4c46182?w=400&h=200&fit=crop',
    'Roller':           '/static/images/sports/roller.jpg',
    'Volley-ball':      'https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=400&h=200&fit=crop',
    'Danse':            'https://images.unsplash.com/photo-1547153760-18fc86324498?w=400&h=200&fit=crop',
    'Judo':             'https://images.unsplash.com/photo-1555597673-b21d5c935865?w=400&h=200&fit=crop',
    'Karaté':           'https://images.unsplash.com/photo-1555597408-26bc8e548a46?w=400&h=200&fit=crop',
    'Capoeira':         '/static/images/sports/capoeira.jpg',
    'Ping-pong':        'https://images.unsplash.com/photo-1534158914592-062992fbe900?w=400&h=200&fit=crop',
    'Patinage':         'https://images.unsplash.com/photo-1547483238991-18f79b7ccf8a?w=400&h=200&fit=crop',
    'Taekwondo':        '/static/images/sports/taekwondo.jpg',
    'Kendo':            'https://images.unsplash.com/photo-1509114397022-ed747cca3f65?w=400&h=200&fit=crop',
    'Handball':         'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&h=200&fit=crop',
    'Gymnastique':      'https://images.unsplash.com/photo-1566577739112-5180d4bf9390?w=400&h=200&fit=crop',
    'Escrime':          '/static/images/sports/escrime.jpg',
    'Ski':              'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400&h=200&fit=crop',
    'Parkour':          '/static/images/sports/parkour.jpg',
    'Hockey':           '/static/images/sports/hockey.jpg',
    'Skate':            '/static/images/sports/skate.jpg',
    'Voile':            '/static/images/sports/voile.jpg',
    'Escalade':         'https://images.unsplash.com/photo-1522163182402-834f871fd851?w=400&h=200&fit=crop',
    'Rugby':            'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=400&h=200&fit=crop',
    'Badminton':        'https://images.unsplash.com/photo-1544298621-35a764e4c9d8?w=400&h=200&fit=crop',
    'Boxe':             'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=400&h=200&fit=crop',
    'MMA':              'https://images.unsplash.com/photo-1555597673-b21d5c935865?w=400&h=200&fit=crop',
    'Multijeux':        'https://images.unsplash.com/photo-1461896836934-68f78c8c46b6?w=400&h=200&fit=crop',
    'Ultimate':         'https://images.unsplash.com/photo-1461896836934-68f78c8c46b6?w=400&h=200&fit=crop',
    'Saut à la perche': 'https://images.unsplash.com/photo-1461896836934-68f78c8c46b6?w=400&h=200&fit=crop',
    'Bowling':          'https://images.unsplash.com/photo-1508961990440-f1040e1c6d05?w=400&h=200&fit=crop',
    "Tir à l'arc":      'https://images.unsplash.com/photo-1511884642898-4c92249e20b6?w=400&h=200&fit=crop',
    'Golf':             'https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=400&h=200&fit=crop',
}

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_sport_images():
    """Retourne le dict images des sports (DB en priorité, sinon défauts)"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings WHERE key LIKE 'sport_image_%'")
    rows = c.fetchall()
    conn.close()
    images = dict(DEFAULT_SPORT_IMAGES)
    for key, value in rows:
        sport_name = key[len('sport_image_'):]
        images[sport_name] = value
    return images


# ===========================
# ROUTES D'AUTHENTIFICATION
# ===========================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Vérifier si les inscriptions sont activées
    if get_setting('registration_enabled', '1') == '0':
        flash('Les inscriptions sont actuellement désactivées.', 'error')
        return redirect(url_for('login'))

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
            flash(f'Bienvenue sur Olympus, {username} !', 'success')
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

        whitelist_enabled = get_setting('whitelist_enabled', '0') == '1'

        # --- Mode liste blanche ---
        if whitelist_enabled and user_data and not bool(user_data.get('is_admin', 0)):
            whitelist = json.loads(get_setting('whitelist', '[]'))
            entry = next((e for e in whitelist if e.get('username') == username), None)
            if not entry:
                flash('Accès refusé. Votre compte n\'est pas dans la liste autorisée.', 'error')
                return render_template('login.html')
            if not check_password_hash(entry['password_hash'], password):
                flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
                return render_template('login.html')
            # Credentials whitelist OK → connecter avec le compte DB
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                points=user_data['points'],
                avatar_color=user_data['avatar_color'],
                is_admin=False
            )
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))

        # --- Mode normal ---
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                points=user_data['points'],
                avatar_color=user_data['avatar_color'],
                is_admin=bool(user_data.get('is_admin', 0))
            )
            login_user(user, remember=remember)
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
    conn = sqlite3.connect(DATABASE_PATH)
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

    # Récupérer tous les événements actifs (pour section favoris)
    c.execute("""
        SELECT e.id, e.sport, e.niveau, e.lieu, e.date_heure, e.genre, u.username as organizer
        FROM events e
        JOIN users u ON e.organizer_id = u.id
        WHERE e.is_cancelled = 0
        ORDER BY e.id DESC
    """)
    all_events = [dict(row) for row in c.fetchall()]

    conn.close()

    return render_template('profile.html',
                         organized_events=organized_events,
                         participated_events=participated_events,
                         all_events=all_events)


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

    conn = sqlite3.connect(DATABASE_PATH)
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
    sports_list = ['Running', 'Tennis', 'Yoga', 'Football', 'Natation', 'Basketball', 'Cyclisme',
                   'Roller', 'Volley-ball', 'Danse', 'Judo', 'Karaté', 'Capoeira',
                   'Ping-pong', 'Patinage', 'Taekwondo', 'Kendo', 'Handball',
                   'Gymnastique', 'Escrime', 'Skate', 'Voile',
                   'Escalade', 'Rugby', 'Badminton', 'Multijeux', 'Ultimate',
                   'Boxe', 'MMA', 'Parkour', 'Hockey',
                   'Saut à la perche', 'Bowling', 'Tir à l\'arc', 'Golf', 'Ski']
    niveaux_list = ['Débutant', 'Intermédiaire', 'Expert']
    genres_list = ['Mixte', 'Homme', 'Femme']

    return render_template('index.html',
                         events=event_list,
                         sports_list=sports_list,
                         niveaux_list=niveaux_list,
                         genres_list=genres_list,
                         sport_images=get_sport_images(),
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
    conn = sqlite3.connect(DATABASE_PATH)
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
    sports_list = ['Running', 'Tennis', 'Yoga', 'Football', 'Natation', 'Basketball', 'Cyclisme',
                   'Roller', 'Volley-ball', 'Danse', 'Judo', 'Karaté', 'Capoeira',
                   'Ping-pong', 'Patinage', 'Taekwondo', 'Kendo', 'Handball',
                   'Gymnastique', 'Escrime', 'Skate', 'Voile',
                   'Escalade', 'Rugby', 'Badminton', 'Multijeux', 'Ultimate',
                   'Boxe', 'MMA', 'Parkour', 'Hockey',
                   'Saut à la perche', 'Bowling', 'Tir à l\'arc', 'Golf', 'Ski']

    # Convertir en JSON pour JavaScript
    import json
    events_json = json.dumps(event_list)

    return render_template('map.html',
                         events=event_list,
                         events_json=events_json,
                         sports_list=sports_list)


# ===========================
# ROUTE CALENDRIER
# ===========================

@app.route('/calendar')
@login_required
def calendar_view():
    """Page calendrier des activités sportives"""
    # Récupérer le mois demandé (défaut = mois courant)
    month_param = request.args.get('month', '')
    try:
        if month_param:
            year, month = map(int, month_param.split('-'))
        else:
            today = date.today()
            year, month = today.year, today.month
    except (ValueError, TypeError):
        today = date.today()
        year, month = today.year, today.month

    # Calculer mois précédent et suivant
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    prev_month_str = f"{prev_year}-{prev_month:02d}"
    next_month_str = f"{next_year}-{next_month:02d}"

    # Premier et dernier jour du mois
    first_day_weekday, days_in_month = cal_module.monthrange(year, month)

    # Noms des mois en français
    mois_fr = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }

    # Récupérer les événements du mois
    month_start = f"{year}-{month:02d}-01"
    month_end = f"{year}-{month:02d}-{days_in_month}"

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Récupérer les événements auxquels l'utilisateur participe ou qu'il organise
    c.execute("""
        SELECT DISTINCT e.* FROM events e
        LEFT JOIN participations p ON e.id = p.event_id AND p.user_id = ?
        WHERE e.is_cancelled = 0
          AND (p.id IS NOT NULL OR e.organizer_id = ?)
        ORDER BY e.id DESC
    """, (current_user.id, current_user.id))
    events = c.fetchall()

    conn.close()

    # Jours de la semaine en français pour le parsing
    jours_semaine_fr = {
        'lundi': 0, 'mardi': 1, 'mercredi': 2, 'jeudi': 3,
        'vendredi': 4, 'samedi': 5, 'dimanche': 6
    }
    mois_fr_parse = {
        'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
        'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
        'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
    }

    def parse_date_heure(dt_str, current_year, current_month):
        """Parse une date en texte libre français et retourne (jour, heure_str)"""
        if not dt_str:
            return None, ''
        dt_lower = dt_str.lower().strip()
        jour = None
        heure = ''

        # Extraire l'heure (formats: 14h, 14h00, 15h30)
        h_match = re.search(r'(\d{1,2})\s*h\s*(\d{2})?', dt_lower)
        if h_match:
            h = h_match.group(1).zfill(2)
            m = h_match.group(2) or '00'
            heure = f"{h}:{m}"

        # Tenter format ISO (YYYY-MM-DD)
        iso_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', dt_lower)
        if iso_match:
            y, mo, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
            if mo == current_month and y == current_year:
                jour = d
            return jour, heure

        # Tenter format "13 février" ou "13 mars 14h"
        date_match = re.search(r'(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)', dt_lower)
        if date_match:
            d = int(date_match.group(1))
            m = mois_fr_parse.get(date_match.group(2))
            if m == current_month and 1 <= d <= days_in_month:
                jour = d
            return jour, heure

        # Tenter format "25/01/2026" ou "25/01"
        slash_match = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?', dt_lower)
        if slash_match:
            d = int(slash_match.group(1))
            m = int(slash_match.group(2))
            if m == current_month and 1 <= d <= days_in_month:
                jour = d
            return jour, heure

        # Tenter jour de la semaine (lundi, mardi, etc.) → premier de ce jour dans le mois
        for jour_nom, jour_idx in jours_semaine_fr.items():
            if jour_nom in dt_lower:
                # Trouver les dates de ce jour de la semaine dans le mois courant
                for d in range(1, days_in_month + 1):
                    try:
                        dt = date(current_year, current_month, d)
                        if dt.weekday() == jour_idx:
                            jour = d
                            break
                    except ValueError:
                        pass
                break

        return jour, heure

    # Grouper les événements par jour
    events_by_day = {}
    events_list = []
    for event in events:
        ev = dict(event)
        jour, heure = parse_date_heure(event['date_heure'], year, month)
        ev['parsed_time'] = heure
        events_list.append(ev)
        if jour:
            if jour not in events_by_day:
                events_by_day[jour] = []
            events_by_day[jour].append(ev)

    # Construire la grille du calendrier
    # first_day_weekday : 0=lundi, 6=dimanche
    calendar_days = []
    # Cases vides avant le premier jour
    for _ in range(first_day_weekday):
        calendar_days.append({'day': None, 'events': []})
    # Jours du mois
    for day in range(1, days_in_month + 1):
        calendar_days.append({
            'day': day,
            'events': events_by_day.get(day, []),
            'is_today': (day == date.today().day and month == date.today().month and year == date.today().year)
        })

    # Couleurs et icônes par sport
    sport_colors = {
        'Running': '#FF6B6B',
        'Tennis': '#4ECDC4',
        'Yoga': '#A78BFA',
        'Football': '#34D399',
        'Natation': '#60A5FA',
        'Basketball': '#F59E0B',
        'Cyclisme': '#F97316',
        'Roller': '#E879F9',
        'Volley-ball': '#FB923C',
        'Danse': '#EC4899',
        'Judo': '#14B8A6',
        'Karaté': '#EF4444',
        'Capoeira': '#F472B6',
        'Ping-pong': '#8B5CF6',
        'Patinage': '#38BDF8',
        'Taekwondo': '#DC2626',
        'Kendo': '#6366F1',
        'Handball': '#10B981',
        'Gymnastique': '#D946EF',
        'Escrime': '#78716C',
        'Skate': '#A3A3A3',
        'Voile': '#0EA5E9',
        'Escalade': '#92400E',
        'Rugby': '#15803D',
        'Badminton': '#0891B2',
        'Multijeux': '#7C3AED',
        'Ultimate': '#0D9488',
        'Boxe': '#B91C1C',
        'MMA': '#1E293B',
        'Parkour': '#D97706',
        'Hockey': '#1D4ED8',
        'Saut à la perche': '#6B7280',
        'Bowling': '#7C2D12',
        'Tir à l\'arc': '#166534',
        'Golf': '#15803D',
        'Ski': '#BAE6FD',
    }
    sport_icons = {
        'Running': '🏃',
        'Tennis': '🎾',
        'Yoga': '🧘',
        'Football': '⚽',
        'Natation': '🏊',
        'Basketball': '🏀',
        'Cyclisme': '🚴',
        'Roller': '🛼',
        'Volley-ball': '🏐',
        'Danse': '💃',
        'Judo': '🥋',
        'Karaté': '🥊',
        'Capoeira': '🤸',
        'Ping-pong': '🏓',
        'Patinage': '⛸️',
        'Taekwondo': '🦶',
        'Kendo': '🗡️',
        'Handball': '🤾',
        'Gymnastique': '🤸‍♀️',
        'Escrime': '🤺',
        'Skate': '🛹',
        'Voile': '⛵',
        'Escalade': '🧗',
        'Rugby': '🏉',
        'Badminton': '🏸',
        'Multijeux': '🎮',
        'Ultimate': '🥏',
        'Boxe': '🥊',
        'MMA': '🤼',
        'Parkour': '🏃‍♂️',
        'Hockey': '🏒',
        'Saut à la perche': '🏅',
        'Bowling': '🎳',
        'Tir à l\'arc': '🏹',
        'Golf': '⛳',
        'Ski': '⛷️',
    }

    return render_template('calendar.html',
                         calendar_days=calendar_days,
                         events_list=events_list,
                         month_name=mois_fr[month],
                         year=year,
                         month=month,
                         prev_month=prev_month_str,
                         next_month=next_month_str,
                         sport_colors=sport_colors,
                         sport_icons=sport_icons)


# ===========================
# ROUTE AJOUT D'ÉVÉNEMENT
# ===========================

@app.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    """Créer un nouvel événement"""
    # Récupérer les lieux pour le menu déroulant
    places = get_all_places(active_only=True)

    sports_list = ['Running', 'Tennis', 'Yoga', 'Football', 'Natation', 'Basketball', 'Cyclisme',
                   'Roller', 'Volley-ball', 'Danse', 'Judo', 'Karaté', 'Capoeira',
                   'Ping-pong', 'Patinage', 'Taekwondo', 'Kendo', 'Handball',
                   'Gymnastique', 'Escrime', 'Skate', 'Voile',
                   'Escalade', 'Rugby', 'Badminton', 'Multijeux', 'Ultimate',
                   'Boxe', 'MMA', 'Parkour', 'Hockey',
                   'Saut à la perche', 'Bowling', 'Tir à l\'arc', 'Golf', 'Ski']

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

        conn = sqlite3.connect(DATABASE_PATH)
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

    return render_template('add.html', places=places, sports_list=sports_list)


# ===========================
# CHATBOT SPORTY
# ===========================

# URL de l'API Albert (format OpenAI-compatible)
ALBERT_API_URL = os.environ.get('ALBERT_API_URL', 'https://albert.api.etalab.gouv.fr/v1')

SPORTY_SYSTEM_PROMPT = """Tu es Sporty, coach sportif virtuel sur Olympus, accessible à tous : jeunes, adultes, débutants et confirmés.

TON ET STYLE :
- Chaleureux, cordial, bienveillant — français courant, sans argot
- Quelques emojis avec modération 😊
- Toujours en français — jamais de listes à puces ni de titres

MÉTHODE EN 2 ÉCHANGES MAXIMUM :

Message 1 (dès la première question) :
- Pose UNE seule question courte pour comprendre le besoin (sport recherché, niveau, ou disponibilités selon ce qui manque).
- Annonce que des activités disponibles s'affichent ci-dessous et invite l'utilisateur à les consulter.
- Exemple : "Bien sûr ! Quel sport souhaitez-vous pratiquer et quel est votre niveau ? Des activités disponibles sont affichées ci-dessous pour vous aider à démarrer 😊"

Message 2 (après la réponse de l'utilisateur) :
- Donne un conseil court et personnalisé (1 phrase).
- Si les activités affichées ne correspondent pas encore, pose UNE question sur les disponibilités (jours, créneaux) pour affiner.
- Exemple : "Pour progresser en football, pratiquez régulièrement avec un groupe de niveau similaire. Êtes-vous plutôt disponible en semaine ou le week-end ?"

À partir du message 3 : conseille et affine uniquement si l'utilisateur le demande.

IMPORTANT : Le système affiche automatiquement les activités sous forme de boutons. Tu n'as pas à les lister toi-même, contente-toi d'y faire référence en une phrase.
Si aucune activité n'est disponible, invite chaleureusement l'utilisateur à en créer une.

ÉTHIQUE :
- Douleur ou blessure → professionnel de santé, sans diagnostic
- Hors sport/bien-être → redirige poliment
- Fair-play, respect, pratique raisonnée

ACTIVITÉS DE L'UTILISATEUR :
"""


SPORTS_DATA = [
    {'name': 'Running', 'emoji': '🏃', 'color': '#FF6B6B'},
    {'name': 'Tennis', 'emoji': '🎾', 'color': '#4ECDC4'},
    {'name': 'Yoga', 'emoji': '🧘', 'color': '#A78BFA'},
    {'name': 'Football', 'emoji': '⚽', 'color': '#34D399'},
    {'name': 'Natation', 'emoji': '🏊', 'color': '#60A5FA'},
    {'name': 'Basketball', 'emoji': '🏀', 'color': '#F59E0B'},
    {'name': 'Cyclisme', 'emoji': '🚴', 'color': '#F97316'},
    {'name': 'Roller', 'emoji': '🛼', 'color': '#E879F9'},
    {'name': 'Volley-ball', 'emoji': '🏐', 'color': '#FB923C'},
    {'name': 'Danse', 'emoji': '💃', 'color': '#EC4899'},
    {'name': 'Judo', 'emoji': '🥋', 'color': '#14B8A6'},
    {'name': 'Karaté', 'emoji': '🥊', 'color': '#EF4444'},
    {'name': 'Capoeira', 'emoji': '🤸', 'color': '#F472B6'},
    {'name': 'Ping-pong', 'emoji': '🏓', 'color': '#8B5CF6'},
    {'name': 'Patinage', 'emoji': '⛸️', 'color': '#38BDF8'},
    {'name': 'Taekwondo', 'emoji': '🦶', 'color': '#DC2626'},
    {'name': 'Kendo', 'emoji': '🗡️', 'color': '#6366F1'},
    {'name': 'Handball', 'emoji': '🤾', 'color': '#10B981'},
    {'name': 'Gymnastique', 'emoji': '🤸‍♀️', 'color': '#D946EF'},
    {'name': 'Escrime', 'emoji': '🤺', 'color': '#78716C'},
    {'name': 'Skate', 'emoji': '🛹', 'color': '#A3A3A3'},
    {'name': 'Voile', 'emoji': '⛵', 'color': '#0EA5E9'},
    {'name': 'Escalade', 'emoji': '🧗', 'color': '#92400E'},
    {'name': 'Rugby', 'emoji': '🏉', 'color': '#15803D'},
    {'name': 'Badminton', 'emoji': '🏸', 'color': '#0891B2'},
    {'name': 'Multijeux', 'emoji': '🎮', 'color': '#7C3AED'},
    {'name': 'Ultimate', 'emoji': '🥏', 'color': '#0D9488'},
    {'name': 'Boxe', 'emoji': '🥊', 'color': '#B91C1C'},
    {'name': 'MMA', 'emoji': '🤼', 'color': '#1E293B'},
    {'name': 'Parkour', 'emoji': '🏃‍♂️', 'color': '#D97706'},
    {'name': 'Hockey', 'emoji': '🏒', 'color': '#1D4ED8'},
    {'name': 'Saut à la perche', 'emoji': '🏅', 'color': '#6B7280'},
    {'name': 'Bowling', 'emoji': '🎳', 'color': '#7C2D12'},
    {'name': 'Tir à l\'arc', 'emoji': '🏹', 'color': '#166534'},
    {'name': 'Golf', 'emoji': '⛳', 'color': '#15803D'},
    {'name': 'Ski', 'emoji': '⛷️', 'color': '#BAE6FD'},
]


@app.route('/chatbot')
@login_required
def chatbot():
    """Page du chatbot Sporty (coach IA unifié)"""
    return render_template('chatbot.html', sports_data=SPORTS_DATA)


@app.route('/coach')
@login_required
def coach():
    """Redirige vers la page Sporty unifiée"""
    return redirect(url_for('chatbot'))


@app.route('/api/chatbot', methods=['POST'])
@login_required
def api_chatbot():
    """Endpoint API pour le chatbot Sporty"""
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'error': 'Message vide'}), 400

    user_message = data['message']
    history = data.get('history', [])

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Activités de l'utilisateur (inscrit ou organisateur)
    c.execute("""
        SELECT DISTINCT e.sport, e.niveau, e.lieu, e.date_heure
        FROM events e
        LEFT JOIN participations p ON e.id = p.event_id AND p.user_id = ?
        WHERE e.is_cancelled = 0
          AND (p.id IS NOT NULL OR e.organizer_id = ?)
        ORDER BY e.id DESC LIMIT 10
    """, (current_user.id, current_user.id))
    user_events = c.fetchall()

    # Activités disponibles sur l'appli (toutes celles auxquelles l'utilisateur n'est pas encore inscrit)
    c.execute("""
        SELECT e.id, e.sport, e.niveau, e.lieu, e.date_heure, u.username as organisateur
        FROM events e
        LEFT JOIN users u ON e.organizer_id = u.id
        WHERE e.is_cancelled = 0
          AND e.id NOT IN (
              SELECT event_id FROM participations WHERE user_id = ?
          )
        ORDER BY e.id DESC LIMIT 20
    """, (current_user.id,))
    available_events = c.fetchall()

    conn.close()

    # Construire le contexte : activités de l'utilisateur
    if user_events:
        user_events_text = "\n".join(
            f"- {ev['sport']} ({ev['niveau']}) à {ev['lieu']}, {ev['date_heure']}"
            for ev in user_events
        )
    else:
        user_events_text = "Aucune activité inscrite pour le moment."

    # Construire le contexte : activités disponibles sur l'appli
    if available_events:
        available_text = "\n".join(
            f"- {ev['sport']} ({ev['niveau']}) à {ev['lieu']}, {ev['date_heure']} — proposé par {ev['organisateur']}"
            for ev in available_events
        )
    else:
        available_text = "Aucune activité disponible en ce moment."

    activites_context = (
        f"{user_events_text}\n\n"
        f"ACTIVITÉS DISPONIBLES SUR L'APPLICATION (non encore rejointes) :\n"
        f"{available_text}"
    )

    # --- Matcher les activités pertinentes selon la conversation ---
    all_sports = [
        'Running', 'Tennis', 'Yoga', 'Football', 'Natation', 'Basketball', 'Cyclisme',
        'Roller', 'Volley-ball', 'Danse', 'Judo', 'Karaté', 'Capoeira', 'Ping-pong',
        'Patinage', 'Taekwondo', 'Kendo', 'Handball', 'Gymnastique', 'Escrime', 'Skate',
        'Voile', 'Escalade', 'Rugby', 'Badminton', 'Multijeux', 'Ultimate',
        'Boxe', 'MMA', 'Parkour', 'Hockey', 'Saut à la perche', 'Bowling',
        "Tir à l'arc", 'Golf', 'Ski'
    ]
    jours_cles = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche',
                  'week-end', 'weekend', 'matin', 'après-midi', 'soir']
    niveaux_cles = ['débutant', 'debutant', 'intermédiaire', 'intermediaire', 'expert', 'confirmé']

    recent_text = " ".join(
        [m.get("content", "") for m in history[-10:]] + [user_message]
    ).lower()

    sports_mentionnes = [s for s in all_sports if s.lower() in recent_text]
    jours_mentionnes = [j for j in jours_cles if j in recent_text]
    niveaux_mentionnes = [n for n in niveaux_cles if n in recent_text]

    # Scorer chaque activité disponible
    scored = []
    for ev in available_events:
        score = 0
        ev_sport = (ev['sport'] or '').lower()
        ev_date = (ev['date_heure'] or '').lower()
        ev_niveau = (ev['niveau'] or '').lower()

        # Correspondance sport (priorité haute)
        if sports_mentionnes and any(s.lower() == ev_sport for s in sports_mentionnes):
            score += 10
        elif not sports_mentionnes:
            score += 1  # pas encore de filtre sport → inclure tous

        # Correspondance jour/créneau
        score += sum(2 for j in jours_mentionnes if j in ev_date)

        # Correspondance niveau
        score += sum(3 for n in niveaux_mentionnes if n in ev_niveau)

        scored.append((score, dict(ev)))

    # Trier par score décroissant, garder les 3 meilleurs
    scored.sort(key=lambda x: x[0], reverse=True)
    suggested_events = [
        {
            'id': ev['id'],
            'sport': ev['sport'] or '',
            'niveau': ev['niveau'] or '',
            'lieu': ev['lieu'] or '',
            'date_heure': ev['date_heure'] or '',
            'organisateur': ev['organisateur'] or 'Anonyme'
        }
        for score, ev in scored[:3]
        if score > 0
    ]

    # Construire les messages pour l'API
    system_content = SPORTY_SYSTEM_PROMPT + activites_context
    messages = [{"role": "system", "content": system_content}]

    for msg in history[-20:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": user_message})

    # Récupérer la clé API depuis les paramètres admin
    api_key = get_setting('albert_api_key')

    if not ALBERT_API_URL or not api_key:
        return jsonify({
            'response': "Mon cerveau IA n'est pas encore configuré. Un administrateur peut renseigner la clé API dans Admin > Réglages. 😊"
        })

    try:
        response = requests.post(
            f"{ALBERT_API_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if not ai_response:
                ai_response = "Je n'ai pas bien compris, pourriez-vous reformuler ? 😊"
            return jsonify({
                'response': ai_response,
                'suggested_events': suggested_events
            })
        else:
            return jsonify({
                'response': f"Une erreur de connexion est survenue (code {response.status_code}). Veuillez réessayer dans quelques instants. 🔄"
            })

    except requests.exceptions.Timeout:
        return jsonify({'response': "La réponse a pris trop de temps. Veuillez réessayer ! 😊"})
    except Exception as e:
        import traceback
        print("COACH ERROR:", traceback.format_exc())
        return jsonify({'response': f"Erreur technique : {type(e).__name__}: {str(e)[:200]}"})


# ===========================
# ROUTES DE PARTICIPATION (AJAX)
# ===========================

@app.route('/event/<int:event_id>/join', methods=['POST'])
@login_required
def join_event(event_id):
    """Rejoindre un événement (API JSON)"""
    conn = sqlite3.connect(DATABASE_PATH)
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
    conn = sqlite3.connect(DATABASE_PATH)
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
    conn = sqlite3.connect(DATABASE_PATH)
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
    conn = sqlite3.connect(DATABASE_PATH)
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
    conn = sqlite3.connect(DATABASE_PATH)
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
# ADMIN - GESTION DES ACTIVITÉS
# ===========================

@app.route('/admin/events')
@admin_required
def admin_events():
    """Liste des événements (admin)"""
    conn = sqlite3.connect(DATABASE_PATH)
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
    conn = sqlite3.connect(DATABASE_PATH)
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
    conn = sqlite3.connect(DATABASE_PATH)
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
    conn = sqlite3.connect(DATABASE_PATH)
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

    conn = sqlite3.connect(DATABASE_PATH)
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


def delete_user_completely(user_id):
    """Supprime un utilisateur et toutes ses données associées"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    # Récupérer les événements organisés par cet utilisateur
    c.execute("SELECT id FROM events WHERE organizer_id = ?", (user_id,))
    event_ids = [row[0] for row in c.fetchall()]
    # Supprimer les messages de ces événements
    for eid in event_ids:
        c.execute("DELETE FROM messages WHERE event_id = ?", (eid,))
    # Supprimer les participations à ces événements
    for eid in event_ids:
        c.execute("DELETE FROM participations WHERE event_id = ?", (eid,))
    # Supprimer les événements organisés
    c.execute("DELETE FROM events WHERE organizer_id = ?", (user_id,))
    # Supprimer les participations de l'utilisateur
    c.execute("DELETE FROM participations WHERE user_id = ?", (user_id,))
    # Supprimer les messages postés par l'utilisateur
    c.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    # Supprimer l'utilisateur
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Supprimer un utilisateur (admin)"""
    # Empêcher de se supprimer soi-même
    if user_id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'error')
        return redirect(url_for('admin_users'))

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT username, is_admin FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()

    if not user:
        flash('Utilisateur introuvable.', 'error')
        return redirect(url_for('admin_users'))
    if user[1]:
        flash('Impossible de supprimer un compte administrateur.', 'error')
        return redirect(url_for('admin_users'))

    delete_user_completely(user_id)
    flash(f'Utilisateur "{user[0]}" et toutes ses données supprimés.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/reset-points', methods=['POST'])
@admin_required
def admin_reset_points(user_id):
    """Remettre les points à zéro (admin)"""
    conn = sqlite3.connect(DATABASE_PATH)
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
# ADMIN - RÉGLAGES
# ===========================

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """Page de réglages administrateur"""
    if request.method == 'POST':
        albert_key = request.form.get('albert_api_key', '').strip()
        set_setting('albert_api_key', albert_key)
        flash('Réglages sauvegardés avec succès !', 'success')
        return redirect(url_for('admin_settings'))

    current_key = get_setting('albert_api_key')
    current_logo = get_setting('logo_path', 'logo.png')
    registration_enabled = get_setting('registration_enabled', '1') == '1'
    whitelist_enabled = get_setting('whitelist_enabled', '0') == '1'
    whitelist = json.loads(get_setting('whitelist', '[]'))
    return render_template('admin/settings.html',
                           albert_api_key=current_key,
                           current_logo=current_logo,
                           registration_enabled=registration_enabled,
                           whitelist_enabled=whitelist_enabled,
                           whitelist=whitelist)


@app.route('/admin/settings/test-albert')
@admin_required
def admin_test_albert():
    """Tester la connexion avec l'API Albert"""
    api_key = get_setting('albert_api_key')
    if not api_key:
        return jsonify({'status': 'error', 'message': 'Aucune clé API configurée.'})
    try:
        response = requests.post(
            f"{ALBERT_API_URL}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
                  "messages": [{"role": "user", "content": "Dis bonjour en une phrase."}],
                  "max_tokens": 30},
            timeout=10
        )
        if response.status_code == 200:
            reply = response.json().get('choices', [{}])[0].get('message', {}).get('content', '...')
            return jsonify({'status': 'success', 'message': f'Connexion réussie ✅ — Réponse : {reply}'})
        else:
            return jsonify({'status': 'error', 'message': f'Erreur {response.status_code} — Clé invalide ou expirée.'})
    except requests.exceptions.Timeout:
        return jsonify({'status': 'error', 'message': 'Timeout — L\'API Albert ne répond pas.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur : {str(e)}'})


@app.route('/admin/settings/upload-logo', methods=['POST'])
@admin_required
def admin_upload_logo():
    """Upload d'un nouveau logo"""
    file = request.files.get('logo_file')
    if file and file.filename and allowed_file(file.filename):
        ext = os.path.splitext(secure_filename(file.filename))[1].lower()
        filename = f'logo_custom{ext}'
        file.save(os.path.join(app.static_folder, filename))
        set_setting('logo_path', filename)
        flash('Logo mis à jour avec succès !', 'success')
    else:
        flash('Fichier invalide. Formats acceptés : jpg, png, gif, webp.', 'error')
    return redirect(url_for('admin_settings'))


@app.route('/admin/settings/reset-logo', methods=['POST'])
@admin_required
def admin_reset_logo():
    """Réinitialiser le logo par défaut"""
    set_setting('logo_path', 'logo.png')
    flash('Logo réinitialisé.', 'success')
    return redirect(url_for('admin_settings'))


@app.route('/admin/settings/toggle-registration', methods=['POST'])
@admin_required
def admin_toggle_registration():
    """Activer ou désactiver les inscriptions"""
    current = get_setting('registration_enabled', '1')
    new_value = '0' if current == '1' else '1'
    set_setting('registration_enabled', new_value)
    state = 'désactivées' if new_value == '0' else 'activées'
    flash(f'Les inscriptions sont maintenant {state}.', 'success')
    return redirect(url_for('admin_settings'))


@app.route('/admin/settings/whitelist/toggle', methods=['POST'])
@admin_required
def admin_toggle_whitelist():
    """Activer ou désactiver la liste blanche"""
    current = get_setting('whitelist_enabled', '0')
    new_value = '0' if current == '1' else '1'
    set_setting('whitelist_enabled', new_value)
    state = 'activée' if new_value == '1' else 'désactivée'
    flash(f'La liste blanche est maintenant {state}.', 'success')
    return redirect(url_for('admin_settings'))


@app.route('/admin/settings/whitelist/add', methods=['POST'])
@admin_required
def admin_whitelist_add():
    """Ajouter manuellement un compte à la liste blanche"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    email = request.form.get('email', '').strip() or None

    if not username or not password:
        flash('Identifiant et mot de passe requis.', 'error')
        return redirect(url_for('admin_settings'))
    if len(password) < 6:
        flash('Le mot de passe doit contenir au moins 6 caractères.', 'error')
        return redirect(url_for('admin_settings'))

    whitelist = json.loads(get_setting('whitelist', '[]'))
    if any(e.get('username') == username for e in whitelist):
        flash(f'« {username} » est déjà dans la liste blanche.', 'info')
        return redirect(url_for('admin_settings'))

    entry = {
        'username': username,
        'password': password,
        'password_hash': generate_password_hash(password)
    }
    if email:
        entry['email'] = email
    whitelist.append(entry)
    set_setting('whitelist', json.dumps(whitelist))

    # Créer le compte utilisateur en base s'il n'existe pas déjà
    if not get_user_by_username(username):
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                  '#F06292', '#64B5F6', '#81C784', '#FFB74D', '#BA68C8']
        create_user(username, entry['password_hash'], email, random.choice(colors))

    flash(f'« {username} » ajouté à la liste blanche et créé dans les utilisateurs.', 'success')
    return redirect(url_for('admin_settings'))


@app.route('/admin/settings/whitelist/generate', methods=['POST'])
@admin_required
def admin_whitelist_generate():
    """Générer automatiquement un compte de test"""
    import secrets, string
    adj = ['rapide', 'fort', 'agile', 'brave', 'vif', 'grand', 'fier', 'sûr']
    sport = ['lion', 'aigle', 'tigre', 'requin', 'faucon', 'puma', 'lynx', 'cobra']
    username = f"{random.choice(adj)}_{random.choice(sport)}_{random.randint(10,99)}"
    alphabet = string.ascii_letters + string.digits + '!@#$'
    password = ''.join(secrets.choice(alphabet) for _ in range(10))

    whitelist = json.loads(get_setting('whitelist', '[]'))
    # Sécurité : éviter les doublons
    if any(e.get('username') == username for e in whitelist):
        username += str(random.randint(1, 9))

    password_hash = generate_password_hash(password)
    entry = {'username': username, 'password': password, 'password_hash': password_hash}
    whitelist.append(entry)
    set_setting('whitelist', json.dumps(whitelist))

    # Créer le compte utilisateur en base
    if not get_user_by_username(username):
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                  '#F06292', '#64B5F6', '#81C784', '#FFB74D', '#BA68C8']
        create_user(username, password_hash, None, random.choice(colors))

    flash(f'Compte « {username} » généré — mot de passe : {password}', 'success')
    return redirect(url_for('admin_settings'))


@app.route('/admin/settings/whitelist/remove', methods=['POST'])
@admin_required
def admin_whitelist_remove():
    """Retirer un compte de la liste blanche et supprimer l'utilisateur associé"""
    username = request.form.get('username', '').strip()
    whitelist = json.loads(get_setting('whitelist', '[]'))
    new_list = [e for e in whitelist if e.get('username') != username]
    if len(new_list) < len(whitelist):
        set_setting('whitelist', json.dumps(new_list))
        # Supprimer aussi le compte utilisateur en base (sauf admin)
        user_data = get_user_by_username(username)
        if user_data and not user_data.get('is_admin'):
            delete_user_completely(user_data['id'])
        flash(f'« {username} » supprimé de la liste blanche et des utilisateurs.', 'success')
    return redirect(url_for('admin_settings'))


# ===========================
# ADMIN - IMAGES DES SPORTS
# ===========================

@app.route('/admin/sport-images')
@admin_required
def admin_sport_images():
    """Visualiser et modifier les images des sports"""
    images = get_sport_images()
    sports = [(sport, images.get(sport, '')) for sport in DEFAULT_SPORT_IMAGES.keys()]
    return render_template('admin/sport_images.html', sports=sports)


@app.route('/admin/sport-images/update', methods=['POST'])
@admin_required
def admin_update_sport_image():
    """Mettre à jour l'image d'un sport (upload fichier ou URL)"""
    sport = request.form.get('sport', '').strip()
    image_url = request.form.get('image_url', '').strip()

    if not sport:
        flash('Sport non spécifié.', 'error')
        return redirect(url_for('admin_sport_images'))

    # Priorité : fichier uploadé
    file = request.files.get('image_file')
    if file and file.filename and allowed_file(file.filename):
        sports_dir = os.path.join(app.static_folder, 'images', 'sports')
        os.makedirs(sports_dir, exist_ok=True)
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', sport).lower()
        ext = os.path.splitext(secure_filename(file.filename))[1].lower() or '.jpg'
        filename = f"{safe_name}{ext}"
        file.save(os.path.join(sports_dir, filename))
        image_url = f'/static/images/sports/{filename}'

    if image_url:
        set_setting(f'sport_image_{sport}', image_url)
        flash(f'Image mise à jour pour « {sport} » !', 'success')
    else:
        flash('Aucune image fournie.', 'error')

    return redirect(url_for('admin_sport_images'))


@app.route('/admin/sport-images/reset', methods=['POST'])
@admin_required
def admin_reset_sport_image():
    """Réinitialiser l'image d'un sport à sa valeur par défaut"""
    sport = request.form.get('sport', '').strip()
    if sport:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM settings WHERE key = ?", (f'sport_image_{sport}',))
        conn.commit()
        conn.close()
        flash(f'Image réinitialisée pour « {sport} ».', 'success')
    return redirect(url_for('admin_sport_images'))


# ===========================
# LANCEMENT DE L'APPLICATION
# ===========================

# Initialiser la base de données au démarrage (Gunicorn ou direct)
init_db()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
