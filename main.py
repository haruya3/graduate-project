from venv import create
from my_google.auth import Auth
from my_google.my_drive.module import *
from googleapiclient.errors import HttpError as HttpError
from dotenv import load_dotenv
load_dotenv()
import os

def main(date, download_flag, delete_flag, create_flag):
    #グーグルサービスクライアント初期化
    SCOPES = [os.getenv('SCOPE')]
    OAUTH_SECRET_PATH = os.getenv('OAUTH_SECRET_PATH')
    CLIENT_SECRET_ID_PATH = os.getenv('CLIENT_SECRET_ID_PATH')
    drive = Auth(SCOPES, OAUTH_SECRET_PATH, CLIENT_SECRET_ID_PATH, 'drive', 'v3')

    keyword = 'logicIndexData'

    if(download_flag):
        download_ditection_data(drive, str(date), keyword)

    if(delete_flag):
        delete_ditection_data(drive, str(date))

    if(create_flag):
        create_graph_from_ditection_data_ready()

#Google Driveの特定のフォルダのファイルの取得
def download_ditection_data(drive, date, keyword):
    params = search_file_ready(date, keyword)

    files = search_file(drive, params['condition'], params['fields'])

    if files:
        for file in files:
            splited_name = file['name'].split('_')
            date_time = splited_name[0]
            download_file_path = f"ditection_data/{date_time}_logicIndexData.csv"

            download_file(drive, file['id'], download_file_path)

#Google Driveの特定のフォルダのファイルの削除
def delete_ditection_data(drive, date):
    params = search_file_ready(date, all_flag=True)
    files = search_file(drive, params['condition'], params['fields'])

    if files:
        for file in files:
            delete_file(drive, file['id'])
        
        print(f'{date}についての{len(files)}個のファイルの削除が完了しました。')

#download_ditection_dataで取得したデータからグラフを作成するための準備
def create_graph_from_ditection_data_ready():
    print("成功")

def search_file_ready(date, keyword=None, all_flag=False):
    folder_id = os.getenv('FOLDER_ID')
    condition_list = [
        f"'{folder_id}' in parents",
        f"fullText contains '{date}'",
        f"fullText contains '{keyword}'"
    ]
    if all_flag:
        condition_list.pop()
        
    condition = " and ".join(condition_list)
    fields = "nextPageToken, files(id, name)"
    
    return {'condition': condition, 'fields': fields}

#TODO: ドライブ内の特定のファイルのダウンロードオプションとデリートオプションを設ける
def set_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--when", help="いつのデータを取得するか指定する。形式: (yyyymmdd)", type=int, required=True)
    parser.add_argument("-d", "--download", help="データを取得する", action='store_true')
    parser.add_argument("-D", "--delete", help="データを削除する", action='store_true')
    parser.add_argument("-c", "--create", help="取得したデータからグラフを作成する", action='store_true')
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
    check_google_drive_action(args.download, args.delete, args.create)

    main(args.when, args.download, args.delete, args.create)
