"""
Script de migration de la base de donnees
Cree les tables users et participations
Modifie la table events pour ajouter les nouvelles colonnes
"""

import sqlite3
import sys
import os

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Chemin vers la base de données
DB_PATH = 'database.db'

def migrate():
    """Exécute la migration de la base de données"""

    if not os.path.exists(DB_PATH):
        print(f"Erreur: La base de données {DB_PATH} n'existe pas.")
        print("Veuillez d'abord exécuter app.py pour créer la base initiale.")
        sys.exit(1)

    print(f"Connexion à la base de données: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # 1. Créer la table users
        print("\n1. Création de la table 'users'...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                points INTEGER DEFAULT 0,
                avatar_color TEXT DEFAULT '#6c757d'
            )
        ''')
        print("✓ Table 'users' créée avec succès")

        # 2. Créer la table participations
        print("\n2. Création de la table 'participations'...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS participations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                points_awarded INTEGER DEFAULT 50,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                UNIQUE(user_id, event_id)
            )
        ''')
        print("✓ Table 'participations' créée avec succès")

        # 3. Vérifier si les colonnes existent déjà dans events
        c.execute("PRAGMA table_info(events)")
        columns = [col[1] for col in c.fetchall()]

        # 4. Ajouter organizer_id à la table events si elle n'existe pas
        if 'organizer_id' not in columns:
            print("\n3. Ajout de la colonne 'organizer_id' à la table 'events'...")
            c.execute('ALTER TABLE events ADD COLUMN organizer_id INTEGER')
            print("✓ Colonne 'organizer_id' ajoutée")
        else:
            print("\n3. La colonne 'organizer_id' existe déjà")

        # 5. Ajouter created_at à la table events si elle n'existe pas
        # Note: SQLite n'autorise pas DEFAULT CURRENT_TIMESTAMP dans ALTER TABLE
        # On utilise NULL par défaut
        if 'created_at' not in columns:
            print("\n4. Ajout de la colonne 'created_at' à la table 'events'...")
            c.execute('ALTER TABLE events ADD COLUMN created_at TIMESTAMP')
            print("✓ Colonne 'created_at' ajoutée")
        else:
            print("\n4. La colonne 'created_at' existe déjà")

        # 6. Ajouter is_cancelled à la table events si elle n'existe pas
        if 'is_cancelled' not in columns:
            print("\n5. Ajout de la colonne 'is_cancelled' à la table 'events'...")
            c.execute('ALTER TABLE events ADD COLUMN is_cancelled BOOLEAN DEFAULT 0')
            print("✓ Colonne 'is_cancelled' ajoutée")
        else:
            print("\n5. La colonne 'is_cancelled' existe déjà")

        # 7. Créer les index pour les performances
        print("\n6. Création des index de performance...")

        indexes = [
            ("idx_events_sport", "CREATE INDEX IF NOT EXISTS idx_events_sport ON events(sport)"),
            ("idx_events_niveau", "CREATE INDEX IF NOT EXISTS idx_events_niveau ON events(niveau)"),
            ("idx_events_lieu", "CREATE INDEX IF NOT EXISTS idx_events_lieu ON events(lieu)"),
            ("idx_participations_user", "CREATE INDEX IF NOT EXISTS idx_participations_user ON participations(user_id)"),
            ("idx_participations_event", "CREATE INDEX IF NOT EXISTS idx_participations_event ON participations(event_id)")
        ]

        for index_name, index_sql in indexes:
            c.execute(index_sql)
            print(f"✓ Index '{index_name}' créé")

        # Commit toutes les modifications
        conn.commit()

        print("\n" + "="*50)
        print("✅ Migration réussie!")
        print("="*50)
        print("\nRésumé:")
        print("- Table 'users' créée")
        print("- Table 'participations' créée")
        print("- Table 'events' mise à jour avec 3 nouvelles colonnes")
        print("- 5 index de performance créés")

    except sqlite3.Error as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        conn.rollback()
        sys.exit(1)

    finally:
        conn.close()
        print("\nConnexion à la base de données fermée")

def rollback():
    """Rollback de la migration (supprime les nouvelles tables)"""

    print("⚠️  ROLLBACK: Suppression des nouvelles tables...")

    if not os.path.exists(DB_PATH):
        print(f"Erreur: La base de données {DB_PATH} n'existe pas.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # Supprimer les tables dans l'ordre inverse (à cause des foreign keys)
        c.execute("DROP TABLE IF EXISTS participations")
        print("✓ Table 'participations' supprimée")

        c.execute("DROP TABLE IF EXISTS users")
        print("✓ Table 'users' supprimée")

        # Note: On ne peut pas facilement supprimer les colonnes ajoutées à events en SQLite
        # Il faudrait recréer la table entière. Pour le MVP, on les laisse.
        print("\nNote: Les colonnes ajoutées à 'events' ne peuvent pas être supprimées facilement")
        print("      Utilisez le backup si nécessaire: database.db.backup")

        conn.commit()
        print("\n✅ Rollback terminé")

    except sqlite3.Error as e:
        print(f"\n❌ Erreur lors du rollback: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        rollback()
    else:
        migrate()
