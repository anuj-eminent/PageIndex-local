document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const questionInput = document.getElementById('question-input');
    const chatContainer = document.getElementById('chat-container');
    const emptyState = document.getElementById('empty-state');
    const sendButton = document.getElementById('send-button');
    const loadingSpinner = document.getElementById('loading-spinner');
    const exchangeTemplate = document.getElementById('exchange-template');

    // Make sure API endpoint is correct
    const API_URL = 'http://localhost:8000/ask';

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const question = questionInput.value.trim();
        if (!question) return;

        // Hide empty state if present
        if (emptyState) {
            emptyState.style.display = 'none';
        }

        // Disable input while processing
        questionInput.value = '';
        questionInput.disabled = true;
        sendButton.style.display = 'none';
        loadingSpinner.style.display = 'block';

        // Create new exchange element from template
        const exchangeClone = exchangeTemplate.content.cloneNode(true);
        const exchangeDiv = exchangeClone.querySelector('.exchange');

        // Set user message
        exchangeClone.querySelector('.user-message').textContent = question;

        // Show typing indicators
        const typingIndicators = exchangeClone.querySelectorAll('.typing-indicator');
        typingIndicators.forEach(ind => ind.style.display = 'flex');

        // Append to chat container and scroll to bottom
        chatContainer.appendChild(exchangeClone);
        scrollToBottom();

        try {
            // Fetch from API
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: question })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();

            // Expected response format:
            // {
            //   "question": "...",
            //   "results": {
            //     "general_rag": "...",
            //     "grpah_ollama": "...",
            //     "page_index": "..."
            //   }
            // }

            const results = data.results || {};

            // Update each card
            updateResponseCard(exchangeDiv, 'general_rag', results.general_rag);
            updateResponseCard(exchangeDiv, 'grpah_ollama', results.grpah_ollama);
            updateResponseCard(exchangeDiv, 'page_index', results.page_index);

        } catch (error) {
            console.error('Error fetching data:', error);

            // Show error in all cards
            const errorMsg = "Sorry, failed to get response. Is the server running?";
            updateResponseCard(exchangeDiv, 'general_rag', errorMsg, true);
            updateResponseCard(exchangeDiv, 'grpah_ollama', errorMsg, true);
            updateResponseCard(exchangeDiv, 'page_index', errorMsg, true);
        } finally {
            // Re-enable input
            questionInput.disabled = false;
            sendButton.style.display = 'flex';
            loadingSpinner.style.display = 'none';
            questionInput.focus();
            scrollToBottom();
        }
    });

    function updateResponseCard(exchangeDiv, modelKey, text, isError = false) {
        const card = exchangeDiv.querySelector(`.response-card[data-model="${modelKey}"]`);
        if (!card) return;

        // Hide typing indicator
        card.querySelector('.typing-indicator').style.display = 'none';

        // Render content
        const contentDiv = card.querySelector('.response-content');

        if (!text) {
            contentDiv.innerHTML = '<span class="response-error">No response provided by model.</span>';
            return;
        }

        if (isError) {
            contentDiv.innerHTML = `<span class="response-error">${escapeHTML(text)}</span>`;
            return;
        }

        // Format newlines to <p> and <br> tags
        const formattedText = text.split('\n\n').map(p =>
            `<p>${p.replace(/\n/g, '<br>')}</p>`
        ).join('');

        contentDiv.innerHTML = formattedText;
    }

    function scrollToBottom() {
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    // Helper to prevent XSS
    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g,
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
});
