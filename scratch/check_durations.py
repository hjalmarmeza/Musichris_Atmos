import json
import subprocess
import os

def get_duration(url):
    try:
        # Usamos ffprobe para leer solo el encabezado del video remoto
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return float(result.stdout.strip())
    except:
        return 0

def main():
    with open('data/landscapes_remote.json', 'r') as f:
        data = json.load(f)
    
    print(f"🔍 Analizando {len(data)} paisajes...")
    
    long_videos = {}
    short_videos = 0
    count = 0
    
    # Probamos los primeros 15 para tener una estadística clara
    for name, url in list(data.items())[:15]:
        count += 1
        dur = get_duration(url)
        print(f"[{count}/15] {name}: {dur:.2f}s")
        if dur >= 60:
            long_videos[name] = url
        else:
            short_videos += 1
            
    print(f"\n📊 Resultado del muestreo:")
    print(f"- Videos largos (>60s): {len(long_videos)}")
    print(f"- Videos cortos: {short_videos}")

if __name__ == "__main__":
    main()
