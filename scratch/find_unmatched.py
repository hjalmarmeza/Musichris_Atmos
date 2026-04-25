import json
import os

BASE_DIR = "/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos"
CATALOG_PATH = os.path.join(BASE_DIR, "data/musichris_master_catalog.json")

def find_unmatched():
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

    all_kws = []
    for kws in atmosphere_map.values(): all_kws.extend(kws)

    unmatched = []
    for s in catalog:
        theme = s.get('theme', '').lower()
        if not any(k in theme for k in all_kws):
            unmatched.append((s.get('title'), s.get('theme')))
    
    for title, theme in unmatched:
        print(f"Title: {title} | Theme: {theme}")

if __name__ == "__main__":
    find_unmatched()
