// ========================================================================
// === CÓDIGO ORIGINAL DEL CARRITO DE COMPRAS (SE MANTIENE SIN CAMBIOS) ===
// ========================================================================

function mostrarCarrito() {
    fetch('/carrito/modal/')
        .then(response => response.json())
        .then(data => {
            let contenido = '';
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
            contenido += `<p style="text-align:right"><strong>Total:</strong> $${data.total}</p>`;

            document.getElementById('carritoContenido').innerHTML = contenido;
            document.getElementById('carritoModal').style.display = 'flex';
        });
}

function eliminarItem(itemId) {
    fetch(`/carrito/eliminar/${itemId}/`)
        .then(() => {
            mostrarCarrito();
        });
}

function cerrarModal() {
    document.getElementById('carritoModal').style.display = 'none';
}

function cambiarCantidad(itemId, accion) {
    fetch(`/carrito/cambiar/${itemId}/${accion}/`)
        .then(() => {
            mostrarCarrito();
        });
}


// ================================================================================
// === NUEVO CÓDIGO PARA EL MODAL DE DETALLES DEL PRODUCTO (SIN CONFLICTOS) ===
// ================================================================================

// Usamos 'DOMContentLoaded' para ejecutar este código solo cuando la página ha cargado.
// Esto evita conflictos y asegura que los elementos HTML existan.
document.addEventListener('DOMContentLoaded', () => {

    // Referencias a los elementos del modal de producto.
    const productoModal = document.getElementById('productoModal');
    const productoContenido = document.getElementById('productoContenido');

    // Función exclusiva para CERRAR el modal de producto.
    function cerrarProductoModal() {
        if (productoModal) {
            productoModal.style.display = 'none';
            productoContenido.innerHTML = ''; 
        }
    }

    // Función para ABRIR el modal de producto y cargar su contenido.
    async function abrirProductoModal(url) {
        if (!productoModal || !productoContenido) {
            console.error("El HTML del modal de producto no se encontró en esta página.");
            return;
        }

        productoModal.style.display = 'flex';
        productoContenido.innerHTML = '<p>Cargando producto...</p>';

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('No se pudo cargar la información del producto.');
            
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            const nombre = doc.querySelector('h1')?.textContent || 'Nombre no disponible';
            const precio = doc.querySelector('.text-xl.text-indigo-600')?.textContent || '$0.00';
            const descripcion = doc.querySelector('.text-gray-600')?.textContent || 'Sin descripción.';
            const imagenSrc = doc.querySelector('img')?.src || '';
            const formHTML = doc.querySelector('form')?.outerHTML || '<p>Opción de compra no disponible.</p>';

            productoContenido.innerHTML = `
                <span class="cerrar" id="cerrarProductoBtn">&times;</span>
                <div class="producto-modal-grid">
                    <div class="producto-modal-imagen">
                        <img src="${imagenSrc}" alt="${nombre}">
                    </div>
                    <div class="producto-modal-detalles">
                        <h1>${nombre}</h1>
                        <p class="precio">${precio}</p>
                        <p class="descripcion">${descripcion}</p>
                        ${formHTML}
                    </div>
                </div>
            `;

            document.getElementById('cerrarProductoBtn').addEventListener('click', cerrarProductoModal);

        } catch (error) {
            productoContenido.innerHTML = `<p>Error: ${error.message}</p><span class="cerrar" id="cerrarProductoBtn">&times;</span>`;
            document.getElementById('cerrarProductoBtn').addEventListener('click', cerrarProductoModal);
        }
    }

    // Escucha clics en TODA la página para detectar si se presiona un botón "Ver detalles".
    document.body.addEventListener('click', (event) => {
        const link = event.target.closest('.ver-detalles-btn');
        if (link) {
            event.preventDefault();
            const url = link.getAttribute('href');
            abrirProductoModal(url);
        }
    });

    // Cierra el modal de producto si se presiona ESC o se hace clic fuera.
    window.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && productoModal && productoModal.style.display === 'flex') {
            cerrarProductoModal();
        }
    });
    window.addEventListener('click', (event) => {
        if (event.target === productoModal) {
            cerrarProductoModal();
        }
    });
});