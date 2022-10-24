from my_google.auth import Auth
from my_google.my_drive.module import *
from googleapiclient.errors import HttpError as HttpError
from graph.module import *
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
        create_graph_from_ditection_data(str(date))

""" Google Driveの特定のフォルダのファイルの取得 """
def download_ditection_data(drive, date, keyword):
    params = search_file_ready(date, keyword)

    files = search_file(drive, params['condition'], params['fields'])

    if files:
        for file in files:
            download_file_path = get_download_file_path(file)

            check_exist_and_may_create(download_file_path)

            download_file(drive, file['id'], download_file_path)
    else:
        print("指定した条件に一致するファイルは見つかりませんでいた。")

""" Google Driveの特定のフォルダのファイルの削除 """
def delete_ditection_data(drive, date):
    params = search_file_ready(date, all_flag=True)
    files = search_file(drive, params['condition'], params['fields'])

    if files:
        for file in files:
            delete_file(drive, file['id'])
        
        print(f'{date}についての{len(files)}個のファイルの削除が完了しました。')


""" Jins memeのデータでグラフ作成 """
def create_graph_from_ditection_data(date):
    hours = list(map(lambda x: int(x), input("時間範囲を指定してください(例)12時から15時なら12-15, 1時なら01とする\n").split('-')))
    result = create_graph_from_ditection_data_ready(date, hours)
    print(result)

""" Google Drive APIで特定ファイル検索する際の条件(q, fieldsなど)に指定する値の準備 """
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
    
""" Google Drive APIでファイルをダウンロードするさいに必要なファイルパスを取得する """
def get_download_file_path(file):
    splited_name = file['name'].split('_')
    date_time = splited_name[0].split('-')
    year = date_time[0][0:4]
    month = date_time[0][4:6]
    day = date_time[0][6:8]
    hour = date_time[1][0:2]
    minitue = date_time[1][2:4]
    second = date_time[1][4:6]

    return  f"ditection_data/{year}/{month}/{day}/{hour}/{minitue}-{second}_logicIndexData.csv"

""" あるパスの存在確認をする。存在しない場合は作成する"""
def check_exist_and_may_create(path):
    directory_path = os.path.dirname(path)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    

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
