from dataclasses import field
from my_google.auth import Auth
from my_google.my_drive.module import *
from googleapiclient.errors import HttpError as HttpError
from dotenv import load_dotenv
load_dotenv()
import os

def main(date):
    #グーグルサービスクライアント初期化
    SCOPES = [os.getenv('SCOPE')]
    GOOGLE_SECRET_PATH = os.getenv('GOOGLE_SECRET_PATH')
    drive = Auth(SCOPES, GOOGLE_SECRET_PATH, 'drive', 'v3')

    download_ditection_data(drive, str(date))

def download_ditection_data(drive, date):
    condition_list = [
        f"fullText contains '{date}'",
        "fullText contains 'logicIndexData'"
    ]
    condition = " and ".join(condition_list)
    fields = "nextPageToken, files(id, name)"

    files = search_file(drive, condition, fields)

    for file in files:
        splited_name = file['name'].split('_')
        date_time = splited_name[0]
        download_file_path = f"ditection_data/{date_time}_logicIndexData.csv"

        download_file(drive, file['id'], download_file_path)

#TODO:--wオプションのバリデーションが緩すぎる。日付型にした方がいいかな
#TODO: ドライブ内の特定のファイルのダウンロードオプションとデリートオプションを設ける
def set_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w","--when", help="いつのデータを取得するか指定する", type=int)
    return parser.parse_args()

#TODO: Jins memeは眼鏡の置き方をミスるとデータ取得されちゃうので欲しい時間までを指定できるようにした方が良いかも
if __name__ == '__main__':
    args = set_args()
    main(args.when)
