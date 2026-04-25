import os
import json
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont

# Rutas Absolutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# MAPEADO MAESTRO DE ATMÓSFERAS (Global)
ATMOSPHERE_MAP = {
    "Refugio": ["refugio", "seguridad", "alivio", "amparo", "abrigo", "protección", "identidad", "pertenencia", "esperanza"],
    "Confianza": ["confianza", "ayuda", "fidelidad", "dirección", "soberanía", "creer", "fe", "estabilidad", "mano de dios"],
    "Descanso": ["descanso", "paz", "quietud", "reposo", "meditación", "bienestar", "calma", "silencio"],
    "Guerra Espiritual": ["guerra", "batalla", "ejército", "valentía", "defensa", "fortaleza", "poder", "victoria"],
    "Poder": ["poder", "autoridad", "gloria", "majestad", "dominio", "grandeza", "soberanía", "hijo"],
    "Victoria & Gozo": ["victoria", "gozo", "celebración", "triunfo", "alegría", "vencer", "reino"],
    "Restauración": ["restauración", "gracia", "sanidad", "renovación", "perdón", "restitución", "redención", "bondad"],
    "Avivamiento": ["avivamiento", "fuego", "espíritu", "santidad", "adoración", "intimidad", "anhelo", "presencia", "luz"],
    "Paz Interior": ["paz", "descanso", "noche", "quietud", "dormir", "refugio", "seguro"],
    "Intimidad": ["intimidad", "adoracion", "santidad", "presencia", "corazon", "amor"]
}

def clean_assets():
    assets_dir = os.path.join(BASE_DIR, 'assets')
    renders_dir = os.path.join(BASE_DIR, 'renders')
    for f in os.listdir(assets_dir):
        if f.endswith('.png') and ('master' in f or 'ref' in f or 'overlay' in f or 'song' in f):
            try: os.remove(os.path.join(assets_dir, f))
            except: pass
    if os.path.exists(renders_dir):
        for f in os.listdir(renders_dir):
            if f.endswith(('.mp4', '.jpg', '.json', '.txt')):
                try: os.remove(os.path.join(renders_dir, f))
                except: pass

def get_font(size):
    paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", "/System/Library/Fonts/Supplemental/Baskerville.ttc", "arial.ttf"]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def get_song_duration(s): return s.get('duration_secs') or 240

def create_reflection_overlay(text, output_path):
    img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = get_font(34)
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        tw = draw.textbbox((0, 0), " ".join(current_line), font=font)[2]
        if tw > 850:
            lines.append(" ".join(current_line[:-1]))
            current_line = [word]
    lines.append(" ".join(current_line))
    final_text = "\n".join(lines)
    bbox = draw.multiline_textbbox((0, 0), final_text, font=font, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    padding_w = 80; padding_h = 60
    draw.rounded_rectangle([(1280-tw)/2 - padding_w + 5, 280 + 5, (1280+tw)/2 + padding_w + 5, 280 + th + padding_h*2 + 5], radius=45, fill=(0,0,0,100))
    draw.rounded_rectangle([(1280-tw)/2 - padding_w, 280, (1280+tw)/2 + padding_w, 280 + th + padding_h*2], radius=45, fill=(10,10,10,190), outline=(197,160,89,150), width=3)
    draw.rounded_rectangle([(1280-tw)/2 - padding_w + 4, 280 + 4, (1280+tw)/2 + padding_w - 4, 280 + th + padding_h*2 - 4], radius=40, outline=(255,255,255,30), width=1)
    draw.multiline_text((1280/2, 280 + padding_h), final_text, font=font, fill="#F5F5DC", anchor="mt", align="center", spacing=12)
    img.save(output_path)

def create_song_info_overlay(title, verse, output_path):
    img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_title = get_font(38); font_verse = get_font(26)
    text_t = title.upper(); text_v = verse.upper()
    bbox_t = draw.textbbox((0, 0), text_t, font=font_title)
    bbox_v = draw.textbbox((0, 0), text_v, font=font_verse)
    max_w = max(bbox_t[2]-bbox_t[0], bbox_v[2]-bbox_v[0])
    x_pos = 1280 - max_w - 100; y_pos = 720 - 180
    draw.rounded_rectangle([x_pos - 30, y_pos - 30, 1280 - 50, y_pos + 120], radius=25, fill=(10,10,10,210), outline=(197,160,89,180), width=3)
    draw.line([x_pos - 15, y_pos - 10, x_pos - 15, y_pos + 100], fill="#C5A059", width=4)
    draw.text((x_pos, y_pos), text_t, font=font_title, fill="#C5A059")
    draw.text((x_pos, y_pos + 55), text_v, font=font_verse, fill="#F5F5DC")
    img.save(output_path)

def generate_atmos_video(duration_secs, theme1, output_name, theme2=None):
    # 1. Sincronización Automática con Google Sheets
    try:
        import sys
        sys.path.append(os.path.join(BASE_DIR, 'scripts'))
        from sync_data import sync_all
        sync_all()
    except Exception as e:
        print(f"⚠️ Aviso: No se pudo sincronizar con Sheets ({e}). Usando datos locales.")

    print(f"🎬 [ATMOS ENGINE v12.0] Iniciando Producción Autónoma Diamond...")
    clean_assets()
    with open(os.path.join(BASE_DIR, 'data/musichris_master_catalog.json'), 'r') as f:
        catalog = json.load(f)
    with open(os.path.join(BASE_DIR, 'data/soul_reflections.json'), 'r') as f:
        reflections_data = json.load(f)
    
    # Cargar Historial de Uso
    history_path = os.path.join(BASE_DIR, 'data/usage_history.json')
    used_titles = []
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r') as f:
                history_data = json.load(f)
                used_titles = [item['title'] for item in history_data if item.get('atmosphere') == theme1]
        except: pass

    target_themes_1 = ATMOSPHERE_MAP.get(theme1, [theme1])
    target_themes_2 = ATMOSPHERE_MAP.get(theme2, [theme2]) if theme2 and theme2 != "none" else []

    # Filtrar canciones relevantes
    relevant_songs_1 = [s for s in catalog if any(t.lower() in str(s.get('moments', [])).lower() for t in target_themes_1)]
    relevant_songs_2 = [s for s in catalog if any(t.lower() in str(s.get('moments', [])).lower() for t in target_themes_2)] if target_themes_2 else []
    
    # Aplicar filtro de USO solo para atmósfera PURA (si theme2 es none)
    if not theme2 or theme2 == "none":
        original_count = len(relevant_songs_1)
        relevant_songs_1 = [s for s in relevant_songs_1 if s['title'] not in used_titles]
        if not relevant_songs_1 and original_count > 0:
            print(f"⚠️ [AVISO] Inventario agotado para '{theme1}'. Repitiendo catálogo.")
            relevant_songs_1 = [s for s in catalog if any(t.lower() in str(s.get('moments', [])).lower() for t in target_themes_1)]

    selected_songs = []
    current_audio_time = 0
    random.shuffle(relevant_songs_1)
    
    if theme2 and theme2 != "none":
        random.shuffle(relevant_songs_2)
        # En cruces, mezclamos ambas listas
        for s in relevant_songs_1:
            if current_audio_time >= duration_secs/2: break
            selected_songs.append(s); current_audio_time += get_song_duration(s)
        for s in relevant_songs_2:
            if current_audio_time >= duration_secs: break
            selected_songs.append(s); current_audio_time += get_song_duration(s)
    else:
        for s in relevant_songs_1:
            if current_audio_time >= duration_secs: break
            selected_songs.append(s); current_audio_time += get_song_duration(s)


    # FILTRAR CANCIONES VÁLIDAS
    selected_songs = [s for s in selected_songs if s.get('audio_url') and len(s['audio_url']) > 5]
    if not selected_songs:
        print("❌ [ERROR] No se encontraron canciones con audio válido.")
        return
    current_audio_time = sum(get_song_duration(s) for s in selected_songs)

    # Assets fijos
    intro_path = os.path.join(BASE_DIR, "assets/intro_diamond.png")
    outro_path = os.path.join(BASE_DIR, "assets/outro_diamond.png")
    img_intro = Image.new('RGBA', (1280, 720), (10, 10, 10, 255))
    ImageDraw.Draw(img_intro).text((1280/2, 720/2), f"EXPERIENCIA {theme1.upper()}", font=get_font(60), fill="#C5A059", anchor="mm")
    img_intro.save(intro_path)
    img_outro = Image.new('RGBA', (1280, 720), (10, 10, 10, 255))
    ImageDraw.Draw(img_outro).text((1280/2, 720/2), "GRACIAS POR ADORAR CON NOSOTROS", font=get_font(40), fill="#C5A059", anchor="mm")
    img_outro.save(outro_path)

    # Overlays
    reflection_overlays = []
    refs_list = reflections_data.get(theme1, reflections_data.get("Paz Interior", []))
    for i, ref_text in enumerate(refs_list[:3]):
        path = os.path.join(BASE_DIR, f"assets/ref_{i}.png")
        create_reflection_overlay(ref_text, path)
        start_t = 15 + (duration_secs / 4) * (i+1)
        if start_t < current_audio_time - 30: reflection_overlays.append((path, start_t, start_t + 20)) 

    song_overlays = []; change_points = [0]; acc_time = 0
    for i, song in enumerate(selected_songs):
        path = os.path.join(BASE_DIR, f"assets/song_{i}.png")
        create_song_info_overlay(song.get('title', 'MusiChris'), song.get('context', {}).get('verse', 'Salmos'), path)
        song_overlays.append((path, acc_time + 2, acc_time + 14))
        acc_time += get_song_duration(song)
        if (i + 1) % 2 == 0: change_points.append(acc_time)

    # Paisajes
    with open(os.path.join(BASE_DIR, 'data/landscapes_remote.json'), 'r') as f: landscapes_map = json.load(f)
    video_urls = list(landscapes_map.values())
    selected_landscapes = [random.choice(video_urls) for _ in range(len(change_points))]
    
    cmd = ["/opt/homebrew/bin/ffmpeg", "-y"]
    for l_url in selected_landscapes: cmd += ["-stream_loop", "-1", "-i", l_url]
    cmd += ["-stream_loop", "-1", "-i", os.path.join(BASE_DIR, "assets/Logo Hjalmar Animado.mp4")]
    cmd += ["-i", intro_path]; cmd += ["-i", outro_path]
    for r_ov in reflection_overlays: cmd += ["-i", r_ov[0]]
    for s_ov in song_overlays: cmd += ["-i", s_ov[0]]
    audio_idx = len(selected_landscapes) + 3 + len(reflection_overlays) + len(song_overlays)
    for s in selected_songs: cmd += ["-i", s['audio_url']]
    
    # 3. Filtros de Video y Capa de Partículas (Procedural Dust)
    v_filters = ""
    num_l = len(selected_landscapes)
    for i in range(num_l): v_filters += f"[{i}:v]scale=1280:720,format=yuv420p[bg{i}];"
    
    # Mezcla de paisajes
    last_v = "bg0"
    for i in range(1, num_l):
        next_v = f"mix{i}"
        v_filters += f"[{last_v}][bg{i}]overlay=enable='gt(t,{change_points[i]})'[{next_v}];"
        last_v = next_v
    
    # GENERACIÓN DE PARTÍCULAS (Capa sutil de polvo de luz)
    v_filters += f"nullsrc=size=1280x720 [particles_base]; [particles_base] noise=alls=20:allf=t+u, format=yuv420p, boxblur=10:1, lutyuv='y=if(gt(val,200),val,0)' [particles_raw]; [particles_raw] format=rgba, colorchannelmixer=aa=0.1 [particles_final];"
    
    # Capas Extra y Fades
    v_filters += f"[{num_l}:v]colorkey=0x000000:0.1:0.1,scale=-1:180,format=rgba[logo_clean];"
    v_filters += f"[{last_v}][particles_final]overlay=0:0[v_dust];"
    v_filters += f"[v_dust][logo_clean]overlay=50:50[v_logo];"
    
    # Aplicar FADE-IN (5s)
    v_filters += f"[{num_l+1}:v]fade=in:st=0:d=1,fade=out:st=9:d=1[intro_f];"
    v_filters += f"[v_logo][intro_f]overlay=enable='between(t,0,10)'[v_intro];"
    
    # Outro y Fade-out Final
    fade_duration = 5
    video_end = current_audio_time
    fade_start = video_end - fade_duration
    
    v_filters += f"[{num_l+2}:v]fade=in:st={current_audio_time-15}:d=2,fade=out:st={current_audio_time-2}:d=2[outro_f];"
    v_filters += f"[v_intro][outro_f]overlay=enable='gt(t,{current_audio_time-15})'[v_main_f];"
    
    last_v = "v_main_f"; idx_ref = num_l + 3
    for i, r_ov in enumerate(reflection_overlays):
        next_v = f"v_ref_{i}"
        v_filters += f"[{last_v}][{idx_ref+i}:v]overlay=0:0:enable='between(t,{r_ov[1]},{r_ov[2]})'[{next_v}];"
        last_v = next_v
    idx_song = idx_ref + len(reflection_overlays)
    for i, s_ov in enumerate(song_overlays):
        next_v = f"v_song_{i}"
        v_filters += f"[{last_v}][{idx_song+i}:v]overlay=0:0:enable='between(t,{s_ov[1]},{s_ov[2]})'[{next_v}];"
        last_v = next_v
    
    # Aplicar FADES FINALES (Audio y Video)
    v_filters += f"[{last_v}]fade=in:st=0:d=5,fade=out:st={fade_start}:d=5[v_f_pre];"
    # AÑADIR BARRA DE PROGRESO DIAMOND (Línea de 2px dorada)
    v_filters += f"[v_f_pre]drawbox=y=ih-2:w=iw*t/{video_end}:h=2:color=#C5A059@0.8:t=fill[v_final]"
    
    a_concat = "".join([f"[{audio_idx+i}:a]" for i in range(len(selected_songs))]) + f"concat=n={len(selected_songs)}:v=0:a=1[a_raw]"
    a_filters = f"{a_concat};[a_raw]afade=t=in:st=0:d=5,afade=t=out:st={fade_start}:d=5[a_final]"
    
    output_path = os.path.join(BASE_DIR, f"renders/{output_name}")
    cmd += ["-filter_complex", f"{v_filters.strip(';')};{a_filters}", "-map", "[v_final]", "-map", "[a_final]", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-t", str(video_end), output_path]
    full_cmd = " ".join(cmd)
    print(f"DEBUG CMD: [COMANDO FFmpeg OCULTO POR LONGITUD]")
    
    print(f"🚀 [DIAMOND ENGINE] Renderizando Sesión Atmos con Partículas y Fades...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ [FFMPEG ERROR]: {result.stderr}")
        return

    if not os.path.exists(output_path):
        print(f"❌ [ERROR] El video no se generó. Revisar logs de FFmpeg.")
        return
    # 3. Registrar Uso en Historial
    try:
        history_path = os.path.join(BASE_DIR, 'data/usage_history.json')
        history = []
        if os.path.exists(history_path):
            with open(history_path, 'r') as f: history = json.load(f)
        
        for s in selected_songs:
            history.append({
                "title": s['title'],
                "atmosphere": theme1,
                "date": str(subprocess.check_output(['date']).decode().strip()),
                "render": output_name
            })
            
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        print(f"✅ [HISTORIAL] {len(selected_songs)} canciones marcadas como 'Usadas'.")
    except Exception as e:
        print(f"⚠️ Error al actualizar historial: {e}")

    generate_thumbnail_intelligent(theme1, output_name, selected_landscapes[0], selected_songs, theme2)
    generate_metadata_intelligent(theme1, output_name, selected_songs, theme2)

    
    # 2. Intento de Subida Automática a YouTube
    try:
        import sys
        sys.path.append(os.path.join(BASE_DIR, 'scripts'))
        from youtube_uploader import upload_video
        thumb_file = output_path.replace('.mp4', '_THUMB.jpg')
        meta_file = output_path.replace('.mp4', '_META.txt')
        upload_video(output_path, thumb_file, meta_file)
    except Exception as e:
        print(f"⚠️ [YOUTUBE] Subida automática pendiente o fallida (Verificar credenciales): {e}")

def generate_thumbnail_intelligent(theme1, output_name, landscape_path, selected_songs, theme2=None):
    print(f"🖼️ [THUMBNAIL] Generando Portada Diamond...")
    thumb_path = os.path.join(BASE_DIR, f"renders/{output_name.replace('.mp4', '')}_THUMB.jpg")
    temp_frame = os.path.join(BASE_DIR, "assets/temp_frame.jpg")
    subprocess.run(["/opt/homebrew/bin/ffmpeg", "-y", "-ss", "00:00:05", "-i", landscape_path, "-frames:v", "1", temp_frame], capture_output=True)
    if not os.path.exists(temp_frame): return
    img = Image.open(temp_frame).convert('RGBA'); overlay = Image.new('RGBA', img.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    draw.rectangle([0, 0, 1280, 720], fill=(0,0,0,80))
    final_theme = f"{theme1} & {theme2}" if theme2 and theme2 != "none" else theme1
    hook = selected_songs[0].get('context', {}).get('focus', 'PAZ INTERIOR').upper()
    font_main = get_font(110); font_sub = get_font(45)
    draw.text((1280/2 + 4, 300 + 4), final_theme.upper(), font=font_main, fill=(0,0,0,150), anchor="mm")
    draw.text((1280/2, 300), final_theme.upper(), font=font_main, fill="#C5A059", anchor="mm")
    draw.text((1280/2 + 2, 450 + 2), hook[:50], font=font_sub, fill=(0,0,0,150), anchor="mm")
    draw.text((1280/2, 450), hook[:50], font=font_sub, fill="#F5F5DC", anchor="mm")
    Image.alpha_composite(img, overlay).convert('RGB').save(thumb_path, "JPEG", quality=95)
    try: os.remove(temp_frame)
    except: pass

def generate_metadata_intelligent(theme1, output_name, selected_songs, theme2=None):
    print(f"📝 [SEO] Generando Metadatos Potentes...")
    final_theme = f"{theme1} y {theme2}" if theme2 and theme2 != "none" else theme1
    hook_title = selected_songs[0].get('context', {}).get('focus', 'Encuentra Paz').upper()
    title = f"💎 {final_theme.upper()}: {hook_title} | Sesión Atmos Completa (Música para el Alma)"
    description = f"✨ BIENVENIDO A UNA NUEVA EXPERIENCIA ATMOS DE MUSICHRIS STUDIO ✨\n\n"
    description += f"Sumérgete en esta sesión de {final_theme} diseñada para momentos de oración y descanso profundo.\n\n"
    description += "📍 CAPÍTULOS Y VERSÍCULOS:\n"
    acc = 0
    for s in selected_songs:
        m, s_r = divmod(int(acc), 60); timestamp = f"{m:02d}:{s_r:02d}"
        description += f"[{timestamp}] {s['title']} - (Versículo: {s.get('context', {}).get('verse', 'Salmos')})\n"
        acc += get_song_duration(s)
    description += "\n#MusiChris #Atmos #MusicaCristiana #Worship #PazInterior #Oracion #Adoracion #DiosEsFiel"
    meta_path = os.path.join(BASE_DIR, f"renders/{output_name.replace('.mp4', '')}_META.txt")
    with open(meta_path, "w", encoding="utf-8") as f: f.write(f"TITLE:\n{title}\n\nDESCRIPTION:\n{description}")

if __name__ == "__main__":
    import sys
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 1800
    theme1 = sys.argv[2] if len(sys.argv) > 2 else "Paz Interior"
    theme2 = sys.argv[3] if len(sys.argv) > 3 else "none"
    output_name = f"STUDIO_DIAMOND_{random.randint(1000,9999)}.mp4"
    generate_atmos_video(duration, theme1, output_name, theme2)
