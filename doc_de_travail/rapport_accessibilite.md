# 🔍 AUDIT D'ACCESSIBILITÉ - SPORT CONNECT

**Date:** 28 janvier 2026
**Version auditée:** MVP Sport Connect
**Auditeur:** Claude Code
**Normes de référence:** WCAG 2.1 (Niveau AA)

---

## 📊 RÉSUMÉ EXÉCUTIF

**Note globale : 6/10** - Plusieurs bonnes pratiques en place, mais des améliorations critiques sont nécessaires pour assurer une accessibilité conforme aux normes WCAG 2.1.

---

## ✅ POINTS FORTS

### 1. Structure de base solide
- ✓ Attribut `lang="fr"` présent sur `<html>`
- ✓ Utilisation de Bootstrap 5 avec composants accessibles
- ✓ Viewport configuré correctement

### 2. Formulaires bien structurés
- ✓ Labels associés correctement aux champs (login.html:16-23, register.html:16-26)
- ✓ Attributs `required`, `minlength`, `maxlength` utilisés
- ✓ Messages d'aide (`form-text text-muted`) présents
- ✓ Validation côté client avec retour visuel

### 3. Navigation et ARIA de base
- ✓ Barre de navigation avec `aria-controls` et `aria-expanded` (base.html:22)
- ✓ Role `progressbar` avec `aria-valuenow`, `aria-valuemin`, `aria-valuemax` (base.html:88-94)
- ✓ Alerts avec gestion Bootstrap des messages flash (base.html:111)
- ✓ Liens de navigation sémantiques avec `<nav>`

---

## ❌ PROBLÈMES CRITIQUES (Priorité 1)

### 1. **Cartes d'activités NON accessibles au clavier**
**Localisation:** index.html:73-75
```html
<div class="activity-card" onclick="selectActivity(...)">
```
**Impact:** Les utilisateurs au clavier ne peuvent PAS sélectionner les activités
**Solution:** Transformer en `<button>` ou ajouter `tabindex="0"` + gestion des événements clavier (Enter/Space)

**Exemple de correction:**
```html
<div class="activity-card"
     tabindex="0"
     role="button"
     onclick="selectActivity(...)"
     onkeydown="if(event.key==='Enter'||event.key===' ')selectActivity(...)">
```

### 2. **Labels manquants sur les filtres**
**Localisation:** index.html:32-64
```html
<select name="sport" class="form-select form-select-sm" onchange="autoSubmitFilter()">
```
**Impact:** Lecteurs d'écran ne peuvent pas identifier les filtres
**Solution:** Ajouter des `<label>` visibles ou `aria-label`

**Exemple de correction:**
```html
<label for="filter-sport" class="visually-hidden">Filtrer par sport</label>
<select id="filter-sport" name="sport" class="form-select form-select-sm" aria-label="Filtrer par sport">
```

### 3. **Soumission automatique des filtres problématique**
**Localisation:** index.html:32, 42, 52 - `onchange="autoSubmitFilter()"`
**Impact:** Changement de contexte inattendu sans avertissement (violation WCAG 3.2.2)
**Solution:** Remplacer par un bouton "Appliquer les filtres"

**Exemple de correction:**
```html
<div class="col-md-12 text-end mt-2">
    <button type="submit" class="btn btn-sm btn-primary">Appliquer les filtres</button>
</div>
```

### 4. **Input de chat sans label**
**Localisation:** index.html:225
```html
<input type="text" id="chat-input" class="form-control" placeholder="Votre message...">
```
**Impact:** Non identifiable par les technologies d'assistance
**Solution:** Ajouter un `<label>` ou `aria-label="Écrire un message"`

**Exemple de correction:**
```html
<label for="chat-input" class="visually-hidden">Écrire un message</label>
<input type="text" id="chat-input" class="form-control" placeholder="Votre message..." aria-label="Écrire un message">
```

---

## ⚠️ PROBLÈMES IMPORTANTS (Priorité 2)

### 5. **Hiérarchie de titres incorrecte**
**Localisation:** index.html:23 (H3) → index.html:178 (H5) → index.html:252 (H6)
**Impact:** Saute de H3 à H5, puis H6 - confus pour la navigation par titres
**Solution:** Utiliser H1 → H2 → H3 → H4 dans l'ordre logique

**Correction recommandée:**
- Titre principal "Activités disponibles" → H1
- "Trouver un lieu" dans le sidepanel → H2
- Titre de l'activité sélectionnée → H3

### 6. **Textes alternatifs génériques sur les images**
**Localisation:** index.html:91-92, base.html:17
```html
<img src="..." alt="Football">
<img src="logo.png" alt="Logo">
```
**Impact:** Pas assez descriptif
**Solution:**
- Logo: `alt="Sport Connect - Logo de l'application"`
- Images activités: `alt="Photo d'un terrain de football"` ou `alt=""` si décoratif

### 7. **Symboles Unicode sans alternative textuelle**
**Localisation:** index.html:101-106
```html
<span class="badge-genre">&#9794; Homme</span>
<span class="badge-pmr">♿ PMR</span>
```
**Impact:** Les lecteurs d'écran lisent "symbole mâle" au lieu du contexte
**Solution:** Ajouter `aria-label` ou rendre le symbole décoratif

**Exemple de correction:**
```html
<span class="badge-genre" aria-label="Réservé aux hommes">&#9794; Homme</span>
<span class="badge-pmr" aria-label="Accessible aux personnes à mobilité réduite">♿ PMR</span>
```

### 8. **Boutons sans contexte**
**Localisation:** index.html:89, 113, 137, 161
```html
<button onclick="...">Rejoindre</button>
```
**Impact:** Hors contexte, "Rejoindre" ne dit pas quoi
**Solution:** Ajouter `aria-label="Rejoindre l'activité Football au Parc des Princes"`

**Exemple de correction:**
```html
<button onclick="event.stopPropagation(); joinEvent({{ item.event.id }}, this)"
        class="btn btn-join btn-sm w-100"
        aria-label="Rejoindre l'activité {{ item.event.sport }} à {{ item.event.lieu }}">
    Rejoindre
</button>
```

### 9. **aria-valuetext vide sur la barre de progression**
**Localisation:** base.html:91
```html
aria-valuenow="{{ level_info.progress }}" aria-valuemin="0" aria-valuemax="100"
```
**Impact:** Pas de description textuelle de la progression
**Solution:** Ajouter `aria-valuetext="{{ level_info.progress }}% - {{ level_info.name }}"`

### 10. **onchange sur formulaires d'ajout**
**Localisation:** add.html:51
```html
<select ... onchange="onPlaceChange(this)">
```
**Impact:** Changement de contexte non anticipé
**Solution:** Ajouter un avertissement textuel ou rendre optionnel

---

## 📝 AMÉLIORATIONS RECOMMANDÉES (Priorité 3)

### 11. **Pas de lien "Aller au contenu principal"**
**Impact:** Navigation longue pour utilisateurs au clavier
**Solution:** Ajouter un skip link en début de page

**Exemple:**
```html
<a href="#main-content" class="skip-link visually-hidden-focusable">
    Aller au contenu principal
</a>
```

### 12. **Emojis utilisés comme contenu informatif**
**Localisation:** Partout (🏃, 📍, 🕒, etc.)
**Impact:** Peut être verbeux avec lecteurs d'écran
**Solution:** Utiliser `aria-hidden="true"` sur emojis + texte visible

**Exemple:**
```html
<span aria-hidden="true">📍</span> Parc des Princes, Paris
```

### 13. **Zones cliquables imbriquées**
**Localisation:** index.html:124-151
```html
<div onclick="selectActivity(...)">
    <button onclick="event.stopPropagation(); joinEvent(...)">
```
**Impact:** Comportement imprévisible
**Solution:** Restructurer pour séparer les zones interactives

### 14. **Focus non visible**
**Impact:** Utilisateurs au clavier ne voient pas où ils sont
**Solution:** Vérifier que les états `:focus` ont un indicateur visible (outline)

**CSS recommandé:**
```css
*:focus-visible {
    outline: 2px solid #4A90E2;
    outline-offset: 2px;
}
```

### 15. **Notifications visuelles uniquement**
**Localisation:** index.html:535-561 (playNotificationSound)
**Impact:** Pas d'alternative pour utilisateurs sourds
**Solution:** Utiliser `aria-live` pour annoncer les nouveaux messages

**Exemple:**
```html
<div aria-live="polite" aria-atomic="true" class="visually-hidden" id="chat-announcer"></div>

<script>
document.getElementById('chat-announcer').textContent =
    `Nouveau message de ${username}: ${message}`;
</script>
```

### 16. **Carte Leaflet non accessible**
**Localisation:** index.html:289-300
**Impact:** Les cartes interactives sont difficiles d'accès
**Solution:** Fournir une liste textuelle alternative des lieux

---

## 🎨 CONTRASTE DES COULEURS

**À vérifier avec un outil comme WAVE ou Axe DevTools:**
- Texte blanc sur fond violet (boutons primaires)
- Badges de niveau (jaune sur fond clair)
- Badges de transport (couleurs des lignes RATP)
- Texte gris clair sur fond blanc (small text-muted)

**Ratios minimum requis (WCAG 2.1 AA):**
- Texte normal (<18px): 4.5:1
- Texte large (≥18px ou ≥14px gras): 3:1
- Éléments d'interface: 3:1

**Éléments à tester:**
1. `.text-muted` sur fond blanc
2. `.badge-niveau-debutant` (jaune)
3. `.btn-primary` (texte blanc sur violet)
4. `.activity-date` et `.activity-lieu`

---

## 🔧 PLAN D'ACTION RECOMMANDÉ

### Phase 1 - Corrections critiques (1-2 jours)
1. ✅ Rendre les cartes d'activités accessibles au clavier
2. ✅ Ajouter les labels sur les filtres
3. ✅ Remplacer l'auto-submit par un bouton
4. ✅ Ajouter label sur l'input de chat

**Estimation:** 4-6 heures de développement

### Phase 2 - Améliorations importantes (2-3 jours)
5. ✅ Corriger la hiérarchie de titres
6. ✅ Améliorer les textes alternatifs
7. ✅ Ajouter aria-labels contextuels sur les boutons
8. ✅ Gérer les symboles Unicode
9. ✅ Corriger aria-valuetext sur progressbar

**Estimation:** 8-10 heures de développement

### Phase 3 - Optimisations (1-2 jours)
10. ✅ Ajouter un skip link
11. ✅ Implémenter aria-live pour le chat
12. ✅ Gérer les emojis avec aria-hidden
13. ✅ Vérifier et corriger les contrastes
14. ✅ Tester avec lecteurs d'écran (NVDA, JAWS)
15. ✅ Valider avec WAVE et Axe DevTools

**Estimation:** 6-8 heures de développement + tests

---

## 🛠️ OUTILS RECOMMANDÉS

### Extensions navigateur
1. **axe DevTools** (Chrome/Firefox) - Scan automatique des problèmes
2. **WAVE** (WebAIM) - Évaluation visuelle avec annotations
3. **Lighthouse** (Chrome DevTools) - Score d'accessibilité global

### Lecteurs d'écran
4. **NVDA** (Windows, gratuit) - https://www.nvaccess.org/
5. **JAWS** (Windows, payant mais standard entreprise)
6. **VoiceOver** (macOS, intégré)
7. **TalkBack** (Android, intégré)

### Outils de contraste
8. **Color Contrast Analyzer** (gratuit) - https://www.tpgi.com/color-contrast-checker/
9. **WebAIM Contrast Checker** - https://webaim.org/resources/contrastchecker/

### Validation
10. **W3C Validator** - https://validator.w3.org/
11. **ARIA Validator** - Intégré dans axe DevTools

---

## 📚 RESSOURCES

### Documentation officielle
- **WCAG 2.1 Quick Reference:** https://www.w3.org/WAI/WCAG21/quickref/
- **MDN Accessibility Guide:** https://developer.mozilla.org/fr/docs/Web/Accessibility
- **ARIA Authoring Practices Guide (APG):** https://www.w3.org/WAI/ARIA/apg/

### Guides spécifiques
- **Bootstrap Accessibility:** https://getbootstrap.com/docs/5.3/getting-started/accessibility/
- **WebAIM Articles:** https://webaim.org/articles/
- **A11y Project Checklist:** https://www.a11yproject.com/checklist/

### Formation
- **Introduction à l'accessibilité web (W3C):** https://www.w3.org/WAI/fundamentals/accessibility-intro/
- **Cours gratuit accessibility par Google:** https://web.dev/learn/accessibility/

---

## 📈 MÉTRIQUES DE SUIVI

### Avant corrections
- **Score Lighthouse:** Non mesuré
- **Erreurs axe DevTools:** Non mesuré
- **Navigation clavier:** ❌ Incomplète (cartes non accessibles)
- **Lecteur d'écran:** ⚠️ Fonctionnel partiel

### Objectifs après corrections
- **Score Lighthouse:** ≥ 90/100
- **Erreurs axe DevTools:** 0 erreur critique, < 5 avertissements
- **Navigation clavier:** ✅ Complète sur tous les éléments interactifs
- **Lecteur d'écran:** ✅ Navigation fluide et compréhensible
- **Conformité WCAG:** Niveau AA atteint

---

## 🎯 CONCLUSION

L'application Sport Connect présente une base solide avec des formulaires bien structurés et une utilisation correcte de Bootstrap. Cependant, **les problèmes de navigation au clavier et les labels manquants constituent des obstacles majeurs** pour les utilisateurs de technologies d'assistance.

**Recommandation:** Prioriser la Phase 1 (corrections critiques) avant toute mise en production, puis planifier les Phases 2 et 3 dans les sprints suivants.

**Bénéfices attendus:**
- ♿ Accessibilité pour 15-20% de la population (handicaps permanents ou temporaires)
- 🎯 Conformité légale (obligation pour services publics et grandes entreprises)
- 📈 Meilleur référencement (SEO)
- 👥 Expérience utilisateur améliorée pour tous

---

**Document créé le:** 2026-01-28
**Prochaine révision recommandée:** Après implémentation des corrections Phase 1
