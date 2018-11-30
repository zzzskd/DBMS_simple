import re
import json
import traceback
import os
from static_string import StaticString
from settings import Settings

def check_permission_arr(permission_arr, dbms_settings, static_string):
    ''' 检查 check_perssion_arr '''
    permissions = ['insert', 'select', 'update', 'delete']
    if len(permission_arr) == 1 and permission_arr[0] == '*':
        return True
    for permission in permission_arr:
        if permission not in permissions:
            print("Grant: " + static_string.COMMAND_ERROR)
            return False
        else:
            continue
    return True

def check_database_arr(database_arr, dbms_settings, static_string):
    ''' 检查 databases 是否存在 '''
    for database in database_arr:
        if database not in dbms_settings.dictionary:
            print("Grant: " + static_string.COMMAND_ERROR)
            return False
        else:
            continue
    return True

def check_user_arr(user_arr, dbms_settings, static_string):
    ''' 检查 users 是否存在 '''
    for user in user_arr:
        if user not in dbms_settings.users:
            print("Grant: " + static_string.COMMAND_ERROR)
            return False
        else:
            continue
    return True

def hanle_permission_arr(permission_arr):
    ''' 将其转换为 arr["insert"] = 1 格式 '''
    permission_dictionary = {"select":0,"insert":0,"update":0,"delete":0}
    if len(permission_arr) == 1 and permission_arr[0] == '*':
        permission_dictionary = {"select":1,"insert":1,"update":1,"delete":1}
        return permission_dictionary
    for permission in permission_arr:
        permission_dictionary[permission] = 1
    return permission_dictionary

def handle_grant_sql(sql, sql_arr, dbms_settings, static_string):
    ''' 分析 grant 语法'''
    pattern = 'grant (.{1,}) on (.{1,}) to (.{1,})'
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
    
    # 保存，写入文件
    try:
        for database in database_arr:
            for user in user_arr:
                new_permssion_info = {user: permission_dictionary}
                dbms_settings.dictionary[database]['permissions'].update(new_permssion_info)
        with open(static_string.PATH_DICTIONARY, 'w') as f:
            json.dump(dbms_settings.dictionary, f)
        print(static_string.GRANT_SUCCESS)
    except Exception:
        traceback.print_exc()
        print(static_string.INTTERNAL_ERROR)
                
    
    
