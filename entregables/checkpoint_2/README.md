# PopcornHour – Base de Datos

Este documento explica el esquema de la base de datos utilizado en el proyecto PopcornHour, correspondiente al **Checkpoint 2**.

---

## Tablas creadas
 - Nota: En la base de datos todas las tablas incluyen un atributo de fecha de creación para cada registro. Todo lo descrito a continuación se encuentra en el archivo schema.sql, el cual está listo para ejecutarse y tiene exactamente los mismos querys utilizados para crear la base de datos.
El archivo schema.sql se encuentra en la carpeta de documentation_Entregable1/db


1. **usuarios**  
   - id_usuario (PK)  
   - nombre_usuario  
   - email  
   - contrasena  
   - rol (admin / usuario)

2. **contenido**  
   - id_contenido (PK)  
   - titulo  
   - tipo (película / serie) 
   - fecha_lanzamiento  
   - genero  
   - descripcion   
   - director 

3. **resenias** (reseña)  
   - id_resena (PK)  
   - usuario_id (FK → usuarios.id)  
   - id_contenido (FK → contenido.id)  
   - comentario
   - puntuacion (1-5)    
   - fecha_publicacion

4. **favoritos**  
   - id_lista (PK)  
   - usuario_id (FK → usuarios.id)  
   - pelicula_id (FK → contenido.id)

Para revisar la estructura completa de la base de datos o crear una copia desde cero, consulta el archivo schema.sql.
Basta con ejecutar este script en tu motor de base de datos (por ejemplo, en Supabase) para generar automáticamente todas las tablas con sus relaciones.

---

## Relaciones entre tablas

- Un usuario puede escribir muchas reseñas, pero cada reseña pertenece a un solo usuario y a una sola película.  
- Una película puede tener muchas reseñas, pero cada reseña se conecta solo con una película.  
- Un usuario puede marcar varias películas como favoritas, y una película puede estar en favoritos de muchos usuarios.  

En resumen:  
- usuarios ↔ reseñas = 1 a muchos  
- peliculas ↔ reseñas = 1 a muchos  
- usuarios ↔ favoritos = 1 a muchos  
- peliculas ↔ favoritos = 1 a muchos  

---

## Ejemplos de datos de prueba

### Para la tabla usuarios
```sql
INSERT INTO usuarios (nombre_usuario, correo, contraseña, rol)
VALUES 
('juan23', 'juan@example.com', '1234', 'usuario'),
('admin1', 'admin@example.com', 'adminpass', 'admin');
