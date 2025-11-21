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
                
                // 🆕 AGREGAR TOTAL Y BOTÓN DE PAGO
                contenido += `
                    <div class="carrito-footer">
                        <div class="carrito-total">
                            <strong>Total:</strong> 
                            <span style="color: #667eea; font-size: 1.3em;">$${data.total.toLocaleString('es-CO')}</span>
                        </div>
                        <a href="/pagos/checkout-carrito/" class="btn-proceder-pago">
                            Proceder al Pago
                        </a>
                    </div>
                `;
            }

            document.getElementById('carritoContenido').innerHTML = contenido;
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
