import csv
import json
import re

def clean_title(title):
    if not title: return ""
    # Remove "v1", "v2", etc. and extra spaces
    title = re.sub(r'\s+v\d+$', '', title, flags=re.IGNORECASE)
    return title.strip().upper()

# 1. Load BPM Data from Google Sheet CSV
bpm_data = {}
with open('/Users/hjalmarmeza/.gemini/antigravity/brain/0117bc47-6117-481f-9d89-305343ab9f14/.system_generated/steps/2001/content.md', 'r') as f:
    lines = f.readlines()[5:] # Skip headers
    reader = csv.reader(lines)
    for row in reader:
        if len(row) > 9:
            title = clean_title(row[1])
            try:
                bpm = int(row[9])
            except:
                bpm = 0
            bpm_data[title] = {
                "bpm": bpm,
                "style": row[6],
                "theme": row[7],
                "instrumentation": row[8],
                "verse": row[2]
            }

# 2. Load Main Songs List
master_catalog = []
with open('/Users/hjalmarmeza/Downloads/Antigravity/MusiChris Live Station/songs_list.csv', 'r') as f:
    # The file seems to have a weird structure in line 1, let's parse carefully
    lines = f.readlines()
    
    # Simple parser for this specific CSV format
    for i, line in enumerate(lines):
        if i == 0: continue # Skip first line header mess
        parts = line.strip().split('","')
        if len(parts) >= 6:
            album = parts[0].replace('"', '')
            img_url = parts[1]
            title_raw = parts[2]
            audio_url = parts[3]
            yt_id = parts[5].replace('"', '')
            
            title = clean_title(title_raw)
            info = bpm_data.get(title, {"bpm": 0, "style": "", "theme": "", "instrumentation": "", "verse": ""})
            
            # Logic for Moments
            moments = []
            bpm = info["bpm"]
            theme = info["theme"].lower()
            
            if "sufrimiento" in theme or "prueba" in theme or "desesperada" in theme or "carga" in theme or "duelo" in theme:
                moments.append("Valle de Prueba")
            
            if bpm > 0 and bpm < 80 or any(word in theme for word in ["paz", "confianza", "refugio", "calma", "descanso", "quietud"]):
                moments.append("Paz Interior")
                
            if bpm > 0 and bpm < 65 and any(word in theme for word in ["paz", "descanso", "sueño", "quietud", "noche"]):
                moments.append("Dulces Sueños")
                
            if any(word in theme for word in ["oración", "adoración", "intimidad", "entrega", "humildad", "contemplación", "santuario"]):
                moments.append("Oración")
                
            if bpm > 100 or any(word in theme for word in ["victoria", "gozo", "celebración", "alegría", "triunfo", "fiesta"]):
                moments.append("Victoria & Gozo")
                
            if bpm > 110 and any(word in theme for word in ["guerra", "poder", "victoria", "fuerza", "ejército"]):
                moments.append("Guerra Espiritual")
                
            if any(word in theme for word in ["mañana", "amanecer", "renovación", "esperanza", "luz"]):
                moments.append("Mañanas de Esperanza")
                
            if (bpm >= 70 and bpm <= 100) and any(word in theme for word in ["sabiduría", "guía", "palabra", "dirección", "instrucción"]):
                moments.append("Estudio & Enfoque")

            # Fallback if no moments found
            if not moments:
                if bpm > 100: moments = ["Victoria & Gozo"]
                elif bpm < 75: moments = ["Paz Interior"]
                else: moments = ["Oración"]

            master_catalog.append({
                "id": i,
                "title": title_raw,
                "clean_title": title,
                "album": album,
                "verse": info["verse"],
                "bpm": bpm,
                "style": info["style"],
                "theme": info["theme"],
                "instrumentation": info["instrumentation"],
                "moments": list(set(moments)), # Unique moments
                "audio_url": audio_url,
                "image_url": img_url,
                "youtube_id": yt_id,
                "youtube_url": f"https://www.youtube.com/watch?v={yt_id}" if yt_id else ""
            })

# 3. Write Master JSON
with open('/Users/hjalmarmeza/Downloads/Antigravity/musichris_master_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(master_catalog, f, indent=2, ensure_ascii=False)

print(f"Successfully generated master catalog with {len(master_catalog)} songs.")
