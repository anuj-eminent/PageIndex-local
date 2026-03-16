document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const pdfFileInput = document.getElementById('pdf-file');
    const fileNameDisplay = document.getElementById('file-name-display');
    const uploadBtn = document.getElementById('upload-btn');
    
    const statusArea = document.getElementById('status-area');
    const timerDisplay = document.getElementById('timer');
    const resultMessage = document.getElementById('result-message');
    const processingSpinner = document.getElementById('processing-spinner');

    const API_URL = 'http://localhost:8000/upload';
    let timerInterval;

    // Update filename display on selection
    pdfFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = e.target.files[0].name;
            fileNameDisplay.style.color = 'var(--accent-primary)';
            fileNameDisplay.style.fontWeight = '500';
        } else {
            fileNameDisplay.textContent = 'Click to select a PDF file';
            fileNameDisplay.style.color = '';
            fileNameDisplay.style.fontWeight = '';
        }
    });

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const file = pdfFileInput.files[0];
        if (!file) {
            alert("Please select a file first.");
            return;
        }

        // Setup UI for processing
        uploadBtn.disabled = true;
        pdfFileInput.disabled = true;
        uploadForm.style.display = 'none';
        
        statusArea.style.display = 'block';
        resultMessage.textContent = 'Processing...';
        resultMessage.className = 'result-message';
        processingSpinner.style.display = 'block';

        // Start 10-minute timer (600 seconds)
        let secondsLeft = 600;
        updateTimerDisplay(secondsLeft);
        
        timerInterval = setInterval(() => {
            secondsLeft--;
            updateTimerDisplay(secondsLeft);
            
            if (secondsLeft <= 0) {
                clearInterval(timerInterval);
                showResult('Timeout', false);
            }
        }, 1000);

        // Prepare FormData for the API call
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Note: do not set Content-Type header manually for multipart/form-data
            // The browser will set it with the required boundary parameter automatically
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'accept': 'application/json'
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            
            // If response received before timer finishes
            if (secondsLeft > 0) {
                clearInterval(timerInterval);
                showResult('yes', true);
            }

        } catch (error) {
            console.error('Upload Error:', error);
            if (secondsLeft > 0) {
                clearInterval(timerInterval);
                showResult(`Error: ${error.message}`, false);
            }
        }
    });

    function updateTimerDisplay(totalSeconds) {
        if (totalSeconds < 0) totalSeconds = 0;
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    function showResult(message, isSuccess) {
        processingSpinner.style.display = 'none';
        
        if (isSuccess && message === 'yes') {
            resultMessage.innerHTML = 'yes <i class="fa-solid fa-check-circle" style="margin-left:8px;"></i>';
            resultMessage.className = 'result-message success';
        } else {
            resultMessage.textContent = message;
            resultMessage.className = 'result-message error';
        }
        
        // Return to upload screen after 5 seconds to upload another file
        setTimeout(() => {
            uploadBtn.disabled = false;
            pdfFileInput.disabled = false;
            uploadForm.style.display = 'block';
            statusArea.style.display = 'none';
            // Reset file input
            pdfFileInput.value = '';
            fileNameDisplay.textContent = 'Click to select a PDF file';
            fileNameDisplay.style.color = '';
            fileNameDisplay.style.fontWeight = '';
        }, 5000);
    }
});
