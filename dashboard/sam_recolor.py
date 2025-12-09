import os
import io
import numpy as np
from PIL import Image

_SAM_MODEL = None
_MASK_GENERATOR = None

# Configuraciones optimizadas por categoría de producto
CATEGORY_CONFIGS = {
    'zapatos': {
        # ⭐ CONFIGURACIÓN ULTRA PREMIUM - MÁXIMA CALIDAD ⭐
        # Parámetros básicos de color - Autenticidad fotográfica
        'saturation_mix': 0.92,  # 92% color objetivo - Color muy fiel
        'min_saturation': 85,    # Saturación mínima alta - Colores vivos
        'brightness_boost': 1.28,  # +28% brillo - Extra luminoso
        'saturation_brightness_factor': 0.45,  # Mayor respuesta a luz
        # Parámetros avanzados - Máximo realismo
        'shadow_preservation': 0.60,      # Menos sombras - Más uniforme
        'contrast_enhancement': 0.15,     # Contraste reducido para menos sombras
        'texture_preservation': 0.95,     # Máxima preservación de textura
        'edge_preservation': 0.95,        # Bordes ultra definidos
        'material_depth_factor': 0.40,    # Menos profundidad - Más plano
        'light_uniformity': 0.30,         # Luz más uniforme (menos sombras)
        'temperature_adjustment': 1.05    # +5% temperatura para realismo
    },
    'ropa': {
        # ⭐ CONFIGURACIÓN ULTRA PREMIUM - MÁXIMA CALIDAD ⭐
        'saturation_mix': 0.92,
        'min_saturation': 85,
        'brightness_boost': 1.28,
        'saturation_brightness_factor': 0.45,
        'shadow_preservation': 0.60,
        'contrast_enhancement': 0.15,
        'texture_preservation': 0.95,
        'edge_preservation': 0.95,
        'material_depth_factor': 0.40,
        'light_uniformity': 0.30,
        'temperature_adjustment': 1.05
    },
    'accesorios': {
        # ⭐ CONFIGURACIÓN ULTRA PREMIUM - MÁXIMA CALIDAD ⭐
        'saturation_mix': 0.92,
        'min_saturation': 85,
        'brightness_boost': 1.28,
        'saturation_brightness_factor': 0.45,
        'shadow_preservation': 0.60,
        'contrast_enhancement': 0.15,
        'texture_preservation': 0.95,
        'edge_preservation': 0.95,
        'material_depth_factor': 0.40,
        'light_uniformity': 0.30,
        'temperature_adjustment': 1.05
    },
    'bolsos': {
        # ⭐ CONFIGURACIÓN ULTRA PREMIUM - MÁXIMA CALIDAD ⭐
        'saturation_mix': 0.92,
        'min_saturation': 85,
        'brightness_boost': 1.28,
        'saturation_brightness_factor': 0.45,
        'shadow_preservation': 0.60,
        'contrast_enhancement': 0.15,
        'texture_preservation': 0.95,
        'edge_preservation': 0.95,
        'material_depth_factor': 0.40,
        'light_uniformity': 0.30,
        'temperature_adjustment': 1.05
    },
    'general': {  # ⭐ CONFIGURACIÓN ULTRA PREMIUM - MÁXIMA CALIDAD ⭐
        'saturation_mix': 0.92,
        'min_saturation': 85,
        'brightness_boost': 1.28,
        'saturation_brightness_factor': 0.45,
        'shadow_preservation': 0.60,
        'contrast_enhancement': 0.15,
        'texture_preservation': 0.95,
        'edge_preservation': 0.95,
        'material_depth_factor': 0.40,
        'light_uniformity': 0.30,
        'temperature_adjustment': 1.05
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


def _analyze_material_type(image_rgb: np.ndarray, mask: np.ndarray):
    """Analiza el tipo de material del producto para ajustar parámetros."""
    import cv2
    
    # Extraer región del producto
    masked_region = image_rgb[mask]
    
    if len(masked_region) < 100:
        return 'smooth'  # Default
    
    # Convertir a escala de grises
    gray_region = cv2.cvtColor(masked_region.reshape(-1, 1, 3), cv2.COLOR_RGB2GRAY).flatten()
    
    # Calcular textura (desviación estándar local)
    texture_std = np.std(gray_region)
    
    # Calcular brillo promedio
    avg_brightness = np.mean(gray_region)
    
    # Detectar tipo de material
    if texture_std > 50 and avg_brightness > 180:
        return 'furry'  # Pelaje, textura suave y clara (botas blancas con pelaje)
    elif texture_std > 45:
        return 'textured'  # Texturas pronunciadas (cuero arrugado, telas)
    elif texture_std < 25 and avg_brightness > 200:
        return 'glossy'  # Superficies brillantes (cuero liso, satén)
    elif avg_brightness < 80:
        return 'dark'  # Materiales oscuros
    else:
        return 'smooth'  # Materiales lisos estándar


def _get_adaptive_config(categoria: str, material_type: str):
    """Obtiene configuración adaptativa según categoría y tipo de material."""
    base_config = CATEGORY_CONFIGS.get(categoria, CATEGORY_CONFIGS['general']).copy()
    
    # Ajustar según tipo de material
    if material_type == 'furry':
        # Pelaje requiere MÁXIMA preservación de detalles (moñito, pelos, texturas)
        base_config['shadow_preservation'] = 0.85  # MÁXIMAS sombras = textura visible
        base_config['contrast_enhancement'] = 0.30  # CONTRASTE MÁXIMO para pelos
        base_config['brightness_boost'] = 1.18  # MENOS brillo (más natural)
        base_config['material_depth_factor'] = 0.70  # MÁXIMA profundidad 3D
        base_config['saturation_mix'] = 0.20  # 20% saturación = color MUY suave
        base_config['min_saturation'] = 20  # Saturación mínima 20
        base_config['texture_preservation'] = 0.99  # 99% textura original
        base_config['edge_preservation'] = 0.99  # 99% bordes (cada pelo)
        base_config['light_uniformity'] = 0.05  # LUZ MÍNIMA uniformidad = máxima textura
        print(f"  🐰 Material: PELAJE - ULTRA TEXTURA - saturación=20%, textura=99%, contraste=30%")
    elif material_type == 'textured':
        # Texturas pronunciadas - mantener textura pero controlar sombras
        base_config['shadow_preservation'] = 0.65
        base_config['texture_preservation'] = 0.98
        base_config['material_depth_factor'] = 0.50
        print(f"  📐 Material: TEXTURIZADO - Config: textura=98%, profundidad=50%")
    elif material_type == 'glossy':
        # Superficies brillantes - máximo brillo y contraste
        base_config['brightness_boost'] = 1.30
        base_config['contrast_enhancement'] = 0.22
        base_config['shadow_preservation'] = 0.70
        print(f"  ✨ Material: BRILLANTE - Config: brillo=+30%, contraste=22%")
    elif material_type == 'dark':
        # Materiales oscuros - más brillo para visibilidad
        base_config['brightness_boost'] = 1.40
        base_config['shadow_preservation'] = 0.50
        print(f"  🌑 Material: OSCURO - Config: brillo=+40%, sombras=50%")
    else:
        print(f"  📦 Material: ESTÁNDAR - Config por defecto")
    
    return base_config


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
    
    # ANÁLISIS INTELIGENTE: Detectar tipo de material
    material_type = _analyze_material_type(image_rgb, mask)
    
    # Obtener configuración adaptativa
    config = _get_adaptive_config(categoria, material_type)
    print(f"  📊 Categoría: [{categoria or 'general'}] | saturation_mix={config['saturation_mix']:.0%}, "
          f"brightness={config['brightness_boost']:.2f}x")
    
    img_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    target_h, target_s, target_v = _hex_to_hsv(target_hex)
    
    # Detectar si el color objetivo es acromático (blanco, negro, gris)
    is_achromatic = target_s < 30
    print(f"  🎨 Color objetivo: {target_hex} | Acromático: {is_achromatic} (S={target_s})")

    # Verificar que la máscara tenga elementos
    if not np.any(mask):
        return image_rgb

    # Extraer valores originales
    original_sat = img_hsv[:, :, 1][mask].copy()
    original_val = img_hsv[:, :, 2][mask].copy()
    original_hue = img_hsv[:, :, 0][mask].copy()
    
    # Factor de brillo (0-1): 0=sombra, 1=luz
    brightness_factor = original_val / 255.0
    
    # === MANEJO ESPECIAL PARA COLORES ACROMÁTICOS (BLANCO, NEGRO, GRIS) ===
    if is_achromatic:
        print(f"  ⚪ Aplicando algoritmo para color acromático...")
        # Para blanco/negro/gris: eliminar saturación y ajustar solo brillo
        img_hsv[:, :, 1][mask] = 0  # Saturación = 0 (sin color)
        
        # Ajustar brillo según el target_v (Value/Brightness del color objetivo)
        # Blanco = 255, Negro = 0, Grises = valores intermedios
        # Preservar la estructura de sombras original
        brightness_scale = target_v / 128.0  # Normalizar respecto al gris medio
        new_brightness = original_val * brightness_scale
        
        # Preservar algo de la estructura original para mantener sombras
        new_brightness = new_brightness * 0.7 + original_val * 0.3
        
        img_hsv[:, :, 2][mask] = np.clip(new_brightness, 0, 255)
        
        print(f"    → Saturación eliminada, brillo ajustado a escala {brightness_scale:.2f}")
    else:
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
    
    # === 6. POST-PROCESAMIENTO ULTRA CALIDAD ===
    if config.get('texture_preservation', 0) > 0.9:  # Detectar configuración premium
        print(f"  ✨ Aplicando post-procesamiento de máxima calidad...")
        
        # Sharpening AGRESIVO para detalles ultra nítidos (pelos, moñitos, texturas)
        kernel_sharpen = np.array([[-1, -1, -1],
                                   [-1,  9, -1],
                                   [-1, -1, -1]])
        sharpened = cv2.filter2D(result_bgr, -1, kernel_sharpen)
        result_bgr = cv2.addWeighted(result_bgr, 0.5, sharpened, 0.5, 0)  # 50% sharpening
        
        # Ajuste de micro-contraste MÁS FUERTE para definir pelos individuales
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4,4))  # Más agresivo
        for i in range(3):  # Aplicar a cada canal BGR
            result_bgr[:, :, i] = clahe.apply(result_bgr[:, :, i])
        
        # Reducción de ruido MUY SUAVE (preservar texturas)
        result_bgr = cv2.fastNlMeansDenoisingColored(result_bgr, None, 2, 2, 7, 21)
        
        print(f"    → Nitidez ULTRA mejorada (50%), micro-contraste ALTO, detalles preservados")
    
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


def _is_background_mask(mask_data, image_rgb):
    """Detecta si una máscara corresponde a un fondo de color sólido."""
    segmentation = mask_data['segmentation']
    
    # Extraer píxeles de la máscara
    masked_pixels = image_rgb[segmentation]
    
    if len(masked_pixels) < 100:
        return False
    
    # Calcular desviación estándar de cada canal RGB
    std_r = np.std(masked_pixels[:, 0])
    std_g = np.std(masked_pixels[:, 1])
    std_b = np.std(masked_pixels[:, 2])
    
    # Si la desviación es muy baja, es un color sólido (fondo)
    avg_std = (std_r + std_g + std_b) / 3
    
    # Fondos sólidos tienen std < 35 (aumentado para detectar más fondos)
    # Productos tienen texturas con std > 35
    is_solid_color = avg_std < 35
    
    return is_solid_color


def _pick_best_mask(masks, image_rgb=None):
    """Selecciona SOLO las máscaras del producto principal, excluyendo fondos.
    
    Estrategia:
    1. Excluir fondos de colores sólidos (rosa, blanco, gris)
    2. Excluir máscaras muy grandes (>50% área) 
    3. Tomar el producto más grande restante
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
    
    # Filtrar máscaras: excluir fondos y ruido
    product_masks = []
    for m in sorted_masks:
        area = m.get('area', 0)
        area_ratio = area / total_area
        
        # Excluir muy grandes (>45% = probablemente fondo)
        if area_ratio > 0.45:
            print(f"  ❌ Máscara muy grande ({area_ratio*100:.1f}%) - probablemente fondo")
            continue
        
        # Excluir muy pequeñas (<0.5% = ruido)
        if area_ratio < 0.005:
            continue
        
        # Detectar fondos de color sólido (rosa, blanco, gris, etc)
        if image_rgb is not None and _is_background_mask(m, image_rgb):
            print(f"  ❌ Fondo de color sólido detectado ({area_ratio*100:.1f}%)")
            continue
        
        product_masks.append(m)
    
    print(f"📊 Total máscaras: {len(sorted_masks)}, Productos válidos: {len(product_masks)}")
    
    # Tomar solo el producto MÁS GRANDE (no combinar)
    if product_masks:
        best_mask = product_masks[0]  # Ya está ordenado por área
        print(f"  ✅ Producto principal: {best_mask.get('area', 0) / total_area * 100:.1f}% del área")
        return np.asarray(best_mask['segmentation'], dtype=bool)
    else:
        # Fallback: usar la segunda máscara más grande
        print(f"  ⚠️ Fallback: usando segunda máscara más grande")
        return np.asarray(sorted_masks[1]['segmentation'], dtype=bool)


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

    mask = _pick_best_mask(masks, image_rgb=image_rgb)
    if mask is None:
        return pil_image

    recolored = _recolor_hsv_preserve_texture(image_rgb, mask, target_hex, categoria=categoria)
    return Image.fromarray(recolored)
