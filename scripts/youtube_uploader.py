import json
import os
import sys

# Cargar configuración de Musichris Soul para reutilizar la conexión a YouTube
sys.path.append('/Users/hjalmarmeza/Downloads/Antigravity/PROYECTOS_FINALIZADOS/Musichris_Soul/src')

# Nota: En Oracle, esta ruta cambiará a la ubicación donde subas el proyecto.
try:
    from google_connector import uploadToYouTube
    YOUTUBE_READY = True
except ImportError:
    YOUTUBE_READY = False
    print("⚠️ Alerta: No se pudo cargar el conector de YouTube. El video solo se guardará localmente.")

def prepare_youtube_metadata(moment, songs):
    # Generador de Títulos Inspiradores (MusiChris Style)
    titles = {
        "Paz Interior": "SOLO EN ÉL: El Descanso que tu Alma necesita | MusiChris Studio",
        "Victoria & Gozo": "MÁS QUE VENCEDOR: El Grito de Victoria en tu Prueba | MusiChris Studio",
        "Guerra Espiritual": "GIGANTES CAERÁN: Himnos de Poder y Autoridad | MusiChris Studio"
    }
    
    title = titles.get(moment, f"{moment} | MusiChris Studio")
    
    # Construcción de la Descripción con Timestamps y Versículos
    description = f"🕊️ {title}\n\n"
    description += "Cuando el ruido del mundo te quite la paz, deja que estas promesas bíblicas restauren tu alma.\n\n"
    description += "--- CONTENIDO DEL VIDEO ---\n"
    
    # Añadir tracklist automático
    # TODO: Implementar cálculo de tiempo real para los timestamps
    for i, song in enumerate(songs):
        description += f"- {song['title']} (Reflexión: {song['verse']})\n"
        
    description += "\n\nSuscríbete a MusiChris Studio para más momentos de conexión con Dios."
    
    return title, description

# Esta función se llamará después del renderizado exitoso
def execute_upload(video_path, moment, songs):
    if not YOUTUBE_READY: return
    
    title, description = prepare_youtube_metadata(moment, songs)
    
    print(f"📡 [YOUTUBE] Iniciando subida de: {title}")
    # Creamos un objeto ficticio para el conector que ya conoces
    metadata_obj = {
        "reflection_title": title,
        "verse_citation": "Varios Versículos (Ver descripción)"
    }
    
    # uploadToYouTube(video_path, metadata_obj)
    print("✅ [YOUTUBE] Video subido con éxito (Simulado para esta prueba).")

if __name__ == "__main__":
    print("Módulo de Subida ATMOS configurado.")
