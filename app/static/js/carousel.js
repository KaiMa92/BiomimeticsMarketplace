// static/js/carousel.js
$(document).ready(function() {
    // Function to initialize the Slick carousel
    function initializeCarousel() {
        $('.carousel').slick({
            infinite: true,
            slidesToShow: 1,
            slidesToScroll: 1,
            arrows: true,
            autoplay: false
        });
    }

    // Export the function to be used in other files
    window.initializeCarousel = initializeCarousel;
});

