/**
 * OPTIMIZACIONES JAVASCRIPT PARA MEJORAR RENDIMIENTO
 * Implementa estas mejoras en tus archivos JS
 */

// 1. Debounce para búsquedas y filtros
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Uso: 
// const buscarProductos = debounce(function(termino) {
//     // Lógica de búsqueda
// }, 300);

// 2. Lazy loading de imágenes
const lazyLoadImages = () => {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
};

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', lazyLoadImages);
} else {
    lazyLoadImages();
}

// 3. Cache de solicitudes AJAX
const cache = new Map();

async function fetchWithCache(url, options = {}) {
    const cacheKey = url + JSON.stringify(options);
    
    if (cache.has(cacheKey)) {
        return cache.get(cacheKey);
    }
    
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        cache.set(cacheKey, data);
        return data;
    } catch (error) {
        console.error('Error en fetch:', error);
        throw error;
    }
}

// 4. Optimizar actualizaciones del carrito
let carritoUpdateTimeout;
function actualizarCarritoOptimizado(itemId, accion) {
    clearTimeout(carritoUpdateTimeout);
    
    carritoUpdateTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/carrito/item/${itemId}/${accion}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                actualizarUICarrito(data);
            }
        } catch (error) {
            console.error('Error actualizando carrito:', error);
        }
    }, 500);
}

// 5. Obtener CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 6. Preload de recursos críticos
function preloadCriticalResources() {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'image';
    link.href = '/static/imagenes/logo.png';
    document.head.appendChild(link);
}

// 7. Virtual scrolling para listas largas (si tienes muchos productos)
class VirtualScroll {
    constructor(container, items, itemHeight) {
        this.container = container;
        this.items = items;
        this.itemHeight = itemHeight;
        this.visibleItems = Math.ceil(container.clientHeight / itemHeight);
        this.init();
    }

    init() {
        this.container.addEventListener('scroll', this.handleScroll.bind(this));
        this.render();
    }

    handleScroll() {
        requestAnimationFrame(() => this.render());
    }

    render() {
        const scrollTop = this.container.scrollTop;
        const startIndex = Math.floor(scrollTop / this.itemHeight);
        const endIndex = Math.min(startIndex + this.visibleItems, this.items.length);

        // Renderizar solo items visibles
        this.container.innerHTML = '';
        for (let i = startIndex; i < endIndex; i++) {
            const item = this.items[i];
            // Crear elemento del producto
            const element = this.createProductElement(item);
            element.style.transform = `translateY(${i * this.itemHeight}px)`;
            this.container.appendChild(element);
        }
    }

    createProductElement(item) {
        const div = document.createElement('div');
        div.className = 'producto-item';
        div.innerHTML = `
            <img src="${item.imagen}" alt="${item.nombre}" loading="lazy">
            <h3>${item.nombre}</h3>
            <p>$${item.precio}</p>
        `;
        return div;
    }
}

// 8. Performance monitoring
if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            if (entry.duration > 100) {
                console.warn(`Tarea lenta detectada: ${entry.name} - ${entry.duration}ms`);
            }
        }
    });
    observer.observe({ entryTypes: ['measure'] });
}

// 9. Prefetch de páginas al hacer hover
document.querySelectorAll('a[data-prefetch]').forEach(link => {
    link.addEventListener('mouseenter', function() {
        const url = this.href;
        const linkTag = document.createElement('link');
        linkTag.rel = 'prefetch';
        linkTag.href = url;
        document.head.appendChild(linkTag);
    }, { once: true });
});

// 10. Reducir trabajo del main thread
function yieldToMain() {
    return new Promise(resolve => {
        setTimeout(resolve, 0);
    });
}

async function procesamientoHeavy(data) {
    for (let i = 0; i < data.length; i++) {
        // Procesar item
        procesarItem(data[i]);
        
        // Ceder al main thread cada 50 items
        if (i % 50 === 0) {
            await yieldToMain();
        }
    }
}
