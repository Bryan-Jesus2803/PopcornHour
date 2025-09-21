import os
from supabase import create_client
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env si existe
load_dotenv()

# Esta configurado de este modo debido a que se emplaron variables de entorno
# las cuales se encuentran en un archivo ".env" separado para no hacer publicos 
# los accesos a mi base de datos, implementando asi un sistema seguro.
SUPABASE_URL = os.getenv("SUPABASE_URL", "TU_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "TU_SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_change_me")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
