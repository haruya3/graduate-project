from datetime import datetime
from venv import create
from my_google.auth import Auth
from my_google.my_drive.module import *
from googleapiclient.errors import HttpError as HttpError
from dotenv import load_dotenv
load_dotenv()
import os, glob
import pandas as pd

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

#Google Driveの特定のフォルダのファイルの取得
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

#Google Driveの特定のフォルダのファイルの削除
def delete_ditection_data(drive, date):
    params = search_file_ready(date, all_flag=True)
    files = search_file(drive, params['condition'], params['fields'])

    if files:
        for file in files:
            delete_file(drive, file['id'])
        
        print(f'{date}についての{len(files)}個のファイルの削除が完了しました。')


def create_graph_from_ditection_data(date):
    hours = list(map(lambda x: int(x), input("時間範囲を指定してください(例)12時から15時なら12-15, 1時なら01とする\n").split('-')))
    result = create_graph_from_ditection_data_ready(date, hours)
    print(result)

#Google Drive APIで特定ファイル検索する際の条件(q, fieldsなど)に指定する値の準備
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

#download_ditection_dataで取得したデータからグラフを作成するための準備
def create_graph_from_ditection_data_ready(date, hours):
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]

    #(例)[[X1(VDT作業開始からの経過時間(5分ごと)) Y1(瞬目の間隔時間平均(5分ごと)) Z1(疲労度申告(5分ごと))], [X2 Y2 Z1],...[Xn Yn Zn]]
    date_blink_interval_time_fatigue_data = []
    #疲労度
    fatigue = 0
    #VDT作業開始時間
    start_vdt_minitue = 0
    
    #1時間ごとにデータ(date_blink_interval_time_fatigue_data)を取得していく->hours[-1]とすることで配列要素1つだけの時エラー回避
    for hour in range(hours[0], hours[-1] + 1):
        #12-15で12から15時の間のデータのグラフを作るという意味にして、rangeでrang(12, 15)でhourをfor分で回せば、できそう？
        pathes = glob.glob(f'./ditection_data/{year}/{month}/{day}/{hour}/*')
        date_blink_interval_time_per_hour_data = []

        if pathes:
            for path in pathes:
                #空ファイルは無視する
                if os.path.getsize(path) != 0:
                    #デフォルトで、delimiterが,になっている
                    csv_data = pd.read_csv(path, usecols=['date', 'blinkIntervalMean'], )
                    date_blink_interval_time_per_hour_data.append(csv_data.values)
        else:
            print("指定したファイルは存在しません。恐らく時間指定を間違っているかそのようなファイルパスは存在しません。")
            
        # 一つの配列はcsvファイルでいう一つの行レコードとなる。
        date_blink_interval_time_fatigue_data = []
        
        if date_blink_interval_time_per_hour_data:
            #まだVDT作業開始時間を設定していない場合
            if start_vdt_minitue == 0:
                start_vdt_minitue = int(date_blink_interval_time_per_hour_data[0][0][0][14:16])

            #VDT作業開始時間
            for index, per_minitue_data in enumerate(date_blink_interval_time_per_hour_data):
                blink_interval_time_average = 0
                blink_interval_time_sum = 0

                #5分ごとに疲労度のデータ取得
                if index % 4 == 0:
                    fatigue = 3

                #1分ごとの瞬目の時間間隔のデータの取得
                for data in per_minitue_data:
                    blink_interval_time_sum += data[1]

                blink_interval_time_average = int(blink_interval_time_sum / len(per_minitue_data))

                #経過時間の取得
                pass_time = int(data[0][14:16]) - start_vdt_minitue

                #1分ごとの経過時間・瞬目の間隔時間平均・疲労度のレコードを作成
                date_blink_interval_time_fatigue_data.append([pass_time, blink_interval_time_average, fatigue])
        
        #もし該当する時間にデータが取得されていなかったらスキップする
        else:
            continue

    return date_blink_interval_time_fatigue_data 
    
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
