import json
import os

BASE_DIR = "/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos"
CATALOG_PATH = os.path.join(BASE_DIR, "data/musichris_master_catalog.json")

def count_with_keywords():
    with open(CATALOG_PATH, 'r') as f:
        catalog = json.load(f)

    atmosphere_map = {
        "Refugio": ["refugio", "seguridad", "alivio", "amparo", "abrigo", "protección", "esperanza"],
        "Confianza": ["confianza", "ayuda", "fidelidad", "dirección", "soberanía", "creer", "fe"],
        "Descanso": ["descanso", "paz", "quietud", "reposo", "meditación", "bienestar"],
        "Guerra Espiritual": ["guerra", "batalla", "ejército", "valentía", "defensa", "fortaleza", "poder"],
        "Poder": ["poder", "autoridad", "gloria", "majestad", "dominio", "grandeza"],
        "Victoria": ["victoria", "triunfo", "vencer", "gozo", "celebración", "exaltación"],
        "Restauración": ["restauración", "gracia", "sanidad", "renovación", "perdón", "restitución"],
        "Avivamiento": ["avivamiento", "fuego", "espíritu", "santidad", "adoración", "intimidad", "anhelo"]
    }

    stats = {}
    matched_any = set()
    for atm, keywords in atmosphere_map.items():
        count = 0
        for i, s in enumerate(catalog):
            song_theme = s.get('theme', '').lower()
            if any(k.lower() in song_theme for k in keywords):
                count += 1
                matched_any.add(i)
        stats[atm] = count
    
    print(f"Total Canciones: {len(catalog)}")
    print(f"Canciones con Match: {len(matched_any)}")
    print(f"Canciones sin Match: {len(catalog) - len(matched_any)}")
    
    print("\nResultados:")
    for atm, count in stats.items():
        print(f"- {atm}: {count} canciones")

if __name__ == "__main__":
    count_with_keywords()
