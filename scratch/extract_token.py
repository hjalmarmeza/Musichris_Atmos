import pickle
import os

token_path = 'scripts/token.pickle'
if os.path.exists(token_path):
    with open(token_path, 'rb') as token:
        credentials = pickle.load(token)
        print(f"REFRESH_TOKEN: {credentials.refresh_token}")
        print(f"CLIENT_ID: {credentials.client_id}")
        print(f"CLIENT_SECRET: {credentials.client_secret}")
else:
    print("Token not found.")
