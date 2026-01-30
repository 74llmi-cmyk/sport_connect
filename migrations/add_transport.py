"""
Script de migration pour ajouter les informations de transport
Ajoute les colonnes transport_station et transport_lines a la table events
"""

import sqlite3
import sys
import os

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Chemin vers la base de donnees
DB_PATH = 'database.db'

def migrate():
    """Ajoute les colonnes de transport a la table events"""

    if not os.path.exists(DB_PATH):
        print(f"Erreur: La base de donnees {DB_PATH} n'existe pas.")
        sys.exit(1)

    print(f"Connexion a la base de donnees: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # Verifier les colonnes existantes
        c.execute("PRAGMA table_info(events)")
        columns = [col[1] for col in c.fetchall()]

        # 1. Ajouter transport_station
        if 'transport_station' not in columns:
            print("\n1. Ajout de la colonne 'transport_station'...")
            c.execute('ALTER TABLE events ADD COLUMN transport_station TEXT')
            print("   Colonne 'transport_station' ajoutee")
        else:
            print("\n1. La colonne 'transport_station' existe deja")

        # 2. Ajouter transport_lines (stocke en JSON: ["M4", "M6", "RER B"])
        if 'transport_lines' not in columns:
            print("\n2. Ajout de la colonne 'transport_lines'...")
            c.execute('ALTER TABLE events ADD COLUMN transport_lines TEXT')
            print("   Colonne 'transport_lines' ajoutee")
        else:
            print("\n2. La colonne 'transport_lines' existe deja")

        conn.commit()

        print("\n" + "="*50)
        print("Migration reussie!")
        print("="*50)
        print("\nColonnes ajoutees:")
        print("- transport_station: Station la plus proche")
        print("- transport_lines: Lignes de transport (JSON)")

    except sqlite3.Error as e:
        print(f"\nErreur lors de la migration: {e}")
        conn.rollback()
        sys.exit(1)

    finally:
        conn.close()
        print("\nConnexion fermee")

if __name__ == '__main__':
    migrate()
