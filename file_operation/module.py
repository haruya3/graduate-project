import os
import pandas as pd

""" あるパスの存在確認をする。存在しない場合は作成する"""
def check_exist_and_may_create(path):
    directory_path = os.path.dirname(path)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

""" csvファイルから指定した列のデータを読み込む  """
#(注意)target_pathes: array
def readCsv(target_pathes, colums):
    result = []
    #ひとつずつcsvファイルの中身を取得する
    for path in target_pathes:
        #空ファイルは無視する
        if os.path.getsize(path) != 0:
            #デフォルトで、delimiterが,になっている
            csv_data = pd.read_csv(path, usecols=colums)
            result.append(csv_data.values)
        
    return result