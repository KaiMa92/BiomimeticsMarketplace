// static/js/load_query.js
$(document).ready(function () {
    // Function to fetch query results from the server
    function fetchQueryResults(queryId) {
        $.ajax({
            url: `/get-results/${queryId}`,  // Flask route to fetch results
            method: 'GET',
            success: function (data) {
                if (data && data.results.length > 0) {
                    renderResults(data.results);  // Render the actual results
                    window.initializeCarousel(); // Initialize the carousel after loading results
                } else {
                    $('#no-results-message').show();  // Show "No results found" message
                }
            },
            error: function (err) {
                $('#results-carousel').html('<p>Error loading results. Please try again later.</p>');
            }
        });
    }

    // Function to render results into the carousel
    function renderResults(results) {
        let html = '';
        results.forEach(result => {
            html += `
                <div class="carousel-item" data-id="${result._id}">
                    <div class="carousel-image-wrapper">
                        <img src="${result.image}" alt="${result.title}" class="carousel-image">
                        <div class="carousel-title">${result.title}</div>
                    </div>
                    <p>${result.description}</p>
                    <div class="carousel-actions">
                        <button class="like-button" data-title="${result.title}" data-query-id="${queryId}">Like</button>
                        <button class="dislike-button" data-title="${result.title}" data-query-id="${queryId}">Dislike</button>
                    </div>
                </div>
            `;
        });
        $('#results-carousel').html(html);

        // Reattach event listeners for dynamically added elements
        window.attachButtonListeners();
    }

    // Call the function to fetch query results when the page loads
    fetchQueryResults(queryId);
});
