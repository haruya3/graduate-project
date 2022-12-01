import datetime, time
from tkinter import messagebox
from file_operation.module import *
from my_google.my_drive.helper import get_start_time, execute_search_file, execute_download_file
from my_google.auth import Auth
from data_edit.module import get_date_from_jins_meme_file, get_fatigue_file_path
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
    print(f"開始時刻: {start_time}")
    pass_time = None

    date_for_search_file = start_time.date().strftime('%Y%m%d')
    while True:
        now = datetime.datetime.now()
        pass_time = get_pass_time(start_time, now)
        
        if pass_time != 0 and pass_time % 5 == 0:
            messagebox.showinfo('入力通知','1分以内に被験者の疲労度を入力してください')
            #TODO:入力のバリデーションしてないから余裕あればやる
            fatigue = input("被験者の疲労度を入力してください(終了するにはexitと打ってください)\n")
            
            if fatigue == 'exit':
                print("終了します")
                exit()
            files = execute_search_file(drive, date_for_search_file, jins_meme_data_name, page_limit=1)
            date_for_file_path = get_date_from_jins_meme_file(drive, files, jins_meme_data_name)
            
            file_path = get_fatigue_file_path(date_for_file_path)
            check_exist_and_may_create(file_path)

            print("経過時間: ")
            print(pass_time)
            print("ファイルの保存先: ")
            print(file_path)
            
            with open(file_path, 'w') as file:
                file.write(fatigue)
            
            time.sleep(60)

""" 経過時間の取得 """
def get_pass_time(start_time, now):
    pass_time_delta = now - start_time
    hour, minute = conversion_hour_minute_from_second(pass_time_delta.seconds)

    return hour * 60 + minute

""" 秒数を時間や分に変換する """
def conversion_hour_minute_from_second(second):
    minute, _ = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    return hour, minute

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