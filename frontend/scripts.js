document.getElementById('recap-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const year = document.getElementById('year').value;
    const week = document.getElementById('week').value;
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');

    // Show loading indicator and hide previous results/errors
    loadingDiv.style.display = 'block';
    resultsDiv.style.display = 'none';
    errorDiv.style.display = 'none';

    try {
        const response = await fetch('/api/generate_recap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                year: parseInt(year),
                week: parseInt(week)
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Something went wrong');
        }

        const data = await response.json();

        // Populate the results
        document.getElementById('summary-text').textContent = data.summary;
        document.getElementById('audio-player').src = data.audioUrl;
        
        // Show the results
        resultsDiv.style.display = 'block';

    } catch (error) {
        errorDiv.textContent = `Error: ${error.message}`;
        errorDiv.style.display = 'block';
    } finally {
        loadingDiv.style.display = 'none';
    }
});