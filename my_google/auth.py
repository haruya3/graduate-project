from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

class Auth:
    def __init__(self, scope, secret_path, client_secret_id_path, service, version):
        credentials = self.OAuth(scope, secret_path, client_secret_id_path)
        self.client = build(service, version, credentials=credentials)
    
    def OAuth(self, scope, secret_path, client_secret_id_path):
        credentials = None

        if os.path.exists(secret_path):
            credentials = Credentials.from_authorized_user_file(secret_path, scope)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_id_path, scope)
                credentials = flow.run_local_server(port=0)

            with open(secret_path, 'w') as token:
                token.write(credentials.to_json())
        
        return credentials


