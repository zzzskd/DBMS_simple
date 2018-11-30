import re
import json
import traceback
import os
from static_string import StaticString
from settings import Settings
from handle_grant_functions import check_permission_arr, check_database_arr, check_user_arr, hanle_permission_arr
def handle_revoke_sql(sql, sql_arr, dbms_settings, static_string):
    ''' 分析 revoke 语法 '''
    pattern = 'revoke (.{1,}) on (.{1,}) from (.{1,})'
    if not re.match(pattern, sql):
        print("Grant: " + static_string.COMMAND_ERROR)
        return
    permissions = re.sub(' ', '', re.match(pattern, sql).group(1))
    databases = re.sub(' ', '', re.match(pattern, sql).group(2))
    users = re.sub(' ', '', re.match(pattern, sql).group(3))
    permission_arr = permissions.split(',')
    database_arr = databases.split(',')
    user_arr = users.split(',')
    if not check_permission_arr(permission_arr, dbms_settings, static_string):
        return
    if not check_database_arr(database_arr, dbms_settings, static_string):
        return
    if not check_user_arr(user_arr, dbms_settings, static_string):
        return
    # 将其转换为 {"insert":1} 格式
    permission_dictionary = hanle_permission_arr(permission_arr)
    # 查看用户是否在权限表中
    for user in user_arr:
        for database in database_arr:
            if user not in dbms_settings.dictionary[database]['permissions']:
                print("Revoke: " + static_string.REVOKE_USER_NOT_EXSIT)
                return
            else:
                continue
    # 查看用户是否拥有要删除的权限
    for user in user_arr:
        select = dbms_settings.dictionary[database]['permissions'][user]['select'] - permission_dictionary['select']
        delete = dbms_settings.dictionary[database]['permissions'][user]['delete'] - permission_dictionary['delete']
        update = dbms_settings.dictionary[database]['permissions'][user]['update'] - permission_dictionary['update']
        insert = dbms_settings.dictionary[database]['permissions'][user]['insert'] - permission_dictionary['insert']
        if select < 0 or delete < 0 or update < 0 or insert < 0:
            print("Revoke: " + static_string.REVOKE_USER_PERMISSION_NOT_EXSIT)
            return

    # 保存，写入文件
    try:
        for database in database_arr:
            for user in user_arr:
                dbms_settings.dictionary[database]['permissions'][user]['select'] -= permission_dictionary['select']
                dbms_settings.dictionary[database]['permissions'][user]['delete'] -= permission_dictionary['delete']
                dbms_settings.dictionary[database]['permissions'][user]['update'] -= permission_dictionary['update']
                dbms_settings.dictionary[database]['permissions'][user]['insert'] -= permission_dictionary['insert']
        with open(static_string.PATH_DICTIONARY, 'w') as f:
            json.dump(dbms_settings.dictionary, f)
        print(static_string.GRANT_SUCCESS)
    except Exception:
        traceback.print_exc()
        print(static_string.INTTERNAL_ERROR)
