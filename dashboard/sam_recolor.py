import os
import io
import numpy as np
from PIL import Image

_SAM_MODEL = None
_MASK_GENERATOR = None

# Configuraciones optimizadas por categoría de producto
CATEGORY_CONFIGS = {
    'zapatos': {
        # Parámetros básicos de color
        'saturation_mix': 0.80,  # 80% target, 20% original
        'min_saturation': 70,
        'brightness_boost': 1.10,  # +10%
        'saturation_brightness_factor': 0.35,
        # Parámetros avanzados de procesamiento
        'shadow_preservation': 0.85,      # Mantiene sombras naturales
        'contrast_enhancement': 0.12,     # Realza contraste
        'texture_preservation': 0.80,     # Preserva textura del material
        'edge_preservation': 0.90,        # Mantiene bordes definidos
        'material_depth_factor': 0.45,    # Profundidad del material
        'light_uniformity': 0.25,         # Uniformidad de luz
        'temperature_adjustment': 1.01    # +1% temperatura de color
    },
    'ropa': {
        # Parámetros básicos de color
        'saturation_mix': 0.75,  # 75% target, 25% original
        'min_saturation': 60,
        'brightness_boost': 1.08,  # +8%
        'saturation_brightness_factor': 0.40,
        # Parámetros avanzados de procesamiento
        'shadow_preservation': 0.70,      # Sombras más suaves
        'contrast_enhancement': 0.10,     # Contraste moderado
        'texture_preservation': 0.60,     # Textura de tela natural
        'edge_preservation': 0.85,        # Bordes suaves
        'material_depth_factor': 0.30,    # Menos profundidad (tela)
        'light_uniformity': 0.22,         # Luz más uniforme
        'temperature_adjustment': 1.03    # +3% temperatura cálida
    },
    'accesorios': {
        # Parámetros básicos de color
        'saturation_mix': 0.85,  # 85% target, 15% original
        'min_saturation': 80,
        'brightness_boost': 1.12,  # +12%
        'saturation_brightness_factor': 0.30,
        # Parámetros avanzados de procesamiento
        'shadow_preservation': 0.80,      # Sombras balanceadas
        'contrast_enhancement': 0.18,     # Alto contraste para detalles
        'texture_preservation': 0.75,     # Textura de metal/plástico
        'edge_preservation': 0.88,        # Bordes bien definidos
        'material_depth_factor': 0.25,    # Materiales más planos
        'light_uniformity': 0.20,         # Luz variable
        'temperature_adjustment': 0.98    # -2% temperatura fría
    },
    'bolsos': {
        # Parámetros básicos de color
        'saturation_mix': 0.78,
        'min_saturation': 65,
        'brightness_boost': 1.09,  # +9%
        'saturation_brightness_factor': 0.38,
        # Parámetros avanzados de procesamiento
        'shadow_preservation': 0.75,      # Sombras moderadas
        'contrast_enhancement': 0.14,     # Contraste medio-alto
        'texture_preservation': 0.70,     # Textura de cuero/lona
        'edge_preservation': 0.87,        # Bordes definidos
        'material_depth_factor': 0.40,    # Profundidad media
        'light_uniformity': 0.23,         # Luz semi-uniforme
        'temperature_adjustment': 1.02    # +2% temperatura neutral
    },
    'general': {  # Configuración por defecto
        # Parámetros básicos de color
        'saturation_mix': 0.75,
        'min_saturation': 60,
        'brightness_boost': 1.08,
        'saturation_brightness_factor': 0.40,
        # Parámetros avanzados de procesamiento
        'shadow_preservation': 0.75,
        'contrast_enhancement': 0.12,
        'texture_preservation': 0.70,
        'edge_preservation': 0.86,
        'material_depth_factor': 0.35,
        'light_uniformity': 0.22,
        'temperature_adjustment': 1.00
    }
}


class SamUnavailableError(Exception):
    pass


def _hex_to_hsv(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    import cv2
    color_bgr = np.uint8([[[b, g, r]]])
    hsv = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2HSV)[0][0]
    return int(hsv[0]), int(hsv[1]), int(hsv[2])


def _recolor_hsv_preserve_texture(image_rgb: np.ndarray, mask: np.ndarray, target_hex: str, categoria: str = None):
    """Recoloriza con ALTA CALIDAD preservando texturas, sombras y detalles originales.
    
    Args:
        image_rgb: Imagen en formato RGB numpy array
        mask: Máscara booleana de la región a recolorear
        target_hex: Color objetivo en formato hex (ej: '#FF0000')
        categoria: Categoría del producto ('zapatos', 'ropa', 'accesorios', 'bolsos')
                  Si es None, usa configuración 'general'
    """
    import cv2
    
    # Obtener configuración según categoría
    config = CATEGORY_CONFIGS.get(categoria, CATEGORY_CONFIGS['general'])
    print(f"  📊 Configuración [{categoria or 'general'}]: saturation_mix={config['saturation_mix']:.0%}, "
          f"min_sat={config['min_saturation']}, brightness_boost={config['brightness_boost']:.2f}")
    
    img_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    target_h, target_s, target_v = _hex_to_hsv(target_hex)

    # Verificar que la máscara tenga elementos
    if not np.any(mask):
        return image_rgb

    # Extraer valores originales
    original_sat = img_hsv[:, :, 1][mask].copy()
    original_val = img_hsv[:, :, 2][mask].copy()
    original_hue = img_hsv[:, :, 0][mask].copy()
    
    # Factor de brillo (0-1): 0=sombra, 1=luz
    brightness_factor = original_val / 255.0
    
    # === 1. CAMBIAR TONO al color objetivo ===
    img_hsv[:, :, 0][mask] = target_h
    
    # === 2. AJUSTAR SATURACIÓN con preservación de sombras ===
    sat_mix = config['saturation_mix']
    new_sat = target_s * sat_mix + original_sat * (1 - sat_mix)
    
    # Aplicar factor de brillo para preservar sombras
    shadow_pres = config['shadow_preservation']
    new_sat = new_sat * (0.7 + config['saturation_brightness_factor'] * brightness_factor)
    
    # Preservar sombras: zonas oscuras mantienen más del color original
    new_sat = new_sat * shadow_pres + original_sat * (1 - shadow_pres)
    
    # Aplicar límites de saturación
    img_hsv[:, :, 1][mask] = np.clip(new_sat, config['min_saturation'], 255)
    
    # === 3. AJUSTAR BRILLO con profundidad de material ===
    brightness_boost = original_val * config['brightness_boost']
    
    # Material depth: dar más profundidad visual
    material_depth = config['material_depth_factor']
    depth_adjustment = 1.0 + (brightness_factor - 0.5) * material_depth
    brightness_boost = brightness_boost * depth_adjustment
    
    # Light uniformity: uniformizar la luz
    light_uniform = config['light_uniformity']
    target_brightness = np.mean(brightness_boost)
    brightness_boost = brightness_boost * (1 - light_uniform) + target_brightness * light_uniform
    
    img_hsv[:, :, 2][mask] = np.clip(brightness_boost, 0, 255)
    
    # === 4. PROCESAMIENTO AVANZADO EN BGR ===
    recolored_bgr = cv2.cvtColor(img_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    # Contrast enhancement: realzar contraste
    contrast_factor = 1.0 + config['contrast_enhancement']
    recolored_bgr = recolored_bgr.astype(np.float32)
    mean_color = np.mean(recolored_bgr)
    recolored_bgr = (recolored_bgr - mean_color) * contrast_factor + mean_color
    recolored_bgr = np.clip(recolored_bgr, 0, 255).astype(np.uint8)
    
    # Texture preservation: mezclar con imagen original para preservar textura
    original_bgr = img_bgr.copy()
    texture_pres = config['texture_preservation']
    blended_bgr = cv2.addWeighted(
        recolored_bgr, texture_pres,
        original_bgr, 1 - texture_pres,
        0
    )
    
    # Edge preservation: aplicar bilateral filter solo en áreas no-borde
    edge_pres = config['edge_preservation']
    if edge_pres < 1.0:
        # Detectar bordes
        gray = cv2.cvtColor(blended_bgr, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges_dilated = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
        
        # Aplicar filtro bilateral para suavizar no-bordes
        smoothed = cv2.bilateralFilter(blended_bgr, 9, 75, 75)
        
        # Combinar: bordes originales, resto suavizado
        edge_mask = (edges_dilated > 0)
        result_bgr = np.where(edge_mask[:, :, np.newaxis], blended_bgr, 
                             blended_bgr * edge_pres + smoothed * (1 - edge_pres))
        result_bgr = result_bgr.astype(np.uint8)
    else:
        result_bgr = blended_bgr
    
    # === 5. AJUSTE DE TEMPERATURA DE COLOR ===
    temp_adjust = config['temperature_adjustment']
    if temp_adjust != 1.0:
        # Convertir a LAB para ajustar temperatura
        lab = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        # Ajustar canal b (amarillo-azul) para temperatura
        lab[:, :, 2] = lab[:, :, 2] * temp_adjust
        lab = np.clip(lab, 0, 255).astype(np.uint8)
        result_bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # Convertir de BGR a RGB
    recolored_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
    return recolored_rgb


def _load_sam():
    global _SAM_MODEL, _MASK_GENERATOR
    if _SAM_MODEL is not None and _MASK_GENERATOR is not None:
        return _SAM_MODEL, _MASK_GENERATOR

    try:
        from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
    except Exception as e:
        raise SamUnavailableError('segment-anything no está instalado o no se puede importar: ' + str(e))

    checkpoint = os.environ.get('SAM_CHECKPOINT', '')
    model_type = os.environ.get('SAM_MODEL_TYPE', 'vit_h')
    if not checkpoint or not os.path.exists(checkpoint):
        raise SamUnavailableError('Checkpoint SAM no encontrado. Defina la variable de entorno `SAM_CHECKPOINT` con la ruta al .pth')

    sam = sam_model_registry[model_type](checkpoint=checkpoint)
    
    # Mover a GPU si está disponible
    try:
        import torch
        if torch.cuda.is_available():
            sam = sam.to(device='cuda')
            print('✅ SAM cargado en GPU')
        else:
            print('⚠️ SAM usando CPU (no hay GPU disponible)')
    except:
        pass
    
    # Configuración optimizada para detectar TODOS los productos individuales
    mask_generator = SamAutomaticMaskGenerator(
        sam,
        points_per_side=32,           # Más puntos = más objetos detectados
        pred_iou_thresh=0.70,         # Umbral más bajo para capturar más objetos
        stability_score_thresh=0.80,  # Umbral más bajo para incluir más máscaras
        crop_n_layers=1,              # Procesar en múltiples escalas
        crop_n_points_downscale_factor=2,
        min_mask_region_area=100      # Capturar objetos pequeños (gafas, accesorios)
    )

    _SAM_MODEL = sam
    _MASK_GENERATOR = mask_generator
    return _SAM_MODEL, _MASK_GENERATOR


def _generate_masks_for_image(image_np: np.ndarray):
    _, mask_generator = _load_sam()
    masks = mask_generator.generate(image_np)
    return masks


def _pick_best_mask(masks):
    """Selecciona TODAS las máscaras de productos, excluyendo solo el fondo.
    
    Combina múltiples máscaras para capturar todos los productos:
    abrigo, camisa, pantalones, zapatos, botas, bolso, bufanda, gafas, accesorios.
    """
    if not masks:
        return None
    
    # Ordenar por área de mayor a menor
    sorted_masks = sorted(masks, key=lambda m: m.get('area', 0), reverse=True)
    
    if len(sorted_masks) < 2:
        # Si solo hay una máscara, usarla
        return np.asarray(sorted_masks[0]['segmentation'], dtype=bool)
    
    # Calcular área total de la imagen
    total_area = sorted_masks[0]['segmentation'].shape[0] * sorted_masks[0]['segmentation'].shape[1]
    
    # El fondo suele ser > 40% del área total, lo excluimos
    background_threshold = total_area * 0.40
    
    # Filtrar máscaras: excluir el fondo (muy grande) y objetos muy pequeños (ruido)
    product_masks = [
        m for m in sorted_masks 
        if m.get('area', 0) < background_threshold  # No es fondo
        and m.get('area', 0) > (total_area * 0.002)  # No es ruido (>0.2% del área)
    ]
    
    print(f"📊 Total máscaras: {len(sorted_masks)}, Productos detectados: {len(product_masks)}")
    
    # Combinar TODAS las máscaras de productos en una sola
    if product_masks:
        combined_mask = np.zeros_like(sorted_masks[0]['segmentation'], dtype=bool)
        for mask_data in product_masks:
            combined_mask = combined_mask | np.asarray(mask_data['segmentation'], dtype=bool)
        return combined_mask
    else:
        # Fallback: usar todas menos la más grande
        combined_mask = np.zeros_like(sorted_masks[0]['segmentation'], dtype=bool)
        for mask_data in sorted_masks[1:]:
            combined_mask = combined_mask | np.asarray(mask_data['segmentation'], dtype=bool)
        return combined_mask


def process_image_recolor(pil_image: Image.Image, target_hex: str, categoria: str = None):
    """Procesa una PIL image y devuelve una PIL image recoloreada usando SAM.

    Args:
        pil_image: Imagen PIL a procesar
        target_hex: Color objetivo en formato hex (ej: '#FF0000')
        categoria: Categoría del producto para usar configuración optimizada
                  ('zapatos', 'ropa', 'accesorios', 'bolsos')
                  Si es None, usa configuración 'general'

    Requisitos: tener instalado `segment-anything` y la variable de entorno `SAM_CHECKPOINT` apuntando al .pth.
    """
    try:
        sam, _ = _load_sam()
    except SamUnavailableError:
        raise

    image_rgb = np.array(pil_image.convert('RGB'))

    masks = _generate_masks_for_image(image_rgb)
    if not masks:
        return pil_image

    mask = _pick_best_mask(masks)
    if mask is None:
        return pil_image

    recolored = _recolor_hsv_preserve_texture(image_rgb, mask, target_hex, categoria=categoria)
    return Image.fromarray(recolored)
