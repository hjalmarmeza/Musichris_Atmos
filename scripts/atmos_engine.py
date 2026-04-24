import os
import json
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont

# Rutas Absolutas para ejecución en servidor
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clean_assets():
    assets_dir = os.path.join(BASE_DIR, 'assets')
    renders_dir = os.path.join(BASE_DIR, 'renders')
    
    # Limpiar assets temporales
    for f in os.listdir(assets_dir):
        if f.endswith('.png') and ('master' in f or 'ref' in f or 'overlay' in f or 'song' in f):
            try: os.remove(os.path.join(assets_dir, f))
            except: pass
            
    # Limpiar renders anteriores para ahorrar espacio
    if os.path.exists(renders_dir):
        for f in os.listdir(renders_dir):
            if f.endswith(('.mp4', '.jpg', '.json')):
                try: os.remove(os.path.join(renders_dir, f))
                except: pass

def create_reflection_overlay(text, output_path):
    img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Baskerville.ttc", 65)
    except: font = ImageFont.load_default()
    tw, th = draw.textbbox((0, 0), text, font=font)[2:4]
    draw.rounded_rectangle([(1280-tw)/2-40, 300, (1280+tw)/2+40, 300+th+40], radius=20, fill=(0,0,0,130))
    draw.text((1280/2, 300+20), text, font=font, fill="white", anchor="mt")
    img.save(output_path)

def create_master_overlays(main_title, output_prefix):
    # Intro
    img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: 
        f_main = ImageFont.truetype("/System/Library/Fonts/Supplemental/Baskerville.ttc", 85)
        f_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Baskerville.ttc", 40)
    except: f_main = f_sub = ImageFont.load_default()
    tw, th = draw.textbbox((0, 0), main_title, font=f_main)[2:4]
    draw.rounded_rectangle([(1280-tw)/2-50, 250, (1280+tw)/2+50, 250+th+120], radius=25, fill=(0,0,0,180))
    draw.text((1280/2, 280), main_title, font=f_main, fill="white", anchor="mt")
    draw.text((1280/2, 280+th+20), "¡CAMINEMOS JUNTOS EN FE!", font=f_sub, fill=(255,255,255,200), anchor="mt")
    img.save(f"{output_prefix}_intro.png")

    # Footer
    img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: f_foot = ImageFont.truetype("/System/Library/Fonts/Supplemental/Baskerville.ttc", 38)
    except: f_foot = ImageFont.load_default()
    draw.text((1280/2, 620), "Suscríbete para más momentos de paz", font=f_foot, fill=(255,255,255,220), anchor="mm")
    draw.text((1280/2, 680), "MusiChris Studio | Música para tu alma", font=f_foot, fill=(255,255,255,100), anchor="mm")
    img.save(os.path.join(BASE_DIR, f"{output_prefix}_footer.png"))

def generate_atmos_video(duration_secs, theme, output_name):
    print(f"🎬 [ATMOS ENGINE] Iniciando Protocolo de Turnos...")
    
    # 1. Suspender Radio para liberar RAM
    print("🛰️ Deteniendo Radio 24/7 temporalmente...")
    subprocess.run(['sudo', 'pkill', '-9', '-f', 'live_manager.py'], capture_output=True)
    subprocess.run(['sudo', 'pkill', '-9', '-f', 'ffmpeg'], capture_output=True)
    
    print(f"🎬 [ATMOS ENGINE FINAL] Iniciando Producción Maestra...")
    clean_assets()
    
    with open(os.path.join(BASE_DIR, 'data/musichris_master_catalog.json'), 'r') as f:
        catalog = json.load(f)
    with open(os.path.join(BASE_DIR, 'data/soul_reflections.json'), 'r') as f:
        reflections = json.load(f)
    
    # Cargar canciones desactivadas
    disabled_songs = []
    disabled_path = os.path.join(BASE_DIR, 'data/disabled_songs.json')
    if os.path.exists(disabled_path):
        with open(disabled_path, 'r') as f:
            disabled_songs = json.load(f)
    
    # Familias de Atmósferas (Herencia)
    families = {
        "Protección": ["Refugio", "Confianza", "Descanso", "Noche", "Fortaleza"],
        "Batalla": ["Guerra Espiritual", "Poder", "Victoria Final", "Fortaleza"],
        "Presencia": ["Adoración Celestial", "Selah", "Santidad", "Intimidad"],
        "Triunfo": ["Victoria", "Gozo", "Celebración", "Gratitud"],
        "Renovación": ["Avivamiento", "Restauración", "Renovación", "Redención"]
    }
    
    category_keywords = {
        "Refugio": ["refugio", "amparo", "abrigo"], "Confianza": ["confianza", "creer", "fe"], "Descanso": ["descanso", "reposo", "quietud"],
        "Noche": ["noche", "medianoche", "madrugada"], "Guerra Espiritual": ["guerra", "batalla", "ejército"], "Poder": ["poder", "autoridad", "fuerza"],
        "Fortaleza": ["fortaleza", "roca", "castillo"], "Victoria Final": ["victoria final", "triunfo eterno"], "Adoración Celestial": ["adoración", "celestial", "trono"],
        "Selah": ["selah", "meditación", "reflexión"], "Santidad": ["santidad", "santo", "puro"], "Intimidad": ["intimidad", "secreto", "presencia"],
        "Victoria": ["victoria", "vencer", "triunfo"], "Gozo": ["gozo", "alegría", "deleite"], "Celebración": ["celebración", "fiesta", "exaltación"],
        "Gratitud": ["gratitud", "gracias", "reconocimiento"], "Avivamiento": ["avivamiento", "despertar", "fuego"], "Restauración": ["restauración", "restitución", "sanidad"],
        "Renovación": ["renovación", "nuevo", "transformación"], "Redención": ["redención", "rescate", "gracia"]
    }

    # 1. Buscar canciones EXACTAS
    eligible_songs = []
    primary_keywords = category_keywords.get(theme, [theme.lower()])
    
    for s in catalog:
        if s['title'] in disabled_songs: continue
        song_text = f"{s.get('title','')} {s.get('theme','')} {s.get('verse','')} {','.join(s.get('moments', []))}".lower()
        if any(k in song_text for k in primary_keywords):
            eligible_songs.append(s)
            
    # 2. Si no hay suficientes canciones (menos de 15), buscar en la FAMILIA
    if len(eligible_songs) < 15:
        print(f"⚠️ Poco contenido en {theme}. Buscando herencia familiar...")
        family_members = []
        for fam, members in families.items():
            if theme in members:
                family_members = members
                break
        
        for member in family_members:
            if member == theme: continue
            member_keywords = category_keywords.get(member, [])
            for s in catalog:
                if s['title'] in disabled_songs or s in eligible_songs: continue
                song_text = f"{s.get('title','')} {s.get('theme','')} {s.get('verse','')} {','.join(s.get('moments', []))}".lower()
                if any(k in song_text for k in member_keywords):
                    eligible_songs.append(s)
            
    random.shuffle(eligible_songs)
            
    random.shuffle(eligible_songs)
    
    # Seleccionamos canciones y hacemos LOOP si es necesario para cubrir el tiempo
    selected_songs = []
    current_audio_time = 0
    
    if not eligible_songs:
        print("❌ Error: No hay canciones para este tema.")
        return

    # Loop infinito hasta llenar el tiempo solicitado
    while current_audio_time < duration_secs:
        for s in eligible_songs:
            if current_audio_time >= duration_secs:
                break
            selected_songs.append(s)
            # Intentamos obtener duración real, si no usamos 250s como fallback
            current_audio_time += s.get('duration_secs', 250)
        
        # Mezclamos para la siguiente vuelta si el loop continúa
        random.shuffle(eligible_songs)
    
    create_master_overlays(theme.upper(), os.path.join(BASE_DIR, "assets/master"))
    
    # Reflexiones distribuidas
    num_refs = max(2, int(duration_secs / 600)) # 1 cada 10 min
    reflection_overlays = []
    for i in range(num_refs):
        ref_text = random.choice(reflections)
        path = os.path.join(BASE_DIR, f"assets/ref_{i}.png")
        create_reflection_overlay(ref_text, path)
        start_t = (duration_secs / (num_refs+1)) * (i+1)
        reflection_overlays.append((path, start_t, start_t + 12))

    # Definimos la duración real orgánica + 12 segundos para el cierre maestro
    final_duration = current_audio_time + 12

    # Seleccionar PAISAJE y extraer FOTOGRAMA para velocidad
    landscapes_dir = os.path.join(BASE_DIR, 'assets/landscapes')
    landscapes = [f for f in os.listdir(landscapes_dir) if f.endswith('.mp4')]
    selected_landscape = os.path.join(landscapes_dir, random.choice(landscapes) if landscapes else 'landscape_test.mp4')
    master_bg_image = os.path.join(BASE_DIR, "assets/master_bg_frame.jpg")
    
    print(f"🌍 Capturando fotograma maestro de: {selected_landscape}")
    subprocess.run([
        "ffmpeg", "-y", "-ss", "00:00:05", "-i", selected_landscape,
        "-frames:v", "1", master_bg_image
    ], capture_output=True)

    # Componer Comando FFmpeg
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "15", "-i", master_bg_image,
        "-i", os.path.join(BASE_DIR, "assets/master_intro.png"),
        "-i", os.path.join(BASE_DIR, "assets/master_footer.png"),
        "-i", os.path.join(BASE_DIR, "assets/watermark_layer.png"),
        "-stream_loop", "-1", "-i", os.path.join(BASE_DIR, "assets/logo_animado.mp4"),
        "-i", os.path.join(BASE_DIR, "assets/outro_layer_premium.png")
    ]
    
    # Añadir overlays de reflexiones
    for r_ov in reflection_overlays: cmd += ["-i", r_ov[0]]
    
    # Añadir AUDIOS
    audio_start_idx = 6 + len(reflection_overlays)
    for s in selected_songs:
        cmd += ["-i", s['audio_url']]

    # Filtros
    v_filters = "[0:v]scale=1280:720,format=yuv420p[v_bg];"
    v_filters += "[v_bg][1:v]overlay=0:0:enable='between(t,2,15)'[v_intro];"
    v_filters += f"[v_intro][2:v]overlay=0:0:enable='lt(t,{duration_secs-10})'[v_footer];"
    v_filters += "[v_footer][3:v]overlay=0:0[v_wm];"
    
    last_v = "v_wm"
    for i, r_ov in enumerate(reflection_overlays):
        next_v = f"v_ref_{i}"
        v_filters += f"[{last_v}][{i+6}:v]overlay=0:0:enable='between(t,{r_ov[1]},{r_ov[2]})'[{next_v}];"
        last_v = next_v

    v_filters += f"[4:v]colorkey=0x000000:0.1:0.1,scale=-1:600,format=rgba[logo_clean];"
    v_filters += f"[{last_v}][logo_clean]overlay=(W-w)/2:(H-h)/2-150:enable='between(t,{final_duration-12},{final_duration-2})'[v_logo];"
    v_filters += f"[v_logo][5:v]overlay=0:0:enable='between(t,{final_duration-12},{final_duration})'[v_final]"

    print(f"⏱️ Duración total de la producción: {final_duration/60:.2f} minutos")

    # Filtro de Audio (Concat)
    a_filters = "".join([f"[{audio_start_idx+i}:a]" for i in range(len(selected_songs))])
    a_filters += f"concat=n={len(selected_songs)}:v=0:a=1[a_final]"

    output_path = os.path.join(BASE_DIR, f"renders/{output_name}")
    cmd += [
        "-filter_complex", f"{v_filters};{a_filters}",
        "-map", "[v_final]", "-map", "[a_final]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30", "-b:v", "2000k", "-maxrate", "2500k", "-bufsize", "4000k", "-r", "15", "-c:a", "aac", "-b:a", "128k",
        "-t", str(final_duration), # Usamos la duración real calculada
        output_path
    ]
    
    print(f"🚀 EJECUTANDO COMANDO MAESTRO:\n{' '.join(cmd)}")
    subprocess.run(cmd)
    
    # NUEVO: Generar Miniatura y Metadatos post-renderizado
    generate_thumbnail(theme, output_name, selected_landscape)
    generate_metadata(theme, output_name)

    # 2. Reiniciar Radio Automáticamente
    print("🛰️ Producción Terminada. Resucitando Radio 24/7...")
    try:
        # Volvemos a la carpeta home para lanzar la radio
        home_dir = os.path.expanduser("~")
        subprocess.Popen(['python3', os.path.join(home_dir, 'live_manager.py')], 
                         cwd=home_dir,
                         stdout=open(os.path.join(home_dir, 'live_manager.log'), 'a'),
                         stderr=subprocess.STDOUT,
                         start_new_session=True)
        print("✅ Radio 24/7 reactivada con éxito.")
    except Exception as e:
        print(f"⚠️ Error al reactivar la radio: {e}")

def generate_thumbnail(theme, output_name, video_path):
    print(f"🖼️ Capturando fotograma de impacto desde {video_path}...")
    temp_frame = os.path.join(BASE_DIR, f"renders/{output_name.replace('.mp4', '')}_FRAME.jpg")
    thumb_path = os.path.join(BASE_DIR, f"renders/{output_name.replace('.mp4', '')}_THUMB.jpg")
    
    # 1. Capturar fotograma al segundo 5 (para asegurar que haya imagen)
    cap_cmd = [
        "ffmpeg", "-y", "-ss", "00:00:05", "-i", video_path,
        "-frames:v", "1", temp_frame
    ]
    subprocess.run(cap_cmd, capture_output=True)
    
    # 2. Aplicar diseño ministerial sobre el fotograma capturado
    hooks = {
        "Refugio": "TU LUGAR SEGURO", "Confianza": "CREE SIN DUDAR", "Descanso": "PAZ PARA TU ALMA",
        "Noche": "DUERME EN SU PAZ", "Guerra Espiritual": "PODER Y VICTORIA", "Poder": "FUERZA DIVINA",
        "Fortaleza": "TU ROCA ETERNA", "Victoria Final": "EL TRIUNFO DE LA FE", "Adoración Celestial": "PRESENCIA DIVINA",
        "Santidad": "PURO ANTE EL PADRE", "Intimidad": "EN EL LUGAR SECRETO", "Victoria": "VENCIENDO EL MIEDO",
        "Gozo": "ALEGRÍA INAGOTABLE", "Celebración": "FIESTA EN EL CIELO", "Gratitud": "GRACIAS SEÑOR",
        "Avivamiento": "FUEGO EN TU INTERIOR", "Restauración": "DIOS TE SANA HOY", "Renovación": "TODO NUEVO",
        "Redención": "POR SU GRACIA"
    }
    hook = hooks.get(theme, "MÚSICA PARA ORAR")

    design_cmd = [
        "ffmpeg", "-y", "-i", temp_frame,
        "-vf", f"drawtext=text='{theme.upper()}':fontcolor=white:fontsize=130:x=(w-tw)/2:y=(h-th)/2-100:shadowcolor=black:shadowx=6:shadowy=6,drawtext=text='{hook}':fontcolor=white:fontsize=60:x=(w-tw)/2:y=(h-th)/2+40:shadowcolor=black:shadowx=4:shadowy=4,drawtext=text='MUSICHRIS STUDIO':fontcolor=#ffcc00:fontsize=35:x=(w-tw)/2:y=h-80:letter_spacing=15",
        "-frames:v", "1", thumb_path
    ]
    subprocess.run(design_cmd, capture_output=True)
    
    # Limpiar temporal
    if os.path.exists(temp_frame): os.remove(temp_frame)
    print(f"✅ Miniatura capturada y diseñada: {thumb_path}")

def generate_metadata(theme, output_name):
    print(f"📝 Generando Metadatos SEO Potentes...")
    meta_path = os.path.join(BASE_DIR, f"renders/{output_name.replace('.mp4', '')}_METADATA.json")
    
    metadata = {
        "title": f"1 HORA DE {theme.upper()} | Música para Orar en Intimidad y Paz | MusiChris Studio",
        "description": f"Bienvenido a MusiChris Studio. \n\n¿Buscas {theme.lower()}? Esta selección ha sido creada para transformar tu ambiente y llevarte a un nivel profundo de comunión con Dios. \n\n✨ Lo que sentirás en esta hora: \n- Paz profunda para tu alma.\n- Renovación espiritual.\n- Conexión real con el Padre.\n\nIdeal para momentos de oración, lectura bíblica o simplemente para descansar en Su presencia. \n\n🕊️ SUSCRÍBETE AHORA y activa la campana para no perderte ninguna atmósfera ministerial.\n\n#MusiChrisStudio #MusicaParaOrar #InstrumentalCristiano #OracionMatutina #PazInterior #MusicaCristiana #{theme.replace(' ', '')}",
        "tags": ["musichris studio", "musica para orar", "musica cristiana instrumental", "instrumental para orar", theme.lower(), "paz de dios", "meditacion espiritual", "musica de adoracion", "adoracion instrumental"]
    }
    
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print(f"✅ Metadatos de alto impacto listos: {meta_path}")

if __name__ == "__main__":
    import sys
    # Valores por defecto: 1 hora, Confianza, Nombre automático
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
    theme = sys.argv[2] if len(sys.argv) > 2 else "Confianza"
    
    # Nombre de salida dinámico basado en tema y tiempo
    timestamp = random.randint(1000, 9999)
    output_name = f"STUDIO_{theme.replace(' ', '_').upper()}_{duration//60}MIN_{timestamp}.mp4"
    
    generate_atmos_video(duration, theme, output_name)
