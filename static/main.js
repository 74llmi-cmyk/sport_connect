/**
 * Sport Connect - Fonctions JavaScript
 * Gestion des interactions AJAX pour les événements
 */

/**
 * Rejoindre un événement
 * @param {number} eventId - ID de l'événement
 */
function joinEvent(eventId, btn) {
    const button = btn || document.activeElement;
    const originalText = button.innerText;

    // Désactiver le bouton pendant la requête
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Chargement...';

    fetch(`/event/${eventId}/join`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Succès : afficher le message
            showAlert(data.message, 'success');

            // Mettre à jour les points dans la navbar
            const pointsElement = document.getElementById('user-points');
            if (pointsElement) {
                pointsElement.innerText = data.new_points;
            }

            // Recharger la page pour afficher les changements
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            // Erreur
            showAlert(data.message, 'danger');
            button.disabled = false;
            button.innerText = originalText;
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showAlert('Une erreur est survenue lors de l\'inscription.', 'danger');
        button.disabled = false;
        button.innerText = originalText;
    });
}

/**
 * Quitter un événement
 * @param {number} eventId - ID de l'événement
 */
function leaveEvent(eventId, btn) {
    if (!confirm('Êtes-vous sûr de vouloir quitter cet événement ? Vous perdrez vos points.')) {
        return;
    }

    const button = btn || document.activeElement;
    const originalText = button.innerText;

    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Annulation...';

    fetch(`/event/${eventId}/leave`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'warning');

            // Mettre à jour les points
            const pointsElement = document.getElementById('user-points');
            if (pointsElement) {
                pointsElement.innerText = data.new_points;
            }

            // Recharger la page
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showAlert(data.message, 'danger');
            button.disabled = false;
            button.innerText = originalText;
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showAlert('Une erreur est survenue.', 'danger');
        button.disabled = false;
        button.innerText = originalText;
    });
}

/**
 * Annuler un événement (organisateur seulement)
 * @param {number} eventId - ID de l'événement
 */
function cancelEvent(eventId, btn) {
    if (!confirm('Êtes-vous sûr de vouloir annuler cet événement ? Cette action est irréversible.')) {
        return;
    }

    const button = btn || document.activeElement;
    const originalText = button.innerText;

    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Annulation...';

    fetch(`/event/${eventId}/cancel`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'info');

            // Recharger la page pour cacher l'événement annulé
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showAlert(data.message, 'danger');
            button.disabled = false;
            button.innerText = originalText;
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showAlert('Une erreur est survenue.', 'danger');
        button.disabled = false;
        button.innerText = originalText;
    });
}

/**
 * Affiche un message d'alerte Bootstrap
 * @param {string} message - Message à afficher
 * @param {string} type - Type d'alerte (success, danger, warning, info)
 */
function showAlert(message, type) {
    // Créer l'élément d'alerte
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Insérer l'alerte en haut de la page
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-fermer après 5 secondes
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 5000);
    }
}

/**
 * Soumettre le formulaire de filtre automatiquement
 */
function autoSubmitFilter() {
    const form = document.getElementById('filter-form');
    if (form) {
        form.submit();
    }
}

/**
 * Réinitialiser les filtres
 */
function resetFilters() {
    window.location.href = '/';
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sport Connect loaded');

    // Auto-dismiss des alertes après 5 secondes
    const alerts = document.querySelectorAll('.alert:not(.alert-dismissible)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });
});
