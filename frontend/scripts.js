document.getElementById('recap-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');

    // Show loading indicator and hide previous results/errors
    loadingDiv.style.display = 'block';
    resultsDiv.style.display = 'none';
    errorDiv.style.display = 'none';

    try {
        const response = await fetch('/api/generate-recap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}), // No parameters needed - uses most recent week
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Something went wrong');
        }

        const data = await response.json();

        if (data.success) {
            // Populate the results
            document.getElementById('summary-text').textContent = data.summary;
            document.getElementById('audio-player').src = `/api/audio/${data.audio_filename}`;
            
            // Show the results
            resultsDiv.style.display = 'block';
        } else {
            throw new Error(data.message || 'Failed to generate recap');
        }

    } catch (error) {
        errorDiv.textContent = `Error: ${error.message}`;
        errorDiv.style.display = 'block';
    } finally {
        loadingDiv.style.display = 'none';
    }
});

// Add a function to get league info on page load
async function loadLeagueInfo() {
    try {
        const response = await fetch('/api/league-info');
        if (response.ok) {
            const data = await response.json();
            // You could display league info here if desired
            console.log('League info loaded:', data);
        }
    } catch (error) {
        console.log('Could not load league info:', error);
    }
}

// Load league info when page loads
document.addEventListener('DOMContentLoaded', loadLeagueInfo);