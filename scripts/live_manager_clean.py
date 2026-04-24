import subprocess
import re
import os
import sys
import time

TEXT_FILE = '/home/ubuntu/current_song.txt'
BACKGROUND_IMAGE = '/home/ubuntu/background_720p.png'

FFMPEG_CMD = [
    'ffmpeg', '-v', 'info',
    '-loop', '1', '-framerate', '15', '-i', BACKGROUND_IMAGE,
    '-f', 'concat', '-safe', '0', '-stream_loop', '-1', '-re', '-i', '/home/ubuntu/playlist.txt',
    '-vf', 'scale=1280:720,format=yuv420p',
    '-map', '0:v',
    '-map', '1:a',
    '-c:v', 'libx264', '-preset', 'ultrafast', '-tune', 'stillimage', '-threads', '2',
    '-b:v', '1800k', '-maxrate', '1800k', '-bufsize', '3600k',
    '-pix_fmt', 'yuv420p', '-g', '30', '-r', '15', '-fps_mode', 'cfr',
    '-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-af', 'aresample=async=1',
    '-f', 'flv', 'rtmp://a.rtmp.youtube.com/live2/ze35-jyw1-drvs-90ku-6617'
]

def update_song_title(filepath):
    try:
        if not filepath: return
        filename = os.path.basename(filepath)
        title = os.path.splitext(filename)[0].strip().replace("_", " ")
        
        with open(TEXT_FILE, 'w') as f:
            f.write(title)
        print(f'NOW PLAYING: {title}', flush=True)
    except: pass

def run():
    print('Starting MusiChris Live Station (Immortal Mode)...', flush=True)
    
    while True:
        print('Launching FFmpeg process...', flush=True)
        process = subprocess.Popen(FFMPEG_CMD, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)

        try:
            for line in iter(process.stderr.readline, ''):
                l = line.strip()
                if 'frame=' not in l:
                    print(f'LOG: {l}', flush=True)
                    # Detectar cambio de canción
                    if '.mp3' in l.lower() or '.m4a' in l.lower():
                        m = re.search(r"'(.+?\.(mp3|m4a))'", l)
                        if m:
                            update_song_title(m.group(1))
        except Exception as e:
            print(f'Monitor error: {e}', flush=True)
        
        process.wait()
        print('FFmpeg crashed or stopped. Restarting in 5 seconds...', flush=True)
        time.sleep(5)

if __name__ == '__main__':
    run()
