import glob, os
import pandas as pd

#download_ditection_dataで取得したデータからグラフを作成するための準備
def create_graph_from_ditection_data_ready(date, hours):
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]

    #(例)[[X1(VDT作業開始からの経過時間(5分ごと)) Y1(瞬目の間隔時間平均(5分ごと)) Z1(疲労度申告(5分ごと))], [X2 Y2 Z1],...[Xn Yn Zn]], 全てint型。
    date_blink_interval_time_fatigue_data = []
    #疲労度
    fatigue = 0
    #VDT作業開始時間
    start_vdt_minitue = 0
    
    #1時間ごとにデータ(date_blink_interval_time_fatigue_data)を取得していく->hours[-1]とすることで配列要素1つだけの時エラー回避
    for hour in range(hours[0], hours[-1] + 1):
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
            for per_minitue_data in date_blink_interval_time_per_hour_data:
                blink_interval_time_average = 0
                blink_interval_time_sum = 0
                minute = per_minitue_data[0][0][14:16]
                fatigue_data_file_path = f'./fatigue_data/{year}/{month}/{day}/{hour}/{minute}.txt'

                #経過時間の取得
                pass_time = int(minute) - start_vdt_minitue

                #5分ごとに疲労度のデータ取得
                if pass_time % 5 == 0 and os.path.exists(fatigue_data_file_path):
                    fatigue = get_fatigue_data(fatigue_data_file_path)

                #1分ごとの瞬目の時間間隔のデータの取得
                for data in per_minitue_data:
                    blink_interval_time_sum += data[1]

                blink_interval_time_average = int(blink_interval_time_sum / len(per_minitue_data))

                #1分ごとの経過時間・瞬目の間隔時間平均・疲労度のレコードを作成
                date_blink_interval_time_fatigue_data.append([pass_time, blink_interval_time_average, fatigue])
        
        #もし該当する時間にデータが取得されていなかったらスキップする
        else:
            continue

    return date_blink_interval_time_fatigue_data 

""" 疲労度の値を取得 """
def get_fatigue_data(file_path):
    with open(file_path, 'r') as file:
        value = file.read()
    return int(value)
