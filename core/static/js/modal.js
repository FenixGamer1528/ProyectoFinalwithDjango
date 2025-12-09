// =======================================================
// MODAL.JS - v99999999
// Carrito de compras + Modal de producto
// =======================================================

console.log('✅ Modal.js cargado - versión 99999999');

// ==================== CARRITO DE COMPRAS ====================
function mostrarCarrito() {
    fetch('/carrito/modal/')
        .then(response => response.json())
        .then(data => {
            let contenido = '';
            
            // Verificar si hay items en el carrito
            if (data.items.length === 0) {
                contenido = `
                    <div style="text-align: center; padding: 40px; color: #666;">
                        <p style="font-size: 1.2em; margin-bottom: 10px;">🛒</p>
                        <p>Tu carrito está vacío</p>
                    </div>
                `;
            } else {
                // Generar HTML de los items
                data.items.forEach(item => {
                    contenido += `
                        <div class="item-carrito">
                            <img src="${item.imagen}" alt="${item.producto}" class="img-carrito">
                            <div class="info-carrito">
                                <p><strong>${item.producto}</strong></p>
                                <p>$${item.precio} x ${item.cantidad} = <strong>$${item.subtotal}</strong></p>
                                <div class="acciones">
                                    <button onclick="cambiarCantidad(${item.id}, 'menos')">➖</button>
                                    <button onclick="cambiarCantidad(${item.id}, 'mas')">➕</button>
                                    <button onclick="eliminarItem(${item.id})">❌</button>
                                </div>
                            </div>
                        </div>
                        <hr>
                    `;
                });
            }

            document.getElementById('carritoContenido').innerHTML = contenido;
            
            // Agregar footer con total y botón fuera del body
            const modalContenido = document.querySelector('#carritoModal .modal-contenido');
            let footer = modalContenido.querySelector('.carrito-footer');
            
            // Remover footer existente si hay
            if (footer) {
                footer.remove();
            }
            
            // Crear nuevo footer solo si hay items
            if (data.items.length > 0) {
                footer = document.createElement('div');
                footer.className = 'carrito-footer';
                footer.innerHTML = `
                    <div class="carrito-total">
                        <strong>Total:</strong> 
                        <span>$${data.total.toLocaleString('es-CO')}</span>
                    </div>
                    <a href="/pagos/checkout-carrito/" class="btn-proceder-pago">
                        💳 Procesar la Compra
                    </a>
                `;
                modalContenido.appendChild(footer);
            }
            
            document.getElementById('carritoModal').style.display = 'flex';
        });
}

function eliminarItem(itemId) {
    fetch(`/carrito/eliminar/${itemId}/`).then(() => mostrarCarrito());
}

function cerrarModal() {
    document.getElementById('carritoModal').style.display = 'none';
}

function cambiarCantidad(itemId, accion) {
    fetch(`/carrito/cambiar/${itemId}/${accion}/`).then(() => mostrarCarrito());
}

// ==================== MODAL DE PRODUCTO ====================
document.addEventListener('DOMContentLoaded', () => {
    const productoModal = document.getElementById('productoModal');
    const productoContenido = document.getElementById('productoContenido');

    console.log('🔍 Modal elementos:', {
        productoModal: productoModal ? '✅' : '❌',
        productoContenido: productoContenido ? '✅' : '❌'
    });

    if (!productoModal || !productoContenido) return;

    // Cerrar modal
    window.cerrarProductoModal = function() {
        productoModal.style.display = 'none';
        productoContenido.innerHTML = '';
    };

    // Abrir modal
    window.abrirProductoModal = async function(url) {
        console.log('🚀 Abriendo modal para:', url);
        
        productoModal.style.display = 'flex';
        productoContenido.innerHTML = '<div class="text-center py-8 text-white"><i class="fas fa-spinner fa-spin text-4xl text-[#C0A76B]"></i><p class="mt-4">Cargando...</p></div>';

        try {
            const modalUrl = url + (url.includes('?') ? '&' : '?') + 'modal=true';
            const response = await fetch(modalUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const html = await response.text();
            productoContenido.innerHTML = html;
            console.log('✅ Modal cargado correctamente');
            
            // EJECUTAR SCRIPTS DEL MODAL DESPUÉS DE CARGAR EL CONTENIDO
            const scriptMatches = html.match(/<script[^>]*>([\s\S]*?)<\/script>/gi);
            if (scriptMatches) {
                scriptMatches.forEach((scriptTag, index) => {
                    const scriptContent = scriptTag.replace(/<script[^>]*>|<\/script>/gi, '');
                    try {
                        console.log(`🔧 Ejecutando script ${index + 1} del modal...`);
                        eval(scriptContent);
                        console.log(`✅ Script ${index + 1} ejecutado correctamente`);
                    } catch (error) {
                        console.error(`❌ Error en script ${index + 1}:`, error);
                    }
                });
            }
            
        } catch (error) {
            console.error('❌ Error:', error);
            productoContenido.innerHTML = `
                <button class="cerrar text-white text-4xl absolute top-4 right-6" onclick="cerrarProductoModal()">&times;</button>
                <div class="text-center py-12 text-red-400">
                    <i class="fas fa-exclamation-triangle text-5xl mb-4"></i>
                    <p class="text-lg">Error al cargar</p>
                    <p class="text-sm mt-2">${error.message}</p>
                </div>
            `;
        }
    };

    // Event listener global para .ver-detalles-btn
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.ver-detalles-btn');
        if (btn) {
            console.log('👆 Click en Ver detalles');
            e.preventDefault();
            e.stopPropagation();
            abrirProductoModal(btn.getAttribute('href'));
            return false;
        }
    });

    // Cerrar con ESC
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && productoModal.style.display === 'flex') {
            cerrarProductoModal();
        }
    });

    // Cerrar al hacer clic fuera
    productoModal.addEventListener('click', (e) => {
        if (e.target === productoModal) cerrarProductoModal();
    });
});


// ==================== SISTEMA DE DESEOS ====================
function toggleFavorito(productoId, button) {
    // Obtener el token CSRF
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/toggle-favorito/${productoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const icon = button.querySelector('i');
            
            if (data.is_favorito) {
                // Producto agregado a favoritos
                icon.classList.remove('fa-regular');
                icon.classList.add('fa-solid');
                icon.style.color = '#C0A76B'; // Dorado cuando está en favoritos
                button.style.background = 'rgba(255, 255, 255, 0.95)'; // Botón siempre blanco
                button.setAttribute('data-favorito', 'true');
                button.setAttribute('title', 'Eliminar de mis deseos');
                
                // Animación de feedback
                button.classList.add('animate-bounce');
                setTimeout(() => button.classList.remove('animate-bounce'), 500);
            } else {
                // Producto eliminado de favoritos
                icon.classList.remove('fa-solid');
                icon.classList.add('fa-regular');
                icon.style.color = '#666'; // Gris cuando NO está en favoritos
                button.style.background = 'rgba(255, 255, 255, 0.95)'; // Botón siempre blanco
                button.setAttribute('data-favorito', 'false');
                button.setAttribute('title', 'Agregar a mis deseos');
            }
            
            // Actualizar contador de deseos en el header si existe
            actualizarContadorDeseos(data.total_favorites);
            
            // Mostrar mensaje de éxito
            mostrarNotificacion(data.is_favorito ? 'Agregado a mis deseos ❤️' : 'Eliminado de mis deseos', data.is_favorito ? 'success' : 'info');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Hubo un error. Por favor, intenta de nuevo.', 'error');
    });
}

// Función para eliminar favorito (usada en página de Mis Deseos)
function eliminarFavorito(productoId, button) {
    console.log('🗑️ Iniciando eliminación de favorito:', productoId);
    
    const csrftoken = getCookie('csrftoken');
    
    if (!csrftoken) {
        console.error('❌ No se encontró el token CSRF');
        mostrarNotificacion('Error de seguridad. Recarga la página.', 'error');
        return;
    }
    
    // Deshabilitar botón para evitar múltiples clicks
    button.disabled = true;
    button.style.opacity = '0.5';
    
    console.log('📤 Enviando petición a /toggle-favorito/' + productoId + '/');
    
    fetch(`/toggle-favorito/${productoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        console.log('📥 Respuesta recibida:', response.status, response.statusText);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('✅ Datos recibidos:', data);
        
        if (data.success) {
            // Eliminar la tarjeta con animación
            const card = button.closest('.carousel-slide');
            console.log('🎯 Tarjeta encontrada:', card ? 'Sí' : 'No');
            
            if (card) {
                card.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => {
                    card.remove();
                    console.log('🗑️ Tarjeta eliminada del DOM');
                    
                    // Si no quedan productos, recargar la página
                    const remainingProducts = document.querySelectorAll('.carousel-slide').length;
                    console.log('📊 Productos restantes:', remainingProducts);
                    
                    if (remainingProducts === 0) {
                        console.log('🔄 Recargando página...');
                        location.reload();
                    }
                }, 300);
            }
            
            // Actualizar contador
            actualizarContadorDeseos(data.total_favorites);
            
            // Mostrar notificación
            mostrarNotificacion('Eliminado de mis deseos', 'info');
        } else {
            console.error('❌ La operación no fue exitosa:', data);
            button.disabled = false;
            button.style.opacity = '1';
            mostrarNotificacion(data.mensaje || 'Error al eliminar el producto', 'error');
        }
    })
    .catch(error => {
        console.error('❌ Error al eliminar favorito:', error);
        button.disabled = false;
        button.style.opacity = '1';
        mostrarNotificacion('Hubo un error al eliminar el producto: ' + error.message, 'error');
    });
}

// Función auxiliar para obtener el CSRF token
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

// Actualizar contador de deseos en el header
function actualizarContadorDeseos(total) {
    const wishlistLinks = document.querySelectorAll('a[href*="mis_deseos"]');
    wishlistLinks.forEach(link => {
        const counter = link.querySelector('span');
        if (counter) {
            counter.textContent = total;
            
            // Animar el contador
            counter.style.transform = 'scale(1.3)';
            setTimeout(() => {
                counter.style.transform = 'scale(1)';
            }, 200);
        }
    });
}

// Mostrar notificaciones temporales
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear el elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = 'notificacion-favorito';
    notificacion.textContent = mensaje;
    
    // Estilos según el tipo - DORADO para success e info (agregar/eliminar deseos)
    let bgColor = 'linear-gradient(135deg, #C0A76B, #d4b876, #e6c98a)'; // Dorado por defecto
    let textColor = '#000';
    let boxShadow = '0 8px 25px rgba(192, 167, 107, 0.6), 0 0 30px rgba(192, 167, 107, 0.4)';
    
    if (tipo === 'error') {
        bgColor = '#f44336';
        textColor = 'white';
        boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
    }
    // Tanto 'success' como 'info' usan el estilo dorado
    
    notificacion.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${bgColor};
        color: ${textColor};
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: ${boxShadow};
        z-index: 9999;
        font-weight: 600;
        animation: slideIn 0.3s ease;
    `;
    
    // Agregar al DOM
    document.body.appendChild(notificacion);
    
    // Eliminar después de 3 segundos
    setTimeout(() => {
        notificacion.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notificacion);
        }, 300);
    }, 3000);
}

// Agregar animaciones CSS
if (!document.getElementById('favoritos-animations')) {
    const style = document.createElement('style');
    style.id = 'favoritos-animations';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
        
        @keyframes fadeOut {
            from {
                opacity: 1;
                transform: scale(1);
            }
            to {
                opacity: 0;
                transform: scale(0.8);
            }
        }
        
        .animate-bounce {
            animation: bounce 0.5s ease;
        }
        
        @keyframes bounce {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.2);
            }
        }
    `;
    document.head.appendChild(style);
}

