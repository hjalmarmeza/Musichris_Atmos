import json
import csv
import os

# CONFIGURACIÓN
MASTER_CSV = '/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos/data/master_sheet.csv'
CATALOG_JSON = '/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos/data/musichris_master_catalog.json'

ATMOSPHERE_MAP = {
    "Refugio": ["refugio", "castillo", "amparo", "abrigo", "esconder", "escondedero", "guardián", "protección", "escudo", "ampara"],
    "Confianza": ["confianza", "creer", "fe", "fidelidad", "roca", "firme", "seguridad", "socorro", "ayuda", "sostener", "manten", "firmeza"],
    "Descanso": ["descanso", "reposo", "paz", "calma", "quietud", "silbo", "susurro", "dormir", "prado", "aguas", "duerme"],
    "Paz Interior": ["paz", "tranquilidad", "sereno", "clara", "limpio", "sosegado", "mente", "conciencia", "alivio"],
    "Intimidad": ["intimidad", "cerca", "presencia", "mirar", "ojo", "rostro", "amor", "buscar", "contemplar", "pies", "susurro", "hablar"],
    "Poder": ["poder", "fuerza", "majestad", "gloria", "rey", "soberano", "digno", "kadosh", "santo", "trueno", "maravilla"],
    "Restauración": ["restauración", "sanar", "perdón", "misericordia", "piedad", "bondad", "renovar", "hágase", "alma mía", "limpiar", "redención"],
    "Avivamiento": ["avivamiento", "vida", "fuego", "soplo", "aliento", "espíritu", "hueso", "despertar", "levántate", "resucitar"],
    "Guerra Espiritual": ["guerra", "batalla", "pelea", "escudo", "espada", "arma", "enemigo", "asedio", "muro", "jericó", "warfare", "vencer"],
    "Victoria & Gozo": ["victoria", "gozo", "triunfo", "alegre", "fiesta", "júbilo", "cantar", "alabanza", "risa", "exaltación", "maranatha", "viva", "grande"]
}

def load_sheet_data():
    data = {}
    if not os.path.exists(MASTER_CSV): return data
    with open(MASTER_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('Título', '').strip().upper()
            if title:
                data[title] = {
                    "verse": row.get('Verso Bíblico / Pasaje', 'Salmos 23:1'),
                    "bpm": row.get('BPM', 'Slow'),
                    "focus": row.get('Enfoque de Composición', '')
                }
    return data

def refresh():
    if not os.path.exists(CATALOG_JSON): return
    
    with open(CATALOG_JSON, 'r') as f:
        catalog = json.load(f)
    
    sheet_data = load_sheet_data()
    
    for song in catalog:
        title = song.get('title', '').upper()
        metadata = sheet_data.get(title, {})
        
        # Actualizar metadatos
        if metadata:
            if 'context' not in song: song['context'] = {}
            song['context']['verse'] = metadata.get('verse', 'Salmos 23:1')
            song['context']['focus'] = metadata.get('focus', '')
            song['bpm'] = metadata.get('bpm', 'Slow')
        
        # Categorización Inteligente (Usar datos ya actualizados o defaults)
        ctx = song.get('context', {})
        text = f"{song.get('title', '')} {ctx.get('verse', '')} {ctx.get('focus', '')} {song.get('bpm', 'Slow')}".lower()
        found = []
        for atm, keywords in ATMOSPHERE_MAP.items():
            if any(k in text for k in keywords):
                found.append(atm)
        
        # Fallback si no hay nada
        if not found:
            found = ["Descanso"] # Fallback a Descanso por defecto
            
        song['moments'] = found

    with open(CATALOG_JSON, 'w') as f:
        json.dump(catalog, f, indent=4)
    
    print(f"✅ Catálogo refrescado: {len(catalog)} canciones procesadas.")

if __name__ == "__main__":
    refresh()
