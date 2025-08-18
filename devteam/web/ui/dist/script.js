document.addEventListener('DOMContentLoaded', () => {
    const startBuildBtn = document.getElementById('start-build');
    const goalTextarea = document.getElementById('goal');
    const logContainer = document.getElementById('log-container');
    const filesTabs = document.getElementById('files-tabs');
    const codeDisplay = document.querySelector('#code-display pre code');

    let sessionId = 'default'; // Keep track of the session

    startBuildBtn.addEventListener('click', async () => {
        const goal = goalTextarea.value;
        if (!goal) {
            alert('Please enter a high-level goal.');
            return;
        }

        logContainer.innerHTML = ''; // Clear previous logs
        filesTabs.innerHTML = '';
        codeDisplay.textContent = '';
        logMessage('Build started...');

        try {
            const response = await fetch('http://localhost:8082/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: goal, session: `session-${Date.now()}` }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Build failed to start.');
            }

            sessionId = data.session_id;
            logMessage(`Build started with session ID: ${sessionId}`);
            logMessage('Polling for file updates...');

            // Poll for files every 2 seconds
            const intervalId = setInterval(async () => {
                const files = await fetchFiles(sessionId);
                if (files && Object.keys(files).length > 0) {
                    logMessage('Build complete! Displaying files.');
                    displayFiles(files);
                    clearInterval(intervalId); // Stop polling
                }
            }, 2000);

        } catch (error) {
            logMessage('Error: ' + error.message);
            console.error('Error:', error);
        }
    });

    async function fetchFiles(sessionId) {
        try {
            const response = await fetch(`http://localhost:8082/files?session_id=${sessionId}`);
            if (!response.ok) return null;
            const data = await response.json();
            return data.files;
        } catch (error) {
            console.error('Error fetching files:', error);
            return null;
        }
    }

    function displayFiles(files) {
        filesTabs.innerHTML = '';
        const fileNames = Object.keys(files);

        fileNames.forEach((fileName, index) => {
            const tab = document.createElement('button');
            tab.className = 'px-4 py-2 text-sm font-medium border-b-2';
            tab.textContent = fileName;
            tab.onclick = () => {
                // Deactivate other tabs
                document.querySelectorAll('#files-tabs button').forEach(t => t.classList.remove('border-blue-500', 'text-white'));
                // Activate this tab
                tab.classList.add('border-blue-500', 'text-white');
                codeDisplay.textContent = files[fileName];
            };
            filesTabs.appendChild(tab);

            // Activate the first tab by default
            if (index === 0) {
                tab.click();
            }
        });
    }

    function logMessage(message) {
        const logEntry = document.createElement('div');
        logEntry.textContent = message;
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }
});
