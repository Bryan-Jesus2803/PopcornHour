from .config import supabase

def get_all_users():
    return supabase.table("usuarios").select("*").execute().data
