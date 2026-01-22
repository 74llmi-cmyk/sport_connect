"""
Migration : Ajout de la géolocalisation aux événements
Ajoute les colonnes latitude et longitude à la table events
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
    """Ajoute les colonnes de géolocalisation"""

    if not os.path.exists(DB_PATH):
        print(f"Erreur: La base de données {DB_PATH} n'existe pas.")
        sys.exit(1)

    print(f"Connexion à la base de données: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # Vérifier si les colonnes existent déjà
        c.execute("PRAGMA table_info(events)")
        columns = [col[1] for col in c.fetchall()]

        # Ajouter latitude
        if 'latitude' not in columns:
            print("\n1. Ajout de la colonne 'latitude' à la table 'events'...")
            c.execute('ALTER TABLE events ADD COLUMN latitude REAL')
            print("✓ Colonne 'latitude' ajoutée")
        else:
            print("\n1. La colonne 'latitude' existe déjà")

        # Ajouter longitude
        if 'longitude' not in columns:
            print("\n2. Ajout de la colonne 'longitude' à la table 'events'...")
            c.execute('ALTER TABLE events ADD COLUMN longitude REAL')
            print("✓ Colonne 'longitude' ajoutée")
        else:
            print("\n2. La colonne 'longitude' existe déjà")

        conn.commit()

        print("\n" + "="*50)
        print("✅ Migration géolocalisation réussie!")
        print("="*50)
        print("\nRésumé:")
        print("- Colonne 'latitude' ajoutée à events")
        print("- Colonne 'longitude' ajoutée à events")

    except sqlite3.Error as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        conn.rollback()
        sys.exit(1)

    finally:
        conn.close()
        print("\nConnexion à la base de données fermée")

if __name__ == '__main__':
    migrate()
