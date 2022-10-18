from googleapiclient.discovery import build
from google.oauth2 import service_account

class Auth:
    def __init__(self, scope, secret_path, service, version):
        sarvice_acount_credentials = service_account.Credentials.from_service_account_file(secret_path)
        scoped_creds = sarvice_acount_credentials.with_scopes(scope)
        self.client = build(service, version, credentials=scoped_creds)

