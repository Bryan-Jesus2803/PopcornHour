from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .config import supabase

main_bp = Blueprint("main", __name__)

# ---------------- INDEX ----------------
@main_bp.route("/")
def index():
    contenido = supabase.table("contenido").select("*").order("created_at", desc=True).execute().data or []
    return render_template("index.html", contenido=contenido)

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

    return render_template("signup.html")

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

    return render_template("login.html")

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
        return redirect(url_for("main.login"))
    contenido = supabase.table("contenido").select("*").order("created_at", desc=True).execute().data or []
    return render_template("home.html", contenido=contenido)

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

# ---------------- Admin (solo rol admin) ----------------
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

        # valida
        try:
            fecha_int = int(fecha_lanzamiento) if fecha_lanzamiento else None
        except ValueError:
            fecha_int = None

        nuevo = {
            "titulo": titulo,
            "tipo": tipo,
            "fecha_lanzamiento": fecha_int,
            "genero": genero,
            "descripcion": descripcion,
            "director": director
        }
        supabase.table("contenido").insert(nuevo).execute()
        flash("Contenido agregado con éxito", "success")
        return redirect(url_for("main.home"))
    
    return render_template("moderador.html")
