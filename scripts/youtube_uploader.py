import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Alcances para la API de YouTube
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_authenticated_service():
    credentials = None
    token_path = os.path.join(BASE_DIR, 'scripts/token.pickle')
    secrets_path = os.path.join(BASE_DIR, 'scripts/client_secrets.json')

    # 1. Intentar cargar desde pickle local (Mac)
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)
    
    # 2. Si no hay credenciales válidas, intentar usar Secretos de Entorno (GitHub Actions)
    if not credentials or not credentials.valid:
        raw_token = os.environ.get("YOUTUBE_TOKEN")
        raw_client_id = os.environ.get("YOUTUBE_CLIENT_ID")
        raw_client_secret = os.environ.get("YOUTUBE_CLIENT_SECRETS")

        if raw_token and raw_client_secret:
            try:
                # 1. Extraer Refresh Token (del JSON o del texto)
                refresh_token = raw_token
                if raw_token.startswith('{'):
                    try:
                        token_data = json.loads(raw_token)
                        refresh_token = token_data.get('refresh_token', raw_token)
                    except: pass
                
                # 2. Extraer Client ID y Secret (del JSON o de los campos individuales)
                client_id = raw_client_id
                client_secret = raw_client_secret
                
                if raw_client_secret.startswith('{'):
                    try:
                        creds_data = json.loads(raw_client_secret)
                        # Buscar en los niveles típicos de Google (installed o web)
                        inner = creds_data.get('installed', creds_data.get('web', creds_data))
                        client_id = inner.get('client_id', client_id)
                        client_secret = inner.get('client_secret', client_secret)
                    except: pass

                # 3. Validar que no estemos mandando un JSON entero como secreto
                if client_secret and client_secret.startswith('{'):
                    print("⚠️ [YOUTUBE] Alerta: El secreto extraído sigue pareciendo un JSON. Verificando...")

                from google.oauth2.credentials import Credentials
                credentials = Credentials(
                    None,
                    refresh_token=refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=SCOPES
                )
                credentials.refresh(Request())
                print("✅ [YOUTUBE] Autenticación exitosa (Motor de Extracción v2).")
            except Exception as e:
                print(f"⚠️ [YOUTUBE] Error en autenticación: {e}")
        
        # 3. Si fallan los secretos, intentar flujo local (Requiere client_secrets.json)
        elif os.path.exists(secrets_path):
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            credentials = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(credentials, token)
            print("✅ [YOUTUBE] Autenticación exitosa mediante Flujo Local.")
        else:
            print("❌ [YOUTUBE] Error: No hay Secretos de Entorno ni 'client_secrets.json' disponible.")
            return None

    return build('youtube', 'v3', credentials=credentials)

def upload_video(video_file, thumb_file, meta_file):
    print(f"📡 [YOUTUBE] Iniciando proceso de autenticación...")
    youtube = get_authenticated_service()
    if not youtube: 
        print("❌ [YOUTUBE] No se pudo obtener el servicio de autenticación.")
        return

    # Leer Metadatos
    with open(meta_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    title = lines[1].strip() # Según el formato de nuestro meta.txt
    description = "".join(lines[4:])
    
    print(f"📤 [YOUTUBE] Subiendo: {title}...")
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['MusiChris', 'Atmos', 'Adoración', 'Paz'],
            'categoryId': '10' # Música
        },
        'status': {
            'privacyStatus': 'unlisted',
            'selfDeclaredMadeForKids': False
        }
    }

    print(f"🚀 [YOUTUBE] Iniciando transferencia de medios (Resumable)...")
    media = MediaFileUpload(video_file, chunksize=1024*1024, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📊 [YOUTUBE] Progreso de subida: {int(status.progress() * 100)}%")
            
    video_id = response.get('id')
    print(f"✅ [YOUTUBE] Video subido con ID: {video_id}")

    # Subir Miniatura
    youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumb_file)).execute()
    print("🖼️ [YOUTUBE] Miniatura vinculada correctamente.")

if __name__ == "__main__":
    # Esto se llamará desde el motor principal al terminar el render
    pass
