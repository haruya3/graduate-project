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
    start_time = get_start_time(drive, jins_meme_data_name, date_time, rest_flag=True)
    date = start_time.date().strftime('%Y%m%d')
    pass_time = None
    fatigue = 1
    rest_flag = False

    print(f"開始時刻: {start_time}")
    #こういうdict式ではなくデータクラスにした方がエラー検知できる(キー名のタイプミスdictだとスルーされる)
    while True:
        download_file_pathes = []
        now = datetime.datetime.now()
        pass_time = get_pass_time(start_time, now)
        #今のJins memeのCSVファイルを取得
        files = execute_search_file(drive, date, jins_meme_data_name, page_limit=1)
        
        if not files:
            print(f'{date}についてのファイルが存在しません。終了します。')
            exit()

        download_file_pathes.append(execute_download_file(drive, files[0], jins_meme_data_name, rest_flag=True))
        #今の瞬目の間隔時間平均値を取得
        fatigue_relation_value_multi_array = readCsv(download_file_pathes, [os.getenv('FATIGUE_RELATION_VALUE')])
        fatigue_relation_value = list(itertools.chain.from_iterable(fatigue_relation_value_multi_array))
        rest_flag = compare_blink_interval_threshold(fatigue_relation_value[0][0], float(os.getenv('BLINK_INTERVAL_THRESHOLD')), rest_flag)
        
        if pass_time != 0 and pass_time % 5 == 0:
            #今の疲労度を取得するため、疲労度の記録ファイルが作成されるのを待つ
            time.sleep(20)
            #TODO:すでにダウンロード済みなので以下でまたダウンロードする必要性はないので処理を変更する
            date_from_jins_meme_file = get_date_from_jins_meme_file(drive, files, jins_meme_data_name, rest_flag=rest_flag)
            fatigue_file_path = get_fatigue_file_path(date_from_jins_meme_file, rest_flag=True)
            count_per_five_second = 0
            #疲労度の取得(リトライ処理は5秒間に一回する、30秒経ったらリトライ処理は終了)
            while True:
                if count_per_five_second == 6:
                    break

                if os.path.exists(fatigue_file_path):
                    time.sleep(3)
                    fatigue = get_fatigue_data(fatigue_file_path)
                else:
                    print(f"以下の疲労度のファイルは存在しませんでした。ファイル名を以下に表示するものに変更してください。なお、35秒内に変更されない場合は5分前の疲労度になります。\n{fatigue_file_path}")
                time.sleep(5)
                count_per_five_second += 1

        if rest_flag:
            print("休憩中の計測情報")
        rest_process(pass_time, fatigue_relation_value[0][0], fatigue)
        print()

        time.sleep(60)

""" 経過時間の取得 """
def get_pass_time(start_time, now):
    pass_time_delta = now - start_time
    minute, _ = divmod(pass_time_delta.seconds, 60)
    hour, minute = divmod(minute, 60)

    return hour * 60 + minute

""" 今の瞬目の間隔時間平均値と閾値を比較する """
def compare_blink_interval_threshold(value, threshold, rest_flag):
    if not rest_flag and value >= threshold:
        messagebox.showinfo('休憩通知','疲れが取れるまで休憩したほうがよいです。')
        rest_flag = True
    elif rest_flag and value < int(os.getenv('BLINK_INTERVAL_THRESHOLD_RESTART')):
        if int(input("疲労度を入力してください")) < 3:
            messagebox.showinfo('再開通知','疲れが取れたようなので作業を再開可能です。')
            rest_flag = False
            print("休憩を終了します。休憩終了時の計測情報")
    return rest_flag

""" 休憩前後に行う処理 """
#TODO:名前が良くない変える
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