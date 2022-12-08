""" 日付から年月日それぞれに分ける """
def get_date(date):
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    return year, month, day

###########疲労度について#############
""" 疲労度の値を取得 """
def get_fatigue_data(file_path):
    with open(file_path, 'r') as file:
        value = file.read()
    if value == '':
        print(f"以下のファイルが空です\n{file_path}\nファイルに疲労度を記録してください")
        exit()
    return int(value)

import datetime
from file_operation.module import readCsv
from my_google.my_drive.helper import execute_download_file
""" 
    Jins memeでGoogle Driveに作成されたCSVファイルのdateキーから時間を取得する
    これをfatigue保存先パスで使うことでfatigueファイルを読み込む(graph/module.pyで5分ごと(このpass_timeもCSVファイルのdateキーの値)に読み込む際に)際の誤差がなくなる
"""
def get_date_from_jins_meme_file(drive, files, jins_meme_data_name, rest_flag=False):
    if files:
        download_file_path = execute_download_file(drive, files[0], jins_meme_data_name, rest_flag=rest_flag)
        #date=[[['date', dtype=object]]]
        date = readCsv([download_file_path], ['date'])
        #日本時間に合わせる
        JST = datetime.timedelta(hours=9)
        
        return datetime.datetime.fromisoformat(date[0][0][0][:16]) + JST
    else:
        print('入力された日付時間のデータはありませんでした。')
        exit()

""" 疲労度を保存するファイルパスを取得 """
def get_fatigue_file_path(date, rest_flag=False):
    year = date.year
    month = str(date.month).zfill(2)
    day = str(date.day).zfill(2)
    hour = str(date.hour).zfill(2)
    minute = str(date.minute).zfill(2)
    file_path = f'./fatigue_data/{year}/{month}/{day}/{hour}/{minute}.txt'

    if rest_flag:
        file_path = f'./fatigue_data/rest/{year}/{month}/{day}/{hour}/{minute}.txt'
    
    return file_path

#TODO:これは、旧式。よって、上記のget_fatigue_file_path関数に置き換える必要がある。
#そのためには、pass_timeの求め方もdatetime.timedeltaでやらないといけないかも
""" 疲労度のパスを取得 """
def get_fatigue_data_path_old(date_time, rest_flag=False):
    year = date_time[0:4]
    month = date_time[5:7]
    day = date_time[8:10]
    hour_in_japan = str(int(date_time[11:13]) + 9).zfill(2)
    minute = date_time[14:16]    
    fatigue_data_path = f'./fatigue_data/{year}/{month}/{day}/{hour_in_japan}/{minute}.txt'

    if rest_flag:
        fatigue_data_path = f'./fatigue_data/rest/{year}/{month}/{day}/{hour_in_japan}/{minute}.txt'
    
    return fatigue_data_path