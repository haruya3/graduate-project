import glob, os, re
import pandas as pd
import matplotlib.pyplot as plt
from file_operation.module import *

def create_graph_from_ditection_data(alt_date, hours, result, colums):
    plt.rcParams['font.family'] = 'Meiryo'
    year, month, day = get_date(alt_date)
    rest_or_non = check_rest_or_non(input("「休憩あり」か「休憩なし」か入力してください: (例) 休憩ありの場合は->rest, 休憩なしの場合は->non-rest\n"))
    image_path = f'./graph/{year}/{month}/{day}/{hours[0]}/{rest_or_non}/blinkIntervalMean-fatigue.png'
    check_exist_and_may_create(image_path)

    df = pd.DataFrame(data=result, columns=colums)
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(9, 6))
    plt.subplots_adjust(wspace=0.6)
    per_five_minute = list(filter(lambda x: x % 5 == 0, range(0, 61)))

    df.plot(
         title='VDT開始からの経過時間による瞬目の間隔時間平均の変化',
         ax=axes[0],
         x=colums[0], 
         y=colums[1],
         xlabel='経過時間',
         ylabel='瞬目の間隔時間平均',
         xticks= per_five_minute,
         yticks= per_five_minute
        )
    df.plot(
        title='VDT開始からの経過時間による疲労度の変化',
        ax=axes[1], 
        x=colums[0], 
        y=colums[2],
        xlabel='経過時間',
        ylabel='疲労度',
        xticks= per_five_minute,
        yticks= range(1, 6)
        )
    fig.savefig(image_path)


#download_ditection_dataで取得したデータからグラフを作成するための準備
def create_graph_from_ditection_data_ready(alt_date, hours, colums, jins_meme_data_name):
    year, month, day = get_date(alt_date)

    #(例)[[X1(VDT作業開始からの経過時間(5分ごと)) Y1(瞬目の間隔時間平均(5分ごと)) Z1(疲労度申告(5分ごと))], [X2 Y2 Z1],...[Xn Yn Zn]], 全てint型。
    date_blink_interval_time_fatigue_data = []
    #疲労度)
    fatigue = 0
    #VDT作業開始時間
    start_vdt_minitue = 0
    
    #1時間ごとにデータ(date_blink_interval_time_fatigue_data)を取得していく->hours[-1]とすることで配列要素1つだけの時エラー回避
    for hour in range(hours[0], hours[-1] + 1):
        target_pathes = glob.glob(f'./ditection_data/{year}/{month}/{day}/{hour}/*{jins_meme_data_name}.csv')

        date_blink_interval_time_per_hour_data = []

        if target_pathes:
            #ひとつずつcsvファイルの中身を取得する
            for path in target_pathes:
                #空ファイルは無視する
                if os.path.getsize(path) != 0:
                    #デフォルトで、delimiterが,になっている
                    csv_data = pd.read_csv(path, usecols=colums)
                    date_blink_interval_time_per_hour_data.append(csv_data.values)
        else:
            print("指定したファイルは存在しません。恐らく時間指定を間違っているかそのようなファイルパスは存在しません。")
            
        # 一つの配列はcsvファイルでいう一つの行レコードとなる
        date_blink_interval_time_fatigue_data = []
        
        if date_blink_interval_time_per_hour_data:
            #まだVDT作業開始時間を設定していない場合
            if start_vdt_minitue == 0:
                start_vdt_minitue = int(date_blink_interval_time_per_hour_data[0][0][0][14:16])

            #VDT作業開始時間
            for per_minitue_data in date_blink_interval_time_per_hour_data:
                #per_minitue_data=[[date, {jins_meme_data_name}], type=object]となっている。
                minute = per_minitue_data[0][0][14:16]
                
                #次のhourにデータが先行しているためノイズとして排除する
                if minute == '00':
                    continue
                
                fatigue_data_file_path = f'./fatigue_data/{year}/{month}/{day}/{hour}/{minute}.txt'

                #経過時間の取得(最初のpass_timeが0となってしまうので、開始pass_timeを1にした)
                pass_time = int(minute) - start_vdt_minitue + 1

                #疲労度に関係のある指標を取得(基本はstrongBlinkIntervalAvgを使っている)
                fatigue_relation_value = get_fatigue_relation_value(jins_meme_data_name, per_minitue_data)

                #5分ごとに疲労度のデータ取得
                if pass_time % 5 == 0 and os.path.exists(fatigue_data_file_path):
                    fatigue = get_fatigue_data(fatigue_data_file_path)

                #1分ごとの経過時間・瞬目の間隔時間平均・疲労度のレコードを作成
                date_blink_interval_time_fatigue_data.append([pass_time, fatigue_relation_value, fatigue])
        
        #もし該当する時間にデータが取得されていなかったらスキップする
        else:
            continue

    return date_blink_interval_time_fatigue_data 

""" 日付から年月日それぞれに分ける """
def get_date(date):
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    return year, month, day

""" csvファイルにある疲労度に関係のある指標を取得する """
def get_fatigue_relation_value(jins_meme_data_name, per_minute_data):
    #blink_interval_time_average = 0
    #blink_interval_time_sum = 0
    value = None

    if jins_meme_data_name == 'logicIndexData':
        #logicIndexData15秒ごとのデータなのでcsvファイルに4つのレコードが入っている。
        for data in per_minute_data:
            value += data[1]

    elif jins_meme_data_name == 'summaryData':
        value = per_minute_data[0][1]
    
    return value

""" 疲労度の値を取得 """
def get_fatigue_data(file_path):
    with open(file_path, 'r') as file:
        value = file.read()
    return int(value)

""" グラフ作成時に「休憩あり」か「休憩なし」か入力する際のバリデーション """
def check_rest_or_non(input):
    if input == 'rest' or input == 'non-rest':
        return input
    else:
        print("restかnon-restで入力してください。")
        exit()

