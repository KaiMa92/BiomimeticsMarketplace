document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.getElementById('carousel');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    let currentIndex = 0;
    const resultsToShow = 2; // Show two results at a time
    const totalResults = carousel.children.length;

    // Show initial results
    updateCarousel();

    prevBtn.addEventListener('click', function() {
        if (currentIndex > 0) {
            currentIndex -= resultsToShow;
            updateCarousel();
        }
    });

    nextBtn.addEventListener('click', function() {
        if (currentIndex + resultsToShow < totalResults) {
            currentIndex += resultsToShow;
            updateCarousel();
        }
    });

    function updateCarousel() {
        for (let i = 0; i < totalResults; i++) {
            if (i >= currentIndex && i < currentIndex + resultsToShow) {
                carousel.children[i].style.display = 'block';
            } else {
                carousel.children[i].style.display = 'none';
            }
        }
    }
});