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
                    
                    const productoId = producto.variantes[0]?.producto_id;
                    
                    html += `
                        <div class="bg-gray-900 rounded-lg overflow-hidden border border-[#C0A76B] border-opacity-30 hover:border-[#C0A76B] hover:border-opacity-60 transition-all">
                            <div class="flex items-center gap-4 p-4 bg-black bg-opacity-30">
                                ${producto.imagen ? `
                                    <img src="${producto.imagen}" alt="${producto.nombre}" 
                                         class="w-20 h-20 object-cover rounded-lg border-2 border-[#C0A76B] border-opacity-30"
                                         onerror="this.src='https://placehold.co/64x64/1a1a1a/C0A76B?text=Sin+Imagen'">
                                ` : `
                                    <div class="w-20 h-20 bg-gray-800 rounded-lg border-2 border-[#C0A76B] border-opacity-30 flex items-center justify-center">
                                        <i class="fas fa-image text-gray-600 text-2xl"></i>
                                    </div>
                                `}
                                <div class="flex-1">
                                    <h3 class="font-bold text-xl text-white mb-1">${producto.nombre}</h3>
                                    <p class="text-sm text-gray-400 mb-2">
                                        <i class="fas fa-boxes mr-1"></i>${producto.variantes.length} variante(s) · 
                                        <span class="${totalStock > 20 ? 'text-green-400' : totalStock > 10 ? 'text-yellow-400' : 'text-red-400'} font-semibold">
                                            <i class="fas fa-warehouse mr-1"></i>Stock total: ${totalStock}
                                        </span>
                                    </p>
                                    <a href="/dashboard/producto/${productoId}/variantes/" 
                                       class="inline-flex items-center gap-2 bg-[#C0A76B] hover:bg-yellow-400 text-black font-bold px-4 py-2 rounded-lg transition-all text-sm shadow-lg hover:shadow-[#C0A76B]/50">
                                        <i class="fas fa-cog"></i>
                                        Gestionar Variantes
                                    </a>
                                </div>
                            </div>
                            <div class="overflow-x-auto">
                                <table class="w-full">
                                    <thead class="bg-[#C0A76B] bg-opacity-20 border-b-2 border-[#C0A76B]">
                                        <tr>
                                            <th class="px-4 py-3 text-left text-[#C0A76B] font-bold text-sm">
                                                <i class="fas fa-ruler mr-1"></i>Talla
                                            </th>
                                            <th class="px-4 py-3 text-left text-[#C0A76B] font-bold text-sm">
                                                <i class="fas fa-palette mr-1"></i>Color
                                            </th>
                                            <th class="px-4 py-3 text-right text-[#C0A76B] font-bold text-sm">
                                                <i class="fas fa-boxes mr-1"></i>Stock
                                            </th>
                                            <th class="px-4 py-3 text-right text-[#C0A76B] font-bold text-sm">
                                                <i class="fas fa-tag mr-1"></i>Precio
                                            </th>
                                            <th class="px-4 py-3 text-center text-[#C0A76B] font-bold text-sm">
                                                ID
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                    `;

                    producto.variantes.forEach((v, index) => {
                        const stockClass = v.stock >= 10 ? 'text-green-400' : v.stock >= 5 ? 'text-yellow-400' : 'text-red-400';
                        const stockIcon = v.stock >= 10 ? 'fa-check-circle' : v.stock >= 5 ? 'fa-exclamation-circle' : 'fa-times-circle';
                        const rowBg = index % 2 === 0 ? 'bg-gray-800 bg-opacity-30' : 'bg-transparent';
                        
                        html += `
                            <tr class="border-t border-gray-800 hover:bg-[#C0A76B] hover:bg-opacity-10 transition-all ${rowBg}">
                                <td class="px-4 py-3">
                                    <span class="inline-flex items-center justify-center bg-[#C0A76B] bg-opacity-20 text-[#C0A76B] font-bold px-3 py-1 rounded-md text-sm border border-[#C0A76B] border-opacity-40">
                                        ${v.talla}
                                    </span>
                                </td>
                                <td class="px-4 py-3">
                                    <span class="text-white font-semibold text-sm">${v.color}</span>
                                </td>
                                <td class="px-4 py-3 text-right">
                                    <span class="inline-flex items-center gap-1 font-bold ${stockClass} text-sm">
                                        <i class="fas ${stockIcon}"></i>
                                        ${v.stock} unidades
                                    </span>
                                </td>
                                <td class="px-4 py-3 text-right">
                                    <span class="text-[#C0A76B] font-bold text-sm">$${v.precio.toLocaleString()}</span>
                                </td>
                                <td class="px-4 py-3 text-center">
                                    <span class="text-gray-400 text-xs font-mono">#${v.variante_id}</span>
                                </td>
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
                    <div class="mt-6 pt-6 border-t-2 border-[#C0A76B] border-opacity-30">
                        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div class="bg-gradient-to-br from-blue-900 to-blue-800 p-4 rounded-lg border border-blue-400 border-opacity-30">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-blue-300 text-sm font-semibold">Total Productos</p>
                                        <p class="text-3xl font-bold text-white mt-1">${Object.keys(productosMap).length}</p>
                                    </div>
                                    <i class="fas fa-boxes text-blue-400 text-3xl opacity-50"></i>
                                </div>
                            </div>
                            <div class="bg-gradient-to-br from-purple-900 to-purple-800 p-4 rounded-lg border border-purple-400 border-opacity-30">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-purple-300 text-sm font-semibold">Total Variantes</p>
                                        <p class="text-3xl font-bold text-white mt-1">${inventario.length}</p>
                                    </div>
                                    <i class="fas fa-layer-group text-purple-400 text-3xl opacity-50"></i>
                                </div>
                            </div>
                            <div class="bg-gradient-to-br from-green-900 to-green-800 p-4 rounded-lg border border-green-400 border-opacity-30">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-green-300 text-sm font-semibold">Stock Total</p>
                                        <p class="text-3xl font-bold text-white mt-1">${inventario.reduce((sum, v) => sum + v.stock, 0)}</p>
                                    </div>
                                    <i class="fas fa-warehouse text-green-400 text-3xl opacity-50"></i>
                                </div>
                            </div>
                            <div class="bg-gradient-to-br from-yellow-900 to-yellow-800 p-4 rounded-lg border border-yellow-400 border-opacity-30">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-yellow-300 text-sm font-semibold">Valor Total</p>
                                        <p class="text-2xl font-bold text-white mt-1">$${inventario.reduce((sum, v) => sum + (v.stock * v.precio), 0).toLocaleString()}</p>
                                    </div>
                                    <i class="fas fa-dollar-sign text-yellow-400 text-3xl opacity-50"></i>
                                </div>
                            </div>
                        </div>
                        <div class="mt-4 bg-[#C0A76B] bg-opacity-10 border border-[#C0A76B] border-opacity-30 rounded-lg p-4">
                            <p class="text-center text-gray-300">
                                <i class="fas fa-info-circle text-[#C0A76B] mr-2"></i>
                                Haz clic en <strong class="text-[#C0A76B]">"Gestionar Variantes"</strong> para distribuir o ajustar el stock de cada producto
                            </p>
                        </div>
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
