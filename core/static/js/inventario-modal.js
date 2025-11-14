// ==================== MODAL DE INVENTARIO ====================
document.addEventListener('DOMContentLoaded', function() {
    const inventarioModal = document.getElementById('inventarioModal');
    const inventarioContent = document.getElementById('inventarioContent');
    const closeInventarioModal = document.getElementById('closeInventarioModal');
    const inventarioCompletoBtn = document.getElementById('inventarioCompletoBtn');

    if (!inventarioModal || !inventarioContent || !closeInventarioModal) {
        return; // No hacer nada si los elementos no existen
    }

    // Función para mostrar el inventario completo de todos los productos
    window.showInventarioCompleto = async function() {
        try {
            const response = await fetch('/dashboard/api/inventario/completo/');
            const inventario = await response.json();

            if (inventario.length === 0) {
                inventarioContent.innerHTML = `
                    <div class="text-center py-8 text-gray-400">
                        <i class="fas fa-box-open text-5xl mb-4"></i>
                        <p>No hay productos en el inventario.</p>
                    </div>
                `;
            } else {
                // Agrupar por producto
                const productosMap = {};
                inventario.forEach(item => {
                    if (!productosMap[item.producto_id]) {
                        productosMap[item.producto_id] = {
                            nombre: item.producto_nombre,
                            imagen: item.producto_imagen,
                            variantes: []
                        };
                    }
                    productosMap[item.producto_id].variantes.push(item);
                });

                let html = `
                    <div class="space-y-6 max-h-[70vh] overflow-y-auto">
                `;

                Object.values(productosMap).forEach(producto => {
                    const totalStock = producto.variantes.reduce((sum, v) => sum + v.stock, 0);
                    
                    html += `
                        <div class="bg-gray-900 rounded-lg overflow-hidden border border-[#C0A76B] border-opacity-30">
                            <div class="flex items-center gap-4 p-4 bg-black bg-opacity-30">
                                ${producto.imagen ? `
                                    <img src="${producto.imagen}" alt="${producto.nombre}" 
                                         class="w-16 h-16 object-cover rounded"
                                         onerror="this.src='https://placehold.co/64x64/1a1a1a/C0A76B?text=Sin+Imagen'">
                                ` : `
                                    <div class="w-16 h-16 bg-gray-800 rounded flex items-center justify-center">
                                        <i class="fas fa-image text-gray-600"></i>
                                    </div>
                                `}
                                <div class="flex-1">
                                    <h3 class="font-bold text-lg text-white">${producto.nombre}</h3>
                                    <p class="text-sm text-gray-400">
                                        ${producto.variantes.length} variante(s) · 
                                        <span class="${totalStock > 20 ? 'text-green-400' : totalStock > 10 ? 'text-yellow-400' : 'text-red-400'}">
                                            Stock total: ${totalStock}
                                        </span>
                                    </p>
                                </div>
                            </div>
                            <div class="overflow-x-auto">
                                <table class="w-full">
                                    <thead class="bg-[#C0A76B] bg-opacity-10">
                                        <tr>
                                            <th class="px-4 py-2 text-left text-[#C0A76B] text-sm">Talla</th>
                                            <th class="px-4 py-2 text-left text-[#C0A76B] text-sm">Color</th>
                                            <th class="px-4 py-2 text-right text-[#C0A76B] text-sm">Stock</th>
                                            <th class="px-4 py-2 text-right text-[#C0A76B] text-sm">Precio</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                    `;

                    producto.variantes.forEach(v => {
                        const stockClass = v.stock >= 10 ? 'text-green-400' : v.stock >= 5 ? 'text-yellow-400' : 'text-red-400';
                        html += `
                            <tr class="border-t border-gray-800 hover:bg-gray-800 transition-all">
                                <td class="px-4 py-2 font-semibold text-sm">${v.talla}</td>
                                <td class="px-4 py-2 text-sm">${v.color}</td>
                                <td class="px-4 py-2 text-right font-bold ${stockClass} text-sm">${v.stock}</td>
                                <td class="px-4 py-2 text-right text-[#C0A76B] font-semibold text-sm">$${v.precio.toLocaleString()}</td>
                            </tr>
                        `;
                    });

                    html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;
                });

                html += `
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-700 text-center">
                        <p class="text-sm text-gray-400">
                            Total de productos: <span class="text-[#C0A76B] font-bold">${Object.keys(productosMap).length}</span> · 
                            Total de variantes: <span class="text-[#C0A76B] font-bold">${inventario.length}</span>
                        </p>
                    </div>
                `;

                inventarioContent.innerHTML = html;
            }

            inventarioModal.classList.remove('hidden');
        } catch (error) {
            console.error('Error cargando inventario completo:', error);
            inventarioContent.innerHTML = `
                <div class="text-center py-8 text-red-400">
                    <i class="fas fa-exclamation-triangle text-5xl mb-4"></i>
                    <p>Error al cargar el inventario completo</p>
                </div>
            `;
            inventarioModal.classList.remove('hidden');
        }
    }

    // Event listener para el botón de inventario completo
    if (inventarioCompletoBtn) {
        inventarioCompletoBtn.addEventListener('click', showInventarioCompleto);
    }

    closeInventarioModal.addEventListener('click', () => {
        inventarioModal.classList.add('hidden');
    });

    // Cerrar modal de inventario con ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !inventarioModal.classList.contains('hidden')) {
            inventarioModal.classList.add('hidden');
        }
    });
});
