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

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(secrets_path):
                print("⚠️ Error: Falta 'client_secrets.json' en scripts/")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)

    return build('youtube', 'v3', credentials=credentials)

def upload_video(video_file, thumb_file, meta_file):
    youtube = get_authenticated_service()
    if not youtube: return

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
            'privacyStatus': 'unlisted', # Por seguridad, se sube como No Listado para revisión final
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    
    response = request.execute()
    video_id = response.get('id')
    print(f"✅ [YOUTUBE] Video subido con ID: {video_id}")

    # Subir Miniatura
    youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumb_file)).execute()
    print("🖼️ [YOUTUBE] Miniatura vinculada correctamente.")

if __name__ == "__main__":
    # Esto se llamará desde el motor principal al terminar el render
    pass
