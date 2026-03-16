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

            // Always try to parse JSON (even if status is non-OK) so we can still show useful info.
            const data = await response.json().catch(() => null);
            const hadHttpError = !response.ok;

            if (hadHttpError) {
                const statusText = response.statusText || response.status;
                console.warn('API returned non-OK status', response.status, statusText, data);
            }

            if (!data) {
                throw new Error('Invalid JSON response from API');
            }

            // Expected response format:
            // {
            //   "question": "...",
            //   "results": {
            //     "general_rag": {"answer":"...","context":"..."},
            //     "grpah_ollama": {"answer":"...","context":"..."},
            //     "page_index": {"answer":"...","context":"..."}
            //   }
            // }

            const results = data.results || {};

            // Update each card (if the API returned an error object, it will be rendered as an error message)
            updateResponseCard(exchangeDiv, 'general_rag', results.general_rag, hadHttpError);
            updateResponseCard(exchangeDiv, 'grpah_ollama', results.grpah_ollama, hadHttpError);
            updateResponseCard(exchangeDiv, 'page_index', results.page_index, hadHttpError);

        } catch (error) {
            console.error('Error fetching data:', error);

            // Show error in all cards
            const errorMsg = error?.message ? `Error: ${error.message}` : "Sorry, failed to get response.";
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
        const contextDiv = card.querySelector('.context-content');

        // Support response formats like:
        // { error: "..." }
        // { answer: "...", context: "..." }
        // and raw string responses.
        let answerText = '';
        let contextText = '';

        const isObject = text && typeof text === 'object' && !Array.isArray(text);

        if (isObject) {
            // If the backend returns an error object, treat it as an error response.
            if (text.error) {
                isError = true;
                answerText = String(text.error);
            }

            // Normalize answer/context fields
            answerText = answerText || String(text.answer ?? text.response ?? '');

            const rawContext = text.context ?? text.ctx ?? '';
            if (Array.isArray(rawContext)) {
                contextText = rawContext.join('\n\n');
            } else {
                contextText = String(rawContext ?? '');
            }
        } else if (Array.isArray(text)) {
            // If a model returns an array (e.g., list of chunks), join them
            answerText = text.join('\n\n');
        } else {
            answerText = String(text ?? '');
        }

        if (!answerText) {
            contentDiv.innerHTML = '<span class="response-error">No response provided by model.</span>';
        } else if (isError) {
            contentDiv.innerHTML = `<span class="response-error">${escapeHTML(answerText)}</span>`;
        } else {
            // Format newlines to <p> and <br> tags
            const formattedText = answerText.split('\n\n').map(p =>
                `<p>${p.replace(/\n/g, '<br>')}</p>`
            ).join('');
            contentDiv.innerHTML = formattedText;
        }

        // Populate context (if available)
        if (contextDiv) {
            if (contextText) {
                const formattedContext = contextText.split('\n\n').map(p =>
                    `<p>${p.replace(/\n/g, '<br>')}</p>`
                ).join('');
                contextDiv.innerHTML = formattedContext;
            } else {
                contextDiv.innerHTML = 'No context available.';
            }
        }
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
