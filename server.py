import http.server
import socketserver
import subprocess
import os
import json

PORT = 8080

class AtmosHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stats':
            try:
                catalog_path = '../data/musichris_master_catalog.json'
                disabled_path = '../data/disabled_songs.json'
                if not os.path.exists(catalog_path): catalog_path = 'data/musichris_master_catalog.json'
                if not os.path.exists(disabled_path): disabled_path = 'data/disabled_songs.json'
                
                with open(catalog_path, 'r') as f:
                    catalog = json.load(f)
                
                disabled_songs = []
                if os.path.exists(disabled_path):
                    with open(disabled_path, 'r') as f:
                        disabled_songs = json.load(f)
                
                # Familias de Atmósferas (Herencia)
                families = {
                    "Protección": ["Refugio", "Confianza", "Descanso", "Noche", "Fortaleza"],
                    "Batalla": ["Guerra Espiritual", "Poder", "Victoria Final", "Fortaleza"],
                    "Presencia": ["Adoración Celestial", "Santidad", "Intimidad"],
                    "Triunfo": ["Victoria", "Gozo", "Celebración", "Gratitud"],
                    "Renovación": ["Avivamiento", "Restauración", "Renovación", "Redención"]
                }
                
                # Palabras clave por categoría
                category_keywords = {
                    "Refugio": ["refugio", "amparo", "abrigo"], "Confianza": ["confianza", "creer", "fe"], "Descanso": ["descanso", "reposo", "quietud"],
                    "Noche": ["noche", "medianoche", "madrugada"], "Guerra Espiritual": ["guerra", "batalla", "ejército"], "Poder": ["poder", "autoridad", "fuerza"],
                    "Fortaleza": ["fortaleza", "roca", "castillo"], "Victoria Final": ["victoria final", "triunfo eterno"], "Adoración Celestial": ["adoración", "celestial", "trono"],
                    "Santidad": ["santidad", "santo", "puro"], "Intimidad": ["intimidad", "secreto", "presencia", "selah", "meditación"],
                    "Victoria": ["victoria", "vencer", "triunfo"], "Gozo": ["gozo", "alegría", "deleite"], "Celebración": ["celebración", "fiesta", "exaltación"],
                    "Gratitud": ["gratitud", "gracias", "reconocimiento"], "Avivamiento": ["avivamiento", "despertar", "fuego"], "Restauración": ["restauración", "restitución", "sanidad"],
                    "Renovación": ["renovación", "nuevo", "transformación"], "Redención": ["redención", "rescate", "gracia"]
                }

                stats = {k: 0 for k in category_keywords.keys()}
                for s in catalog:
                    if s['title'] in disabled_songs: continue
                    song_text = f"{s.get('title','')} {s.get('theme','')} {s.get('verse','')} {','.join(s.get('moments', []))}".lower()
                    
                    # Para cada canción, ver en qué categorías entra (incluyendo herencia)
                    matched_categories = []
                    for cat, keywords in category_keywords.items():
                        if any(k in song_text for k in keywords):
                            matched_categories.append(cat)
                    
                    # Aplicar Herencia: si una canción es de "Refugio", también suma a su familia
                    for cat in matched_categories:
                        stats[cat] += 1
                        # Si pertenece a una familia, las hermanas también pueden usarla como "backfill"
                        for fam_name, members in families.items():
                            if cat in members:
                                for member in members:
                                    if member != cat and member not in matched_categories:
                                        # Solo sumamos si la categoría principal de la canción es compatible
                                        stats[member] += 0.5 # Peso menor para indicar que es "relleno"
                
                # Enviar datos enriquecidos para la UI
                response_data = {
                    "stats": stats,
                    "ready": {k: (v >= 12) for k, v in stats.items()}
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
            except Exception as e:
                self.send_error(500, str(e))
        elif self.path == '/catalog':
            try:
                catalog_path = '../data/musichris_master_catalog.json'
                disabled_path = '../data/disabled_songs.json'
                if not os.path.exists(catalog_path): catalog_path = 'data/musichris_master_catalog.json'
                if not os.path.exists(disabled_path): disabled_path = 'data/disabled_songs.json'
                
                with open(catalog_path, 'r') as f:
                    catalog = json.load(f)
                
                disabled_songs = []
                if os.path.exists(disabled_path):
                    with open(disabled_path, 'r') as f:
                        disabled_songs = json.load(f)
                
                for s in catalog:
                    s['disabled'] = s['title'] in disabled_songs
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(catalog).encode())
            except Exception as e:
                self.send_error(500, str(e))
        elif self.path == '/toggle_song':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                title = post_data.get('title')
                disabled = post_data.get('disabled')
                
                disabled_path = '../data/disabled_songs.json'
                if not os.path.exists(disabled_path): 
                    disabled_songs = []
                else:
                    with open(disabled_path, 'r') as f:
                        disabled_songs = json.load(f)
                
                if disabled and title not in disabled_songs:
                    disabled_songs.append(title)
                elif not disabled and title in disabled_songs:
                    disabled_songs.remove(title)
                
                with open(disabled_path, 'w') as f:
                    json.dump(disabled_songs, f)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
            except Exception as e:
                self.send_error(500, str(e))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/run_atmos':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                
                duration = post_data.get('duration', 3600)
                theme = post_data.get('theme', 'Paz Interior')
                
                # Ejecutar motor con argumentos
                subprocess.Popen(['python3', '../scripts/atmos_engine.py', str(duration), theme])
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'Production Started', 'theme': theme, 'duration': duration}).encode())
            except Exception as e:
                self.send_error(500, str(e))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# Ajustar directorio para que funcione en cualquier entorno
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(script_dir, 'ui'))

with socketserver.TCPServer(('', PORT), AtmosHandler) as httpd:
    print(f'🚀 MusiChris Atmos Server en puerto {PORT}')
    httpd.serve_forever()
