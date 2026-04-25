import csv
import json
import os
import re

# CONFIGURACIÓN DE RUTAS
PROJECT_ROOT = "/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos"
METADATA_FILE = os.path.join(PROJECT_ROOT, "data/hoja4_correct.csv")
SONGS_LIST_FILE = "/Users/hjalmarmeza/Downloads/Antigravity/MusiChris Live Station/songs_list.csv"
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data/musichris_master_catalog.json")

def super_clean(text):
    if not text: return ""
    text = text.upper()
    accents = {'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U', 'Ñ':'N'}
    for k, v in accents.items(): text = text.replace(k, v)
    text = re.sub(r'[^A-Z0-9\s]', '', text)
    return text.strip()

def parse_songs_list():
    urls_map = {}
    if not os.path.exists(SONGS_LIST_FILE):
        return urls_map

    with open(SONGS_LIST_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0: continue 
            if len(row) >= 4:
                title = super_clean(row[2])
                urls_map[title] = {
                    "album": row[0],
                    "audio_url": row[3],
                    "youtube_id": row[5] if len(row) > 5 else ""
                }
    return urls_map

def generate_catalog():
    print("--- GENERANDO CATÁLOGO EXPANDIDO (INCLUSIVO) v2.5 ---")
    urls_map = parse_songs_list()

    catalog = []
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title_meta = row.get("Título", "").strip()
                if not title_meta: continue
                
                sc = super_clean(title_meta)
                url_data = urls_map.get(sc, {})
                
                # Manual Fallbacks
                if not url_data:
                    if "SUEÑO DE JOSE" in sc: url_data = {"audio_url": "https://res.cloudinary.com/dveqs8f3n/video/upload/v1765357562/ggemhfn0tararn06ghxk.mp3"}
                    elif "SI DE MARIA" in sc: url_data = {"audio_url": "https://res.cloudinary.com/dveqs8f3n/video/upload/v1765357513/bm03vfa6jhy7kfevv8yn.mp3"}
                    elif "TRAVESIA TRANQUILA" in sc: url_data = {"audio_url": "https://res.cloudinary.com/dveqs8f3n/video/upload/v1765357613/zaewdj4uocvax3sud4c1.mp3"}

                if not url_data.get("audio_url"): continue

                bpm = int(row.get("BPM", 0)) if row.get("BPM", "").isdigit() else 0
                context = {
                    "verse": row.get("Verso Bíblico / Pasaje", ""),
                    "theme": row.get("Temática Central", ""),
                    "focus": row.get("Enfoque de Composición", ""),
                    "bpm": bpm
                }

                m = []
                full_text = f"{context['theme']} {context['focus']}".lower()
                
                is_slow = bpm < 90
                is_mid = 90 <= bpm <= 110
                is_fast = bpm > 110

                # 1. PAZ INTERIOR (Base sólida)
                if (is_slow or bpm == 0) and any(w in full_text for w in ["paz", "descanso", "noche", "quietud", "dormir", "refugio", "seguro"]):
                    m.append("Paz Interior")
                
                # 2. INTIMIDAD (Base sólida)
                if (is_slow or is_mid or bpm == 0) and any(w in full_text for w in ["intimidad", "adoracion", "santidad", "presencia", "corazon", "amor"]):
                    m.append("Intimidad")
                
                # 3. GUERRA ESPIRITUAL (Base sólida)
                if (is_mid or is_fast) and any(w in full_text for w in ["guerra", "batalla", "poder", "fuerza", "fortaleza", "ejercito"]):
                    m.append("Guerra Espiritual")
                
                # 4. VICTORIA & GOZO (EXPANDIDO: Incluye Guerra de alta energía y celebraciones de ritmo medio)
                # La victoria es el resultado de la guerra, por lo que comparten canciones de alta energía.
                if (is_mid or is_fast) and any(w in full_text for w in ["gozo", "celebracion", "alegria", "triunfo", "victoria", "vencer", "reino"]):
                    m.append("Victoria & Gozo")
                
                # 5. RESTAURACIÓN (EXPANDIDO: Incluye canciones de Paz e Intimidad que hablen de sanidad o gracia)
                if (is_slow or is_mid) and any(w in full_text for w in ["restauracion", "sanidad", "perdon", "gracia", "bondad", "misericordia", "levantar"]):
                    m.append("Restauración")

                # REGLAS DE HERENCIA (Para evitar listas vacías)
                # Si una canción es de Guerra Espiritual y es rápida, también es de Victoria.
                if "Guerra Espiritual" in m and is_fast: m.append("Victoria & Gozo")
                # Si una canción es de Intimidad y es lenta, también puede ser de Restauración.
                if "Intimidad" in m and is_slow: m.append("Restauración")
                # Si una canción es de Paz Interior, también es Restauración (la paz restaura).
                if "Paz Interior" in m: m.append("Restauración")

                if not m:
                    if is_slow: m.append("Paz Interior")
                    elif is_mid: m.append("Intimidad")
                    else: m.append("Guerra Espiritual")

                entry = {
                    "title": title_meta,
                    "audio_url": url_data["audio_url"],
                    "moments": list(set(m)),
                    "context": context
                }
                catalog.append(entry)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"Total canciones catalogadas (Modo Expandido): {len(catalog)}")

if __name__ == "__main__":
    generate_catalog()
