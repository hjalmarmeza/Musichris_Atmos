import json
import os

BASE_DIR = "/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos"
CATALOG_PATH = os.path.join(BASE_DIR, "data/musichris_master_catalog.json")
PAISAJES_DIR = os.path.join(BASE_DIR, "ui/assets/Paisajes")

def count_assets():
    # 1. Paisajes
    paisajes = [f for f in os.listdir(PAISAJES_DIR) if f.endswith('.mp4')]
    print(f"Total Paisajes: {len(paisajes)}")

    # 2. Canciones por Atmósfera
    with open(CATALOG_PATH, 'r') as f:
        catalog = json.load(f)

    atmosphere_map = {
        "Refugio": ["Refugio / Seguridad", "Alivio / Refugio Inmersivo", "Compendio de Protección Divina", "Refugio Ancestral"],
        "Confianza": ["Confianza / Omnisciencia", "Confianza en la ayuda", "Confianza exclusiva / Silencio activo", "La decisión activa de creer"],
        "Descanso": ["Descanso / Hogar espiritual", "Paz / Meditación / Descanso", "Vigilancia divina / Descanso seguro", "Quietud / Confianza Silenciosa"],
        "Guerra Espiritual": ["Refugio activo / Protección en la guerra", "Valentía / Confianza en medio del peligro", "Protección / Poder", "Victoria / Fe activa", "Seguridad en la Defensa Divina"],
        "Poder": ["El Poder de Dios a nuestro favor", "Protección / Poder", "Autoridad del Hijo", "El Dominio Eterno de Dios"],
        "Victoria": ["El Mensaje de Victoria", "El Triunfo de la Fe", "La Victoria y el Desfile Divino", "Victoria Final", "Victoria en Dios"],
        "Restauración": ["Avivamiento / Restauración", "Restauración / Gracia", "La petición de una renovación espiritual completa", "Sanidad"],
        "Avivamiento": ["Avivamiento / Restauración", "Santidad de Dios", "Fuego en tu interior", "Sed espiritual / Renovación"]
    }

    stats = {}
    for atm, targets in atmosphere_map.items():
        count = 0
        for s in catalog:
            song_theme = s.get('theme', '')
            if any(target.lower() in song_theme.lower() for target in targets):
                count += 1
        stats[atm] = count
    
    print("\nCanciones por Atmósfera:")
    for atm, count in stats.items():
        print(f"- {atm}: {count} canciones")

if __name__ == "__main__":
    count_assets()
