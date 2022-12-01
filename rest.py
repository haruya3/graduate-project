import time, itertools, os, datetime
from tkinter import messagebox
from my_google.my_drive.helper import get_start_time, execute_download_file, execute_search_file
from my_google.auth import Auth
from file_operation.module import readCsv
from data_edit.module import get_fatigue_data, get_fatigue_file_path, get_date_from_jins_meme_file
from dotenv import load_dotenv
load_dotenv()

def main():
    SCOPES = [os.getenv('SCOPE')]
    OAUTH_SECRET_PATH = os.getenv('OAUTH_SECRET_PATH')
    CLIENT_SECRET_ID_PATH = os.getenv('CLIENT_SECRET_ID_PATH')
    drive = Auth(SCOPES, OAUTH_SECRET_PATH, CLIENT_SECRET_ID_PATH, 'drive', 'v3')

    jins_meme_data_name = 'summaryData'
    
    date_time = check_date(input('日付を入力してください(例): 20221102 12:30\n'))
    start_time = get_start_time(drive, jins_meme_data_name, date_time)
    date = start_time.date().strftime('%Y%m%d')
    pass_time = None
    fatigue = 1
    download_file_pathes = []
    rest_flag = False

    print(f"開始時刻: {start_time}")
    #こういうdict式ではなくデータクラスにした方がエラー検知できる(キー名のタイプミスdictだとスルーされる)
    while True:
        now = datetime.datetime.now()
        pass_time = get_pass_time(start_time, now)
        #今のJins memeのCSVファイルを取得
        files = execute_search_file(drive, date, jins_meme_data_name, page_limit=1)
        if files:
            download_file_pathes.append(execute_download_file(drive, files[0], jins_meme_data_name))
            
            #今の瞬目の間隔時間平均値を取得
            fatigue_relation_value_multi_array = readCsv(download_file_pathes, [os.getenv('FATIGUE_RELATION_VALUE')])
            fatigue_relation_value = list(itertools.chain.from_iterable(fatigue_relation_value_multi_array))
            rest_flag = compare_blink_interval_threshold(fatigue_relation_value[0][0], int(os.getenv('BLINK_INTERVAL_THRESHOLD')), rest_flag)
            
            if pass_time != 0 and pass_time % 5 == 0:
                #今の疲労度を取得する
                time.sleep(30)
                date_from_jins_meme_file = get_date_from_jins_meme_file(drive, files, jins_meme_data_name)
                fatigue = get_fatigue_data(get_fatigue_file_path(date_from_jins_meme_file))

            if rest_flag:
                print("休憩中の計測情報")
            rest_process(pass_time, fatigue_relation_value[0][0], fatigue)
            print()
        else:
            print(f'{date}についてのファイルが存在しません。')
        time.sleep(60)

""" 経過時間の取得 """
def get_pass_time(start_time, now):
    pass_time_delta = now - start_time
    minute, _ = divmod(pass_time_delta.seconds, 60)
    hour, minute = divmod(minute, 60)

    return hour * 60 + minute

""" 今の瞬目の間隔時間平均値と閾値を比較する """
#TODO:通知は一回したら、休憩終わるまで通知しないとかにする。
def compare_blink_interval_threshold(value, threshold, rest_flag):
    if not rest_flag and value >= threshold:
        messagebox.showinfo('休憩通知','疲れが取れるまで休憩したほうがよいです。')
        rest_flag = True
    elif rest_flag and value < threshold:
        messagebox.showinfo('再開通知','疲れが取れたようなので作業を再開可能です。')
        rest_flag = False
        print("休憩を終了します。休憩終了時の計測情報")
    return rest_flag

""" 休憩前後に行う処理 """
def rest_process(pass_time, fatigue_relation_value, fatigue):
    print(f"経過時間: {pass_time}分")
    print(f"瞬目の間隔時間平均値: {fatigue_relation_value}")
    print(f"疲労度: {fatigue}")

""" 入力された日付時間が正しいフォーマットかチェック """
def check_date(date):
    try:
        datetime.datetime.strptime(date, '%Y%m%d %H:%M')
    except ValueError as e:
        print(f'[ERROR] {type(e)}: {str(e)}')
        print('例に従い正しい入力をしてください。')
        exit()
    except Exception as e:
        print(f'[ERROR] {type(e)}: {str(e)}')
        print('例に従い正しい入力をしてください。')
        exit()
    return date

if __name__ == '__main__':
    main()