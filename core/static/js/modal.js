function mostrarCarrito() {
    fetch('/carrito/carrito/modal/')
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
