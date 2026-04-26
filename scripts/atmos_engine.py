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

def create_hook_overlay(text, output_path):
    img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = get_font(50)
    # Box semi-transparente central Diamond
    w, h = 900, 220
    x, y = (1280-w)//2, (720-h)//2
    draw.rounded_rectangle([x, y, x+w, y+h], radius=25, fill=(0,0,0,160), outline=(197,160,89,200), width=4)
    # Asegurar dos líneas para el Hook (Algoritmo Retención)
    if "\n" not in text:
        words = text.split(' ')
        mid = len(words)//2
        text = " ".join(words[:mid]) + "\n" + " ".join(words[mid:])
    draw.multiline_text((640, 360), text.upper(), font=font, fill="#C5A059", anchor="mm", align="center", spacing=20)
    img.save(output_path)

def create_song_info_overlay(title, verse, output_path):
    img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_t = get_font(36); font_v = get_font(24)
    text_t = title.upper(); text_v = verse.upper()
    # Box más elegante y minimalista
    draw.rounded_rectangle([60, 590, 520, 690], radius=15, fill=(0,0,0,160), outline=(197,160,89,200), width=3)
    draw.text((90, 610), text_t, font=font_t, fill="#C5A059")
    draw.text((90, 650), text_v, font=font_v, fill="#F5F5DC")
    img.save(output_path)

def wrap_text(text, font, max_width):
    lines = []
    words = text.split(' ')
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        w = ImageFont.FreeTypeFont.getbbox(font, test_line)[2]
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
    
    # 1. Sacar el fondo
    subprocess.run(["ffmpeg", "-y", "-ss", "00:00:05", "-i", local_landscape_path, "-frames:v", "1", temp_frame], capture_output=True)
    
    img = Image.open(temp_frame).convert('RGBA') if os.path.exists(temp_frame) else Image.new('RGBA', (1280, 720), (20,20,20,255))
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    
    phrase = SEO_PHRASES.get(theme1, f"Música para {theme1}")
    title_text = phrase.upper()
    
    # 2. Caja Central Semitransparente
    box_w = 950; box_h = 350; box_x = (1280 - box_w) / 2; box_y = (720 - box_h) / 2
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=40, fill=(0,0,0,180), outline=(197,160,89,255), width=6)
    
    # 3. Texto con Wrapping (Doble línea)
    font_main = get_font(65)
    lines = wrap_text(title_text, font_main, box_w - 100)
    
    y_text = 360 - (len(lines)-1)*40 # Ajuste vertical según número de líneas
    for line in lines:
        draw.text((640, y_text), line, font=font_main, fill="#C5A059", anchor="mm")
        y_text += 80
    
    # 4. Handle Instagram/YouTube
    font_sub = get_font(28)
    draw.text((640, box_y + box_h - 40), "@MusiChris_Studio", font=font_sub, fill="#C5A059", anchor="mm")
    
    # 5. Logo Diamond (Sin recuadro negro)
    logo_path = os.path.join(BASE_DIR, "assets/brand/logo_musichris.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((120, 120))
        img.paste(logo, (50, 50), logo) # El tercer argumento 'logo' es la máscara para transparencia
    
    # Combinar y Guardar
    out = Image.alpha_composite(img, overlay)
    out.convert('RGB').save(thumb_path, "JPEG", quality=95)
    if os.path.exists(temp_frame): os.remove(temp_frame)

def generate_metadata_intelligent(theme1, output_name, selected_songs, theme2=None):
    meta_path = os.path.join(RENDERS_DIR, f"{output_name.replace('.mp4', '')}_META.txt")
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
    original_theme = theme1
    if is_cross:
        theme2 = CROSS_MAP[theme1][1]
        theme1 = CROSS_MAP[theme1][0]
        print(f"🔀 [CROSS] Detectado Cruce: {theme1} + {theme2}")

    # Cargar historial de uso global para el descuento
    used_titles_global = [item['title'] for item in history_data] if history_data else []
    
    rel_1 = [s for s in catalog if theme1 in s.get('moments', [])]
    rel_2 = [s for s in catalog if theme2 in s.get('moments', [])] if theme2 and theme2 != "none" else []
    
    source_pool = [s for s in (rel_1 + rel_2) if s['title'] not in used_titles] or (rel_1 + rel_2)
    random.shuffle(source_pool)
    
    selected_songs = []; acc_time = 0
    for s in source_pool:
        dur = get_song_duration(s)
        if acc_time + dur > duration_secs: break
        selected_songs.append(s); acc_time += dur

    if not selected_songs: return print("❌ Sin canciones.")
    n_songs = len(selected_songs)

    # Construir tiempos de overlay (sin PNGs)
    song_times = []
    curr_t = 0
    for s in selected_songs:
        song_times.append((s['title'], s.get('verse', 'Salmos 23'), curr_t + 2, curr_t + 12))
        curr_t += get_song_duration(s)

    # 1. Cargar catálogo de paisajes
    with open(os.path.join(BASE_DIR, 'data/landscapes_remote.json'), 'r') as f: 
        land_pool = list(json.load(f).values())
    
    # 2. Descargar canciones
    local_songs = []
    for i, s in enumerate(selected_songs):
        path = os.path.join(TEMP_DIR, f"song_{i}.mp3")
        r = requests.get(s['audio_url'], timeout=30)
        with open(path, 'wb') as f: f.write(r.content)
        local_songs.append(path)

    # 3. Descargar y procesar Paisaje Único (Zen)
    print(f"🎬 [PRE-PASO] Preparando paisaje único...")
    sel_land = random.choice(land_pool)
    p_orig = os.path.join(TEMP_DIR, "land_orig.mp4")
    r = requests.get(sel_land, timeout=30)
    with open(p_orig, 'wb') as f: f.write(r.content)
    # Verificar si el archivo se descargó bien
    if not os.path.exists(p_orig) or os.path.getsize(p_orig) < 1000:
        raise ValueError(f"❌ El paisaje descargado es inválido o está vacío: {p_orig}")

    # PASO 1/3: Preparar Landscape Base (Con Bucle Infinito)
    print(f"🎞️ [PASO 1/3] Procesando fondo (Loop Infinito)...")
    p_cut = os.path.join(TEMP_DIR, "land_main_cut.mp4")
    cmd_cut = [
        'ffmpeg', '-y', 
        '-stream_loop', '-1', # Bucle infinito para que nunca falte video
        '-i', p_orig, 
        '-t', str(acc_time), 
        '-vf', 'scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1/1,fps=30,format=yuv420p',
        '-an', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23', p_cut
    ]
    subprocess.run(cmd_cut, check=True)
    
    try: os.remove(p_orig)
    except: pass

    # 4. Preparar Logo
    logo_path = os.path.join(BASE_DIR, "assets", "Logo Hjalmar Animado.mp4")
    logo_small = os.path.join(TEMP_DIR, "logo_small.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-i', logo_path,
        '-vf', 'scale=120:-1,fps=30,format=yuv420p',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23', logo_small
    ], check=True)
    
    print(f"   ✅ Recursos normalizados.")

    # ══════════════════════════════════════════════
    # PASO 1/2: Generar Video Base (Bucle + Logo Transparente)
    # ══════════════════════════════════════════════
    print(f"🎞️ [PASO 1/2] Creando base con Logo Transparente...")
    base_video = os.path.join(TEMP_DIR, "base_video_flat.mp4")
    
    # Aplicar colorkey al logo para eliminar el fondo negro
    cmd_base = [
        'ffmpeg', '-y',
        '-stream_loop', '-1', '-i', p_cut,
        '-stream_loop', '-1', '-i', logo_small,
        '-filter_complex', "[1:v]colorkey=0x000000:0.1:0.1[logo_clear]; [0:v][logo_clear]overlay=x=40:y=40:shortest=1[out]",
        '-map', '[out]', '-c:v', 'libx264', '-preset', 'superfast', '-crf', '24',
        '-t', str(acc_time), base_video
    ]
    subprocess.run(cmd_base, check=True)

    try: os.remove(p_cut)
    except: pass

    # ══════════════════════════════════════════════
    # PASO 2/3: Crear Audio Maestro (Estrategia El Tanque)
    # ══════════════════════════════════════════════
    print(f"🎵 [PASO 2/3] Aplanando pistas de audio...")
    
    norm_songs = []
    for i, p in enumerate(local_songs):
        n_path = os.path.join(TEMP_DIR, f"norm_{i}.mp3")
        subprocess.run(['ffmpeg', '-y', '-i', p, '-ar', '44100', '-ac', '2', '-b:a', '192k', n_path], capture_output=True)
        norm_songs.append(n_path)
    
    list_path = os.path.join(TEMP_DIR, "pistas.txt")
    with open(list_path, 'w') as f:
        for p in norm_songs: f.write(f"file '{os.path.abspath(p)}'\n")
    
    audio_master = os.path.join(TEMP_DIR, "audio_master.mp3")
    cmd_audio = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_path,
        '-af', f"afade=t=in:st=0:d=2,afade=t=out:st={max(0, int(acc_time)-2)}:d=2",
        '-c:a', 'libmp3lame', '-q:a', '2', audio_master
    ]
    subprocess.run(cmd_audio, check=True)
    
    # ══════════════════════════════════════════════
    # PASO 3/3: Ensamblaje Final (Agua de marca + Títulos)
    # ══════════════════════════════════════════════
    print(f"🎞️ [PASO 3/3] Capas de branding y títulos dinámicos...")
    
    # Detección de fuente más robusta
    ff_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" # Estándar en Ubuntu/GitHub
    if not os.path.exists(ff_path): ff_path = "sans"
    ff = f":fontfile='{ff_path}'"
    
    # Filtro base con Watermark Central
    vf = f"drawtext=text='@MusiChris_Studio':x=(W-tw)/2:y=(H-th)/2:fontsize=50:fontcolor=white@0.12{ff}"
    
    # Añadir títulos de canciones
    for title, verse, start, end in song_times:
        clean_title = title.replace("'", "").upper()
        clean_verse = verse.replace("'", "").upper()
        vf += f",drawtext=text='{clean_title}':{ff}:fontsize=32:fontcolor=0xC5A059FF:x=90:y=612:box=1:boxcolor=black@0.63:boxborderw=20:enable='between(t,{start},{end})'"
        vf += f",drawtext=text='{clean_verse}':{ff}:fontsize=22:fontcolor=0xF5F5DCFF:x=90:y=652:box=1:boxcolor=black@0.63:boxborderw=10:enable='between(t,{start},{end})'"

    # Intro y Outro
    vf += f",drawtext=text='MÚSICA PARA':{ff}:fontsize=46:fontcolor=0xC5A059FF:x=(W-tw)/2:y=(H/2-60):box=1:boxcolor=black@0.63:boxborderw=40:enable='between(t,0,8)'"
    vf += f",drawtext=text='{theme2.upper() if theme2 else theme1.upper()}':{ff}:fontsize=46:fontcolor=0xC5A059FF:x=(W-tw)/2:y=(H/2+10):box=1:boxcolor=black@0.63:boxborderw=40:enable='between(t,0,8)'"
    
    os_t, os_e = max(0, int(acc_time - 8)), int(acc_time)
    vf += f",drawtext=text='CAMINEMOS JUNTOS EN FE':{ff}:fontsize=44:fontcolor=0xC5A059FF:x=(W-tw)/2:y=(H/2-60):box=1:boxcolor=black@0.63:boxborderw=40:enable='between(t,{os_t},{os_e})'"
    vf += f",drawtext=text='SUSCRÍBETE @MUSICHRIS_STUDIO':{ff}:fontsize=32:fontcolor=0xF5F5DCFF:x=(W-tw)/2:y=(H/2+10):box=1:boxcolor=black@0.63:boxborderw=40:enable='between(t,{os_t},{os_e})'"
    
    # Fades finales
    vf += f",fade=t=in:st=0:d=2,fade=t=out:st={max(0, int(acc_time)-2)}:d=2"

    final_video = os.path.join(RENDERS_DIR, f'{output_name}.mp4')
    cmd_final = [
        'ffmpeg', '-y', 
        '-i', base_video, 
        '-i', audio_master,
        '-filter_complex', f"[0:v]{vf}[v_out]",
        '-map', '[v_out]', '-map', '1:a',
        '-c:v', 'libx264', '-preset', 'superfast', '-crf', '26', 
        '-c:a', 'copy', '-threads', '2', '-t', str(acc_time - 0.5), final_video
    ]
    subprocess.run(cmd_final, check=True)
    
    print(f"✅ [PASO FINAL] Video final listo.")
    generate_thumbnail_intelligent(theme1, output_name, final_video, selected_songs, theme2)
    generate_metadata_intelligent(theme1, output_name, selected_songs, theme2)
    
    # Limpieza Total Final
    for f in [base_video, audio_master, p_cut, logo_small]:
        try: 
            if os.path.exists(f): os.remove(f)
        except: pass
    
    try:
        hist = []
        if os.path.exists(history_path):
            with open(history_path, 'r') as f: hist = json.load(f)
        for s in selected_songs: hist.append({"title": s['title'], "atmosphere": original_theme, "date": time.ctime(), "render": output_name})
        with open(history_path, 'w') as f: json.dump(hist, f, indent=4)
    except: pass
    print(f"✅ Completado: {output_name}")

import sys

if __name__ == "__main__":
    dur = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    thm = sys.argv[2] if len(sys.argv) > 2 else "Paz Interior"
    
    timestamp = time.strftime("%Y%m%d-%H%M")
    out = f"ATMOS_{thm.replace(' ', '_')}_{timestamp}"
    
    generate_atmos_video(dur, thm, out)
    
    # Subir a YouTube
    print(f"📡 [UPLOAD] Iniciando despacho a YouTube Studio...")
    sys.path.append(os.path.join(BASE_DIR, 'scripts'))
    import youtube_uploader
    v_path = os.path.join(RENDERS_DIR, f"{out}.mp4")
    t_path = os.path.join(RENDERS_DIR, f"{out}_THUMB.jpg")
    m_path = os.path.join(RENDERS_DIR, f"{out}_META.txt")
    
    if not os.path.exists(v_path):
        raise FileNotFoundError(f"❌ El video no se generó en: {v_path}")
        
    youtube_uploader.upload_video(v_path, t_path, m_path)
    print(f"🚀 [SISTEMA] Producción finalizada y publicada con éxito.")
