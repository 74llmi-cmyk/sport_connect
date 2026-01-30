# 🤖 Coach Sport+ - Chatbot IA

Un assistant virtuel intelligent pour conseiller les enfants et leurs parents sur les activités sportives, propulsé par l'API Albert (IA de l'État français).

## 🎯 Fonctionnalités

- **Expert en sport pour enfants** : Conseils adaptés à l'âge et au niveau
- **Ton encourageant** : Motivation et positivité pour stimuler l'engagement
- **Conseils pratiques** : Nutrition, hydratation, sécurité, échauffement
- **Règles de jeu** : Explications simples et ludiques des différents sports
- **Interface moderne** : Chat responsive avec animations fluides

## 🚀 Installation

### 1. Configuration de l'API Albert

1. Créez un compte sur [Albert API](https://albert.api.etalab.gouv.fr)
2. Obtenez votre clé API
3. Copiez `config.example.py` vers `config.py`
4. Remplissez vos informations dans `config.py` :

```python
ALBERT_API_URL = "https://albert.api.etalab.gouv.fr/v1"
ALBERT_API_KEY = "votre-cle-api-ici"
```

### 2. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancement

```bash
python app.py
```

Le chatbot sera automatiquement disponible dans la navbar pour tous les utilisateurs connectés.

## 💬 Utilisation

1. **Connectez-vous** à votre compte Sport Connect
2. **Cliquez sur le bouton "⚽ Coach"** dans la navbar (en haut à droite)
3. **Posez vos questions** au coach sportif

### Exemples de questions

- "Quel sport est adapté pour un enfant de 7 ans ?"
- "Comment bien s'échauffer avant de jouer au football ?"
- "Quels sont les bienfaits du yoga pour les enfants ?"
- "Comment rester motivé pour faire du sport régulièrement ?"
- "Quelles sont les règles du basketball ?"
- "Que manger avant et après le sport ?"

## 🎨 Interface

### Desktop
- **Bouton dans la navbar** : Dégradé orange-rouge, à côté du profil utilisateur
- **Fenêtre de chat** : Popup fixe en bas à droite (380x550px)
- **Messages** : Bulles différenciées pour l'utilisateur et le coach
- **Animation** : Indicateur de frappe pendant que le coach réfléchit

### Mobile
- **Bouton flottant** : En bas à droite de l'écran
- **Fenêtre plein écran** : Pour une meilleure expérience tactile
- **Interface optimisée** : Tailles et espacements adaptés

## 🔧 Architecture technique

### Backend (`app.py`)
```python
@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot():
    # Gère les requêtes vers l'API Albert
    # Maintient l'historique de conversation
    # Retourne les réponses formatées
```

### Frontend (`main.js`)
- Gestion de l'état du chatbot
- Affichage des messages
- Communication AJAX avec le backend
- Animations et interactions utilisateur

### Styles (`style.css`)
- Design moderne et responsive
- Animations fluides
- Thème cohérent avec Sport Connect

## 🔒 Sécurité

⚠️ **IMPORTANT** : Ne versionnez JAMAIS le fichier `config.py` contenant votre clé API !

Le fichier est déjà ajouté au `.gitignore` :
```
# Configuration avec clés API
config.py
```

### Bonnes pratiques

1. ✅ Utilisez `config.example.py` comme template
2. ✅ Ne partagez jamais votre clé API
3. ✅ Régénérez votre clé si elle est compromise
4. ✅ Utilisez des variables d'environnement en production

## 📊 Modèle utilisé

**AgentPublic/albertlight-7b**
- Modèle de langage français de l'État
- Optimisé pour les services publics
- Spécialisé pour le contexte français

### Paramètres
```python
{
    "temperature": 0.7,  # Créativité modérée
    "max_tokens": 500,   # Réponses concises
    "stream": False      # Réponse complète
}
```

## 🎯 Personnalisation du prompt

Modifiez `CHATBOT_SYSTEM_PROMPT` dans `config.py` pour adapter :
- Le ton du coach
- Le niveau de langue
- Les domaines d'expertise
- Les restrictions

### Exemple de modification

```python
CHATBOT_SYSTEM_PROMPT = """Tu es Coach Sport+, un expert en sports collectifs pour adolescents.

Ton rôle :
- Conseiller sur le football, basketball, volleyball
- Promouvoir l'esprit d'équipe et le fair-play
- Donner des tactiques et stratégies de jeu
- Encourager la cohésion de groupe

..."""
```

## 📈 Améliorations futures

- [ ] Sauvegarde des conversations en base de données
- [ ] Suggestions de réponses rapides
- [ ] Partage de conversations intéressantes
- [ ] Statistiques d'utilisation
- [ ] Mode vocal (speech-to-text)
- [ ] Multilangue (anglais, espagnol, etc.)
- [ ] Recommandations d'activités personnalisées

## 🐛 Dépannage

### Le chatbot ne répond pas
1. Vérifiez votre connexion internet
2. Vérifiez que la clé API est valide
3. Consultez la console du navigateur (F12)
4. Vérifiez les logs Flask

### Erreur "API unavailable"
- L'API Albert peut être temporairement indisponible
- Vérifiez le status sur le site d'Albert
- Attendez quelques minutes et réessayez

### Messages tronqués
- Augmentez `max_tokens` dans `app.py`
- Gardez vos questions concises pour de meilleures réponses

## 📝 License

Développé dans le cadre du projet **Sove For Tomorrow (SFT) 2026**

---

**Développé avec ❤️ pour encourager le sport chez les jeunes**
