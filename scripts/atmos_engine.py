import os
import json
import random
import time
import subprocess
import requests
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "assets/temp_assets")
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

# MAPEADO DE CRUCES
CROSS_MAP = {
    "Serenidad Profunda": ["Paz Interior", "Descanso"],
    "Roca de Salvación": ["Refugio", "Confianza"],
    "Presencia Sagrada": ["Intimidad", "Avivamiento"],
    "Triunfo Espiritual": ["Guerra Espiritual", "Victoria & Gozo"],
    "Gracia Renovadora": ["Restauración", "Poder"]
}

# FRASES SEO POTENTES
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

def get_real_duration(file_path):
    """Sonda FFprobe para obtener duración exacta del archivo"""
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip()) if result.stdout else 0

def wrap_text(text, font, max_width):
    lines = []
    words = text.split(' ')
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        w = font.getlength(test_line) if hasattr(font, 'getlength') else font.getsize(test_line)[0]
        if w <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    return lines

def generate_thumbnail_intelligent(theme1, output_name, local_landscape_path, songs, theme2=None):
    print(f"🖼️ [THUMBNAIL] Generando Portada Diamond Premium...")
    thumb_path = os.path.join(RENDERS_DIR, f"{output_name.replace('.mp4', '')}_THUMB.jpg")
    temp_frame = os.path.join(TEMP_DIR, "temp_frame.jpg")
    subprocess.run(["ffmpeg", "-y", "-ss", "00:00:05", "-i", local_landscape_path, "-frames:v", "1", temp_frame], capture_output=True)
    img = Image.open(temp_frame).convert('RGBA') if os.path.exists(temp_frame) else Image.new('RGBA', (1280, 720), (20,20,20,255))
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    phrase = SEO_PHRASES.get(theme1, f"Música para {theme1}").upper()
    box_w = 950; box_h = 350; box_x = (1280 - box_w) / 2; box_y = (720 - box_h) / 2
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=40, fill=(0,0,0,180), outline=(197,160,89,255), width=6)
    font_main = get_font(65)
    lines = wrap_text(phrase, font_main, box_w - 100)
    y_text = 360 - (len(lines)-1)*40
    for line in lines:
        draw.text((640, y_text), line, font=font_main, fill="#C5A059", anchor="mm")
        y_text += 80
    draw.text((640, box_y + box_h - 40), "@MusiChris_Studio", font=get_font(28), fill="#C5A059", anchor="mm")
    logo_path = os.path.join(BASE_DIR, "assets/brand/logo_musichris.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((120, 120))
        img.paste(logo, (50, 50), logo)
    out = Image.alpha_composite(img, overlay)
    out.convert('RGB').save(thumb_path, "JPEG", quality=95)
    if os.path.exists(temp_frame): os.remove(temp_frame)

def generate_metadata_intelligent(theme1, output_name, selected_songs, theme2=None):
    meta_path = os.path.join(RENDERS_DIR, f"{output_name.replace('.mp4', '')}_META.txt")
    phrase = SEO_PHRASES.get(theme1, theme1.upper())
    with open(meta_path, 'w', encoding='utf-8') as f:
        f.write(f"TITLE:\n💎 {phrase}: ADORACIÓN Y DESCANSO\n\n")
        f.write(f"DESCRIPTION:\n✨ BIENVENIDO A MUSICHRIS STUDIO ✨\n\nCaminemos juntos en fe con esta sesión diseñada para tu alma.\n\n📍 CAPÍTULOS:\n")
        # Aquí usaremos las duraciones reales que se calculen en el motor
        pass # Se llena dinámicamente en el motor

def generate_atmos_video(duration_secs, theme1, output_name, theme2=None):
    print(f"🎬 [ATMOS ENGINE v12.9.90] Master Integrity Flow...")
    clean_assets()
    
    with open(os.path.join(BASE_DIR, 'data/musichris_master_catalog.json'), 'r') as f: catalog = json.load(f)
    history_path = os.path.join(BASE_DIR, 'data/usage_history.json')
    history_data = []
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r') as f: history_data = json.load(f)
        except: pass
    
    used_titles = [item['title'] for item in history_data if item.get('atmosphere') == theme1]
    is_cross = theme1 in CROSS_MAP
    original_theme = theme1
    if is_cross:
        theme2 = CROSS_MAP[theme1][1]
        theme1 = CROSS_MAP[theme1][0]
    
    rel_1 = [s for s in catalog if theme1 in s.get('moments', [])]
    rel_2 = [s for s in catalog if theme2 in s.get('moments', [])] if theme2 and theme2 != "none" else []
    source_pool = [s for s in (rel_1 + rel_2) if s['title'] not in used_titles] or (rel_1 + rel_2)
    random.shuffle(source_pool)
    
    # Pre-selección de canciones (Estimada)
    candidate_songs = []; est_acc = 0
    for s in source_pool:
        if est_acc > duration_secs: break
        candidate_songs.append(s); est_acc += (s.get('duration_secs') or 240)

    # 1. Descarga y Medición Real (Sonda FFprobe)
    print(f"🎵 [PASO 1/3] Descargando y midiendo duración real...")
    local_songs = []; real_acc = 0; song_times = []; selected_songs = []
    list_path = os.path.join(TEMP_DIR, "audio_list.txt")
    
    with open(list_path, 'w', encoding='utf-8') as f_list:
        for i, s in enumerate(candidate_songs):
            p = os.path.join(TEMP_DIR, f"song_{i}.mp3")
            try:
                r = requests.get(s['audio_url'], timeout=45)
                with open(p, 'wb') as f_song: f_song.write(r.content)
                dur = get_real_duration(p)
                if real_acc + dur > duration_secs + 120: # Margen pequeño
                    break
                v = s.get('context', {}).get('verse', s.get('verse', 'Salmos 23'))
                song_times.append((s['title'], v, real_acc + 2, real_acc + 15))
                real_acc += dur
                selected_songs.append(s)
                f_list.write(f"file '{p}'\n")
                local_songs.append(p)
            except: continue

    if not selected_songs: return print("❌ Error en descarga.")
    
    # 2. Audio Maestro
    audio_master = os.path.join(TEMP_DIR, "audio_master.mp3")
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_path, '-c', 'copy', audio_master], check=True)

    # 3. Paisaje y Logos
    with open(os.path.join(BASE_DIR, 'data/landscapes_remote.json'), 'r') as f: land_pool = list(json.load(f).values())
    sel_land = random.choice(land_pool)
    p_orig = os.path.join(TEMP_DIR, "land_orig.mp4")
    with open(p_orig, 'wb') as f: f.write(requests.get(sel_land, timeout=45).content)
    
    p_cut = os.path.join(TEMP_DIR, "land_main_cut.mp4")
    subprocess.run(['ffmpeg', '-y', '-stream_loop', '-1', '-i', p_orig, '-t', str(real_acc), '-vf', 'scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1/1,fps=30,format=yuv420p', '-an', '-c:v', 'libx264', '-preset', 'ultrafast', p_cut], check=True)

    logo_path = os.path.join(BASE_DIR, "assets", "Logo Hjalmar Animado.mp4")
    l_small = os.path.join(TEMP_DIR, "logo_small.mp4")
    l_large = os.path.join(TEMP_DIR, "logo_large.mp4")
    subprocess.run(['ffmpeg', '-y', '-i', logo_path, '-vf', 'scale=120:-2,format=yuv420p', '-c:v', 'libx264', '-preset', 'ultrafast', l_small], check=True)
    subprocess.run(['ffmpeg', '-y', '-i', logo_path, '-vf', 'scale=450:-2,format=yuv420p', '-c:v', 'libx264', '-preset', 'ultrafast', l_large], check=True)

    # 4. Mezcla Visual y Cierre
    print(f"🎞️ [PASO 3/3] Mezclando estética visual...")
    base_video = os.path.join(TEMP_DIR, "base_video_flat.mp4")
    os_t = max(0, int(real_acc - 10))
    cmd_base = [
        'ffmpeg', '-y', '-stream_loop', '-1', '-i', p_cut,
        '-stream_loop', '-1', '-i', l_small,
        '-stream_loop', '-1', '-i', l_large,
        '-filter_complex', 
        f"[1:v]colorkey=0x000000:0.1:0.1[ls]; [2:v]colorkey=0x000000:0.1:0.1[ll]; "
        f"[0:v][ls]overlay=x=40:y=40:enable='lt(t,{os_t})'[v1]; [v1][ll]overlay=x=(W-w)/2:y=(H-h)/2-60:enable='gt(t,{os_t})'[out]",
        '-map', '[out]', '-c:v', 'libx264', '-preset', 'superfast', '-crf', '24', '-t', str(real_acc), base_video
    ]
    subprocess.run(cmd_base, check=True)

    # 5. Capas y Títulos (Opacidad corregida a 0.22)
    ff_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not os.path.exists(ff_path): ff_path = "sans"
    ff = f":fontfile='{ff_path}'"
    vf = f"drawtext=text='@MusiChris_Studio':x=(W-tw)/2:y=(H-th)/2:fontsize=50:fontcolor=white@0.22{ff}:enable='lt(t,{os_t})'"
    for t, v, s, e in song_times:
        clean_t = t.replace("'", "").replace(":", "\\:").upper()
        clean_v = v.replace("'", "").replace(":", "\\:").upper()
        vf += f",drawtext=text='{clean_t}':{ff}:fontsize=32:fontcolor=0xC5A059FF:x=90:y=612:box=1:boxcolor=black@0.63:boxborderw=20:enable='between(t,{s},{e})'"
        vf += f",drawtext=text='{clean_v}':{ff}:fontsize=22:fontcolor=0xF5F5DCFF:x=90:y=652:box=1:boxcolor=black@0.63:boxborderw=10:enable='between(t,{s},{e})'"
    
    # Outro Textos (Grandes y centrados debajo del logo de 450px)
    vf += f",drawtext=text='@MusiChris_Studio':{ff}:fontsize=60:fontcolor=white:x=(W-tw)/2:y=(H/2+210):enable='gt(t,{os_t})'"
    vf += f",drawtext=text='¡CAMINEMOS JUNTOS EN FE!':{ff}:fontsize=35:fontcolor=0xC5A059FF:x=(W-tw)/2:y=(H/2+290):enable='gt(t,{os_t})'"
    vf += f",fade=t=in:st=0:d=2,fade=t=out:st={max(0, int(real_acc)-2)}:d=2"

    final_v = os.path.join(RENDERS_DIR, f'{output_name}.mp4')
    subprocess.run(['ffmpeg', '-y', '-i', base_video, '-i', audio_master, '-filter_complex', f"[0:v]{vf}[v_out]", '-map', '[v_out]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'superfast', '-crf', '26', '-c:a', 'copy', '-t', str(real_acc), final_v], check=True)
    
    generate_thumbnail_intelligent(theme1, output_name, final_v, selected_songs, theme2)
    # Generar Meta con tiempos reales
    meta_path = os.path.join(RENDERS_DIR, f"{output_name.replace('.mp4', '')}_META.txt")
    phrase = SEO_PHRASES.get(theme1, theme1.upper())
    with open(meta_path, 'w', encoding='utf-8') as f:
        f.write(f"TITLE:\n💎 {phrase}: ADORACIÓN Y DESCANSO\n\n")
        f.write(f"DESCRIPTION:\n✨ BIENVENIDO A MUSICHRIS STUDIO ✨\n\nCaminemos juntos en fe con esta sesión diseñada para tu alma.\n\n📍 CAPÍTULOS:\n")
        acc = 0
        for s in selected_songs:
            p = os.path.join(TEMP_DIR, f"song_{selected_songs.index(s)}.mp3")
            m = int(acc // 60); s_ = int(acc % 60)
            v = s.get('context', {}).get('verse', s.get('verse', 'Salmos 23'))
            f.write(f"[{m:02d}:{s_:02d}] {s['title']} - {v}\n")
            acc += get_real_duration(p)
        f.write(f"\n#MusiChris #Worship #PazInterior #Fe #CaminemosJuntosEnFe\n")
    
    # Historial
    try:
        hist = []
        if os.path.exists(history_path):
            with open(history_path, 'r') as f: hist = json.load(f)
        for s in selected_songs: hist.append({"title": s['title'], "atmosphere": original_theme, "date": time.ctime(), "render": output_name})
        with open(history_path, 'w', encoding='utf-8') as f: json.dump(hist, f, indent=4)
    except: pass
    print(f"✅ Completado: {output_name}")

if __name__ == "__main__":
    import sys
    dur = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    thm = sys.argv[2] if len(sys.argv) > 2 else "Paz Interior"
    timestamp = time.strftime("%Y%m%d-%H%M")
    out = f"ATMOS_{thm.replace(' ', '_')}_{timestamp}"
    generate_atmos_video(dur, thm, out)
    sys.path.append(os.path.join(BASE_DIR, 'scripts'))
    import youtube_uploader
    youtube_uploader.upload_video(os.path.join(RENDERS_DIR, f"{out}.mp4"), os.path.join(RENDERS_DIR, f"{out}_THUMB.jpg"), os.path.join(RENDERS_DIR, f"{out}_META.txt"))
