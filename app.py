from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Configuration de la base de données
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # On crée une table pour stocker les événements sportifs
    # Correspond aux données citées dans le PDF (Sport, Niveau, Lieu...) [cite: 28-33]
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

# Route 1 : Page d'accueil (Le "Matching")
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM events ORDER BY id DESC")
    events = c.fetchall()
    conn.close()
    return render_template('index.html', events=events)

# Route 2 : Page pour ajouter une activité
@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        # Récupération des données du formulaire
        organisateur = request.form['organisateur']
        sport = request.form['sport']
        niveau = request.form['niveau']
        lieu = request.form['lieu']
        date_heure = request.form['date_heure']
        accessibilite = request.form.get('accessibilite') # Checkbox

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO events (organisateur, sport, niveau, lieu, date_heure, accessibilite) VALUES (?, ?, ?, ?, ?, ?)",
                  (organisateur, sport, niveau, lieu, date_heure, accessibilite))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

if __name__ == '__main__':
    init_db()
    # Lancement sur le port 5000, accessible depuis l'extérieur (0.0.0.0)
    app.run(host='0.0.0.0', port=5000, debug=True)