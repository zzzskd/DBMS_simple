import os
import json
import re
import sys
from static_string import StaticString
from settings import Settings
from handle_create import *
from handle_help import *
from handle_insert_functions import check_data_is_legal,insert_values_into_table
from handle_select_functions import handle_select_sql, print_select_result
from handle_grant_functions import handle_grant_sql
from handle_revoke_functions import handle_revoke_sql
from handle_delete_functions import handle_delete_sql
from handle_update_functions import handle_update_sql

def pre_handle_sql(sql):
    ''' sql 语句预处理 '''
    # 将多个空格、回车、制表符转换为一个空格，将字符转换为小写，去除行首行尾空格
    sql = re.sub('[\\n\\r\\t]+', ' ', sql).lower()
    # 将多个空格转换为一个空格
    sql = re.sub(' +', ' ', sql)
    sql = sql.strip()
    return sql
    
def handle_login(sql, sql_arr, dbms_settings, static_string):
    ''' 处理用户登录 '''
    if len(sql_arr) != 3:
        print("Login: " + static_string.COMMAND_ERROR)
    else:
        if dbms_settings.users:
            if sql_arr[1] not in dbms_settings.users:
                print(static_string.USER_NOT_EXIST)
            else:
                # 校验密码
                if sql_arr[2] == dbms_settings.users[sql_arr[1]]['password']:
                    dbms_settings.current_user = sql_arr[1]
                    dbms_settings.is_login = 1
                    dbms_settings.is_root = dbms_settings.users[sql_arr[1]]['type']
                    print(static_string.LOGIN_SUCCESS)
                else:
                    print(static_string.PASSWORD_WRONG)
        else:
            print(static_string.INTTERNAL_ERROR)

def handle_exit(sql, sql_arr, dbms_settings, static_string):
    ''' 处理用户登出 数据库 或 DBMS '''
    if len(sql_arr) == 1:
        if dbms_settings.current_database:
            dbms_settings.current_database = None
            dbms_settings.select_permission = 0
            dbms_settings.insert_permission = 0
            dbms_settings.delete_permission = 0
            dbms_settings.update_permission = 0
            print(static_string.EXIT_DATABASE)
        else:
            print(static_string.EXIT_SYSTEM)
            sys.exit()
    else:
        print("Exit: " + static_string.COMMAND_ERROR)
        
def handle_create(sql, sql_arr, dbms_settings, static_string):
    if len(sql_arr) < 3:
        print("Create: " + static_string.COMMAND_ERROR)
    else:
        commands = {
            'database' : handle_create_database,
            'table'    : handle_create_table,
            'index'    : handle_create_index,
            'view'     : handle_create_view,
            'user'     : handle_create_user
            }
        command = commands.get(sql_arr[1], handle_create_error)
        command(sql, sql_arr, dbms_settings, static_string)
    
def handle_select(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 select 命令 '''
    # 判断是否选择了数据库
    if not dbms_settings.current_database:
        print("Select: " + static_string.NO_DATABASE_SELECT)
        return
    # 权限判断
    if not dbms_settings.select_permission:
        print("Select: " + static_string.ACCESS_DENIED)
        return
    result = handle_select_sql(sql, dbms_settings, static_string)
    if result:
        (nature_arr, order_arr, type_arr, data) = result
        print_select_result(nature_arr, order_arr, data)

def handle_insert(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 insert 命令 '''
    # 判断是否选择了数据库
    if not dbms_settings.current_database:
        print("Insert: " + static_string.NO_DATABASE_SELECT)
        return
    # 权限判断
    if not dbms_settings.insert_permission:
        print("Insert: " + static_string.ACCESS_DENIED)
        return
    # 格式判断
    # insert into table_name values (,) 只处理了此情况
    # insert into table_name (colum_name, ...) values (, ) 这整情况未做处理   
    pattern_1 = 'insert into (.{1,}) values ?\((.{1,})\)$'
    pattern_2 = '(( ?.{1,} ?,?)+)'
    if re.match(pattern_1, sql):
        if re.match(pattern_2, re.search(pattern_1, sql).group(2)):
            table_name = re.search(pattern_1, sql).group(1).strip()
            temp_values = re.search(pattern_1, sql).group(2)
            values = temp_values.split(',')
            for i in range(len(values)):
                values[i] = values[i].strip()
            # 检查表是否存在
            if table_name in dbms_settings.dictionary[dbms_settings.current_database]['tables']:
                # 检查数据类型是否匹配
                if check_data_is_legal(values, table_name, dbms_settings, static_string):
                    # 将数据存入文件
                    insert_values_into_table(values, table_name, dbms_settings, static_string)
                else:
                    # 不合法的提示消息在 check_data_is_legal 函数中输出
                    return
            else:
                print("Insert: " + static_string.TABLE_NOT_EXIST)
                return
        else:
            print("Insert: " + static_string.COMMAND_ERROR)
            return
    else:
        print("Insert: " + static_string.COMMAND_ERROR)
        return
    
    
def handle_delete(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 delete 语句 '''
    # 判断是否选择了数据库
    if not dbms_settings.current_database:
        print("Delete: " + static_string.NO_DATABASE_SELECT)
        return
    # 权限判断
    if not dbms_settings.delete_permission:
        print("Delete: " + static_string.ACCESS_DENIED)
        return
    handle_delete_sql(sql, sql_arr, dbms_settings, static_string)
    
def handle_update(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 update 命令 '''
    # 判断是否选择了数据库
    if not dbms_settings.current_database:
        print("Update: " + static_string.NO_DATABASE_SELECT)
        return
    # 权限判断
    if not dbms_settings.update_permission:
        print("Update: " + static_string.ACCESS_DENIED)
        return
    handle_update_sql(sql, sql_arr, dbms_settings, static_string)
         
def handle_grant(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 grant 命令 '''
    # 权限判断
    if not dbms_settings.is_root:
        print("Grant: " + static_string.ACCESS_DENIED)
        return
    handle_grant_sql(sql, sql_arr, dbms_settings, static_string)
    
def handle_revoke(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 revoke 命令 '''
    # 权限判断
    if not dbms_settings.is_root:
        print("Revoke: " + static_string.ACCESS_DENIED)
        return
    handle_revoke_sql(sql, sql_arr, dbms_settings, static_string)

def handle_help(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 help 命令 '''
    if len(sql_arr) < 2:
        print("Help: " + static_string.COMMAND_ERROR)
        return
        
    commands = {
        'database' : handle_help_database,
        'table'    : handle_help_table,
        'index'    : handle_help_index,
        'view'     : handle_help_view
        }
    command = commands.get(sql_arr[1], handle_help_error)
    command(sql, sql_arr, dbms_settings, static_string)
        
        
def handle_use(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 use 数据库 '''
    # 语法判断
    if len(sql_arr) != 2:
        print("Use: " + static_string.COMMAND_ERROR)
        return
    # 是否存在
    if sql_arr[1] not in dbms_settings.dictionary:
        print("Use: " + static_string.DATABASE_NOT_EXIST)
        return
    # 权限检查
    if not dbms_settings.is_root:
        print("Use: " + static_string.ACCESS_DENIED)
        return
    # 修改运行设置 dbms_settings
    dbms_settings.current_database = sql_arr[1]
    if dbms_settings.current_user in dbms_settings.dictionary[dbms_settings.current_database]['permissions']:
        # print("hello there is use")
        dbms_settings.select_permission = dbms_settings.dictionary[dbms_settings.current_database]['permissions'][dbms_settings.current_user]['select']
        dbms_settings.insert_permission = dbms_settings.dictionary[dbms_settings.current_database]['permissions'][dbms_settings.current_user]['insert']
        dbms_settings.delete_permission = dbms_settings.dictionary[dbms_settings.current_database]['permissions'][dbms_settings.current_user]['update']
        dbms_settings.update_permission = dbms_settings.dictionary[dbms_settings.current_database]['permissions'][dbms_settings.current_user]['delete']
    print(static_string.USE_DATABASE_SUCCESS)
    
def handle_error(sql, sql_arr, dbms_settings, static_string):
    ''' sql 命令中第一个词出现错误 '''
    print(static_string.COMMAND_ERROR)

def handle_sql(sql, dbms_settings, static_string):
    ''' 检查sql语句，判断用户要进行的操作 '''
    sql = pre_handle_sql(sql)
    # 如果用户输入为空则无错误提示信息
    if sql == '':
        return
    # print(sql)
    sql_arr = sql.split(' ')
    # print(sql_arr)
    # print(len(sql_arr))
    if not dbms_settings.is_login:
        if sql_arr[0] == 'login':
            handle_login(sql, sql_arr, dbms_settings, static_string)
        else:
            print(static_string.LOGIN_FIRST)
    else:
        if sql_arr[0] == 'login':
            print(static_string.LOGIN_AGANIN)
        else:
            # 用字典模拟 Switch case
            commands = {
                'exit'   : handle_exit,
                'create' : handle_create,
                'select' : handle_select,
                'insert' : handle_insert,
                'delete' : handle_delete,
                'update' : handle_update,
                'grant'  : handle_grant,
                'revoke' : handle_revoke,
                'help'   : handle_help,
                'use'    : handle_use
                }
            command = commands.get(sql_arr[0],handle_error)
            command(sql, sql_arr, dbms_settings, static_string)

    
