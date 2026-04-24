#!/bin/bash
# Musichris ATMOS - Renderizado de Compilación v1.0
# Aplicando Reglas de Integridad Skill Flow v3.7

# Directorios (Ajustables para Oracle)
MUSIC_DIR="/home/ubuntu/music"
LANDSCAPES_DIR="/home/ubuntu/landscapes"
OUTPUT_DIR="/home/ubuntu/Musichris_Atmos/renders"
ASSETS_DIR="/home/ubuntu/Musichris_Atmos/assets"

# 1. Crear el archivo de lista para FFmpeg
TIMESTAMP=$(date +"%Y%m%d_%H%M")
FILE_LIST="playlist_${TIMESTAMP}.txt"

echo "🎵 Generando lista de reproducción para Paz Interior..."

# Este bloque será alimentado por el JSON, aquí un ejemplo de la estructura:
# file '/home/ubuntu/music/Soplo de Vida.mp3'
# file '/home/ubuntu/music/A Medianoche.mp3'

# 2. Renderizado con Prioridad Baja (nice -n 19)
# Usamos un solo paisaje de fondo para optimizar recursos
BACKGROUND_VIDEO=$(ls $LANDSCAPES_DIR/*.mp4 | head -n 1)

nice -n 19 ffmpeg -y \
    -stream_loop -1 -i "$BACKGROUND_VIDEO" \
    -f concat -safe 0 -i "$FILE_LIST" \
    -filter_complex "[0:v]scale=1920:1080,format=yuv420p[bg];[bg]drawtext=text='Musichris Studio':fontcolor=white@0.3:fontsize=40:x=w-text_w-50:y=50[v]" \
    -map "[v]" -map 1:a \
    -c:v libx264 -preset veryfast -crf 23 \
    -c:a aac -b:a 192k \
    -shortest "$OUTPUT_DIR/Atmos_Paz_Interior_${TIMESTAMP}.mp4"

echo "✅ Compilación terminada y guardada en $OUTPUT_DIR"
