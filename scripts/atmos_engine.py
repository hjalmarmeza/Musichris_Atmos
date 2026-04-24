import os
import json
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont

def clean_assets():
    for f in os.listdir('assets'):
        if f.endswith('.png') and ('master' in f or 'ref' in f or 'overlay' in f or 'song' in f):
            try: os.remove(os.path.join('assets', f))
            except: pass

def create_reflection_overlay(text, output_path):
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Baskerville.ttc", 65)
    except: font = ImageFont.load_default()
    tw, th = draw.textbbox((0, 0), text, font=font)[2:4]
    draw.rounded_rectangle([(1920-tw)/2-40, 450, (1920+tw)/2+40, 450+th+40], radius=20, fill=(0,0,0,130))
    draw.text((1920/2, 450+20), text, font=font, fill="white", anchor="mt")
    img.save(output_path)

def create_master_overlays(main_title, output_prefix):
    # Intro
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: 
        f_main = ImageFont.truetype("/System/Library/Fonts/Supplemental/Baskerville.ttc", 85)
        f_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Baskerville.ttc", 40)
    except: f_main = f_sub = ImageFont.load_default()
    tw, th = draw.textbbox((0, 0), main_title, font=f_main)[2:4]
    draw.rounded_rectangle([(1920-tw)/2-50, 400, (1920+tw)/2+50, 400+th+120], radius=25, fill=(0,0,0,180))
    draw.text((1920/2, 430), main_title, font=f_main, fill="white", anchor="mt")
    draw.text((1920/2, 430+th+20), "¡CAMINEMOS JUNTOS EN FE!", font=f_sub, fill=(255,255,255,200), anchor="mt")
    img.save(f"{output_prefix}_intro.png")

    # Footer
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: f_foot = ImageFont.truetype("/System/Library/Fonts/Supplemental/Baskerville.ttc", 38)
    except: f_foot = ImageFont.load_default()
    draw.text((1920/2, 940), "Suscríbete para más momentos de paz", font=f_foot, fill=(255,255,255,220), anchor="mm")
    draw.text((1920/2, 1010), "MusiChris Studio | Música para tu alma", font=f_foot, fill=(255,255,255,100), anchor="mm")
    img.save(f"{output_prefix}_footer.png")

def generate_atmos_video(duration_secs, theme, output_name):
    print(f"🎬 [ATMOS ENGINE FINAL] Iniciando Producción Maestra...")
    clean_assets()
    
    with open('data/musichris_master_catalog.json', 'r') as f:
        catalog = json.load(f)
    with open('data/soul_reflections.json', 'r') as f:
        reflections = json.load(f)
    
    # Cargar canciones desactivadas
    disabled_songs = []
    if os.path.exists('data/disabled_songs.json'):
        with open('data/disabled_songs.json', 'r') as f:
            disabled_songs = json.load(f)
    
    # Filtrar por momentos o tema, y quitar las desactivadas
    eligible_songs = [s for s in catalog if (theme in s.get('moments', []) or theme == s.get('theme')) and s['title'] not in disabled_songs]
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
    
    create_master_overlays(theme.upper(), "assets/master")
    
    # Reflexiones distribuidas
    num_refs = max(2, int(duration_secs / 600)) # 1 cada 10 min
    reflection_overlays = []
    for i in range(num_refs):
        ref_text = random.choice(reflections)
        path = f"assets/ref_{i}.png"
        create_reflection_overlay(ref_text, path)
        start_t = (duration_secs / (num_refs+1)) * (i+1)
        reflection_overlays.append((path, start_t, start_t + 12))

    # Definimos la duración real orgánica + 12 segundos para el cierre maestro
    final_duration = current_audio_time + 12

    # Seleccionar PAISAJE ALEATORIO
    landscapes_dir = 'assets/landscapes'
    landscapes = [f for f in os.listdir(landscapes_dir) if f.endswith('.mp4')]
    selected_landscape = os.path.join(landscapes_dir, random.choice(landscapes) if landscapes else 'landscape_test.mp4')
    print(f"🌍 Paisaje seleccionado: {selected_landscape}")

    # Componer Comando FFmpeg
    cmd = [
        "nice", "-n", "19", "/opt/homebrew/bin/ffmpeg", "-y",
        "-stream_loop", "-1", "-i", selected_landscape,
        "-i", "assets/master_intro.png",
        "-i", "assets/master_footer.png",
        "-i", "assets/watermark_layer.png",
        "-stream_loop", "-1", "-i", "assets/logo_animado.mp4",
        "-i", "assets/outro_layer_premium.png"
    ]
    
    # Añadir overlays de reflexiones
    for r_ov in reflection_overlays: cmd += ["-i", r_ov[0]]
    
    # Añadir AUDIOS
    audio_start_idx = 6 + len(reflection_overlays)
    for s in selected_songs:
        cmd += ["-i", s['audio_url']]

    # Filtros
    v_filters = "[0:v]scale=1920:1080[v_bg];"
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

    cmd += [
        "-filter_complex", f"{v_filters};{a_filters}",
        "-map", "[v_final]", "-map", "[a_final]",
        "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-b:a", "192k",
        "-t", str(final_duration), # Usamos la duración real calculada
        f"renders/{output_name}"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    import sys
    # Valores por defecto: 1 hora, Paz Interior, Nombre automático
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
    theme = sys.argv[2] if len(sys.argv) > 2 else "Paz Interior"
    
    # Nombre de salida dinámico basado en tema y tiempo
    timestamp = random.randint(1000, 9999)
    output_name = f"ATMOS_{theme.replace(' ', '_').upper()}_{duration//60}MIN_{timestamp}.mp4"
    
    generate_atmos_video(duration, theme, output_name)
