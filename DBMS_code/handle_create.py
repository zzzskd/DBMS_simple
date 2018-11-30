import re
import json
import traceback
import os
from static_string import StaticString
from settings import Settings
from handle_select_functions import handle_select_sql

def get_table_name(sql):
    ''' 获取将要创建的表名 '''
    table_name = re.search('create table (.+)\(', sql).group(1).strip()
    return table_name
    
def get_view_name(sql):
    ''' 获取将要创建的视图名 '''
    view_name = re.search('create view (.+) as', sql).group(1).strip()
    return view_name

def handle_create_error(sql, sql_arr, dbms_settings, static_string):
    ''' create 命令时出现错误 '''
    print("Create：" + static_string.COMMAND_ERROR)
    
def handle_create_database(sql, sql_arr, dbms_settings, static_string):
    ''' 创建数据库 '''
    # 数据库命名规范
    if not re.match('[a-z_][a-z0-9_]{0,99}$', sql_arr[2]):
        handle_create_erro(sql_arr, dbms_settings, static_string)
        return
    # 检查权限
    if not dbms_settings.is_root:
        print(static_string.ACCESS_DENIE)
        return
    # 是否存在
    if sql_arr[2] in dbms_settings.dictionary:
        print(static_string.DATABASE_EXIST)
        return
    # 创建数据库：追加写入文件，创建相应文件夹，并更新当前字典
    try:
        new_db_info = {sql_arr[2] : {"views":{}, "permissions":{dbms_settings.current_user : {"select":1,"insert":1,"update":1,"delete":1}},"tables":{}}}
        # print(new_db_info)
        # print(dbms_settings.dictionary)
        dbms_settings.dictionary.update(new_db_info) # 追加到字典中
        # print(dbms_settings.dictionary)
        with open(static_string.PATH_DICTIONARY, 'w') as f:
            json.dump(dbms_settings.dictionary, f)
        new_path = static_string.PATH_ROOT + sql_arr[2] 
        if not os.path.exists(new_path):
            os.mkdir(new_path) # 创建目录
        print(static_string.CREATE_DATABASE_SUCCESS)
    except Exception:
        traceback.print_exc()
        print(static_string.INTTERNAL_ERROR)
    
def handle_create_table(sql, sql_arr, dbms_settings, static_string):
    ''' 创建数据表 '''
    # 判断是否选择了数据库
    if not dbms_settings.current_database:
        print("Create table: " + static_string.NO_DATABASE_SELECT)
        return
    # 格式判断
    pattern = (
        'create table [a-z_][a-z0-9_]{0,99} ?\( ?( ?[a-z_][a-z0-9_]{0,99}' +
        ' (( ?int ?)|( ?double ?)|( ?varchar ?))(( ?primary key ?)|' +
        '( ?not null ?)|( unique ?))?)( ?, ?[a-z_][a-z0-9_]{0,99} ' + 
        '(( ?int ?)|( ?double ?)|( ?varchar ?))(( ?primary key ?)|' +
        '( ?not null ?)|( unique ?))?){0,} ?\)$'
        )
    if not re.match(pattern, sql):
        print("Create table: " + static_string.COMMAND_ERROR)
        return
    # 权限判断
    if not dbms_settings.is_root:
        print("Create table: " + static_string.ACCESS_DENIED)
        return
    # 是否存在
    if get_table_name(sql) in dbms_settings.dictionary[dbms_settings.current_database]['tables']:
        print("Create table: " + static_string.TABLE_EXIST)
        return
    # 创建
    try:
        handled_sql = re.search('\((.+)\)', sql).group(1)
        table_nature_arr = handled_sql.split(',')
        items = []
        table_name = get_table_name(sql)
        for table_nature in table_nature_arr:
            nature_detail_arr = table_nature.strip().split(' ')
            # print(nature_detail_arr)
            # 如果大于 2 则说明有约束关系
            if len(nature_detail_arr) > 2:
                # 约束关系最多有两个单词(not null 或者 primary key)
                limit = nature_detail_arr[2] if len(nature_detail_arr) < 4 else nature_detail_arr[2] + ' ' + nature_detail_arr[3]
                nature_detail = {"nature": nature_detail_arr[0], "limit": limit, "type": nature_detail_arr[1]}
            else:
                nature_detail = {"nature": nature_detail_arr[0], "type": nature_detail_arr[1]}
            items.append(nature_detail)
        new_table_info = {table_name:{"size":0, "items":items}}
        dbms_settings.dictionary[dbms_settings.current_database]['tables'].update(new_table_info)
        with open(static_string.PATH_DICTIONARY, 'w') as f:
            json.dump(dbms_settings.dictionary, f)
        # 创建文件
        file_path = static_string.PATH_ROOT + './' + dbms_settings.current_database + './' + table_name + '.sql'
        if not os.path.exists(file_path):
            f = open(file_path, 'w')
            f.close()
        print(static_string.CREATE_TABLE_SUCCESS)
    except Exception:
        traceback.print_exc()
        print(static_string.INTTERNAL_ERROR)
    
def handle_create_index(sql, sql_arr, dbms_settings, static_string):
    ''' 创建数据索引 '''
    # 未完成


def handle_create_view(sql, sql_arr, dbms_settings, static_string):
    ''' 创建视图 '''
     # 判断是否选择了数据库
    if not dbms_settings.current_database:
        print("Create view: " + static_string.NO_DATABASE_SELECT)
        return
    # 格式判断
    pattern = ('create view ([a-z_][a-z0-9_]{0,99}) as (.+)')
    if not re.match(pattern, sql):
        print("Create view: " + static_string.COMMAND_ERROR)
        return
    # select 语句校验，获取数据
    select_sql = re.match(pattern, sql).group(2)
    pattern = 'select (.{1,}) from ([a-z0-9_]+)$'
    if not re.match(pattern, select_sql):
        print("Create view: " + static_string.COMMAND_ERROR)
        return
    # 权限判断
    if not dbms_settings.is_root:
        print("Create view: " + static_string.ACCESS_DENIED)
        return
    # 是否存在
    if get_view_name(sql) in dbms_settings.dictionary[dbms_settings.current_database]['views']:
        print("Create table: " + static_string.VIEW_EXSIT)
        return
    # 分析 select 语句 并找出要插入 view 中的数据
    result = handle_select_sql(select_sql, dbms_settings, static_string)
    if not result:
        print("Create view failed!")
        return
    (nature_arr, order_arr, type_arr, data) = result
    # 创建 view
    items = []
    content = select_sql
    view_name = get_view_name(sql)
    for i in range(len(nature_arr)):
        item = {"nature": nature_arr[i], "type": type_arr[order_arr[i]]}
        items.append(item)
    new_view_info = {view_name: {"items": items, "content": content}}
    # 写入dictionary
    try:
        dbms_settings.dictionary[dbms_settings.current_database]['views'].update(new_view_info)
        with open(static_string.PATH_DICTIONARY, 'w') as f:
            json.dump(dbms_settings.dictionary, f)
        print(static_string.CREATE_VIEW_SUCCESS)
        
    except Exception:
        traceback.print_exc()
        print(static_string.INTTERNAL_ERROR)
    
def handle_create_user(sql, sql_arr, dbms_settings, static_string):
    ''' 创建用户 '''
    # 格式判断
    if not re.match('create user [a-z_][a-z0-9_]{0,99} (\w){0,99}( [0|1])?$', sql):
        print("Create user: " + static_string.COMMAND_ERROR)
        return
    # 权限判断
    if not dbms_settings.is_root:
        print("Create user: " + static_string.ACCESS_DENIED)
        return
    # 是否存在
    if sql_arr[2] in dbms_settings.users:
        print("Create user: " + static_string.USER_EXIST)
        return
    # 写入文件并更新
    try:
        new_user_type = 0 if len(sql_arr) == 4 else int(sql_arr[4])
        new_user_info = {sql_arr[2]:{"password":sql_arr[3], "type":new_user_type}}
        dbms_settings.users.update(new_user_info)
        with open(static_string.PATH_USERS, 'w') as f:
            json.dump(dbms_settings.users, f)
        print(static_string.CREATE_USER_SUCCESS)
    except Exception:
        traceback.print_exc()
        print(static_string.INTTERNAL_ERROR)
        
