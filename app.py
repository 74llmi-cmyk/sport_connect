from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random

# Import du modèle User
from models import User, get_user_by_id, get_user_by_username, create_user, update_user_points

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre-cle-secrete-a-changer-en-production-sft2026'

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


def init_db():
    """Initialise la base de données avec la table events"""
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
                avatar_color=user_data['avatar_color']
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

    return render_template('index.html',
                         events=event_list,
                         sports_list=sports_list,
                         niveaux_list=niveaux_list,
                         filters={
                             'sport': sport_filter,
                             'niveau': niveau_filter,
                             'lieu': lieu_filter
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
    if request.method == 'POST':
        sport = request.form['sport']
        niveau = request.form['niveau']
        lieu = request.form['lieu']
        date_heure = request.form['date_heure']
        accessibilite = request.form.get('accessibilite')

        # Récupérer les coordonnées (optionnelles)
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

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
                     (organisateur, sport, niveau, lieu, date_heure, accessibilite, organizer_id, latitude, longitude)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (current_user.username, sport, niveau, lieu, date_heure, accessibilite, current_user.id, latitude, longitude))
        conn.commit()
        conn.close()

        # Ajouter des points pour la création d'événement
        update_user_points(current_user.id, 20)

        flash(f'Événement "{sport}" créé avec succès ! +20 points', 'success')
        return redirect(url_for('index'))

    return render_template('add.html')


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
# LANCEMENT DE L'APPLICATION
# ===========================

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
