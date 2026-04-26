import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Alcances necesarios para subir videos
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def main():
    secrets_path = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
    
    if not os.path.exists(secrets_path):
        print(f"❌ No se encontró {secrets_path}. Asegúrate de que el archivo existe.")
        return

    # Iniciar el flujo de autenticación
    flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
    
    # Esto abrirá el navegador localmente
    print("🌐 Abriendo navegador para autenticación...")
    credentials = flow.run_local_server(port=0)

    print("\n✅ ¡Autenticación exitosa!")
    print("-" * 50)
    print(f"CLIENT_ID: {credentials.client_id}")
    print(f"CLIENT_SECRET: {credentials.client_secret}")
    print(f"REFRESH_TOKEN: {credentials.refresh_token}")
    print("-" * 50)
    print("\n📋 COPIA EL REFRESH_TOKEN y guárdalo en un lugar seguro.")

if __name__ == "__main__":
    main()
