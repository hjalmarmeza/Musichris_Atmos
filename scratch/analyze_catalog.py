import json
import os

BASE_DIR = "/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos"
CATALOG_PATH = os.path.join(BASE_DIR, "data/musichris_master_catalog.json")

def analyze_catalog():
    with open(CATALOG_PATH, 'r') as f:
        catalog = json.load(f)
    
    print(f"Total Canciones en Catálogo: {len(catalog)}")
    
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

    all_targets = []
    for targets in atmosphere_map.values():
        all_targets.extend([t.lower() for t in targets])
    
    unmatched_themes = set()
    for s in catalog:
        song_theme = s.get('theme', '').lower()
        if not any(target in song_theme for target in all_targets):
            unmatched_themes.add(s.get('theme', 'SIN TEMA'))
    
    print("\nEjemplos de temas que NO coincidieron (Top 20):")
    for theme in sorted(list(unmatched_themes))[:20]:
        print(f"- {theme}")

if __name__ == "__main__":
    analyze_catalog()
