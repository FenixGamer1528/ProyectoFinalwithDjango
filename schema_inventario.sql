-- ========================================
-- SCRIPT SQL PARA SISTEMA DE INVENTARIO
-- Compatible con SQLite (Django db.sqlite3)
-- ========================================
-- Basado en los modelos Django existentes
-- Generado: 14 de noviembre de 2025
-- ========================================

-- ========================================
-- 1. TABLA CATEGORIA
-- ========================================
-- Almacena las categorías principales de productos
CREATE TABLE IF NOT EXISTS core_categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

-- Insertar categorías por defecto
INSERT OR IGNORE INTO core_categoria (nombre) VALUES 
    ('Mujer'),
    ('Hombre'),
    ('Zapatos'),
    ('Ofertas');

-- ========================================
-- 2. TABLA PRODUCTO
-- ========================================
-- Producto base (sin stock individual)
-- El stock real está en ProductoVariante
CREATE TABLE IF NOT EXISTS carrito_producto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    imagen VARCHAR(100),  -- Ruta local opcional
    imagen_url TEXT,      -- URL de Supabase
    talla VARCHAR(20),    -- Talla genérica (opcional, legacy)
    colores VARCHAR(200), -- Colores CSV (legacy, ahora usa variantes)
    destacado INTEGER DEFAULT 0 CHECK (destacado IN (0, 1)),
    stock INTEGER DEFAULT 0,  -- Stock legacy (ahora se usa ProductoVariante.stock)
    precio DECIMAL(10, 2) NOT NULL CHECK (precio >= 0),
    categoria VARCHAR(20) NOT NULL DEFAULT 'mujer' 
        CHECK (categoria IN ('mujer', 'hombre', 'zapatos', 'ofertas'))
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_producto_categoria_destacado 
    ON carrito_producto(categoria, destacado);

CREATE INDEX IF NOT EXISTS idx_producto_precio_desc 
    ON carrito_producto(precio DESC);

CREATE INDEX IF NOT EXISTS idx_producto_nombre 
    ON carrito_producto(nombre);

-- ========================================
-- 3. TABLA PRODUCTOVARIANTE
-- ========================================
-- Variante específica: Producto + Talla + Color
-- Esta tabla maneja el INVENTARIO REAL
CREATE TABLE IF NOT EXISTS carrito_productovariante (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    tipo_producto VARCHAR(20) NOT NULL DEFAULT 'ropa'
        CHECK (tipo_producto IN ('ropa', 'pantalones', 'zapatos')),
    talla VARCHAR(10) NOT NULL,
    color VARCHAR(50) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    imagen VARCHAR(100),          -- Ruta local opcional
    imagen_url TEXT,              -- URL de Supabase
    imagen_generada_ia INTEGER DEFAULT 0 CHECK (imagen_generada_ia IN (0, 1)),
    
    -- CLAVE FORÁNEA
    FOREIGN KEY (producto_id) REFERENCES carrito_producto(id) 
        ON DELETE CASCADE,
    
    -- CONSTRAINT ÚNICO: no puede haber dos variantes iguales
    UNIQUE (producto_id, talla, color)
);

-- Índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_variante_producto_talla_color 
    ON carrito_productovariante(producto_id, talla, color);

CREATE INDEX IF NOT EXISTS idx_variante_stock 
    ON carrito_productovariante(stock);

CREATE INDEX IF NOT EXISTS idx_variante_ordering 
    ON carrito_productovariante(talla, color);

-- ========================================
-- 4. TABLA INVENTARIO (Movimientos)
-- ========================================
-- Rastrea entradas, salidas y ajustes de stock
-- Proporciona trazabilidad completa
CREATE TABLE IF NOT EXISTS carrito_inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variante_id INTEGER NOT NULL,
    tipo_movimiento VARCHAR(10) NOT NULL 
        CHECK (tipo_movimiento IN ('entrada', 'salida', 'ajuste')),
    cantidad INTEGER NOT NULL,
    stock_anterior INTEGER NOT NULL,
    stock_nuevo INTEGER NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER,  -- Puede ser NULL si es automático
    observaciones TEXT,
    
    -- CLAVE FORÁNEA
    FOREIGN KEY (variante_id) REFERENCES carrito_productovariante(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES carrito_usuariopersonalizado(id) 
        ON DELETE SET NULL
);

-- Índice para consultas de historial
CREATE INDEX IF NOT EXISTS idx_inventario_variante_fecha 
    ON carrito_inventario(variante_id, fecha DESC);

CREATE INDEX IF NOT EXISTS idx_inventario_fecha 
    ON carrito_inventario(fecha DESC);

-- ========================================
-- 5. TABLA USUARIOPERSONALIZADO (referencia)
-- ========================================
-- Usuario extendido de Django (ya existe en tu proyecto)
-- Incluye campos personalizados y favoritos
CREATE TABLE IF NOT EXISTS carrito_usuariopersonalizado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME,
    is_superuser INTEGER NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254),
    is_staff INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    telefono VARCHAR(15)
);

-- Tabla intermedia para favoritos (ManyToMany)
CREATE TABLE IF NOT EXISTS carrito_usuariopersonalizado_favoritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuariopersonalizado_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    
    FOREIGN KEY (usuariopersonalizado_id) REFERENCES carrito_usuariopersonalizado(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES carrito_producto(id) 
        ON DELETE CASCADE,
    
    UNIQUE (usuariopersonalizado_id, producto_id)
);

-- ========================================
-- EJEMPLOS DE DATOS DE PRUEBA
-- ========================================

-- Insertar producto ejemplo
INSERT OR IGNORE INTO carrito_producto (
    id, nombre, descripcion, precio, categoria, destacado, stock
) VALUES (
    1, 
    'Camiseta Básica', 
    'Camiseta de algodón 100% ideal para uso diario',
    29990.00,
    'mujer',
    1,
    0  -- El stock real está en las variantes
);

-- Insertar variantes del producto (combinaciones talla + color)
INSERT OR IGNORE INTO carrito_productovariante (
    producto_id, tipo_producto, talla, color, stock
) VALUES 
    (1, 'ropa', 'S', 'Negro', 15),
    (1, 'ropa', 'S', 'Blanco', 10),
    (1, 'ropa', 'M', 'Negro', 20),
    (1, 'ropa', 'M', 'Blanco', 18),
    (1, 'ropa', 'L', 'Negro', 12),
    (1, 'ropa', 'L', 'Blanco', 8);

-- ========================================
-- EJEMPLOS DE CONSULTAS
-- ========================================

-- 1. Ver todas las variantes de un producto con su stock
SELECT 
    p.nombre AS producto,
    pv.talla,
    pv.color,
    pv.stock,
    pv.tipo_producto
FROM carrito_productovariante pv
JOIN carrito_producto p ON pv.producto_id = p.id
WHERE p.id = 1
ORDER BY pv.talla, pv.color;

-- 2. Productos con stock bajo (menos de 10 unidades en alguna variante)
SELECT 
    p.nombre AS producto,
    pv.talla,
    pv.color,
    pv.stock
FROM carrito_productovariante pv
JOIN carrito_producto p ON pv.producto_id = p.id
WHERE pv.stock < 10
ORDER BY pv.stock ASC;

-- 3. Stock total por producto (suma de todas las variantes)
SELECT 
    p.id,
    p.nombre,
    SUM(pv.stock) AS stock_total,
    COUNT(pv.id) AS num_variantes
FROM carrito_producto p
LEFT JOIN carrito_productovariante pv ON p.id = pv.producto_id
GROUP BY p.id, p.nombre
ORDER BY stock_total DESC;

-- 4. Historial de movimientos de una variante específica
SELECT 
    i.fecha,
    i.tipo_movimiento,
    i.cantidad,
    i.stock_anterior,
    i.stock_nuevo,
    i.observaciones,
    u.username AS usuario
FROM carrito_inventario i
LEFT JOIN carrito_usuariopersonalizado u ON i.usuario_id = u.id
WHERE i.variante_id = 1
ORDER BY i.fecha DESC
LIMIT 20;

-- ========================================
-- TRIGGERS PARA CONTROL AUTOMÁTICO
-- ========================================

-- Trigger: Registrar automáticamente movimientos de inventario
-- cuando se actualiza el stock de una variante
CREATE TRIGGER IF NOT EXISTS trg_after_update_stock
AFTER UPDATE OF stock ON carrito_productovariante
FOR EACH ROW
WHEN NEW.stock != OLD.stock
BEGIN
    INSERT INTO carrito_inventario (
        variante_id,
        tipo_movimiento,
        cantidad,
        stock_anterior,
        stock_nuevo,
        fecha,
        observaciones
    ) VALUES (
        NEW.id,
        CASE 
            WHEN NEW.stock > OLD.stock THEN 'entrada'
            WHEN NEW.stock < OLD.stock THEN 'salida'
            ELSE 'ajuste'
        END,
        ABS(NEW.stock - OLD.stock),
        OLD.stock,
        NEW.stock,
        CURRENT_TIMESTAMP,
        'Actualización automática de stock'
    );
END;

-- Trigger: Prevenir stock negativo
CREATE TRIGGER IF NOT EXISTS trg_prevent_negative_stock
BEFORE UPDATE OF stock ON carrito_productovariante
FOR EACH ROW
WHEN NEW.stock < 0
BEGIN
    SELECT RAISE(ABORT, 'Error: El stock no puede ser negativo');
END;

-- ========================================
-- VISTAS ÚTILES
-- ========================================

-- Vista: Resumen de inventario por producto
CREATE VIEW IF NOT EXISTS vista_inventario_productos AS
SELECT 
    p.id AS producto_id,
    p.nombre AS producto,
    p.categoria,
    p.precio,
    COUNT(DISTINCT pv.id) AS total_variantes,
    SUM(pv.stock) AS stock_total,
    MIN(pv.stock) AS stock_minimo,
    MAX(pv.stock) AS stock_maximo,
    AVG(pv.stock) AS stock_promedio
FROM carrito_producto p
LEFT JOIN carrito_productovariante pv ON p.id = pv.producto_id
GROUP BY p.id, p.nombre, p.categoria, p.precio;

-- Vista: Variantes con stock crítico
CREATE VIEW IF NOT EXISTS vista_stock_critico AS
SELECT 
    p.nombre AS producto,
    pv.talla,
    pv.color,
    pv.stock,
    p.categoria
FROM carrito_productovariante pv
JOIN carrito_producto p ON pv.producto_id = p.id
WHERE pv.stock <= 5
ORDER BY pv.stock ASC, p.nombre;

-- ========================================
-- PROCEDIMIENTOS DE EJEMPLO (Queries)
-- ========================================

-- Ejemplo 1: Actualizar stock con registro de movimiento manual
-- (En SQLite no hay stored procedures, se hace con transacciones)
/*
BEGIN TRANSACTION;

-- Actualizar stock
UPDATE carrito_productovariante 
SET stock = stock + 50 
WHERE id = 1;

-- El trigger automáticamente registrará el movimiento en carrito_inventario

COMMIT;
*/

-- Ejemplo 2: Registrar venta (disminuir stock)
/*
BEGIN TRANSACTION;

-- Verificar stock disponible
SELECT stock FROM carrito_productovariante WHERE id = 1;

-- Si hay stock suficiente, restar
UPDATE carrito_productovariante 
SET stock = stock - 3 
WHERE id = 1 AND stock >= 3;

-- El trigger registra automáticamente la salida

COMMIT;
*/

-- ========================================
-- NOTAS IMPORTANTES
-- ========================================
/*
1. ESTRUCTURA ACTUAL:
   - Producto: tabla base con información general
   - ProductoVariante: combinación única de Producto + Talla + Color
   - Inventario: historial de movimientos de stock
   - Categoria: tabla separada en core (si se quiere usar FK)

2. STOCK:
   - El stock REAL está en ProductoVariante.stock
   - Producto.stock es legacy (puede eliminarse o calcularse)
   - Cada variante maneja su propio inventario

3. CONSTRAINTS:
   - UNIQUE (producto_id, talla, color): evita duplicados
   - CHECK (stock >= 0): previene stock negativo
   - ON DELETE CASCADE: elimina variantes si se borra producto
   - Triggers: automatizan registro de movimientos

4. ÍNDICES:
   - Optimizan búsquedas por producto, talla, color
   - Índice en stock para consultas de disponibilidad
   - Índice compuesto para búsquedas exactas

5. DJANGO ORM vs SQL DIRECTO:
   - Preferir Django ORM en producción
   - Este SQL es para entender la estructura
   - Las migraciones Django generan automáticamente este esquema
*/
