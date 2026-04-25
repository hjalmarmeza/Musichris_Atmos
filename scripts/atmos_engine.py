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
            if f.endswith(('.mp4', '.jpg', '.json')):
                try: os.remove(os.path.join(renders_dir, f))
                except: pass

def get_font(size):
    paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", "/System/Library/Fonts/Supplemental/Baskerville.ttc", "arial.ttf"]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def create_reflection_overlay(text, output_path):
    # Imagen de alta resolución para párrafos
    img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = get_font(32) # Tamaño ideal para párrafos
    
    # Envolver texto (Word Wrap)
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        tw = draw.textbbox((0, 0), " ".join(current_line), font=font)[2]
        if tw > 800:
            lines.append(" ".join(current_line[:-1]))
            current_line = [word]
    lines.append(" ".join(current_line))
    
    final_text = "\n".join(lines)
    tw, th = draw.multiline_textbbox((0, 0), final_text, font=font, align="center")[2:4]
    
    padding = 50
    # Caja Glassmorphism
    draw.rounded_rectangle([(1280-tw)/2 - padding, 300, (1280+tw)/2 + padding, 300 + th + padding*2], radius=40, fill=(0,0,0,160), outline=(255,255,255,40), width=1)
    draw.multiline_text((1280/2, 300 + padding), final_text, font=font, fill="white", anchor="mt", align="center", spacing=10)
    img.save(output_path)

def create_song_info_overlay(title, verse, output_path):
    # Overlay elegante para info de canción (esquina inferior derecha)
    img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(36)
    font_verse = get_font(24)
    
    text_t = title.upper()
    text_v = verse.upper()
    
    # Calcular dimensiones
    tw_t = draw.textbbox((0, 0), text_t, font=font_title)[2]
    tw_v = draw.textbbox((0, 0), text_v, font=font_verse)[2]
    max_w = max(tw_t, tw_v)
    
    # Posición: Inferior Derecha
    x_pos = 1280 - max_w - 80
    y_pos = 720 - 150
    
    # Caja Glassmorphism pequeña
    draw.rounded_rectangle([x_pos - 20, y_pos - 20, 1280 - 40, y_pos + 100], radius=20, fill=(0,0,0,180), outline=(197,160,89,100), width=2)
    draw.text((x_pos, y_pos), text_t, font=font_title, fill="#C5A059") # Color Dorado Diamond
    draw.text((x_pos, y_pos + 50), text_v, font=font_verse, fill="white")
    
    img.save(output_path)

def generate_atmos_video(duration_secs, theme1, output_name, theme2=None):
    print(f"🎬 [ATMOS ENGINE v9.0] Iniciando Producción Diamond...")
    clean_assets()
    
    with open(os.path.join(BASE_DIR, 'data/musichris_master_catalog.json'), 'r') as f:
        catalog = json.load(f)
    with open(os.path.join(BASE_DIR, 'data/soul_reflections.json'), 'r') as f:
        reflections_data = json.load(f)
    
    # Selección de canciones
    target_themes_1 = ATMOSPHERE_MAP.get(theme1, [theme1])
    target_themes_2 = ATMOSPHERE_MAP.get(theme2, [theme2]) if theme2 and theme2 != "none" else []
    
    relevant_songs_1 = [s for s in catalog if any(t.lower() in str(s.get('moments', [])).lower() for t in target_themes_1)]
    relevant_songs_2 = [s for s in catalog if any(t.lower() in str(s.get('moments', [])).lower() for t in target_themes_2)] if target_themes_2 else []

    selected_songs = []
    current_audio_time = 0
    if theme2 and theme2 != "none":
        random.shuffle(relevant_songs_1); random.shuffle(relevant_songs_2)
        for s in relevant_songs_1:
            if current_audio_time >= duration_secs/2: break
            selected_songs.append(s); current_audio_time += s.get('duration_secs', 250)
        for s in relevant_songs_2:
            if current_audio_time >= duration_secs: break
            selected_songs.append(s); current_audio_time += s.get('duration_secs', 250)
    else:
        random.shuffle(relevant_songs_1)
        for s in relevant_songs_1:
            if current_audio_time >= duration_secs: break
            selected_songs.append(s); current_audio_time += s.get('duration_secs', 250)

    # 1. Crear Reflexiones (Párrafos)
    refs_list = reflections_data.get(theme1, reflections_data.get("Paz Interior", []))
    reflection_overlays = []
    for i, ref_text in enumerate(refs_list[:3]): # Máximo 3 por video
        path = os.path.join(BASE_DIR, f"assets/ref_{i}.png")
        create_reflection_overlay(ref_text, path)
        # Distribuir reflexiones a lo largo del video
        start_t = (duration_secs / 4) * (i+1)
        reflection_overlays.append((path, start_t, start_t + 20)) 

    # 1.1 Crear Info de Canciones (Overlays Dinámicos)
    song_overlays = []
    accumulated_time = 0
    for i, song in enumerate(selected_songs):
        path = os.path.join(BASE_DIR, f"assets/song_{i}.png")
        title = song.get('title', 'MusiChris')
        verse = song.get('context', {}).get('verse', 'Salmos')
        create_song_info_overlay(title, verse, path)
        
        # Mostrar info al inicio de cada canción por 12 segundos
        song_overlays.append((path, accumulated_time + 2, accumulated_time + 14))
        accumulated_time += song.get('duration_secs', 250)

    # 2. Selección de Paisajes (Variación Dinámica desde la Nube)
    with open(os.path.join(BASE_DIR, 'data/landscapes_remote.json'), 'r') as f:
        landscapes_map = json.load(f)
    
    video_keys = list(landscapes_map.keys())
    selected_keys = random.sample(video_keys, min(3, len(video_keys)))
    selected_landscapes = [landscapes_map[k] for k in selected_keys]
    
    # Comando FFmpeg Base
    cmd = ["ffmpeg", "-y"]
    for l_url in selected_landscapes: 
        cmd += ["-stream_loop", "-1", "-i", l_url]
    
    # Overlays fijos
    logo_path = os.path.join(BASE_DIR, "ui/assets/Logo Hjalmar Animado.mp4")
    cmd += ["-stream_loop", "-1", "-i", logo_path] # Logo [3] (si hay 3 paisajes) o [len(landscapes)]
    
    for r_ov in reflection_overlays: cmd += ["-i", r_ov[0]]
    for s_ov in song_overlays: cmd += ["-i", s_ov[0]]
    
    audio_idx = len(selected_landscapes) + 1 + len(reflection_overlays) + len(song_overlays)
    for s in selected_songs: cmd += ["-i", s['audio_url']]

    # Filtros de Video
    v_filters = ""
    num_l = len(selected_landscapes)
    interval = current_audio_time / num_l
    for i in range(num_l):
        v_filters += f"[{i}:v]scale=1280:720,format=yuv420p[bg{i}];"
    
    # Mezcla de paisajes
    last_v = "bg0"
    for i in range(1, num_l):
        next_v = f"mix{i}"
        v_filters += f"[{last_v}][bg{i}]overlay=enable='gt(t,{i*interval})'[{next_v}];"
        last_v = next_v
    
    # Logo y Reflexiones
    v_filters += f"[{num_l}:v]colorkey=0x000000:0.1:0.1,scale=-1:200,format=rgba[logo_clean];"
    v_filters += f"[{last_v}][logo_clean]overlay=50:50[v_with_logo];"
    
    last_v = "v_with_logo"
    # Overlays de Reflexión (Párrafos)
    for i, r_ov in enumerate(reflection_overlays):
        next_v = f"v_ref_{i}"
        v_filters += f"[{last_v}][{num_l+1+i}:v]overlay=0:0:enable='between(t,{r_ov[1]},{r_ov[2]})'[{next_v}];"
        last_v = next_v

    # Overlays de Canción (Título/Versículo)
    start_idx_song = num_l + 1 + len(reflection_overlays)
    for i, s_ov in enumerate(song_overlays):
        next_v = f"v_song_{i}"
        v_filters += f"[{last_v}][{start_idx_song+i}:v]overlay=0:0:enable='between(t,{s_ov[1]},{s_ov[2]})'[{next_v}];"
        last_v = next_v

    # Audio Concat
    a_filters = "".join([f"[{audio_idx+i}:a]" for i in range(len(selected_songs))]) + f"concat=n={len(selected_songs)}:v=0:a=1[a_final]"

    output_path = os.path.join(BASE_DIR, f"renders/{output_name}")
    cmd += ["-filter_complex", f"{v_filters};{a_filters}", "-map", f"[{last_v}]", "-map", "[a_final]", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30", "-t", str(current_audio_time), output_path]
    
    print(f"🚀 Renderizando Video Híbrido con Variación de Paisajes...")
    subprocess.run(cmd)
    
    # Usar el primer paisaje seleccionado para la miniatura
    generate_thumbnail_intelligent(theme1, output_name, selected_landscapes[0], selected_songs, theme2)
    generate_metadata_intelligent(theme1, output_name, selected_songs, theme2)

def generate_thumbnail_intelligent(theme1, output_name, landscape_path, selected_songs, theme2=None):
    thumb_path = os.path.join(BASE_DIR, f"renders/{output_name.replace('.mp4', '')}_THUMB.jpg")
    final_theme = f"{theme1} + {theme2}" if theme2 and theme2 != "none" else theme1
    hook = selected_songs[0].get('context', {}).get('focus', 'MÚSICA PARA TU ALMA').upper()
    design_cmd = ["ffmpeg", "-y", "-ss", "00:00:05", "-i", landscape_path, "-vf", (f"scale=1280:720,drawbox=x=(w-900)/2:y=(h-450)/2:w=900:h=450:color=black@0.6:t=fill,drawtext=text='{final_theme.upper()}':fontcolor=#C5A059:fontsize=90:x=(w-tw)/2:y=(h-th)/2-80,drawtext=text='{hook[:40]}':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2+60"), "-frames:v", "1", thumb_path]
    subprocess.run(design_cmd, capture_output=True)

def generate_metadata_intelligent(theme1, output_name, selected_songs, theme2=None):
    final_theme = f"{theme1} y {theme2}" if theme2 and theme2 != "none" else theme1
    title = f"💎 EXPERIENCIA DIAMOND: {final_theme.upper()} | MusiChris Studio"
    
    time_codes = "📌 Capítulos de esta sesión:\n"
    current_t = 0
    for s in selected_songs[:15]: # Limitar capítulos para la descripción
        minutes = int(current_t // 60)
        seconds = int(current_t % 60)
        time_codes += f"{minutes:02d}:{seconds:02d} - {s['title']}\n"
        current_t += s.get('duration_secs', 250)

    description = f"{title}\n\n{time_codes}\n\nEsta sesión incluye Variación Dinámica de Paisajes y Párrafos de Reflexión Ministerial para una experiencia profunda.\n\n#MusiChrisStudio #{theme1.replace(' ', '')}"
    metadata = {"title": title, "description": description, "tags": [theme1, theme2, "musichris"]}
    with open(os.path.join(BASE_DIR, f"renders/{output_name.replace('.mp4', '')}_METADATA.json"), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 1800
    theme1 = sys.argv[2] if len(sys.argv) > 2 else "Paz Interior"
    theme2 = sys.argv[3] if len(sys.argv) > 3 else "none"
    output_name = f"STUDIO_DIAMOND_{random.randint(1000,9999)}.mp4"
    generate_atmos_video(duration, theme1, output_name, theme2)
