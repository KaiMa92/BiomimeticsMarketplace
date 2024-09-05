// static/js/buttons.js
$(document).ready(function() {
    // Function to attach event listeners to like and dislike buttons
    function attachButtonListeners() {
        $('.like-button').on('click', function() {
            const resultId = $(this).closest('.carousel-item').data('id');
            const title = $(this).data('title');
            const queryId = $(this).data('query-id');  // Get the query ID
            updateLikeDislike(resultId, title, queryId, 'like');
        });

        $('.dislike-button').on('click', function() {
            const resultId = $(this).closest('.carousel-item').data('id');
            const title = $(this).data('title');
            const queryId = $(this).data('query-id');  // Get the query ID
            updateLikeDislike(resultId, title, queryId, 'dislike');
        });
    }

    // Function to handle like and dislike button actions
    function updateLikeDislike(documentId, title, queryId, action) {
        $.post(`/${action}`, {
            document_id: documentId,
            title: title,
            query_id: queryId  // Include queryId in the POST data
        }).done(function(response) {
            alert(response.message);
        }).fail(function() {
            alert('An error occurred.');
        });
    }

    // Export functions to be used in other files
    window.attachButtonListeners = attachButtonListeners;
});
