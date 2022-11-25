from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from google.auth.exceptions import DefaultCredentialsError
import os

class Auth:
    def __init__(self, scope, secret_path, client_secret_id_path, service, version):
        credentials = self.OAuth(scope, secret_path, client_secret_id_path)
        self.client = build(service, version, credentials=credentials)
    
    def OAuth(self, scope, secret_path, client_secret_id_path):
        credentials = None
        try:
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
        #以下でトークンの再発行を行う。
        except RefreshError as e:
            if input("トークンの期限が切れています。再発行しますか？(yes or no)\n") == "yes":
                os.remove(secret_path)
                self.OAuth(scope, secret_path, client_secret_id_path)
        except DefaultCredentialsError as e:
            print('再実行してください')



