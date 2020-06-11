jQuery(document).ready(function ($) {
    "use strict";
    var nav = $('nav');
    var navHeight = nav.outerHeight();

    $('.navbar-toggler').on('click', function () {
        if (!$('#mainNav').hasClass('navbar-reduce')) {
            $('#mainNav').addClass('navbar-reduce');
        }
    })

    // Smooth scrolling using jQuery easing
    $('a.js-scroll[href*="#"]:not([href="#"])').click(function () {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html, body').animate({
                    scrollTop: (target.offset().top - 56)
                }, 1000, "easeInOutExpo");
                return false;
            }
        }
    });

    // Closes responsive menu when a scroll trigger link is clicked
    $('.js-scroll-trigger').click(function () {
        $('.navbar-collapse').collapse('hide');
    });

    // Activate scrollspy to add active class to navbar items on scroll
    $('body').scrollspy({
        target: '#mainNav',
        offset: navHeight
    });


    // Closes responsive menu when a scroll trigger link is clicked
    $('.js-scroll').on("click", function () {
        $('.navbar-collapse').collapse('hide');
    });

    // Activate scrollspy to add active class to navbar items on scroll
    $('body').scrollspy({
        target: '#mainNav',
        offset: navHeight
    });




    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({
            scrollTop: 0
        }, 1500, 'easeInOutExpo');
        return false;
    });



    $(window).trigger('scroll');
    $(window).on('scroll', function () {
        var pixels = 50;
        var top = 1200;
        if ($(window).scrollTop() > pixels) {
            $('.navbar-expand-md').addClass('navbar-reduce');
            $('.navbar-expand-md').removeClass('navbar-trans');
        } else {
            $('.navbar-expand-md').addClass('navbar-trans');
            $('.navbar-expand-md').removeClass('navbar-reduce');
        }
        if ($(window).scrollTop() > top) {
            $('.scrolltop-mf').fadeIn(1000, "easeInOutExpo");
        } else {
            $('.scrolltop-mf').fadeOut(1000, "easeInOutExpo");
        }
    });
});


jQuery(document).ready(function ($) {

    $('#tohash').on('click', function () {
        $('html, body').animate({
            scrollTop: $(this.hash).offset().top - 5
        }, 1000);
        return false;
    });

 

    //Function to prevent Default Events
    function pde(e) {
        if (e.preventDefault)
            e.preventDefault();
        else
            e.returnValue = false;
    }



    /* Pretty Photo */
    // $("a[data-rel^='prettyPhoto']").prettyPhoto();

});


var typed1 = new Typed('.text-slider1', {
    strings: ['英文學習系統', '課程管理系統', 'NUTC learning management system', 'NUTC Elearning system'],
    typeSpeed: 70,
    backSpeed: 30,
    backDelay: 1100,
    smartBackspace: true,
    loop: true
});
var typed2 = new Typed('.text-slider2', {
    strings: ['NUTC learning management system', 'NUTC Elearning system', '英文學習系統', '課程管理系統'],
    typeSpeed: 70,
    backSpeed: 30,
    backDelay: 1100,
    smartBackspace: true,
    loop: true
});
var typed3 = new Typed('.text-slider3', {
    strings: ['NUTC learning management system', 'NUTC Elearning system', '英文學習系統', '課程管理系統'],
    typeSpeed: 70,
    backSpeed: 30,
    backDelay: 1100,
    smartBackspace: true,
    loop: true
});



/* WOW */
var wow = new WOW({
    boxClass: 'wow', // animated element css class (default is wow)
    animateClass: 'animated', // animation css class (default is animated)
    offset: 0, // distance to the element when triggering the animation (default is 0)
    mobile: true // trigger animations on mobile devices (true is default)
});
wow.init();

// Helper function for add element box list in WOW
WOW.prototype.addBox = function (element) {
    this.boxes.push(element);
};

// Init WOW.js and get instance
var wow = new WOW();
wow.init();

// Attach scrollSpy to .wow elements for detect view exit events,
// then reset elements and add again for animation
$('.wow').on('scrollSpy:exit', function () {
    $(this).css({
        'visibility': 'hidden',
        'animation-name': 'none'
    }).removeClass('animated');
    wow.addBox(this);
}).scrollSpy();

