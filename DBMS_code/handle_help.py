import re
import json
import traceback
import os
from static_string import StaticString
from settings import Settings

def handle_help_error(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 help 命令出现错误 '''
    print("Help：" + static_string.COMMAND_ERROR)
    
def handle_help_database(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 help database'''
    # 检查语法
    if len(sql_arr) != 2 or sql_arr[1] != "database":
        print("Help：" + static_string.COMMAND_ERROR)
        return
    # 检查是否选择数据库
    if not dbms_settings.current_database:
        print("Help：" + static_string.NO_DATABASE_SELECT)
        return
    # 检查权限
    if not dbms_settings.is_root:
        print("Help：" + static_string.ACCESS_DENIED)
        return
    # 输出 views
    views = dbms_settings.dictionary[dbms_settings.current_database]['views']
    print("All Views: " + str(len(views)))
    for view_name in views:
        print("    view name: " + view_name)
    # 输出 tables
    tables = dbms_settings.dictionary[dbms_settings.current_database]['tables']
    print("All Tables: " + str(len(tables)))
    for table_name in tables:
        print("    table name: " + table_name)
    # 输出 indexs， 未完成
    
def handle_help_table(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 help table 命令 '''
    # 检查语法
    if len(sql_arr) != 3:
        print("Help：" + static_string.COMMAND_ERROR)
        return
    # 检查是否选择数据库
    if not dbms_settings.current_database:
        print("Help：" + static_string.NO_DATABASE_SELECT)
        return
    # 检查是否存在
    if sql_arr[2] not in dbms_settings.dictionary[dbms_settings.current_database]['tables']:
        print("Help：" + static_string.TABLE_NOT_EXIST)
        return
    # 检查权限
    if not dbms_settings.is_root:
        print("Help：" + static_string.ACCESS_DENIED)
        return
    # 输出表结构
    table_items = dbms_settings.dictionary[dbms_settings.current_database]['tables'][sql_arr[2]]['items']
    print("Table :" + sql_arr[2])
    print("nature\ttype\tlimit")
    for table_item in table_items:
        out = table_item['nature'] + '\t' + table_item['type']
        if 'limit' in table_item:
            out += '\t' + table_item['limit']
        print(out)
    
def handle_help_index(sql, sql_arr, dbms_settings, static_string):
    ''' 未完成 :) '''
    
def handle_help_view(sql, sql_arr, dbms_settings, static_string):
    ''' 处理 help view 命令 '''
     # 检查语法
    if len(sql_arr) != 3:
        print("Help：" + static_string.COMMAND_ERROR)
        return
    # 检查是否选择数据库
    if not dbms_settings.current_database:
        print("Help：" + static_string.NO_DATABASE_SELECT)
        return
    # 检查是否存在
    if sql_arr[2] not in dbms_settings.dictionary[dbms_settings.current_database]['views']:
        print("Help：" + static_string.VIEW_NOT_EXSIT)
        return
    # 检查权限
    if not dbms_settings.is_root:
        print("Help：" + static_string.ACCESS_DENIED)
        return
    # 输出视图
    view_items = dbms_settings.dictionary[dbms_settings.current_database]['views'][sql_arr[2]]['items']
    print("View :" + sql_arr[2])
    print("nature\ttype")
    for view_item in view_items:
        out = view_item['nature'] + '\t' + view_item['type']
        print(out)
    content = dbms_settings.dictionary[dbms_settings.current_database]['views'][sql_arr[2]]['content']
    print("content: " + content)
