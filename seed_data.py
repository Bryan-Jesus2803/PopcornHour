# seed_data.py
from dotenv import load_dotenv
import os
from supabase import create_client
from werkzeug.security import generate_password_hash

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def seed():
    # usuarios
    admin_pwd = generate_password_hash("adminpass123")
    user_pwd = generate_password_hash("userpass123")

    supabase.table("usuarios").insert([
        {"nombre_usuario": "admin1", "email": "admin@ejemplo.com", "contrasena": admin_pwd, "rol":"admin"},
        {"nombre_usuario": "user2", "email": "user@ejemplo.com", "contrasena": user_pwd, "rol":"user"}
    ]).execute()

    # contenidos
    supabase.table("contenido").insert([
        {"titulo":"F1® La película","tipo":"pelicula","fecha_lanzamiento":2025,"genero":"Accion ▪ Deportes ▪ Drama","descripcion":"Sonny Hayes era el fenómeno más prometedor de la Formula 1 en los años 90 hasta que sufrió un accidente en la pista. Treinta años después, su excompañero, Ruben Cervantes, lo convence de volver para correr junto al talentoso novato Joshua Pearce.","director":"Joseph Kosinski"},
        {"titulo":"Merlina","tipo":"serie","fecha_lanzamiento":2022,"genero":"Misterio ▪ Fantasía ▪ Drama","descripcion":"Mientras asiste a la Academia Nevermore, Merlina Addams intenta dominar su incipiente habilidad psíquica, frustrar una ola de asesinatos y resolver el misterio que involucró a sus padres 25 años atrás.","director":"Alfred Gough ● Miles Millar"},
        {"titulo":"El conjuro 4: últimos ritos","tipo":"pelicula","fecha_lanzamiento":2025,"genero":"Misterio ▪ Horror sobrenatural ▪ Thriller","descripcion":"Cuando los investigadores paranormales Ed y Lorraine Warren se ven envueltos en otro aterrador caso relacionado con misteriosas criaturas, se ven obligados a resolverlo todo por última vez.","director":"Michael Chaves"}
    ]).execute()

    print("Seed completado.")

if __name__ == "__main__":
    seed()
