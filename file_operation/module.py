import os

""" あるパスの存在確認をする。存在しない場合は作成する"""
def check_exist_and_may_create(path):
    directory_path = os.path.dirname(path)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
