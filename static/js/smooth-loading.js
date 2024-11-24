// Handle smooth loading of images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        // Add loaded class when image is loaded
        img.addEventListener('load', function() {
            this.classList.add('loaded');
        });
        
        // If image is already cached, add loaded class immediately
        if (img.complete) {
            img.classList.add('loaded');
        }
    });

    // Handle fade-in elements
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    fadeElements.forEach(element => {
        observer.observe(element);
    });

    // Add smooth scrolling to all internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add page transition on navigation
    const links = document.querySelectorAll('a:not([href^="#"])');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.hostname === window.location.hostname) {
                e.preventDefault();
                document.body.classList.add('page-transition');
                setTimeout(() => {
                    window.location = this.href;
                }, 300);
            }
        });
    });
});
