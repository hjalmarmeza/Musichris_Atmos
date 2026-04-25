import os
import json
import random
import subprocess
import time
from PIL import Image, ImageDraw, ImageFont

# Rutas Absolutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# MAPEADO DE CRUCES
CROSS_MAP = {
    "Serenidad Profunda": ["Paz Interior", "Descanso"],
    "Roca de Salvación": ["Refugio", "Confianza"],
    "Presencia Sagrada": ["Intimidad", "Avivamiento"],
    "Triunfo Espiritual": ["Guerra Espiritual", "Victoria & Gozo"],
    "Gracia Renovadora": ["Restauración", "Poder"]
}

# FRASES SEO POTENTES (Algoritmo)
SEO_PHRASES = {
    "Refugio": "Música para buscar Refugio y Paz",
    "Confianza": "Música para fortalecer tu Fe y Confianza",
    "Descanso": "Música para un Descanso Profundo",
    "Paz Interior": "Música para alcanzar Paz Interior",
    "Intimidad": "Música para orar en Intimidad con Dios",
    "Poder": "Música de Adoración y Poder Celestial",
    "Restauración": "Música para Sanar y Restaurar tu Alma",
    "Avivamiento": "Música para Despertar el Avivamiento",
    "Guerra Espiritual": "Música para Vencer en la Batalla",
    "Victoria & Gozo": "Música de Victoria y Gozo Eterno",
    "Serenidad Profunda": "Música para una Serenidad Profunda",
    "Roca de Salvación": "Música para tu Roca de Salvación",
    "Presencia Sagrada": "Música para entrar en su Presencia Sagrada",
    "Triunfo Espiritual": "Música para un Triunfo Espiritual",
    "Gracia Renovadora": "Música de Gracia Renovadora"
}

def clean_assets():
    assets_dir = os.path.join(BASE_DIR, 'assets')
    for f in os.listdir(assets_dir):
        if f.endswith('.png') and ('master' in f or 'ref' in f or 'overlay' in f or 'song' in f or 'intro' in f or 'outro' in f):
            try: os.remove(os.path.join(assets_dir, f))
            except: pass

def get_font(size):
    paths = ["/System/Library/Fonts/Supplemental/Baskerville.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "arial.ttf"]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def get_song_duration(s): return s.get('duration_secs') or 240

def create_song_info_overlay(title, verse, output_path):
    img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_t = get_font(36); font_v = get_font(24)
    text_t = title.upper(); text_v = verse.upper()
    draw.rounded_rectangle([50, 580, 500, 680], radius=20, fill=(10,10,10,180), outline=(197,160,89,150), width=2)
    draw.text((80, 600), text_t, font=font_t, fill="#C5A059")
    draw.text((80, 640), text_v, font=font_v, fill="#F5F5DC")
    img.save(output_path)

def generate_thumbnail_intelligent(theme1, output_name, landscape_url, songs, theme2=None):
    print(f"🖼️ [THUMBNAIL] Generando Portada Diamond Premium...")
    thumb_path = os.path.join(BASE_DIR, f"renders/{output_name.replace('.mp4', '')}_THUMB.jpg")
    temp_frame = os.path.join(BASE_DIR, "assets/temp_frame.jpg")
    subprocess.run(["/opt/homebrew/bin/ffmpeg", "-y", "-ss", "00:00:05", "-i", landscape_url, "-frames:v", "1", temp_frame], capture_output=True)
    img = Image.open(temp_frame).convert('RGBA') if os.path.exists(temp_frame) else Image.new('RGB', (1280, 720), (20,20,20))
    draw = ImageDraw.Draw(img, 'RGBA')
    phrase = SEO_PHRASES.get(theme1, f"Música para {theme1}")
    title_text = phrase.upper()
    
    box_w = 900; box_h = 320; box_x = (1280 - box_w) / 2; box_y = (720 - box_h) / 2
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=40, fill=(0,0,0,180), outline=(197,160,89,255), width=6)
    draw.text((640, 360 - 50), title_text, font=get_font(60), fill="#C5A059", anchor="mm")
    draw.text((640, 360 + 50), "ADORACIÓN Y DESCANSO PROFUNDO", font=get_font(34), fill="#F5F5DC", anchor="mm")
    draw.text((640, box_y + box_h - 40), "@MusiChris_Studio", font=get_font(28), fill="#C5A059", anchor="mm")
    img.convert('RGB').save(thumb_path, "JPEG", quality=95)
    if os.path.exists(temp_frame): os.remove(temp_frame)

def generate_metadata_intelligent(theme1, output_name, selected_songs, theme2=None):
    meta_path = os.path.join(BASE_DIR, f"renders/{output_name.replace('.mp4', '')}_META.txt")
    phrase = SEO_PHRASES.get(theme1, theme1.upper())
    with open(meta_path, 'w') as f:
        f.write(f"TITLE:\n💎 {phrase}: ADORACIÓN Y DESCANSO | Sesión Atmos Completa\n\n")
        f.write(f"DESCRIPTION:\n✨ BIENVENIDO A MUSICHRIS STUDIO ✨\n\nCaminemos juntos en fe con esta sesión diseñada para tu alma.\n\n📍 CAPÍTULOS:\n")
        acc = 0
        for s in selected_songs:
            m = acc // 60; s_ = acc % 60
            v = s.get('context', {}).get('verse', 'Salmos 23')
            f.write(f"[{m:02d}:{s_:02d}] {s['title']} - {v}\n")
            acc += get_song_duration(s)
        f.write(f"\n#MusiChris #Atmos #Worship #PazInterior #Fe #CaminemosJuntosEnFe\n")

def generate_atmos_video(duration_secs, theme1, output_name, theme2=None):
    print(f"🎬 [ATMOS ENGINE v12.3] Iniciando Producción Diamond Integridad...")
    clean_assets()
    
    with open(os.path.join(BASE_DIR, 'data/musichris_master_catalog.json'), 'r') as f: catalog = json.load(f)
    history_path = os.path.join(BASE_DIR, 'data/usage_history.json')
    used_titles = []
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r') as f:
                history_data = json.load(f)
                used_titles = [item['title'] for item in history_data if item.get('atmosphere') == theme1]
        except: pass

    # Detectar si es un cruce
    is_cross = theme1 in CROSS_MAP
    if is_cross:
        theme2 = CROSS_MAP[theme1][1]
        theme1 = CROSS_MAP[theme1][0]
        print(f"🔀 [CROSS] Detectado Cruce: {theme1} + {theme2}")

    rel_1 = [s for s in catalog if theme1 in s.get('moments', [])]
    rel_2 = [s for s in catalog if theme2 in s.get('moments', [])] if theme2 and theme2 != "none" else []
    
    combined_pool = rel_1 + rel_2
    
    # Filtrar usadas (solo para Puras, en Cruces se permiten repetidas según el usuario)
    if not is_cross:
        available_pool = [s for s in combined_pool if s['title'] not in used_titles]
        if not available_pool: 
            print("⚠️ [WARNING] No hay canciones nuevas, usando pool completo.")
            available_pool = combined_pool
    else:
        available_pool = combined_pool
    if not theme2 or theme2 == "none":
        rel_1 = [s for s in rel_1 if s['title'] not in used_titles] or rel_1

    source_pool = rel_1 + rel_2 if theme2 and theme2 != "none" else rel_1
    random.shuffle(source_pool)
    
    selected_songs = []; acc_time = 0
    for s in source_pool:
        dur = get_song_duration(s)
        if acc_time + dur > duration_secs: break
        selected_songs.append(s); acc_time += dur

    if not selected_songs: return print("❌ Sin canciones.")

    # Crear Intro y Outro
    intro_path = os.path.join(BASE_DIR, "assets/intro.png")
    outro_path = os.path.join(BASE_DIR, "assets/outro.png")
    
    for path, text, font_size in [(intro_path, f"EXPERIENCIA {theme1.upper()}", 50), (outro_path, "CAMINEMOS JUNTOS EN FE\nSUSCRÍBETE A @MUSICHRIS_STUDIO", 40)]:
        img = Image.new('RGBA', (1280, 720), (10, 10, 10, 255))
        draw = ImageDraw.Draw(img)
        draw.multiline_text((640, 360), text, font=get_font(font_size), fill="#C5A059", anchor="mm", align="center")
        img.save(path)

    # Overlays
    song_overlays = []; curr = 5
    for i, s in enumerate(selected_songs):
        p = os.path.join(BASE_DIR, f"assets/song_{i}.png")
        create_song_info_overlay(s['title'], s.get('verse', 'Salmos 23'), p)
        song_overlays.append((p, curr + 2, curr + 12))
        curr += get_song_duration(s)

    # Paisajes
    with open(os.path.join(BASE_DIR, 'data/landscapes_remote.json'), 'r') as f: landscapes = list(json.load(f).values())
    sel_lands = [random.choice(landscapes) for _ in range(3)]
    
    # FFmpeg Command
    cmd = ['/opt/homebrew/bin/ffmpeg', '-y', '-loop', '1', '-t', '5', '-i', intro_path]
    for s in selected_songs: cmd += ['-i', s['audio_url']]
    for l in sel_lands: cmd += ['-stream_loop', '-1', '-i', l]
    cmd += ['-loop', '1', '-t', '5', '-i', outro_path]
    for p, s, e in song_overlays: cmd += ['-i', p]

    # Filtros
    v_f = "[0:v]fade=t=in:st=0:d=1,fade=t=out:st=4:d=1[v0];"
    land_dur = acc_time / 3
    for i in range(3):
        idx = len(selected_songs) + 1 + i
        v_f += f"[{idx}:v]trim=duration={land_dur},setpts=PTS-STARTPTS,fade=t=in:st=0:d=1,fade=t=out:st={land_dur-1}:d=1[vl{i}];"
    
    outro_idx = len(selected_songs) + 4
    v_f += f"[{outro_idx}:v]fade=t=in:st=0:d=1,fade=t=out:st=4:d=1[vout];"
    v_f += f"[v0][vl0][vl1][vl2][vout]concat=n=5:v=1:a=0[v_base];"
    
    # Audio
    a_f = "".join([f"[{i+1}:a]" for i in range(len(selected_songs))]) + f"concat=n={len(selected_songs)}:v=0:a=1[a_final]"
    
    # Overlays
    curr_v = "[v_base]"
    for i, (p, st, en) in enumerate(song_overlays):
        idx = len(selected_songs) + 5 + i
        v_f += f"[{idx}:v]scale=1280:720[ov{i}];"
        v_f += f"{curr_v}[ov{i}]overlay=enable='between(t,{st},{en})'[v{i+1}];"
        curr_v = f"[v{i+1}]"

    final_video = os.path.join(BASE_DIR, f'renders/{output_name}.mp4')
    cmd += ['-filter_complex', f"{v_f}{a_f}", '-map', curr_v, '-map', '[a_final]', '-c:v', 'libx264', '-preset', 'ultrafast', final_video]
    
    subprocess.run(cmd)
    generate_thumbnail_intelligent(theme1, output_name, sel_lands[0], selected_songs, theme2)
    generate_metadata_intelligent(theme1, output_name, selected_songs, theme2)
    
    # Historial
    try:
        hist = []
        if os.path.exists(history_path):
            with open(history_path, 'r') as f: hist = json.load(f)
        for s in selected_songs: hist.append({"title": s['title'], "atmosphere": theme1, "date": time.ctime(), "render": output_name})
        with open(history_path, 'w') as f: json.dump(hist, f, indent=4)
    except: pass
    print(f"✅ Completado: {output_name}")

if __name__ == "__main__":
    generate_atmos_video(600, "Paz Interior", "STUDIO_DIAMOND_FINAL")
