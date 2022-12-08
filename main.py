from my_google.auth import Auth
from my_google.my_drive.module import *
from my_google.my_drive.helper import search_file_ready, get_download_file_path
from googleapiclient.errors import HttpError as HttpError
from data_edit.graph.module import *
from data_edit.table.module import *
from file_operation.module import check_exist_and_may_create
from dotenv import load_dotenv
load_dotenv()
import os

#TODO:下位層でexitで握り潰しが多いので、せめてトレースを出力して終了するようにする。
def main(date, download_flag, delete_flag, create_graph_flag, create_table_flag):
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

    if(create_graph_flag):
        create_graph_from_ditection_data_flow(str(date), jins_meme_data_name)
    
    if(create_table_flag):
        create_blink_interval_time_amplitude_table_flow(str(date), jins_meme_data_name)

""" Google Driveの特定のフォルダのファイルの取得 """
def download_ditection_data_flow(drive, date, jins_meme_data_name):
    params = search_file_ready(date, jins_meme_data_name)

    files = search_file(drive, params['condition'], params['fields'])
    rest_flag = trance_boolean(input("「休憩あり」の実験データとして取得しますか。(例)yes or no\n"))
    specify_hour = input("何時データを取得するか指定しください。(例)10時から12時のデータ->10-12\n").split('-')
    start_specify_hour = int(specify_hour[0])
    end_specify_hour = int(specify_hour[-1])

    if files:
        for file in files:
            download_file_path = get_download_file_path(file, jins_meme_data_name, rest_flag)

            if rest_flag:
                hour = int(download_file_path[31:33])
            else:
                hour = int(download_file_path[26:28])                

            check_exist_and_may_create(download_file_path)
            
            if start_specify_hour > hour or hour > end_specify_hour:
                print(download_file_path)
                continue
                
            download_file(drive, file['id'], download_file_path)
    else:
        print("指定した条件に一致するファイルは見つかりませんでいた。")

""" Google Driveの特定のフォルダのファイルの削除 """
def delete_ditection_data_flow(drive, date):
    params = search_file_ready(date, all_flag=True)
    files = search_file(drive, params['condition'], params['fields'])
    delete_file_count = 0

    if files:
        print(f'{date}についてのファイルは{len(files)}個あります。')
        for index, file in enumerate(files):
            delete_file(drive, file['id'])
            if index % 10 == 0:
                print(f'ファイル削除数: {index}個')
            if index == 100:
                delete_file_count = index
                break
        
        print(f'{date}についての{delete_file_count}個のファイルの削除が完了しました。')
        print(f'{date}の残りファイル数は{len(files) - delete_file_count}個です。')
    else:
        print("指定した条件に一致するファイルは見つかりませんでいた。")

""" Jins memeのデータでグラフ作成 """
def create_graph_from_ditection_data_flow(date, jins_meme_data_name):
    fatigue_relation_value = os.getenv('FATIGUE_RELATION_VALUE')
    csv_colums = ['date', fatigue_relation_value]
    graph_colums = ['pass_time', fatigue_relation_value, 'fatigue']
    
    #ユーザ入力項目
    hours = list(map(lambda x: int(x), input("時間範囲を指定してください(例)12時から15時なら12-15, 1時なら01とする\n").split('-')))
    rest_flag = trance_boolean(input("「休憩あり」の実験ですか。(例)yes or no\n"))

    result, threshold = create_graph_from_ditection_data_ready(date, hours, csv_colums, jins_meme_data_name=jins_meme_data_name, rest_flag=rest_flag)

    if not threshold:
        print("疲労度3に達していません。デフォルトの閾値(4)を設定します")
        threshold['fatigue_relation_value'] = os.getenv('BLINK_INTERVAL_THRESHOLD')
        threshold['pass_time'] = os.getenv('THRESHOLD_DEFAULT_PASS_TIME')
    create_graph_from_ditection_data(date, hours, result, graph_colums, threshold, rest_flag=rest_flag)

""" 疲労度ごとの瞬目の間隔時間平均の振り幅の表作成 """
def create_blink_interval_time_amplitude_table_flow(date, jins_meme_data_name): 
    rest_flag = trance_boolean(input("「休憩あり」の実験ですか。(例)yes or no\n"))
    table_minimum_max, table_average = create_blink_interval_time_amplitude_table(date, jins_meme_data_name, rest_flag=rest_flag)
    print(table_minimum_max)
    print(table_average)


""" 「休憩あり」かの標準入力をBoolean型に変換する(ついでに入力値の正常チェック) """
def trance_boolean(str):
    if str == 'yes':
        return True
    elif str == 'no':
        return False
    else:
        print('yesかnoで答えてください。')
        exit()

#TODO: ドライブ内の特定のファイルのダウンロードオプションとデリートオプションを設ける
def set_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--when", help="いつのデータを取得するか指定する。形式: (yyyymmdd-HH)", required=True)
    parser.add_argument("-d", "--download", help="データを取得する", action='store_true')
    parser.add_argument("-D", "--delete", help="データを削除する", action='store_true')
    parser.add_argument("-cG", "--createGraph", help="取得したデータからグラフを作成する", action='store_true')
    parser.add_argument("-cT", "--createTable", help="取得したデータからグラフを作成する", action='store_true')
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
    check_google_drive_action(args.download, args.delete, args.createGraph, args.createTable)

    main(args.when, args.download, args.delete, args.createGraph, args.createTable)
