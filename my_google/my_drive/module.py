from googleapiclient.errors import HttpError as HttpError
from googleapiclient.http import MediaIoBaseDownload

def search_file(drive, condition, fields):
    try:
        files = []
        next_page_token = None
        page_size = 100
        request_count = 0

        while True:
            result = drive.client.files().list(
                q=condition,
                fields=fields,
                pageSize=page_size,
                pageToken=next_page_token,
            ).execute()
            request_count += 1

            next_page_token = result.get('nextPageToken', None)            
            if request_count == 10:
                print(f'過剰なリクエストです。時間を置いて再度リクエストしてください。')
            
            print(f'最低リクエスト数: {request_count}')
            
            files.extend(result.get('files', []))

            if next_page_token is None:
                break
            
        return files

    except HttpError as error:
        print(f'An error occurred: {error}')

def download_file(drive, file_id, download_file_path):
    request = drive.client.files().get_media(fileId=file_id)

    try:         
        #bufferingが0はバッファリングを行わない。
        with open(download_file_path, 'wb', buffering=0) as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            #ダウンロード完了するまでの処理・ロード時間・next_chank()はファイルを分割していた場合の次の分割部分があるかどうか。
            while not done:
                status, done = downloader.next_chunk()
                print(f'Downloading... {download_file_path}, {status.total_size / 1024 / 1024}MB')
    except HttpError as error:
        print(f'An error occurred: {error}')
    except Exception as e:
        print(f'[ERROR] {type(e)}: {str(e)}')


def delete_file(drive, file_id):
    try:
        drive.client.files().delete(fileId=file_id).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')
    except Exception as e:
        print(f'[ERROR] {type(e): str(e)}')