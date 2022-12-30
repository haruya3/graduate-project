import os, glob, collections
from statistics import mean
from tabulate import tabulate
from data_edit.module import get_date, get_fatigue_data_path_old, get_fatigue_data
from data_edit.graph.module import create_dataframe, plot_scatter
from file_operation.module import readCsv
from dotenv import load_dotenv
load_dotenv()

""" 疲労度ごとの瞬目の間隔時間平均の振り幅の表作成 """
def analyze_blink_interval_at_fatigue(date, jins_meme_data_name, rest_flag):
    #疲労度ごとの瞬目の間隔時間平均値のhashを取得
    blink_interval_at_fatigue_hash = ready_blink_interval_at_fatigue_hash(date, jins_meme_data_name, rest_flag=rest_flag)
    
    #取得したhashの分析
    #TODO:この関数で得るのは疲労度ごとの瞬目の間隔時間平均値の最大値・最小値、平均値、0.5ずつに変換したものである
    #これは別々の関数にして一つずつ取得していくべき
    blink_interval_at_fatigue_minimum_max, blink_interval_at_fatigue_average,  point_five_blink_interval_at_fatigue_hist= get_analyzed_blink_interval_at_fatigue(blink_interval_at_fatigue_hash)
    
    table_data_average = get_table_data_for_average(blink_interval_at_fatigue_average)
    table_data_minimum_max = get_table_data_for_max_minimum(blink_interval_at_fatigue_minimum_max)
    headers = ['1', '2', '3', '4', '5']

    table_minimum_max = tabulate(tabular_data=table_data_minimum_max, headers=headers, tablefmt='html')
    table_average = tabulate(tabular_data=table_data_average, headers=headers, tablefmt='html')
    
    data_hash = {}
    for key, value in point_five_blink_interval_at_fatigue_hist.items():
        data_hash[key] = [ [key, data] for key, data in value.items()]
    hist_data_frame_colums =  [os.getenv('FATIGUE_RELATION_VALUE'), 'count']
    #ヒストグラムの作成のために分かりやすいデータとしてデータフレームにする
    list_dataframe_for_hist = create_dataframe(data_hash, hist_data_frame_colums)

    blink_interval_at_fatigue_for_plot = []
    for fatigue, blink_interval in blink_interval_at_fatigue_average.items():
            blink_interval_at_fatigue_for_plot.append([fatigue, blink_interval])
    
    #TODO:それぞれを求める関数に分けたら、こんな大量のreturnはせずに済むね(Analyzeクラス作ってもよいし)
    return table_minimum_max, table_average, blink_interval_at_fatigue_minimum_max, blink_interval_at_fatigue_average, list_dataframe_for_hist, point_five_blink_interval_at_fatigue_hist, blink_interval_at_fatigue_for_plot


""" 疲労度ごとの瞬目の間隔時間平均の関係を作成(dict形式) """
def ready_blink_interval_at_fatigue_hash(date, jins_meme_data_name, rest_flag):
    year, _, _ = get_date(date)
    target_pathes = glob.glob(f'./ditection_data/{year}/*/*/*/*{jins_meme_data_name}.csv')
    
    if rest_flag:
        target_pathes= glob.glob(f'./ditection_data/rest/{year}/*/*/*/*{jins_meme_data_name}.csv')

    colums = ['date', 'strongBlinkIntervalAvg']
    date_blink_interval_list = readCsv(target_pathes, colums)
    
    #瞬目の間隔時間平均と疲労度の関連付けの初期化
    blink_interval_at_fatigue_hash = {}
    for key in range(1, 6):
        blink_interval_at_fatigue_hash[key] = []

    for date_blink_interval in [value[0] for value in date_blink_interval_list]:
        if len(date_blink_interval) == 0:
            continue
    
        fatigue_data_path = get_fatigue_data_path_old(date_blink_interval[0], rest_flag=rest_flag)
        #毎分ごとのdate_blink_intervalをfor文で回すため疲労度のファイルパスが存在する時は必ずある。
        if not os.path.exists(fatigue_data_path):
            continue
    
        fatigue = get_fatigue_data(fatigue_data_path)
        #特殊なフィルター(不正なデータを取り除く)
        if fatigue == 1 and date_blink_interval[1] > float(os.getenv('FATIGUE_ONE_MAX')):
            continue
        if fatigue == 2 and date_blink_interval[1] > float(os.getenv('FATIGUE_TWO_MAX')):
            continue
        if fatigue == 3 and date_blink_interval[1] < float(os.getenv('FATIGUE_THREE_MINIMUM')):
            continue
        if fatigue == 4 and date_blink_interval[1] <= float(os.getenv('FATIGUE_FOURTH_MINIMUM')):
            continue
        blink_interval_at_fatigue_hash[fatigue].append(date_blink_interval[1])
    
    return blink_interval_at_fatigue_hash

""" 疲労度ごとの瞬目の間隔時間平均値を分析 """
def get_analyzed_blink_interval_at_fatigue(blink_interval_at_fatigue_hash):
    blink_interval_at_fatigue_max_minimum = {}
    blink_interval_at_fatigue_average = {}
    point_five_blink_interval_at_fatigue_hist = {}
    #最大値・最小値を求める
    for key, values in blink_interval_at_fatigue_hash.items():
        blink_interval_at_fatigue_max_minimum[key] = [min(values), max(values)]
    #平均値を求める
    for key, values in blink_interval_at_fatigue_hash.items():
        blink_interval_at_fatigue_average[key] = round(mean(values), 2)
    #散らばりを求める(疲労度に対して瞬目の間隔時間平均値の分布(0.5単位で))
    for key, values in blink_interval_at_fatigue_hash.items():
        point_five_blink_interval_at_fatigue = list(map(lambda x:  (int(x / 0.5) * 0.5) + 0.5, values))
        point_five_blink_interval_at_fatigue_hist[key] = collections.Counter(point_five_blink_interval_at_fatigue)

    return blink_interval_at_fatigue_max_minimum, blink_interval_at_fatigue_average, point_five_blink_interval_at_fatigue_hist

""" 表作成するために加工したデータを取得 """
def get_table_data_for_average(hash):
    return [list(hash.values())] 
     
def get_table_data_for_max_minimum(array):
    result = []
    for values in array.values():
        result.append(' ~ '.join([str(value) for value in values]))
    return [result]
    

""" ヒストグラムで使うx軸のメモり値 """
def get_xticks(point_five_blink_interval_at_fatigue_minimum_max, step):
    result = []
    for key, point_five_minimum_max in point_five_blink_interval_at_fatigue_minimum_max.items():
        array = [point_five_minimum_max[0]]
        n = point_five_minimum_max[0]
        if key >= 3 and key < 5:
            step = 2
        elif key == 5:
            step = 3.5
        while True:
            n = n + step
            if not n <= point_five_minimum_max[1]:
                array.append(point_five_minimum_max[1])
                break
            array.append(n)

        result.append({key: array})
    return result

""" 0.5単位の瞬目の間隔時間平均値の疲労度ごとの最小値・最大値 """
def get_point_five_blink_interval_minimum_max(point_five_blink_interval_at_fatigue_hist):
    point_five_blink_interval_minimum_max = {}
    for key, value in point_five_blink_interval_at_fatigue_hist.items():
        point_five_blink_intervals = [point_five_blink_interval for point_five_blink_interval, count in value.items()]
        point_five_blink_interval_minimum_max[key] = [min(point_five_blink_intervals), max(point_five_blink_intervals)]
    
    return point_five_blink_interval_minimum_max

""" 疲労度と瞬目の間隔時間の相関図の作成 """
def plot_scatter_flow(data_hash, colums):
    fatigue_blink_interval_array = []
    for fatigue, blink_interva_count_hash in data_hash.items():
        for blink_interval, _ in blink_interva_count_hash.items():
            fatigue_blink_interval_array.append([fatigue, blink_interval])
    
    plot_scatter(fatigue_blink_interval_array, colums)