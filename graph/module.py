import glob, os
import pandas as pd
import matplotlib.pyplot as plt
from file_operation.module import *
from statistics import mean
from tabulate import tabulate

#dataframeがあればよいので、csvをひたすらに読み込んで(usecolsは瞬目の間隔時間平均だけ)瞬目の間隔時間平均のデータを取得する。
#読み込む際は、経過時間に対応している疲労度も一緒に読み込み、どの疲労度の時の瞬目の間隔時間平均か求めていく

def create_graph_from_ditection_data(alt_date, hours, result, colums, threshold):
    #グラフの初期設定
    plt.rcParams['font.family'] = 'Meiryo'

    #瞬目の間隔時間平均の閾値(疲労度が3になった時の値)のセット
    if not threshold:
        print('閾値がセットされてません。不具合の可能性があります')
        print(result)
        if input("この結果をグラフにしますか？(yes or no)") == 'yes':
            pass
        else:
            print('終了します。') 
            exit()
    threshold_pass_time = threshold['pass_time']
    threshold_fatigue_relation_value = int(threshold['fatigue_relation_value'])

    #グラフの保存先
    image_path = set_image_path(alt_date, hours)

    #作成するグラフの実験時間に依存する変数を取得する(作成するグラフの時間の範囲に依存する)
    per_five_minute, per_ten_minute, figsize = get_shaft_interval_figsize(hours[0] == hours[-1])

    df = pd.DataFrame(data=result, columns=colums)

    #サブプロット作成
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=figsize)
    plt.subplots_adjust(wspace=0.6)

    #経過時間と瞬目の間隔時間平均のグラフについて
    axes[0].plot(threshold_pass_time, threshold_fatigue_relation_value, "ro")

    df.plot(
         title='VDT開始からの経過時間による瞬目の間隔時間平均の変化',
         ax=axes[0],
         x=colums[0], 
         y=colums[1],
         xlabel='経過時間',
         ylabel='瞬目の間隔時間平均',
         xticks= per_ten_minute,
         yticks= per_five_minute
    )
    
    axes[0].text(
        x=threshold_pass_time, 
        y=threshold_fatigue_relation_value, 
        s=f'閾値 ({threshold_pass_time}, {threshold_fatigue_relation_value})',
        c='magenta',
        ha='left',
        va='bottom'
    )

    #経過時間と疲労度のグラフについて
    df.plot(
        title='VDT開始からの経過時間による疲労度の変化',
        ax=axes[1], 
        x=colums[0], 
        y=colums[2],
        xlabel='経過時間',
        ylabel='疲労度',
        xticks= per_ten_minute,
        yticks= range(1, 6)
    )

    fig.savefig(image_path)
    print('グラフの作成が出来ました。')


#download_ditection_dataで取得したデータからグラフを作成するための準備
def create_graph_from_ditection_data_ready(alt_date, hours, colums, jins_meme_data_name):
    year, month, day = get_date(alt_date)

    #(例)[[X1(VDT作業開始からの経過時間(5分ごと)) Y1(瞬目の間隔時間平均(5分ごと)) Z1(疲労度申告(5分ごと))], [X2 Y2 Z1],...[Xn Yn Zn]], 全てint型。
    date_blink_interval_time_fatigue_data = []
    pass_time = 0
    #疲労度
    fatigue = 0
    #VDT作業開始時間
    start_vdt_minitue = 0
    #瞬目の間隔時間平均の閾値
    threshold = {}
    #時間をまたぐまでの経過時間
    within_hour_pass_time = None
    #疲労度が記録されているファイルパス
    fatigue_data_file_path = None

    #1時間以内のグラフか1時間以上のグラフ両方の準備ができる
    for hour in range(hours[0], hours[-1] + 1):
        date_blink_interval_time_per_hour_data = []
        target_pathes = glob.glob(f'./ditection_data/{year}/{month}/{day}/{hour}/*{jins_meme_data_name}.csv')

        if target_pathes:
            date_blink_interval_time_per_hour_data = readCsv(target_pathes, colums)
        else:
            print("指定したファイルは存在しません。恐らく時間指定を間違っているかそのようなファイルパスは存在しません。")
        
        if date_blink_interval_time_per_hour_data:
            #まだVDT作業開始時間を設定していない場合
            if start_vdt_minitue == 0:
                start_vdt_minitue = int(date_blink_interval_time_per_hour_data[0][0][0][14:16])
            for per_minitue_data in date_blink_interval_time_per_hour_data:
                #per_minitue_data=[[date, {jins_meme_data_name}], type=object]となっている。
                minute = per_minitue_data[0][0][14:16]
                #日本時間に変換
                summary_data_hour = int(per_minitue_data[0][0][11:13]) + 9
                
                #たまにバグで時間(hour)をまたいだデータが入っている(date_blink_interval_time_per_hour_data)。
                if hour != summary_data_hour:
                    hour +=1
                
                #経過時間の取得(最初のpass_timeが0となってしまうので、開始pass_timeを1にした)
                if hour == hours[0]:
                    pass_time = int(minute) - start_vdt_minitue + 1
                else:
                    #時間をまたいだらそれまでの時間をセット(:例)14:06から開始して15:00までの経過時間54をwithin_hour_pass_timeに代入する
                    if not within_hour_pass_time:
                        within_hour_pass_time = pass_time

                    pass_time = within_hour_pass_time +  int(minute)

                #疲労度に関係のある指標を取得(基本はstrongBlinkIntervalAvgを使っている)
                fatigue_relation_value = get_fatigue_relation_value(jins_meme_data_name, per_minitue_data)

                #TODO:この部分もget_fatigue_data_pathで取得するようにするか。minutueの定義もまとめられるし
                fatigue_data_file_path = get_fatigue_data_path(per_minitue_data[0][0])
                #5分ごとに疲労度のデータ取得
                if pass_time % 5 == 0 and os.path.exists(fatigue_data_file_path):
                    fatigue = get_fatigue_data(fatigue_data_file_path)

                #1分ごとの経過時間・瞬目の間隔時間平均・疲労度のレコードを作成
                date_blink_interval_time_fatigue_data.append([pass_time, fatigue_relation_value, fatigue])
                #瞬目の間隔時間平均の閾値を定める
                if fatigue >= 3 and not threshold:
                    threshold  = {'pass_time': pass_time, 'fatigue_relation_value': fatigue_relation_value}
                
    return date_blink_interval_time_fatigue_data, threshold 

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

""" グラフ保存先パスの準備 """
def set_image_path(alt_date, hours):
    year, month, day = get_date(alt_date)
    rest_or_non = check_rest_or_non(input("「休憩あり」か「休憩なし」か入力してください: (例) 休憩ありの場合は->rest, 休憩なしの場合は->non-rest\n"))

    if hours[0] == hours[-1]:
        image_path = f'./graph/{year}/{month}/{day}/{hours[0]}/{rest_or_non}/blinkIntervalMean-fatigue.png'
    else:
        image_path = f'./graph/{year}/{month}/{day}/{hours[0]}-{hours[-1]}/{rest_or_non}/blinkIntervalMean-fatigue.png'

    check_exist_and_may_create(image_path)

    return image_path

""" グラフの設定(軸周りや大きさなど) """
def get_shaft_interval_figsize(less_than_one_hour_flag):
    per_five_minute = list(filter(lambda x: x % 5 == 0, range(0, 61)))

    if less_than_one_hour_flag:
        per_ten_minute = list(filter(lambda x: x % 5 == 0, range(0, 61)))
        figsize = (9, 6)
    else:
        per_ten_minute = list(filter(lambda x: x % 10 == 0, range(0, 121)))
        figsize = (12, 9)
    
    return per_five_minute, per_ten_minute, figsize



""" 疲労度ごとの瞬目の間隔時間平均の振り幅の表作成 """
def create_blink_interval_time_amplitude_table(date, jins_meme_data_name):
    #疲労度ごとの瞬目の間隔時間平均値のhashを取得
    blink_interval_at_fatigue_hash = ready_blink_interval_at_fatigue_hash(date, jins_meme_data_name)
    #取得したhashの分析
    blink_interval_at_fatigue_minimum_max, blink_interval_at_fatigue_average = analyze_blink_interval_at_fatigue(blink_interval_at_fatigue_hash)
    
    table_data_average = get_table_data(blink_interval_at_fatigue_average, default_flag=True)
    table_data_minimum_max = get_table_data(blink_interval_at_fatigue_minimum_max)
    headers = ['1', '2', '3', '4', '5']

    table_minimum_max = tabulate(tabular_data=table_data_minimum_max, headers=headers, tablefmt='html')
    table_average = tabulate(tabular_data=table_data_average, headers=headers, tablefmt='html')
    
    
    if input("疲労度ごとの瞬目の間隔時間平均値の分析結果を表示しますか？(yes or no)\n") == 'yes':
        print('[最小値, 最大値]')
        print(blink_interval_at_fatigue_minimum_max)
        print('平均値')
        print(blink_interval_at_fatigue_average)
        
    return table_minimum_max, table_average

""" 疲労度のパスを取得 """
def get_fatigue_data_path(date_time):
    year = date_time[0:4]
    month = date_time[5:7]
    day = date_time[8:10]
    hour_in_japan = str(int(date_time[11:13]) + 9).zfill(2)
    minute = date_time[14:16]    
    fatigue_data_path = f'./fatigue_data/{year}/{month}/{day}/{hour_in_japan}/{minute}.txt'
    
    return fatigue_data_path

""" 疲労度ごとの瞬目の間隔時間平均の関係を作成(dict形式) """
def ready_blink_interval_at_fatigue_hash(date, jins_meme_data_name):
    year, month, _ = get_date(date)
    target_pathes = glob.glob(f'./ditection_data/{year}/{month}/*/*/*{jins_meme_data_name}.csv')
    colums = ['date', 'strongBlinkIntervalAvg']
    date_blink_interval_list = readCsv(target_pathes, colums)
    
    #瞬目の間隔時間平均と疲労度の関連付けの初期化
    blink_interval_at_fatigue_hash = {}
    for key in range(1, 6):
        blink_interval_at_fatigue_hash[key] = []

    for date_blink_interval in [value[0] for value in date_blink_interval_list]:
        if len(date_blink_interval) != 0:
            fatigue_data_path = get_fatigue_data_path(date_blink_interval[0])
            if os.path.exists(fatigue_data_path):
                fatigue = get_fatigue_data(fatigue_data_path)
                #特殊なフィルター(不正なデータを取り除く)
                if fatigue == 2 and date_blink_interval[1] > 7:
                    continue
                blink_interval_at_fatigue_hash[fatigue].append(date_blink_interval[1])
    
    return blink_interval_at_fatigue_hash

""" 疲労度ごとの瞬目の間隔時間平均値を分析 """
def analyze_blink_interval_at_fatigue(blink_interval_at_fatigue_hash):
    #最大値最小値を求める
    for key, values in blink_interval_at_fatigue_hash.items():
        blink_interval_at_fatigue_hash[key] = [min(values), max(values)]
    blink_interval_at_fatigue_max_minimum = blink_interval_at_fatigue_hash.copy()
    for key, values in blink_interval_at_fatigue_hash.items():
        blink_interval_at_fatigue_hash[key] = mean(values)
    blink_interval_at_fatigue_average = blink_interval_at_fatigue_hash.copy()

    return blink_interval_at_fatigue_max_minimum, blink_interval_at_fatigue_average

""" 表作成するために加工したデータを取得 """
def get_table_data(hash, default_flag=False):
    if default_flag:
        table_data = [list(hash.values())] 
    else:
        array = []
        for values in hash.values():
            array.append(' ~ '.join([str(value) for value in values]))
        table_data = [array]
    
    return table_data