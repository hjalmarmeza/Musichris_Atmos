import os
import json
import requests
import csv
from io import StringIO

# IDs de Google Sheets
SHEET_TEOLOGIA_ID = "1oTVSF7CjrCtnk3pHdBIRE8gzhE9zKDM5NJFyWV-qsJs"
SHEET_URLS_ID = "19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE"

# Nombres de pestañas (Tabs)
TAB_THEOLOGY = "Hoja 4"
TAB_URLS = "Hoja 2"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fetch_sheet_as_csv(sheet_id, sheet_name):
    # Usar gviz para exportar como CSV usando el nombre de la pestaña
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={requests.utils.quote(sheet_name)}"
    print(f"📡 Descargando pestaña '{sheet_name}' de {sheet_id}...")
    response = requests.get(url)
    if response.status_code == 200:
        return list(csv.DictReader(StringIO(response.text)))
    else:
        print(f"⚠️ Error al acceder a la hoja {sheet_id} (Status: {response.status_code})")
        return []

def sync_all():
    print("🔄 [SYNC] Iniciando Sincronización Diamante...")
    
    # 1. Obtener datos crudos
    raw_songs = fetch_sheet_as_csv(SHEET_URLS_ID, TAB_URLS)
    raw_teologia = fetch_sheet_as_csv(SHEET_TEOLOGIA_ID, TAB_THEOLOGY)
    
    if not raw_songs or not raw_teologia:
        print("❌ Error: No se pudieron obtener los datos de las hojas.")
        return

    # 2. Mapear Teología (Hoja 4)
    # Cabeceras esperadas: #, Titulo, Verso Biblico, Contenido Biblico, Tematica Central, ...
    teologia_map = {}
    for row in raw_teologia:
        # Normalizar claves de cabecera porque gviz puede cambiarlas
        title = row.get('Título', row.get('Titulo', '')).strip().lower()
        if not title:
            # Intentar por índice si las cabeceras fallan
            vals = list(row.values())
            if len(vals) > 1: title = vals[1].strip().lower()
            
        if title:
            teologia_map[title] = row
    
    # 3. Cruzar con URLs (Hoja 2)
    master_catalog = []
    for song in raw_songs:
        vals = list(song.values())
        if len(vals) < 4: continue
        
        # Album: vals[0], Thumb: vals[1], Title: vals[2], URL: vals[3]
        title = vals[2].strip()
        audio_url = vals[3].strip()
        
        if not title or not audio_url: continue
        
        teo = teologia_map.get(title.lower(), {})
        
        # Determinar momentos/atmósferas
        moments_str = teo.get('Temática Central', 'Paz Interior')
        moments = [m.strip() for m in moments_str.split(',') if m.strip()]
        
        master_catalog.append({
            "title": title,
            "audio_url": audio_url,
            "duration_secs": 240,
            "moments": moments,
            "context": {
                "verse": teo.get('Verso Bíblico / Pasaje', teo.get('Verso Biblico', 'Salmos 23:1')),
                "focus": teo.get('Contenido Bíblico', teo.get('Contenido Biblico', 'Adoración y descanso'))
            },
            "album": vals[0],
            "thumbnail": vals[1]
        })
    
    # 4. Guardar resultados
    data_dir = os.path.join(BASE_DIR, 'data')
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    
    with open(os.path.join(data_dir, 'musichris_master_catalog.json'), 'w', encoding='utf-8') as f:
        json.dump(master_catalog, f, indent=4, ensure_ascii=False)
    
    # 5. Generar Reflexiones por Atmósfera
    reflections = {}
    for title, teo in teologia_map.items():
        # Obtener la primera atmósfera listada
        atmos_list = teo.get('Temática Central', 'Paz Interior').split(',')
        primary_atmos = atmos_list[0].strip()
        
        ref_text = teo.get('Contenido Bíblico', teo.get('Contenido Biblico', ''))
        if ref_text and len(ref_text) > 15:
            if primary_atmos not in reflections:
                reflections[primary_atmos] = []
            reflections[primary_atmos].append(ref_text)
            
    with open(os.path.join(data_dir, 'soul_reflections.json'), 'w', encoding='utf-8') as f:
        json.dump(reflections, f, indent=4, ensure_ascii=False)

    print(f"✅ [SYNC] Sincronización exitosa: {len(master_catalog)} canciones y {len(reflections)} categorías de reflexión.")

if __name__ == "__main__":
    sync_all()


