// Carrusel de Ofertas - Glamoure
class CarouselOfertas {
    constructor() {
        this.currentSlide = 0;
        this.track = document.querySelector('.carousel-track');
        this.slides = document.querySelectorAll('.carousel-slide');
        this.indicators = document.querySelectorAll('.indicator');
        this.prevBtn = document.querySelector('.carousel-nav.prev');
        this.nextBtn = document.querySelector('.carousel-nav.next');
        this.autoplayInterval = null;
        this.autoplayDelay = 4000; // 4 segundos
        this.isTransitioning = false;
        
        if (!this.track || this.slides.length === 0) return;
        
        this.init();
    }
    
    init() {
        // Event listeners para botones
        this.prevBtn?.addEventListener('click', () => this.prevSlide());
        this.nextBtn?.addEventListener('click', () => this.nextSlide());
        
        // Event listeners para indicadores
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => this.goToSlide(index));
        });
        
        // Pausar autoplay al hacer hover
        const container = document.querySelector('.carousel-container');
        container?.addEventListener('mouseenter', () => this.stopAutoplay());
        container?.addEventListener('mouseleave', () => this.startAutoplay());
        
        // Soporte táctil para móviles
        this.setupTouchEvents();
        
        // Iniciar autoplay
        this.startAutoplay();
        
        // Actualizar indicadores
        this.updateIndicators();
    }
    
    getVisibleSlides() {
        const width = window.innerWidth;
        if (width < 768) return 1;
        if (width < 1024) return 2;
        return 3;
    }
    
    getMaxSlide() {
        return Math.max(0, this.slides.length - this.getVisibleSlides());
    }
    
    nextSlide() {
        if (this.isTransitioning) return;
        
        const maxSlide = this.getMaxSlide();
        
        if (this.currentSlide >= maxSlide) {
            this.currentSlide = 0;
        } else {
            this.currentSlide++;
        }
        
        this.updateCarousel();
    }
    
    prevSlide() {
        if (this.isTransitioning) return;
        
        const maxSlide = this.getMaxSlide();
        
        if (this.currentSlide <= 0) {
            this.currentSlide = maxSlide;
        } else {
            this.currentSlide--;
        }
        
        this.updateCarousel();
    }
    
    goToSlide(index) {
        if (this.isTransitioning) return;
        
        const maxSlide = this.getMaxSlide();
        this.currentSlide = Math.min(index, maxSlide);
        this.updateCarousel();
        this.stopAutoplay();
        this.startAutoplay();
    }
    
    updateCarousel() {
        this.isTransitioning = true;
        
        const slideWidth = this.slides[0].offsetWidth;
        const gap = 30; // Gap entre slides
        const offset = -(this.currentSlide * (slideWidth + gap));
        
        this.track.style.transform = `translateX(${offset}px)`;
        this.updateIndicators();
        
        setTimeout(() => {
            this.isTransitioning = false;
        }, 600);
    }
    
    updateIndicators() {
        this.indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentSlide);
        });
    }
    
    startAutoplay() {
        this.stopAutoplay();
        this.autoplayInterval = setInterval(() => {
            this.nextSlide();
        }, this.autoplayDelay);
    }
    
    stopAutoplay() {
        if (this.autoplayInterval) {
            clearInterval(this.autoplayInterval);
            this.autoplayInterval = null;
        }
    }
    
    setupTouchEvents() {
        let touchStartX = 0;
        let touchEndX = 0;
        
        this.track.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
            this.stopAutoplay();
        }, { passive: true });
        
        this.track.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe(touchStartX, touchEndX);
            this.startAutoplay();
        }, { passive: true });
    }
    
    handleSwipe(startX, endX) {
        const swipeThreshold = 50;
        const diff = startX - endX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                this.nextSlide();
            } else {
                this.prevSlide();
            }
        }
    }
}

// Inicializar el carrusel cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    const carousel = new CarouselOfertas();
    
    // Reinicializar en resize para responsive
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (carousel.track) {
                carousel.currentSlide = 0;
                carousel.updateCarousel();
            }
        }, 250);
    });
});
