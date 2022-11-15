import datetime, time
from tkinter import messagebox
from file_operation.module import *

def main():
    start_time = datetime.datetime.now()
    while True:
        now_time = datetime.datetime.now()
        pass_time = now_time.minute - start_time.minute

        if pass_time != 0 and pass_time % 5 == 0:
            messagebox.showinfo('入力通知','1分以内に被験者の疲労度を入力してください')
            #TODO:入力のバリデーションしてないから余裕あればやる
            fatigue = input("被験者の疲労度を入力してください(終了するにはexitと打ってください)\n")

            if fatigue == 'exit':
                print("終了します")
                exit()
            file_path = get_file_path(now_time)
            
            check_exist_and_may_create(file_path)
            
            with open(file_path, 'w') as file:
                file.write(fatigue)
            
            time.sleep(60)

def get_file_path(pass_time):
    year = pass_time.year
    month = str(pass_time.month).zfill(2)
    day = str(pass_time.day).zfill(2)
    hour = str(pass_time.hour).zfill(2)
    minute = str(pass_time.minute).zfill(2)
    
    return f'./fatigue_data/{year}/{month}/{day}/{hour}/{minute}.txt'

if __name__ == '__main__':
    main()