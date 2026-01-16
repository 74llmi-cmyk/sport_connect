from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
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

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM events ORDER BY id DESC")
    events = c.fetchall()
    conn.close()
    
    # --- SIMULATION GAMIFICATION ---
    # On simule un utilisateur connecté pour la démo
    user_stats = {
        "pseudo": "Eleve_Test",
        "points": 120,
        "niveau": "Explorateur Sportif",
        "next_level": 200
    }
    
    return render_template('index.html', events=events, user=user_stats)

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        organisateur = request.form['organisateur']
        sport = request.form['sport']
        niveau = request.form['niveau']
        lieu = request.form['lieu']
        date_heure = request.form['date_heure']
        accessibilite = request.form.get('accessibilite')

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
    app.run(host='0.0.0.0', port=5000, debug=True)