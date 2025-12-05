"""
Script de prueba independiente para sistema de recolorización SAM
Prueba el procesamiento sin necesidad del servidor Django

Uso:
    python test_sam_standalone.py <imagen.jpg> <color_hex>

Ejemplo:
    python test_sam_standalone.py zapato.jpg "#ff0000"
"""

import sys
import os
from pathlib import Path

# Agregar el proyecto al path para importar sam_recolor
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def test_sam_recolor(imagen_path, color_hex):
    """Prueba el módulo sam_recolor con una imagen local"""
    print("=" * 60)
    print("  TEST SISTEMA RECOLORIZACIÓN SAM")
    print("=" * 60)
    print()
    
    # 1. Verificar archivo
    print("[1/5] Verificando imagen...")
    if not os.path.exists(imagen_path):
        print(f"❌ ERROR: No se encontró la imagen: {imagen_path}")
        return False
    print(f"✓ Imagen encontrada: {imagen_path}")
    print()
    
    # 2. Verificar variables de entorno
    print("[2/5] Verificando configuración...")
    sam_checkpoint = os.environ.get('SAM_CHECKPOINT')
    sam_model_type = os.environ.get('SAM_MODEL_TYPE', 'vit_h')
    
    if not sam_checkpoint:
        print("❌ ERROR: Variable SAM_CHECKPOINT no definida")
        print("   Ejecutar: $env:SAM_CHECKPOINT = 'C:\\models\\sam_vit_h.pth'")
        return False
    
    if not os.path.exists(sam_checkpoint):
        print(f"❌ ERROR: Checkpoint no existe: {sam_checkpoint}")
        return False
    
    print(f"✓ SAM_CHECKPOINT: {sam_checkpoint}")
    print(f"✓ SAM_MODEL_TYPE: {sam_model_type}")
    print()
    
    # 3. Cargar imagen
    print("[3/5] Cargando imagen...")
    try:
        from PIL import Image
        pil_image = Image.open(imagen_path).convert('RGB')
        print(f"✓ Imagen cargada: {pil_image.size[0]}x{pil_image.size[1]} px")
    except Exception as e:
        print(f"❌ ERROR cargando imagen: {e}")
        return False
    print()
    
    # 4. Procesar con SAM
    print("[4/5] Procesando con SAM + recolor...")
    print(f"   Color objetivo: {color_hex}")
    print("   ⏳ Esto puede tardar 10-60 segundos dependiendo de tu hardware...")
    
    try:
        from dashboard.sam_recolor import process_image_recolor, SamUnavailableError
        
        result_image = process_image_recolor(pil_image, color_hex)
        print(f"✓ Procesamiento completado")
        print(f"   Imagen resultante: {result_image.size[0]}x{result_image.size[1]} px")
    except SamUnavailableError as e:
        print(f"❌ ERROR de SAM: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR procesando: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()
    
    # 5. Guardar resultado
    print("[5/5] Guardando resultado...")
    output_name = f"test_recolor_{color_hex.replace('#', '')}.png"
    output_path = BASE_DIR / output_name
    
    try:
        result_image.save(output_path)
        print(f"✓ Imagen guardada: {output_path}")
    except Exception as e:
        print(f"❌ ERROR guardando: {e}")
        return False
    
    print()
    print("=" * 60)
    print("  ✓ TEST COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print()
    print("Resultado guardado en:", output_path)
    return True


def main():
    """Punto de entrada principal"""
    print()
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("Uso: python test_sam_standalone.py <imagen> [color_hex]")
        print()
        print("Ejemplos:")
        print('  python test_sam_standalone.py zapato.jpg "#ff0000"')
        print('  python test_sam_standalone.py camisa.png "#00ff00"')
        print()
        sys.exit(1)
    
    imagen_path = sys.argv[1]
    color_hex = sys.argv[2] if len(sys.argv) > 2 else '#ff0000'
    
    # Validar formato color
    if not color_hex.startswith('#'):
        color_hex = '#' + color_hex
    
    if len(color_hex) != 7:
        print(f"❌ ERROR: Color inválido '{color_hex}' (debe ser formato #RRGGBB)")
        sys.exit(1)
    
    # Ejecutar test
    success = test_sam_recolor(imagen_path, color_hex)
    
    if not success:
        print()
        print("❌ Test falló. Revisa los mensajes de error arriba.")
        print()
        print("Soluciones comunes:")
        print("  1. Verificar que SAM_CHECKPOINT esté definido:")
        print('     $env:SAM_CHECKPOINT = "C:\\models\\sam_vit_h.pth"')
        print()
        print("  2. Instalar dependencias faltantes:")
        print("     pip install torch torchvision opencv-python pillow")
        print("     pip install git+https://github.com/facebookresearch/segment-anything.git")
        print()
        print("  3. Revisar documentación: SISTEMA_RECOLORIZACION_IA.md")
        print()
        sys.exit(1)
    
    print("💡 Tip: Ahora puedes probar la API Django:")
    print("   1. Iniciar servidor: python manage.py runserver")
    print("   2. POST /dashboard/api/variante/<id>/generar-color/")
    print()


if __name__ == '__main__':
    main()
