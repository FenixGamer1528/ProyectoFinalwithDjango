#!/usr/bin/env python3
"""Script para resolver conflictos de merge automáticamente"""
import re
import os

# Archivos a resolver
archivos = [
    r'carrito\models.py',
    r'core\templates\core\index.html',
    r'core\templates\core\ofertas.html',
    r'dashboard\templates\dashboard\editar_producto.html',
    r'dashboard\templates\dashboard\gestion_productos.html'
]

def resolver_conflicto(contenido):
    """Resuelve conflictos de merge tomando ambas versiones cuando sea posible"""
    # Patrón para encontrar conflictos
    patron = r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> ms-david'
    
    def combinar(match):
        head_content = match.group(1).strip()
        david_content = match.group(2).strip()
        
        # Si el contenido de ms-david tiene más características (como carrusel), úsalo
        if 'carousel' in david_content.lower() and 'carousel' not in head_content.lower():
            return david_content
        
        # Si HEAD tiene favoritos y ms-david no, combinar
        if 'favorito' in head_content.lower() and 'favorito' not in david_content.lower():
            # Mantener HEAD pero agregar características de ms-david si existen
            return head_content
        
        # Por defecto, tomar ms-david (más reciente)
        return david_content
    
    # Resolver conflictos
    contenido_resuelto = re.sub(patron, combinar, contenido, flags=re.DOTALL)
    
    return contenido_resuelto

def main():
    base_path = os.path.dirname(__file__)
    
    for archivo in archivos:
        filepath = os.path.join(base_path, archivo)
        if not os.path.exists(filepath):
            print(f"⚠️  Archivo no encontrado: {filepath}")
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            if '<<<<<<< HEAD' not in contenido:
                print(f"✓ Sin conflictos: {archivo}")
                continue
            
            contenido_resuelto = resolver_conflicto(contenido)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(contenido_resuelto)
            
            print(f"✓ Resuelto: {archivo}")
            
        except Exception as e:
            print(f"✗ Error en {archivo}: {e}")

if __name__ == '__main__':
    main()
    print("\n✅ Proceso completado")
