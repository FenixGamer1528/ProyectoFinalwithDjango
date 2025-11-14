// Carrusel de Lo Más Vendido - Glamoure
class CarouselMasVendido {
    constructor(containerId, trackId, indicatorsId) {
        this.currentSlide = 0;
        this.container = document.getElementById(containerId);
        this.track = document.getElementById(trackId);
        this.indicators = document.querySelectorAll(`#${indicatorsId} .indicator`);
        this.slides = this.track?.querySelectorAll('.carousel-slide') || [];
        this.autoplayInterval = null;
        this.autoplayDelay = 4000;
        this.isTransitioning = false;
        
        if (!this.track || this.slides.length === 0) return;
        
        this.init();
    }
    
    init() {
        // Pausar autoplay al hacer hover
        this.container?.addEventListener('mouseenter', () => this.stopAutoplay());
        this.container?.addEventListener('mouseleave', () => this.startAutoplay());
        
        // Soporte táctil
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
        return Math.min(4, this.slides.length);
    }
    
    getMaxSlide() {
        return Math.max(0, this.slides.length - this.getVisibleSlides());
    }
    
    nextSlide() {
        if (this.isTransitioning || this.slides.length === 0) return;
        
        const maxSlide = this.getMaxSlide();
        
        if (this.currentSlide >= maxSlide) {
            this.currentSlide = 0;
        } else {
            this.currentSlide++;
        }
        
        this.updateCarousel();
    }
    
    prevSlide() {
        if (this.isTransitioning || this.slides.length === 0) return;
        
        const maxSlide = this.getMaxSlide();
        
        if (this.currentSlide <= 0) {
            this.currentSlide = maxSlide;
        } else {
            this.currentSlide--;
        }
        
        this.updateCarousel();
    }
    
    goToSlide(index) {
        if (this.isTransitioning || this.slides.length === 0) return;
        
        const maxSlide = this.getMaxSlide();
        this.currentSlide = Math.min(index, maxSlide);
        this.updateCarousel();
        this.stopAutoplay();
        this.startAutoplay();
    }
    
    updateCarousel() {
        if (this.slides.length === 0) return;
        
        this.isTransitioning = true;
        
        const slideWidth = this.slides[0].offsetWidth;
        const gap = 20;
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
        if (this.slides.length > 0) {
            this.autoplayInterval = setInterval(() => {
                this.nextSlide();
            }, this.autoplayDelay);
        }
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

// Variable global para el carrusel de más vendido
let masVendidoCarousel;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    masVendidoCarousel = new CarouselMasVendido('mas-vendido-carousel', 'mas-vendido-track', 'mas-vendido-indicators');
    
    // Reinicializar en resize
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (masVendidoCarousel && masVendidoCarousel.track) {
                masVendidoCarousel.currentSlide = 0;
                masVendidoCarousel.updateCarousel();
            }
        }, 250);
    });
});
