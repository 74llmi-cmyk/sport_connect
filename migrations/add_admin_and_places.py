"""
Migration : Ajout de l'admin et des lieux de pratique sportive
- Ajoute la colonne is_admin à la table users
- Crée la table places pour les lieux de pratique
- Ajoute la colonne place_id à la table events
"""

import sqlite3
import sys
import os

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

DB_PATH = 'database.db'


def migrate():
    """Exécute la migration admin et places"""

    if not os.path.exists(DB_PATH):
        print(f"Erreur: La base de données {DB_PATH} n'existe pas.")
        sys.exit(1)

    print(f"Connexion à la base de données: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # ===========================
        # 1. Ajouter is_admin à users
        # ===========================
        print("\n1. Vérification de la colonne 'is_admin' dans 'users'...")
        c.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in c.fetchall()]

        if 'is_admin' not in user_columns:
            print("   Ajout de la colonne 'is_admin' à la table 'users'...")
            c.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
            print("   ✓ Colonne 'is_admin' ajoutée")
        else:
            print("   ✓ La colonne 'is_admin' existe déjà")

        # ===========================
        # 2. Créer la table places
        # ===========================
        print("\n2. Création de la table 'places'...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                city TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                sports TEXT,
                is_pmr_accessible INTEGER DEFAULT 0,
                transport_station TEXT,
                transport_lines TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("   ✓ Table 'places' créée (ou existait déjà)")

        # ===========================
        # 3. Ajouter place_id à events
        # ===========================
        print("\n3. Vérification de la colonne 'place_id' dans 'events'...")
        c.execute("PRAGMA table_info(events)")
        event_columns = [col[1] for col in c.fetchall()]

        if 'place_id' not in event_columns:
            print("   Ajout de la colonne 'place_id' à la table 'events'...")
            c.execute('ALTER TABLE events ADD COLUMN place_id INTEGER REFERENCES places(id)')
            print("   ✓ Colonne 'place_id' ajoutée")
        else:
            print("   ✓ La colonne 'place_id' existe déjà")

        conn.commit()

        # ===========================
        # Résumé
        # ===========================
        print("\n" + "=" * 50)
        print("✅ Migration admin et places réussie!")
        print("=" * 50)
        print("\nRésumé:")
        print("- Colonne 'is_admin' ajoutée à users (INTEGER, défaut: 0)")
        print("- Table 'places' créée avec les colonnes:")
        print("  * id, name, address, city")
        print("  * latitude, longitude")
        print("  * sports (liste séparée par virgules)")
        print("  * is_pmr_accessible, transport_station, transport_lines")
        print("  * is_active, created_at")
        print("- Colonne 'place_id' ajoutée à events (FK vers places)")

        print("\n📝 Pour promouvoir un utilisateur en admin:")
        print("   sqlite3 database.db")
        print("   UPDATE users SET is_admin = 1 WHERE username = 'votre_username';")

    except sqlite3.Error as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        conn.rollback()
        sys.exit(1)

    finally:
        conn.close()
        print("\nConnexion à la base de données fermée")


if __name__ == '__main__':
    migrate()
