import json
import os
from settings import Settings
from static_string import StaticString 
from handle import handle_sql

def init(dbms_settings, static_string):
    ''' 初始化，创建相应目录及文件，并将文件内容读取到程序中 '''
    try:
        if not os.path.exists(static_string.PATH_ROOT):
            os.mkdir(static_string.PATH_ROOT)
        if not os.path.exists(static_string.PATH_CONFIG):
            os.mkdir(static_string.PATH_CONFIG)
        if not os.path.exists(static_string.PATH_USERS):
            users = {"root":{"password":"root","type":1}}
            with open(static_string.PATH_USERS, 'w') as f:
                json.dump(users, f)
        if not os.path.exists(static_string.PATH_DICTIONARY):
            dictionary = {}
            with open(static_string.PATH_DICTIONARY, 'w') as f:
                json.dump(dictionary, f)
        
        # 将数据读取到程序中
        with open(static_string.PATH_USERS, 'r') as f:
            dbms_settings.users = json.load(f)
        with open(static_string.PATH_DICTIONARY, 'r') as f:
            dbms_settings.dictionary = json.load(f)
    except Exception:
        # traceback.print_exc()
        print(static_string.INIT_FAILED)

def run_dbms():
    
    # 初始化设置
    dbms_settings = Settings()
    static_string = StaticString()
    init(dbms_settings, static_string)
    print(static_string.WELCOME_INFO)
    
    # run dbms
    while True:
        # 未登录
        if not dbms_settings.is_login:
            print("sql@" + 'null', end = ">")
        else:
            print("sql@" + dbms_settings.current_user, end = ">")
        sql = input()
        handle_sql(sql, dbms_settings, static_string)
            
run_dbms()

