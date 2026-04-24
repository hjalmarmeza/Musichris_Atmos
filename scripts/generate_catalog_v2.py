import csv
import json
import re

def super_clean(text):
    if not text: return ""
    text = text.upper()
    accents = {'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U', 'Ñ':'N'}
    for k, v in accents.items(): text = text.replace(k, v)
    text = re.sub(r'[^A-Z0-9\s]', '', text)
    text = re.sub(r'\s+V\d+$', '', text)
    return text.strip()

# 1. Load BPM Data
bpm_data = {}
with open('/Users/hjalmarmeza/.gemini/antigravity/brain/0117bc47-6117-481f-9d89-305343ab9f14/.system_generated/steps/2001/content.md', 'r') as f:
    lines = f.readlines()[5:]
    reader = csv.reader(lines)
    for row in reader:
        if len(row) > 9:
            title = super_clean(row[1])
            try: bpm = int(row[9])
            except: bpm = 0
            bpm_data[title] = {
                "bpm": bpm, "style": row[6], "theme": row[7], "instrumentation": row[8], "verse": row[2]
            }

# 2. Process Master
master_catalog = []
with open('/Users/hjalmarmeza/Downloads/Antigravity/MusiChris Live Station/songs_list.csv', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if i == 0: continue
        parts = line.strip().split('","')
        if len(parts) >= 6:
            album = parts[0].replace('"', '')
            img_url = parts[1]
            title_raw = parts[2]
            audio_url = parts[3]
            yt_id = parts[5].replace('"', '')
            
            sc = super_clean(title_raw)
            info = bpm_data.get(sc, {"bpm": 0, "style": "", "theme": "", "instrumentation": "", "verse": ""})
            
            # Smart Categories
            m = []
            theme = info["theme"].lower()
            if any(w in theme for w in ["paz", "descanso", "refugio", "calma"]): m.append("Paz Interior")
            if any(w in theme for w in ["victoria", "gozo", "alegria"]): m.append("Victoria & Gozo")
            if info["bpm"] > 110: m.append("Guerra Espiritual")
            if not m: m.append("Paz Interior") # Default for MusiChris

            master_catalog.append({
                "title": title_raw, "album": album, "verse": info["verse"],
                "bpm": info["bpm"], "theme": info["theme"], "moments": list(set(m)),
                "audio_url": audio_url, "image_url": img_url, "youtube_id": yt_id
            })

with open('/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos/data/musichris_master_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(master_catalog, f, indent=2, ensure_ascii=False)
print("Catálogo regenerado con éxito.")
