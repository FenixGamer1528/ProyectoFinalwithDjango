function mostrarCarrito() {
    fetch('/carrito/modal/')
        .then(response => response.json())
        .then(data => {
            let contenido = '';
            data.items.forEach(item => {
                contenido += `
                    <p>
                        ${item.producto} x ${item.cantidad} = $${item.subtotal}
                        <button onclick="eliminarItem(${item.id})">❌</button>
                    </p>
                `;
            });
            contenido += `<hr><p><strong>Total:</strong> $${data.total}</p>`;

            document.getElementById('carritoContenido').innerHTML = contenido;
            document.getElementById('carritoModal').style.display = 'block';
        });
}

function eliminarItem(itemId) {
    fetch(`/carrito/eliminar/${itemId}/`)
        .then(() => {
            mostrarCarrito();  // recarga el modal
        });
}

function cerrarModal() {
    document.getElementById('carritoModal').style.display = 'none';
}