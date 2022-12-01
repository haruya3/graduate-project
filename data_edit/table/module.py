import os, glob
from statistics import mean
from tabulate import tabulate
from data_edit.module import get_date, get_fatigue_data_path_old, get_fatigue_data
from file_operation.module import readCsv
from dotenv import load_dotenv
load_dotenv()

""" 疲労度ごとの瞬目の間隔時間平均の振り幅の表作成 """
def create_blink_interval_time_amplitude_table(date, jins_meme_data_name, rest_flag):
    #疲労度ごとの瞬目の間隔時間平均値のhashを取得
    blink_interval_at_fatigue_hash = ready_blink_interval_at_fatigue_hash(date, jins_meme_data_name, rest_flag=rest_flag)
    #取得したhashの分析
    blink_interval_at_fatigue_minimum_max, blink_interval_at_fatigue_average = analyze_blink_interval_at_fatigue(blink_interval_at_fatigue_hash)
    
    table_data_average = get_table_data(blink_interval_at_fatigue_average)
    table_data_minimum_max = get_table_data(blink_interval_at_fatigue_minimum_max, default_flag=False)
    headers = ['1', '2', '3', '4', '5']

    table_minimum_max = tabulate(tabular_data=table_data_minimum_max, headers=headers, tablefmt='html')
    table_average = tabulate(tabular_data=table_data_average, headers=headers, tablefmt='html')
    
    
    if input("疲労度ごとの瞬目の間隔時間平均値の分析結果を表示しますか？(yes or no)\n") == 'yes':
        print('[最小値, 最大値]')
        print(blink_interval_at_fatigue_minimum_max)
        print('平均値')
        print(blink_interval_at_fatigue_average)
        
    return table_minimum_max, table_average

""" 疲労度ごとの瞬目の間隔時間平均の関係を作成(dict形式) """
def ready_blink_interval_at_fatigue_hash(date, jins_meme_data_name, rest_flag):
    year, month, _ = get_date(date)
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
        if len(date_blink_interval) != 0:
            fatigue_data_path = get_fatigue_data_path_old(date_blink_interval[0], rest_flag=rest_flag)
            #毎分ごとのdate_blink_intervalをfor文で回すため疲労度のファイルパスが存在する時は必ずある。
            if os.path.exists(fatigue_data_path):
                fatigue = get_fatigue_data(fatigue_data_path)
                #特殊なフィルター(不正なデータを取り除く)
                if fatigue == 2 and date_blink_interval[1] > float(os.getenv('FATIGUE_TWO_FILTER')):
                    continue
                if fatigue == 3 and date_blink_interval[1] < float(os.getenv('FATIGUE_THREE_FILTER')):
                    continue
                if fatigue == 4 and date_blink_interval[1] <= float(os.getenv('FATIGUE_FOURTH_FILTER')):
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
#defult_flag : hash=[]と一次元配列の時True
#table_minimum_maxの場合[[],[],[]..]の二次元配列配列の時はFalse
def get_table_data(hash, default_flag=True):
    if default_flag:
        table_data = [list(hash.values())] 
    else:
        array = []
        for values in hash.values():
            array.append(' ~ '.join([str(value) for value in values]))
        table_data = [array]
    
    return table_data