# ⚡ Quick Start - Sport Connect

## Installation ultra-rapide (Windows)

```bash
# Cloner
git clone https://github.com/jedeth/sport_connect.git
cd sport_connect

# Installer (double-clic ou dans terminal)
setup.bat

# Lancer (double-clic ou dans terminal)
start.bat
```

**Ouvrez :** http://127.0.0.1:5000

---

## Installation manuelle (toutes plateformes)

```bash
git clone https://github.com/jedeth/sport_connect.git
cd sport_connect
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python migrations/init_db.py
python migrations/add_geolocation.py
python app.py
```

**Ouvrez :** http://127.0.0.1:5000

---

## Premiers pas

1. **Créer un compte** : Cliquez sur "Inscrivez-vous ici"
2. **Explorer** : Naviguez entre 🏃 Activités / 🗺️ Carte / ➕ Proposer
3. **Créer un événement** : Formulaire avec géolocalisation (+20 pts)
4. **Rejoindre un événement** : Bouton "Rejoindre le groupe" (+50 pts)

---

**📖 Documentation complète :** [INSTALL.md](INSTALL.md) | [README.md](README.md)
