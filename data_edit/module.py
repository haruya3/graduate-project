""" 日付から年月日それぞれに分ける """
def get_date(date):
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    return year, month, day

###########疲労度について#############

""" 疲労度のパスを取得 """
def get_fatigue_data_path(date_time):
    year = date_time[0:4]
    month = date_time[5:7]
    day = date_time[8:10]
    hour_in_japan = str(int(date_time[11:13]) + 9).zfill(2)
    minute = date_time[14:16]    
    fatigue_data_path = f'./fatigue_data/{year}/{month}/{day}/{hour_in_japan}/{minute}.txt'
    
    return fatigue_data_path

""" 疲労度の値を取得 """
def get_fatigue_data(file_path):
    with open(file_path, 'r') as file:
        value = file.read()
    return int(value)