import glob, os
import pandas as pd
import matplotlib.pyplot as plt
from file_operation.module import *
from data_edit.module import get_date, get_fatigue_data_path_old, get_fatigue_data

def create_graph_from_ditection_data(alt_date, hours, result, colums, threshold, rest_flag=False):
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
    image_path = set_image_path(alt_date, hours, rest_flag=rest_flag)

    #作成するグラフの実験時間に依存する変数を取得する(作成するグラフの時間の範囲に依存する)
    per_five_minute, per_ten_minute, figsize = get_shaft_interval_figsize(hours[0] == hours[-1])
    df = pd.DataFrame(data=result, columns=colums)

    #サブプロット作成
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=figsize)
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
    
    #TODO:グラフのメモリを指定する方法調べる、横軸疲労度にする必要がある
    df.plot.scatter(
        x=colums[2], 
        y=colums[1],
        ax=axes[2]
    )

    fig.savefig(image_path)

    print('グラフの作成が出来ました。')

""" 
    pass_timeをget_start_timeとget_pass_time関数をつかって求めるようにする。
"""
#download_ditection_dataで取得したデータからグラフを作成するための準備
def create_graph_from_ditection_data_ready(alt_date, hours, colums, jins_meme_data_name, rest_flag=False):
    year, month, day = get_date(alt_date)

    #(例)[[X1(VDT作業開始からの経過時間(5分ごと)) Y1(瞬目の間隔時間平均(5分ごと)) Z1(疲労度申告(5分ごと))], [X2 Y2 Z1],...[Xn Yn Zn]], 全てint型。
    date_blink_interval_time_fatigue_data = []
    pass_time = 0
    #疲労度
    fatigue = 1
    #VDT作業開始時間
    start_vdt_minitue = 0
    #瞬目の間隔時間平均の閾値
    threshold = {}
    #時間をまたぐまでの経過時間
    within_hour_pass_time = None
    previous_hour=None
    #疲労度が記録されているファイルパス
    fatigue_data_file_path = None

    #1時間以内のグラフか1時間以上のグラフ両方の準備ができる
    for hour in range(hours[0], hours[-1] + 1):
        date_blink_interval_time_per_hour_data = []
        target_pathes = glob.glob(f'./ditection_data/{year}/{month}/{day}/{hour}/*{jins_meme_data_name}.csv')

        if rest_flag:
            target_pathes = glob.glob(f'./ditection_data/rest/{year}/{month}/{day}/{hour}/*{jins_meme_data_name}.csv')

        if not target_pathes:
            print("指定したファイルは存在しません。恐らく時間指定を間違っているかそのようなファイルパスは存在しません。")
            exit()

        date_blink_interval_time_per_hour_data = readCsv(target_pathes, colums)

        
        if not date_blink_interval_time_per_hour_data:
            print('csvファイルを読み込めていません。指定する時間に実験をしていたか確認してください。')
            exit()
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
                pass_time = int(minute) - start_vdt_minitue
            else:
                #時間をまたいだらそれまでの時間をセット(:例)14:06から開始して15:00までの経過時間54をwithin_hour_pass_timeに代入する
                if not within_hour_pass_time or hour != previous_hour:
                    #TODO:なぜかwithin_hour_pass_timeには+1しなきゃいけないときとしたらダメな時がある(fatigue_dataとの関連付けについての話)。
                    within_hour_pass_time = pass_time
                    previous_hour = hour
                pass_time = within_hour_pass_time +  int(minute)

            #疲労度に関係のある指標を取得(基本はstrongBlinkIntervalAvgを使っている)
            fatigue_relation_value = get_fatigue_relation_value(jins_meme_data_name, per_minitue_data)

            fatigue_data_file_path = get_fatigue_data_path_old(per_minitue_data[0][0], rest_flag=rest_flag)

            #5分ごとに疲労度のデータ取得
            if pass_time != 0 and pass_time % 5 == 0 and check_fatigue_data_file_path(fatigue_data_file_path):
                fatigue = get_fatigue_data(fatigue_data_file_path)

            #1分ごとの経過時間・瞬目の間隔時間平均・疲労度のレコードを作成
            date_blink_interval_time_fatigue_data.append([pass_time, fatigue_relation_value, fatigue])

            #デバッグ用関数
            #start_debug(minute, pass_time, fatigue_data_file_path, fatigue)

            #瞬目の間隔時間平均の閾値を定める
            if fatigue >= 3 and not threshold:
                threshold  = {'pass_time': pass_time, 'fatigue_relation_value': fatigue_relation_value}
                
    return date_blink_interval_time_fatigue_data, threshold 

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

""" グラフ保存先パスの準備 """
def set_image_path(alt_date, hours, rest_flag=False):
    year, month, day = get_date(alt_date)
    rest_or_non = None

    if rest_flag:
        rest_or_non = 'rest'
    else:
        rest_or_non = 'non-rest'

    if hours[0] == hours[-1]:
        image_path = f'./data_edit/graph/{year}/{month}/{day}/{hours[0]}/{rest_or_non}/blinkIntervalMean-fatigue.png'
    else:
        image_path = f'./data_edit/graph/{year}/{month}/{day}/{hours[0]}-{hours[-1]}/{rest_or_non}/blinkIntervalMean-fatigue.png'

    check_exist_and_may_create(image_path)

    return image_path

""" グラフの設定(軸周りや大きさなど) """
def get_shaft_interval_figsize(less_than_one_hour_flag):
    per_five_minute = list(filter(lambda x: x % 5 == 0, range(0, 61)))

    if less_than_one_hour_flag:
        per_ten_minute = list(filter(lambda x: x % 5 == 0, range(0, 61)))
        figsize = (12, 9)
    else:
        per_ten_minute = list(filter(lambda x: x % 10 == 0, range(0, 121)))
        figsize = (15, 12)
    
    return per_five_minute, per_ten_minute, figsize

""" 
    疲労度のファイルが存在しているか確認する->存在していなかったら終了する
    pass_timeと疲労度のファイルパスがずれる(Read.MEを参考に)ことがあるので、ずれた際は例外処理(障害回復できるように)する。
"""
def check_fatigue_data_file_path(path):
    if os.path.exists(path):
        return True
    else:
        print(f"以下の疲労度のファイルが存在しません。\n{path}")
        print('恐らくファイルの時間と経過時間に対応していない(ずれている)可能性があるのでファイル名を修正してください')
        exit()

""" デバッグ用の関数(グラフが作成できない・疲労度が3を超えているはずなのに超えていない時などに使える) """
def start_debug(minute, pass_time, fatigue_data_file_path, fatigue):
    print(minute)
    print('経過時間')
    print(pass_time)
    print(fatigue_data_file_path)
    print('疲労度')
    print(fatigue)

""" 
    ヒストグラムの作成
    table.moduleから呼び出される 
"""
#TODO:現状うまくグラフ作成できていないので時間ある時修正する->ヒストグラム作成できるｗｅｂサイトあるのでそこで作成した方が早いから
def plot_hist(data_hash, colums, xticks_at_fatigue):
    #グラフの初期設定
    plt.rcParams['font.family'] = 'Meiryo'
    plt.subplots_adjust(wspace=1.5)

    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 15))
    saving_path = f'./data_edit/graph/hist.png'
    check_exist_and_may_create(saving_path)
    i = 0
    k = 0

    ####TODO:なぜか、うまくデータの表示ができない。。・。。
    for key, value in data_hash.items():
        df = pd.DataFrame(data=value, columns=colums)
        #MEMO:これは手動でヒストグラム作る際にデータ表示のために使う。
        #print(df)
        print(key)
        print(df)
        xticks = xticks_at_fatigue[key-1][key]
        df.plot(
            title=f'疲労度{key}についての各瞬目の間隔時間平均値の個数',
            ax=axes[i][k],
            x=colums[0], 
            y=colums[1],
            xlabel='瞬目の間隔時間平均(0.5単位に丸めている)',
            ylabel='個数',
            xticks=xticks,
            yticks= range(1, 11),
            xlim=[xticks[0], xticks[-1]],
            kind='hist'
        )
        if k == 2:
            i += 1
            k = 0
        else:
            k += 1

    fig.savefig(saving_path)
    print('ヒストグラムの作成ができました')


""" 
    ハッシュデータから用途はデータフレームを作成する 
    今のところヒストグラム作成の手動作成したい時の分かりやすいデータ表示のために使う。
"""
def create_dataframe(data_hash, colums):
    result = []
    for _, value in data_hash.items():
        df = pd.DataFrame(data=value, columns=colums)
        result.append(df)
    return result

""" 
    今のところテーブル作成する際にだけ使われる
    疲労度と瞬目の間隔時間の相関図作成
"""
def plot_scatter(data, colums):
    plt.rcParams['font.family'] = 'Meiryo'

    df = pd.DataFrame(data=data, columns=colums)
    xticks = [1, 2, 3, 4, 5]
    df.plot.scatter(
        x=colums[0], 
        y=colums[1],
        xlabel='疲労度',
        ylabel='瞬目の間隔時間',
        xticks=xticks
    )
    plt.show()

def plot_average_blink_interval_at_fatigue(data, colums):
    plt.rcParams['font.family'] = 'Meiryo'
    df = pd.DataFrame(data=data, columns=colums)
    xticks = [1, 2, 3, 4, 5]

    df.plot(
        x=colums[0],
        y=colums[1],
        xlabel='疲労度',
        ylabel='瞬目の間隔時間の平均値',
        xticks=xticks
    )
    plt.show()