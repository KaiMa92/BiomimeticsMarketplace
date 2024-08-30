$(document).ready(function() {
    // Event listener for like buttons
    $('.like-button').on('click', function() {
        const resultId = $(this).closest('.carousel-item').data('id');
        const title = $(this).data('title');
        const queryId = $(this).data('query-id');  // Get the query ID
        updateLikeDislike(resultId, title, queryId, 'like');
    });

    // Event listener for dislike buttons
    $('.dislike-button').on('click', function() {
        const resultId = $(this).closest('.carousel-item').data('id');
        const title = $(this).data('title');
        const queryId = $(this).data('query-id');  // Get the query ID
        updateLikeDislike(resultId, title, queryId, 'dislike');
    });

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
});
