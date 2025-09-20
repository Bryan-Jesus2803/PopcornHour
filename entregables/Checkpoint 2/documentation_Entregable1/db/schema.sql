-- ===============================
-- Script SQL para PopcornHour
-- ===============================

-- 1. Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol TEXT CHECK (role IN ('user','admin')) DEFAULT 'user',
    fecha_registro TIMESTAMP DEFAULT NOW()
);

-- 2. Tabla de contenido (películas/series)
CREATE TABLE contenido (
    id_contenido SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('pelicula','serie')),
    fecha_lanzamiento INT,
    genero VARCHAR(150),
    descripcion TEXT,
    director VARCHAR(100),
    created_at TIMESTAMP DEFAULT now()
);


-- 3. Tabla de reseñas
CREATE TABLE resenias (
    id_resena SERIAL PRIMARY KEY,
    id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    id_contenido INT REFERENCES contenido(id_contenido) ON DELETE CASCADE,
    comentario TEXT NOT NULL,
    puntuacion INT CHECK (rating BETWEEN 1 AND 5),
    fecha_publicacion TIMESTAMP DEFAULT NOW()
);

-- 4. Tabla de favoritos
CREATE TABLE favoritos (
    id_lista SERIAL PRIMARY KEY,
    id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    id_contenido INT REFERENCES contenido(id_contenido) ON DELETE CASCADE,
    fecha_agregado TIMESTAMP DEFAULT NOW()
);
