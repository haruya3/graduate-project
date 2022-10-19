from dataclasses import field
from select import select
from my_google.auth import Auth
from my_google.my_drive.module import *
from googleapiclient.errors import HttpError as HttpError
from dotenv import load_dotenv
load_dotenv()
import os

def main(date, download_flag, delete_flag):
    #グーグルサービスクライアント初期化
    SCOPES = [os.getenv('SCOPE')]
    GOOGLE_SECRET_PATH = os.getenv('GOOGLE_SECRET_PATH')
    drive = Auth(SCOPES, GOOGLE_SECRET_PATH, 'drive', 'v3')

    if(download_flag):
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

#TODO: ドライブ内の特定のファイルのダウンロードオプションとデリートオプションを設ける
def set_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--when", help="いつのデータを取得するか指定する。形式: (yyyymmdd)", type=int, required=True)
    parser.add_argument("-d", "--download", help="ダウンロード", action='store_true')
    parser.add_argument("-D", "--delete", help="いつのデータを取得するか指定する", action='store_true')
    return parser.parse_args()

def check_google_drive_action(*actions):
    selected_actions = list(filter(lambda x: x, actions))
    if len(selected_actions) == 0:
        print('Google Dirveへの操作オプションの指定は必須です。')
        exit()

    if selected_actions.count(True) >= 2:
        print('Google Dirveへの操作オプションの指定は一つしかできません。')
        exit()

if __name__ == '__main__':
    args = set_args()
    check_google_drive_action(args.download, args.delete)

    main(args.when, args.download, args.delete)
