// static/js/load_query.js

$(document).ready(function () {
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
                        <button class="like-button" data-title="${result.title}">Like</button>
                        <button class="dislike-button" data-title="${result.title}">Dislike</button>
                    </div>
                </div>
            `;
        });
        $('#results-carousel').html(html);

        // Reattach event listeners for dynamically added elements
        window.attachButtonListeners();

        // Initialize the carousel after loading results
        $('#results-carousel').slick();
    }

    // Call the function to render results when the page loads
    renderResults(resultsData);
});

