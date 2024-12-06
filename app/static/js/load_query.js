// static/js/load_query.js

$(document).ready(function () {
    console.log('Using queryId:', queryId); // Debugging

    // Function to fetch query results from the server
    function fetchQueryResults(queryId) {
        // Make an AJAX request to get the results
        $.getJSON('/api/results/' + queryId, function (data) {
            if (data.error) {
                $('#no-results-message').show();
            } else {
                if (data.result && data.result.length > 0) {
                    renderResults(data.result);  // Render the actual results
                    // Initialize the carousel after loading results
                    $('#results-carousel').slick();
                } else {
                    $('#no-results-message').show();  // Show "No results found" message
                }
            }
        }).fail(function () {
            $('#results-carousel').html('<p>Error loading results. Please try again later.</p>');
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

