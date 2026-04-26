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

def generate_thumbnail_intelligent(theme1, output_name, landscape_url, songs, theme2=None):
    print(f"🖼️ [THUMBNAIL] Generando Portada Diamond Premium...")
    thumb_path = os.path.join(BASE_DIR, f"renders/{output_name.replace('.mp4', '')}_THUMB.jpg")
    temp_frame = os.path.join(BASE_DIR, "assets/temp_frame.jpg")
    subprocess.run(["ffmpeg", "-y", "-ss", "00:00:05", "-i", landscape_url, "-frames:v", "1", temp_frame], capture_output=True)
    img = Image.open(temp_frame).convert('RGBA') if os.path.exists(temp_frame) else Image.new('RGB', (1280, 720), (20,20,20))
    draw = ImageDraw.Draw(img, 'RGBA')
    phrase = SEO_PHRASES.get(theme1, f"Música para {theme1}")
    title_text = phrase.upper()
    
    box_w = 900; box_h = 320; box_x = (1280 - box_w) / 2; box_y = (720 - box_h) / 2
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=40, fill=(0,0,0,180), outline=(197,160,89,255), width=6)
    draw.text((640, 360), title_text, font=get_font(60), fill="#C5A059", anchor="mm")
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

    # Construir tiempos de overlay (sin PNGs)
    song_times = []
    curr_t = 0
    for s in selected_songs:
        song_times.append((s['title'], s.get('verse', 'Salmos 23'), curr_t + 2, curr_t + 12))
        curr_t += get_song_duration(s)

    with open(os.path.join(BASE_DIR, 'data/landscapes_remote.json'), 'r') as f: landscapes = list(json.load(f).values())
    sel_lands = [random.choice(landscapes) for _ in range(3)]
    
    local_songs = []
    for i, s in enumerate(selected_songs):
        path = os.path.join(TEMP_DIR, f"song_{i}.mp3")
        r = requests.get(s['audio_url'], timeout=30)
        with open(path, 'wb') as f: f.write(r.content)
        local_songs.append(path)

    local_lands = []
    for i, l in enumerate(sel_lands):
        path = os.path.join(TEMP_DIR, f"land_{i}.mp4")
        r = requests.get(l, timeout=30)
        with open(path, 'wb') as f: f.write(r.content)
        local_lands.append(path)

    logo_path = os.path.join(BASE_DIR, "assets", "Logo Hjalmar Animado.mp4")
    base_video  = os.path.join(TEMP_DIR, "base_video.mp4")
    base_logo   = os.path.join(TEMP_DIR, "base_logo.mp4")
    final_video = os.path.join(BASE_DIR, f'renders/{output_name}.mp4')
    
    n_songs = len(selected_songs)
    land_dur = acc_time / 3

    # ══════════════════════════════════════════════
    # PRE-PASO: Normalizar cada paisaje a duración exacta
    # ══════════════════════════════════════════════
    print(f"🎬 [PRE-PASO] Normalizando paisajes a {land_dur:.0f}s cada uno...")
    # PRE-PASO: Normalizar cada paisaje y logo
    # ══════════════════════════════════════════════
    print(f"🎬 [PRE-PASO] Normalizando archivos...")
    cut_lands = []
    for i, src in enumerate(local_lands):
        cut_path = os.path.join(TEMP_DIR, f"land_{i}_cut.mp4")
        subprocess.run([
            'ffmpeg', '-y', '-stream_loop', '-1', '-i', src,
            '-t', str(land_dur),
            '-vf', 'scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1/1,fps=30,format=yuv420p',
            '-an', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28', cut_path
        ], check=True)
        cut_lands.append(cut_path)
        # LIBERAR ESPACIO: Borrar el original descargado
        try:
            os.remove(src)
            print(f"   ✅ Paisaje {i+1} procesado y original liberado.")
        except:
            pass
    
    # Escalar logo después de haber liberado espacio de paisajes
    logo_small = os.path.join(TEMP_DIR, "logo_small.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-i', logo_path,
        '-vf', 'scale=120:-1,fps=30,format=yuv420p',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23', logo_small
    ], check=True)
    print(f"   ✅ Archivos normalizados.")

    # ══════════════════════════════════════════════
    # PASO FINAL: Audio, Textos y Logo en un solo grafo
    # ══════════════════════════════════════════════
    print(f"🎵 [PASO FINAL] Ensamblando Video...")
    
    ff = ":fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'"
    
    # 1. Video Base (Concat Paisajes + Logo)
    vf = "[0:v][1:v][2:v]concat=n=3:v=1:a=0[base_v];"
    vf += "[base_v][3:v]overlay=x=40:y=40[v_logo];"
    
    curr_v = "[v_logo]"
    
    # 2. Hook (Música para...) con Caja integrada
    vf += f"{curr_v}drawtext=text='MÚSICA PARA':{ff}:fontsize=46:fontcolor=0xC5A059FF:x=(W-tw)/2:y=(H/2-60):box=1:boxcolor=black@0.63:boxborderw=40:enable='between(t,0,8)'[v_h1];"
    vf += f"[v_h1]drawtext=text='{theme2.upper() if theme2 else theme1.upper()}':{ff}:fontsize=46:fontcolor=0xC5A059FF:x=(W-tw)/2:y=(H/2+10):box=1:boxcolor=black@0.63:boxborderw=40:enable='between(t,0,8)'[v_hook];"
    curr_v = "[v_hook]"

    # 3. Canciones con Caja integrada
    for i, (title, verse, start, end) in enumerate(song_times):
        v_next = f"[v_t{i}2]"
        vf += f"{curr_v}drawtext=text='{title.upper()}':{ff}:fontsize=32:fontcolor=0xC5A059FF:x=90:y=612:box=1:boxcolor=black@0.63:boxborderw=20:enable='between(t,{start},{end})'[v_t{i}1];"
        vf += f"[v_t{i}1]drawtext=text='{verse.upper()}':{ff}:fontsize=22:fontcolor=0xF5F5DCFF:x=90:y=652:box=1:boxcolor=black@0.63:boxborderw=10:enable='between(t,{start},{end})'{v_next};"
        curr_v = v_next

    # 4. Outro con Caja integrada
    os_t, os_e = int(acc_time - 8), int(acc_time)
    vf += f"{curr_v}drawtext=text='CAMINEMOS JUNTOS EN FE':{ff}:fontsize=44:fontcolor=0xC5A059FF:x=(W-tw)/2:y=(H/2-60):box=1:boxcolor=black@0.63:boxborderw=40:enable='between(t,{os_t},{os_e})'[v_o1];"
    vf += f"[v_o1]drawtext=text='SUSCRÍBETE @MUSICHRIS_STUDIO':{ff}:fontsize=32:fontcolor=0xF5F5DCFF:x=(W-tw)/2:y=(H/2+10):box=1:boxcolor=black@0.63:boxborderw=40:enable='between(t,{os_t},{os_e})'[v_o2];"
    vf += f"[v_o2]fade=t=in:st=0:d=2,fade=t=out:st={int(acc_time)-2}:d=2[v_out]"

    # 5. Audio
    af_parts = []
    for i in range(n_songs):
        af_parts.append(f"[{i+4}:a]aresample=44100:async=1,settb=AVTB[as{i}]")
    
    a_tags = "".join([f"[as{i}]" for i in range(n_songs)])
    af = ";".join(af_parts) + f";{a_tags}concat=n={n_songs}:v=0:a=1,afade=t=in:st=0:d=2,afade=t=out:st={int(acc_time)-2}:d=2[a_out]"

    cmd2 = ['ffmpeg', '-y']
    for p in cut_lands: cmd2 += ['-i', p]
    cmd2 += ['-stream_loop', '-1', '-i', logo_small]
    for p in local_songs: cmd2 += ['-i', p]
    
    cmd2 += [
        '-filter_complex', f"{vf}{af}",
        '-map', '[v_out]', '-map', '[a_out]',
        '-c:v', 'libx264', '-preset', 'superfast', '-crf', '28', 
        '-threads', '2',
        '-t', str(acc_time - 0.5), final_video
    ]
    subprocess.run(cmd2, check=True)
    print(f"✅ [PASO FINAL] Video final listo.")

    generate_thumbnail_intelligent(theme1, output_name, sel_lands[0], selected_songs, theme2)
    generate_metadata_intelligent(theme1, output_name, selected_songs, theme2)
    
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
    v_path = os.path.join(BASE_DIR, f"renders/{out}.mp4")
    t_path = os.path.join(BASE_DIR, f"renders/{out}_THUMB.jpg")
    m_path = os.path.join(BASE_DIR, f"renders/{out}_META.txt")
    
    if not os.path.exists(v_path):
        raise FileNotFoundError(f"❌ El video no se generó en: {v_path}")
        
    youtube_uploader.upload_video(v_path, t_path, m_path)
    print(f"🚀 [SISTEMA] Producción finalizada y publicada con éxito.")
