import os
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .config import supabase, SUPABASE_URL

main_bp = Blueprint("main", __name__)

ALLOWED_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

# ---------------- INDEX (publico) y BUSQUEDA / PAGINACION----------------
@main_bp.route("/")
def index():
    
    q = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 12))
    offset = (page - 1) * per_page

    query = supabase.table("contenido").select("*")

    if q:
        # Buscamos por título con ilike
        query = query.filter("titulo", "ilike", f"%{q}%")
    if genre:
        # Buscamos por genero
        query = query.eq("genero", genre)

    # Paginación con range
    res = query.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
    contenido = res.data or []

    # Si usuario está logueado, traer sus favoritos (para mostrar estado)
    favorite_ids = set()
    if "user" in session:
        fav_res = supabase.table("favoritos").select("id_contenido").eq("id_usuario", session["user"]["id_usuario"]).execute()
        if fav_res.data:
            favorite_ids = {f["id_contenido"] for f in fav_res.data}

    # Usamos same template (index) que visually muestra el contenido
    return render_template("index.html", contenido=contenido, favorite_ids=favorite_ids,
                           q=q, genre=genre, page=page, per_page=per_page)

# ---------------- Registro ----------------
@main_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        nombre_usuario = request.form.get("nombre_usuario", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not nombre_usuario or not email or not password:
            flash("Completa todos los campos", "error")
            return redirect(url_for("main.signup"))

        # Verificar si email existe
        q = supabase.table("usuarios").select("*").eq("email", email).execute()
        if q.data:
            flash("El email ya está registrado", "error")
            return redirect(url_for("main.signup"))
        
        hashed = generate_password_hash(password)
        res = supabase.table("usuarios").insert({
            "nombre_usuario": nombre_usuario,
            "email": email,
            "contrasena": hashed,
            "rol": "user"
        }).execute()

        if res.status_code in (201, 200) or res.data:
            # iniciar sesión automáticamente
            user = supabase.table("usuarios").select("*").eq("email", email).execute().data[0]
            session["user"] = {
                "id_usuario": user["id_usuario"],
                "nombre_usuario": user["nombre_usuario"],
                "email": user["email"],
                "rol": user["rol"]
            }
            flash("Cuenta creada. Bienvenido.", "success")
            return redirect(url_for("main.home"))
        else:
            flash("Error al crear la cuenta", "error")

    return render_template("signup.html", hide_search=True)

# ---------------- LOGIN ----------------
@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        query = supabase.table("usuarios").select("*").eq("email", email).execute()
        if not query.data:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("main.login"))

        user = query.data[0]

        if check_password_hash(user["contrasena"], password):
            session["user"] = {
                "id_usuario": user["id_usuario"],
                "nombre_usuario": user["nombre_usuario"],
                "email": user["email"],
                "rol": user["rol"]
            }
            flash("Sesión iniciada", "success")            
            return redirect(url_for("main.home"))
        else:
            flash("Contraseña incorrecta")

    return render_template("login.html", hide_search=True)

# ---------------- LOGOUT ----------------
@main_bp.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.","info")
    return redirect(url_for("main.index"))

# ---------------- HOME ----------------
@main_bp.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("main.index"))
    
    # Reusamos lógica similar a index pero pasar user-friendly favoritos
    q = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 12))
    
    offset = (page - 1) * per_page
    query = supabase.table("contenido").select("*")
    if q:
        query = query.filter("titulo", "ilike", f"%{q}%")
    if genre:
        query = query.eq("genero", genre)
    res = query.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
    contenido = res.data or []

    fav_res = supabase.table("favoritos").select("id_contenido").eq("id_usuario", session["user"]["id_usuario"]).execute()
    favorite_ids = {f["id_contenido"] for f in (fav_res.data or [])}

    return render_template("home.html", contenido=contenido, favorite_ids=favorite_ids,
                           q=q, genre=genre, page=page, per_page=per_page)

# ---------------- DETALLE CONTENIDO ----------------
@main_bp.route("/contenido/<int:contenido_id>", methods=["GET", "POST"])
def movie_detail(contenido_id):
    results = supabase.table("contenido").select("*").eq("id_contenido", contenido_id).execute()

    if not results.data:
        flash("Contenido no encontrado", "error")
        return redirect(url_for("main.index"))
    contenido = results.data[0]

    # reseñas del contenido
    res = supabase.table("resenias").select("*").eq("id_contenido", contenido_id).order("fecha_publicacion", desc=True).execute()
    resenias = res.data or []
    
    # enriquecer reseñas con nombre de usuario
    enriched = []
    for r in resenias:
        usuario = supabase.table("usuarios").select("nombre_usuario").eq("id_usuario", r["id_usuario"]).execute()
        nombre = usuario.data[0]["nombre_usuario"] if usuario.data else f"Usuario {r['id_usuario']}"
        enriched.append({
            "id_resena": r.get("id_resena"),
            "user_name": nombre,
            "comentario": r.get("comentario"),
            "puntuacion": r.get("puntuacion"),
            "fecha_publicacion": r.get("fecha_publicacion")
        })
    
    # POST: crear reseña (solo usuarios)
    if request.method == "POST":
        if "user" not in session:
            flash("Debes iniciar sesión para comentar", "error")
            return redirect(url_for("main.login"))

        comentario = request.form.get("comentario", "").strip()
        puntuacion = int(request.form.get("puntuacion", 0))
        if not comentario or not (1 <= puntuacion <= 5):
            flash("Comentario o puntuación inválida", "error")
            return redirect(url_for("main.movie_detail", contenido_id=contenido_id))

        supabase.table("resenias").insert({
            "id_usuario": session["user"]["id_usuario"],
            "id_contenido": contenido_id,
            "comentario": comentario,
            "puntuacion": puntuacion
        }).execute()    

        flash("Reseña enviada", "success")
        return redirect(url_for("main.movie_detail", contenido_id=contenido_id))

    return render_template("detalle_contenido.html", contenido=contenido, resenias=resenias)

# ---------- TOGGLE FAVORITO ----------
@main_bp.route("/favorito/toggle/<int:contenido_id>", methods=["POST"])
def toggle_favorite(contenido_id):
    if "user" not in session:
        flash("Debes iniciar sesión para usar favoritos.", "error")
        return redirect(url_for("main.login"))

    user_id = session["user"]["id_usuario"]

    # Verificar si ya existe
    exists = supabase.table("favoritos").select("*").eq("id_usuario", user_id).eq("id_contenido", contenido_id).execute()
    if exists.data:
        # eliminar
        supabase.table("favoritos").delete().match({"id_usuario": user_id, "id_contenido": contenido_id}).execute()
        flash("Eliminado de favoritos.", "success")
    else:
        supabase.table("favoritos").insert({"id_usuario": user_id, "id_contenido": contenido_id}).execute()
        flash("Agregado a favoritos.", "success")

    # Volver a la página anterior (referrer)
    return redirect(request.referrer or url_for("main.home"))

# ---------------- Admin: subir contenido + poster (archivo) ----------------
@main_bp.route("/admin", methods=["GET", "POST"])
def admin():
    if "user" not in session or session["user"].get("rol") != "admin":
        flash("Acceso denegado", "error")
        return redirect(url_for("main.index"))
    
    if request.method == "POST":
        titulo = request.form.get("titulo")
        tipo = request.form.get("tipo")
        fecha_lanzamiento = request.form.get("fecha_lanzamiento")
        genero = request.form.get("genero")
        descripcion = request.form.get("descripcion")
        director = request.form.get("director")

        # validar fecha
        try:
            fecha_int = int(fecha_lanzamiento) if fecha_lanzamiento else None
        except ValueError:
            fecha_int = None

        # manejar poster
        poster_url = None
        file = request.files.get("poster")
        if file and file.filename:
            fname = secure_filename(file.filename)
            ext = os.path.splitext(fname)[1].lower()
            if ext not in ALLOWED_EXT:
                flash("Tipo de archivo no permitido para póster.", "error")
                return redirect(url_for("main.admin"))
            
            # generar key único
            key = f"posters/{uuid4().hex}{ext}"

            try: 
                # Leer bytes (puede ser grande: cuidado con límites)
                file_bytes = file.read()
                # subir bytes al bucket 'posters'
                supabase.storage.from_('posters').upload(key, file_bytes)
                # formar URL pública (si bucket es público)
                poster_url = f"{SUPABASE_URL}/storage/v1/object/public/posters/{key}"
            except Exception as e:
                print("Error subiendo a storage:", e)
                flash("Error subiendo el póster. Revisa la configuración de Storage y la clave.", "error")
                return redirect(url_for("main.admin"))

        nuevo = {
            "titulo": titulo,
            "tipo": tipo,
            "fecha_lanzamiento": fecha_int,
            "genero": genero,
            "descripcion": descripcion,
            "director": director,
            "poster_url": poster_url
        }
        supabase.table("contenido").insert(nuevo).execute()
        flash("Contenido agregado con éxito", "success")
        return redirect(url_for("main.home"))
    
    return render_template("moderador.html")
