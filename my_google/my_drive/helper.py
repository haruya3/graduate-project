import os, datetime
from file_operation.module import readCsv, check_exist_and_may_create
from my_google.my_drive.module import search_file, download_file

""" Google Drive APIで特定ファイル検索する際の条件(q, fieldsなど)に指定する値の準備 """
def search_file_ready(date, jins_meme_data_name=None, page_limit=100, all_flag=False):
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
    page_limit = page_limit

    return {'condition': condition, 'fields': fields, 'page_limit': page_limit}

""" Google Drive APIでファイルをダウンロードするさいに必要なファイルパスを取得する """
#TODO:これ、ファイル名をGoogle Driveに保存されているファイル名の時間にしているけど大丈夫かな？ファイル名とファイル内のdateキーの時間と誤差があるため心配
def get_download_file_path(file, jins_meme_data_name, rest_flag=False):
    splited_name = file['name'].split('_')
    date_time = splited_name[0].split('-')
    year = date_time[0][0:4]
    month = date_time[0][4:6]
    day = date_time[0][6:8]
    hour = date_time[1][0:2]
    minitue = date_time[1][2:4]
    second = date_time[1][4:6]
    file_path =  f"ditection_data/{year}/{month}/{day}/{hour}/{minitue}-{second}_{jins_meme_data_name}.csv"
    #「休憩あり」の実験データ用パス
    if rest_flag:
        file_path = f"ditection_data/rest/{year}/{month}/{day}/{hour}/{minitue}-{second}_{jins_meme_data_name}.csv"

    return file_path

""" 開始時刻を取得する """
def get_start_time(drive, jins_meme_data_name, date_time, rest_flag=False):
    date, time = date_time.split()
    #page_limitで、1時間以内なら開始時刻を探せるようにした
    files = execute_search_file(drive, date, jins_meme_data_name, page_limit=60)
    if files:
        file = get_file_for_start_time(files, time)
        download_file_path = execute_download_file(drive, file, jins_meme_data_name, rest_flag=rest_flag)
        #date=[[['date', dtype=object]]]
        date = readCsv([download_file_path], ['date'])
        #日本時間に合わせる
        JST = datetime.timedelta(hours=9)
        return datetime.datetime.fromisoformat(date[0][0][0][:16]) + JST
    else:
        print('入力された日付時間のデータはありませんでした。')
        exit()

""" 特定のファイルIDをGoogle Driveから取得する処理の実行 """
def execute_search_file(drive, date, jins_meme_data_name, page_limit=100):
    params = search_file_ready(date, jins_meme_data_name, page_limit=page_limit)
    files = search_file(drive, params['condition'], params['fields'], page_limit=params['page_limit'])
     
    return files

""" 特定のファイルをGoogle Driveからダウンロード処理の実行 """
def execute_download_file(drive, file, jins_meme_data_name, rest_flag=False):
    download_file_path = get_download_file_path(file, jins_meme_data_name, rest_flag=rest_flag)
    check_exist_and_may_create(download_file_path)
    download_file(drive, file['id'], download_file_path)

    return download_file_path

""" 開始時間を取得するためのファイルを取得する """
def get_file_for_start_time(files, time):
    file = get_file_specified_by_date_time(files, time.replace(':', ''))
    if not file:
        print("入力された日付時間のファイルは存在しませんでした。\n入力された時間の中で最も古いファイルを探します")
        file = get_file_oldest_in_specified_by_time(files, time[0:2])
        if input(f"以下のファイルが見つかりましたがこちらで処理を進めますか？(yes or no)\n{file}\n") == 'no':
            print('処理を終了します。')
            exit()
    return file

""" 
    入力された日付時間のファイルを取得する 
    ファイル存在しなかったらexit
"""
def get_file_specified_by_date_time(files, time):
    file_specified_by_date_time = [file for file in files if time == file['name'][9:13]]
    if file_specified_by_date_time:
        return file_specified_by_date_time[0]
    else:
        return None

""" 
    入力された日付時間でファイルなかった場合に最も古いファイルを取得する
    もし、それもなかったら強制終了
 """
def get_file_oldest_in_specified_by_time(files, start_experiment_hour):
    files_specified_by_time = [file for file in files if file['name'][9:11] == start_experiment_hour]
    if files_specified_by_time:
        return files_specified_by_time[-1]
    else:
        print('入力された日付時間のファイルは存在しません')
        exit()