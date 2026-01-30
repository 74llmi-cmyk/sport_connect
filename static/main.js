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

    // Initialiser le chatbot
    initChatbot();
});

/**
 * =============================================
 * CHATBOT COACH SPORTIF
 * =============================================
 */

// État du chatbot
const chatbotState = {
    isOpen: false,
    conversationHistory: [],
    isTyping: false
};

/**
 * Initialiser le chatbot
 */
function initChatbot() {
    const toggleBtn = document.getElementById('chatbot-toggle');
    const closeBtn = document.getElementById('chatbot-close');
    const sendBtn = document.getElementById('chatbot-send');
    const input = document.getElementById('chatbot-input');

    if (!toggleBtn) return; // Le chatbot n'est pas présent sur cette page

    // Ouvrir/fermer le chatbot
    toggleBtn.addEventListener('click', toggleChatbot);
    closeBtn.addEventListener('click', closeChatbot);

    // Envoyer un message
    sendBtn.addEventListener('click', sendChatbotMessage);
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatbotMessage();
        }
    });

    // Auto-resize du textarea
    input.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 100) + 'px';
    });
}

/**
 * Ouvrir/fermer le chatbot
 */
function toggleChatbot() {
    const chatbotWindow = document.getElementById('chatbot-window');

    if (chatbotState.isOpen) {
        closeChatbot();
    } else {
        chatbotWindow.classList.add('open');
        chatbotState.isOpen = true;

        // Afficher le message de bienvenue si c'est la première fois
        if (chatbotState.conversationHistory.length === 0) {
            showWelcomeMessage();
        }

        // Focus sur l'input
        setTimeout(() => {
            document.getElementById('chatbot-input').focus();
        }, 300);
    }
}

/**
 * Fermer le chatbot
 */
function closeChatbot() {
    const chatbotWindow = document.getElementById('chatbot-window');
    chatbotWindow.classList.remove('open');
    chatbotState.isOpen = false;
}

/**
 * Afficher le message de bienvenue
 */
function showWelcomeMessage() {
    const messagesContainer = document.getElementById('chatbot-messages');
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'chatbot-welcome';
    welcomeDiv.innerHTML = `
        <div class="chatbot-welcome-icon">⚽</div>
        <h4>Salut champion !</h4>
        <p>Je suis Coach Sport+, ton assistant sportif personnel. Pose-moi tes questions sur le sport, les activités ou comment bien t'entraîner !</p>
    `;
    messagesContainer.appendChild(welcomeDiv);
}

/**
 * Envoyer un message au chatbot
 */
async function sendChatbotMessage() {
    const input = document.getElementById('chatbot-input');
    const message = input.value.trim();

    if (!message || chatbotState.isTyping) return;

    // Ajouter le message de l'utilisateur
    addChatbotMessage('user', message);

    // Sauvegarder dans l'historique
    chatbotState.conversationHistory.push({
        role: 'user',
        content: message
    });

    // Vider l'input
    input.value = '';
    input.style.height = 'auto';

    // Afficher l'indicateur de frappe
    showTypingIndicator();
    chatbotState.isTyping = true;

    try {
        console.log('[CHATBOT] Envoi du message:', message);
        console.log('[CHATBOT] Historique:', chatbotState.conversationHistory);

        // Envoyer la requête à l'API
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                history: chatbotState.conversationHistory
            })
        });

        console.log('[CHATBOT] Response status:', response.status);

        const data = await response.json();
        console.log('[CHATBOT] Response data:', data);

        // Masquer l'indicateur de frappe
        hideTypingIndicator();
        chatbotState.isTyping = false;

        if (data.success && data.message) {
            // Ajouter la réponse du chatbot
            addChatbotMessage('assistant', data.message);

            // Sauvegarder dans l'historique
            chatbotState.conversationHistory.push({
                role: 'assistant',
                content: data.message
            });
        } else {
            // Erreur
            console.error('[CHATBOT] Erreur API:', data);
            addChatbotMessage('assistant', data.message || 'Oups, une petite erreur est survenue. Réessaie !');
        }
    } catch (error) {
        console.error('[CHATBOT] Exception:', error);
        console.error('[CHATBOT] Stack:', error.stack);
        hideTypingIndicator();
        chatbotState.isTyping = false;
        addChatbotMessage('assistant', 'Désolé, je n\'ai pas pu me connecter. Vérifie ta connexion internet et réessaie !');
    }
}

/**
 * Ajouter un message dans l'interface du chatbot
 */
function addChatbotMessage(role, content) {
    const messagesContainer = document.getElementById('chatbot-messages');

    // Masquer le message de bienvenue s'il existe
    const welcome = messagesContainer.querySelector('.chatbot-welcome');
    if (welcome) {
        welcome.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message ${role}`;

    const avatar = role === 'assistant' ? '⚽' : getUserInitials();
    const avatarColor = role === 'assistant' ? '' : getUserAvatarColor();

    messageDiv.innerHTML = `
        <div class="chatbot-avatar" ${role === 'user' ? `style="background-color: ${avatarColor}"` : ''}>
            ${avatar}
        </div>
        <div class="chatbot-bubble">
            ${escapeHtml(content)}
        </div>
    `;

    messagesContainer.appendChild(messageDiv);

    // Scroll vers le bas
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Afficher l'indicateur de frappe
 */
function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatbot-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'chatbot-typing-indicator';
    typingDiv.className = 'chatbot-message assistant';
    typingDiv.innerHTML = `
        <div class="chatbot-avatar">⚽</div>
        <div class="chatbot-typing visible">
            <div class="chatbot-typing-dots">
                <div class="chatbot-typing-dot"></div>
                <div class="chatbot-typing-dot"></div>
                <div class="chatbot-typing-dot"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Masquer l'indicateur de frappe
 */
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('chatbot-typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

/**
 * Récupérer les initiales de l'utilisateur
 */
function getUserInitials() {
    const userElement = document.querySelector('.avatar-circle');
    return userElement ? userElement.textContent.trim() : 'U';
}

/**
 * Récupérer la couleur d'avatar de l'utilisateur
 */
function getUserAvatarColor() {
    const userElement = document.querySelector('.avatar-circle');
    return userElement ? getComputedStyle(userElement).backgroundColor : '#667eea';
}

/**
 * Échapper le HTML pour éviter les XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}
