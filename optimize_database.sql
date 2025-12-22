-- Script de optimización de base de datos PostgreSQL para Glamoure
-- Ejecutar después de hacer las migraciones

-- 1. Crear índices adicionales en tabla carrito_producto
CREATE INDEX IF NOT EXISTS idx_producto_nombre_trgm ON carrito_producto USING gin(nombre gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_producto_descripcion_trgm ON carrito_producto USING gin(descripcion gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_producto_destacado_oferta ON carrito_producto(destacado, en_oferta);

-- 2. Crear índices en tabla carrito_pedido
CREATE INDEX IF NOT EXISTS idx_pedido_usuario_fecha ON carrito_pedido(usuario_id, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_pedido_estado ON carrito_pedido(estado);

-- 3. Crear índices en tabla carrito_itemcarrito
CREATE INDEX IF NOT EXISTS idx_itemcarrito_carrito_producto ON carrito_itemcarrito(carrito_id, producto_id);

-- 4. Crear índices en tabla carrito_productovariante
CREATE INDEX IF NOT EXISTS idx_variante_producto_color ON carrito_productovariante(producto_id, color);
CREATE INDEX IF NOT EXISTS idx_variante_producto_talla ON carrito_productovariante(producto_id, talla);

-- 5. Analizar tablas para actualizar estadísticas
ANALYZE carrito_producto;
ANALYZE carrito_pedido;
ANALYZE carrito_itemcarrito;
ANALYZE carrito_productovariante;
ANALYZE carrito_carrito;

-- 6. Vacuum para recuperar espacio
VACUUM ANALYZE carrito_producto;
VACUUM ANALYZE carrito_pedido;

-- 7. Habilitar extensión pg_trgm para búsquedas de texto más rápidas
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 8. Ver el tamaño de las tablas (opcional, para monitoreo)
SELECT 
    schemaname AS schema,
    tablename AS table,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Notas:
-- - Este script debe ejecutarse con permisos de superusuario en PostgreSQL
-- - Los índices TRGM mejoran significativamente las búsquedas de texto
-- - VACUUM y ANALYZE deben ejecutarse regularmente (semanalmente)
