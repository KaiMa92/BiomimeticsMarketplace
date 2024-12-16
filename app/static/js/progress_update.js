document.getElementById('searchForm').onsubmit = function(event) {
    event.preventDefault();

    var userInput = document.getElementById('search').value;
    var source = new EventSource('/start?query=' + encodeURIComponent(userInput));

    // Show the progress container when we start
    var progressContainer = document.getElementById('progress-container');
    var progressCircle = document.getElementById('progress-circle');
    var progressText = document.getElementById('progress-text');
    progressContainer.style.display = 'flex';

    source.onmessage = function(event) {
        // Update the displayed text to the current progress message
        progressText.textContent = event.data;

        console.log('Progress update:', event.data); // Debugging
    };

    // When we receive the 'done' event, we're finished. Close SSE and redirect.
    source.addEventListener('done', function(event) {
        source.close();
        console.log('Received done event with data:', event.data); // Debugging
        var data = JSON.parse(event.data);
        var queryId = data.query_id;
        console.log('Extracted queryId:', queryId); // Debugging

        // Hide the progress container and redirect to results page
        progressContainer.style.display = 'none';
        window.location.href = '/results?query_id=' + encodeURIComponent(queryId);
    });

    source.onerror = function(err) {
        console.error("EventSource failed:", err);
        source.close();

        // Hide progress and show an error message if desired
        progressContainer.style.display = 'none';
        alert("An error occurred while processing your request. Please try again.");
    };
};

