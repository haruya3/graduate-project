from my_google.auth import Auth
from my_google.my_drive.module import *
from googleapiclient.errors import HttpError as HttpError
from graph.module import *
from file_operation.module import *
from dotenv import load_dotenv
load_dotenv()
import os

def main(date, download_flag, delete_flag, create_flag):
    #グーグルサービスクライアント初期化
    SCOPES = [os.getenv('SCOPE')]
    OAUTH_SECRET_PATH = os.getenv('OAUTH_SECRET_PATH')
    CLIENT_SECRET_ID_PATH = os.getenv('CLIENT_SECRET_ID_PATH')
    drive = Auth(SCOPES, OAUTH_SECRET_PATH, CLIENT_SECRET_ID_PATH, 'drive', 'v3')

    #jins_meme_data_name = 'logicIndexData'
    jins_meme_data_name = 'summaryData'

    if(download_flag):
        download_ditection_data_flow(drive, str(date), jins_meme_data_name)

    if(delete_flag):
        delete_ditection_data_flow(drive, str(date))

    if(create_flag):
        create_graph_from_ditection_data_flow(str(date), jins_meme_data_name)

""" Google Driveの特定のフォルダのファイルの取得 """
def download_ditection_data_flow(drive, date, jins_meme_data_name):
    params = search_file_ready(date, jins_meme_data_name)

    files = search_file(drive, params['condition'], params['fields'])

    if files:
        for file in files:
            download_file_path = get_download_file_path(file, jins_meme_data_name)

            check_exist_and_may_create(download_file_path)

            download_file(drive, file['id'], download_file_path)
    else:
        print("指定した条件に一致するファイルは見つかりませんでいた。")

""" Google Driveの特定のフォルダのファイルの削除 """
def delete_ditection_data_flow(drive, date):
    params = search_file_ready(date, all_flag=True)
    files = search_file(drive, params['condition'], params['fields'])
    delete_file_count = 0

    if files:
        for index, file in enumerate(files):
            delete_file(drive, file['id'])
            if index % 10 == 0:
                print(f'ファイル削除数: {index}個')
            if index == 100:
                break
            delete_file_count = index
        
        print(f'{date}についての{delete_file_count}個のファイルの削除が完了しました。')
        print(f'{date}の残りファイル数は{len(files) - delete_file_count}個です。')
    else:
        print("指定した条件に一致するファイルは見つかりませんでいた。")



""" Jins memeのデータでグラフ作成 """
def create_graph_from_ditection_data_flow(date, jins_meme_data_name):
    fatigue_relation_value = 'strongBlinkIntervalAvg'
    csv_colums = ['date', fatigue_relation_value]
    graph_colums = ['pass_time', fatigue_relation_value, 'fatigue']
    hours = list(map(lambda x: int(x), input("時間範囲を指定してください(例)12時から15時なら12-15, 1時なら01とする\n").split('-')))

    result, threshold = create_graph_from_ditection_data_ready(date, hours, csv_colums, jins_meme_data_name=jins_meme_data_name)

    create_graph_from_ditection_data(date, hours, result, graph_colums, threshold)
    
""" Google Drive APIで特定ファイル検索する際の条件(q, fieldsなど)に指定する値の準備 """
def search_file_ready(date, jins_meme_data_name=None, all_flag=False):
    folder_id = os.getenv('FOLDER_ID')
    condition_list = [
        f"'{folder_id}' in parents",
        f"fullText contains '{date}'",
        f"fullText contains '{jins_meme_data_name}'"
    ]
    if all_flag:
        condition_list.pop()
        
    condition = " and ".join(condition_list)
    fields = "nextPageToken, files(id, name)"
    
    return {'condition': condition, 'fields': fields}
    
""" Google Drive APIでファイルをダウンロードするさいに必要なファイルパスを取得する """
def get_download_file_path(file, jins_meme_data_name):
    splited_name = file['name'].split('_')
    date_time = splited_name[0].split('-')
    year = date_time[0][0:4]
    month = date_time[0][4:6]
    day = date_time[0][6:8]
    hour = date_time[1][0:2]
    minitue = date_time[1][2:4]
    second = date_time[1][4:6]

    return  f"ditection_data/{year}/{month}/{day}/{hour}/{minitue}-{second}_{jins_meme_data_name}.csv"

#TODO: ドライブ内の特定のファイルのダウンロードオプションとデリートオプションを設ける
def set_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--when", help="いつのデータを取得するか指定する。形式: (yyyymmdd-HH)", required=True)
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
