import re
import json
import traceback
import os
from static_string import StaticString
from settings import Settings

def check_is_int(value):
    ''' 检查是否为 int  '''
    if re.match('(\+|\-)?[0-9]+$', value) or value == '':
        #  value 可以== ''， 检查其是否有约束 not null
        return True
    else:
        return False
            
def check_is_double(value):
    ''' 检查是否为 double  '''
    if re.match('(\+|\-)?[0-9]+\.?[0-9]+$', value) or value == '':
        return True
    else:
        return False

def check_is_varchar(value):
    ''' 检查是否为 varchar  '''
    if re.match("'(.+)?'$", value):
        return True
    else:
        return False

def check_is_char(value):
    ''' 检查是否为 char  '''
    if re.match("'(.+)?'$", value) and len(value) <= 3:
        return True
    else:
        return False
    
def no_type_match(value):
    ''' 未找到数据类型 :)   '''
    print("Error: there exits bug")
    
def update_table_size(table_name, dbms_settings, static_string):
    ''' 更新程序中的 dictionary 及 dictionary.json 文件中的 size  '''
    dbms_settings.dictionary[dbms_settings.current_database]['tables'][table_name]['size'] += 1
    # 写入文件
    try:
        with open(static_string.PATH_DICTIONARY, 'w') as f:
            json.dump(dbms_settings.dictionary, f)
    except Exception:
        traceback.print_exc()
        print(static_string.INTTERNAL_ERROR)
         
def load_data_from_file(table_name, dbms_settings, static_string):
    ''' 从文件中读取数据 '''
    table_path = static_string.PATH_ROOT + './' + dbms_settings.current_database + './' + table_name + '.sql'
    try:
        data = []
        with open(table_path,'r') as f:
            lines = f.readlines()
            for line in lines:
                values = line.split('\t')
                data.append(values)
        return data
    except Exception:
        traceback.print_exc()
        print("Error")

def insert_values_into_table(values, table_name, dbms_settings, static_string):
    ''' 将数据写入文件 '''
    values_str = values[0]
    table_path = static_string.PATH_ROOT + './' + dbms_settings.current_database + './' + table_name + '.sql'
    for i in range(1,len(values)):
        values_str += '\t' + values[i]
    values_str += '\n'
    try:
        # print(values_str)
        with open(table_path,'a') as f:
            f.write(values_str)
        # 输出提示信息，有仅有一行受影响 : ) 
        print("Insert: " + static_string.INSERT_DATA_SUCCESS + table_name + "!" + " : " + "1 rows affected")
        # 将 size + 1 同步到 dictionary 中
        update_table_size(table_name, dbms_settings, static_string)
    except Exception:
        traceback.print_exc()
        print("Error")
        

def check_data_type(values, table_name, dbms_settings, static_string):
    ''' 检查数据类型是否合法 '''
    table_items = dbms_settings.dictionary[dbms_settings.current_database]['tables'][table_name]['items']
    # 检查列数
    if len(table_items) != len(values):
        print("Insert: "+ static_string.DATATYPE_NOT_MATCH)
        return False
    # 检查格式
    for i in range(len(table_items)):
        is_legal = False
        commands = {
            'int'    : check_is_int,
            'double' : check_is_double,
            'varchar': check_is_varchar,
            'char'   : check_is_char
            }
        command = commands.get(table_items[i]['type'], no_type_match)
        is_legal = command(values[i])
        if not is_legal:
            print("Insert: "+ static_string.DATATYPE_NOT_MATCH)
            return is_legal
    return True
        
    
def check_primary_key(values, table_name, dbms_settings, static_string):
    ''' 检查主键约束 '''
    table_items = dbms_settings.dictionary[dbms_settings.current_database]['tables'][table_name]['items']
    # 最多只有一个 primary key，遍历 items 如果存在，则判断该值是否为空或是否重复
    # 找出第几列是主键，并判断对应 insert 输入是否正确
    for i in range(len(table_items)):
        if "limit" in table_items[i] and table_items[i]['limit'] == "primary key":
            # 检查输入的数据是否为空
            if values[i] == '' or values[i] == "''":
                print("Insert" + static_string.PRIMARY_KEY_LIMIT_NOT_MATCH)
                return False
            # 打开数据表文件，检查是否有重复
            data = load_data_from_file(table_name, dbms_settings, static_string)
            # 检查是否有重复
            for values_in_file in data:
                if values[i] == values_in_file[i]:
                    print("Insert" + static_string.PRIMARY_KEY_LIMIT_NOT_MATCH)
                    return False
                else:
                    continue
            break
        else:
            continue
    return True
    
def check_not_null(values, table_name, dbms_settings, static_string):
    ''' 检查非空约束 '''
    table_items = dbms_settings.dictionary[dbms_settings.current_database]['tables'][table_name]['items']
    for i in range(len(table_items)):
        if "limit" in table_items[i] and table_items[i]['limit'] == "not null":
            # 检查输入的数据是否为空
            if values[i] == '' or values[i] == "''":
                print("Insert" + static_string.NOT_NULL_LIMIT_NOT_MATCH)
                return False
            # break 可能有多个 not null 约束
        else:
            continue
    return True

def check_unique(values, table_name, dbms_settings, static_string):
    ''' 检查唯一约束 '''
    # 与检查 primary key 相同
    table_items = dbms_settings.dictionary[dbms_settings.current_database]['tables'][table_name]['items']
    # 最多只有一个 primary key，遍历 items 如果存在，则判断该值是否为空或是否重复
    # 找出第几列是主键，并判断对应 insert 输入是否正确
    for i in range(len(table_items)):
        if "limit" in table_items[i] and table_items[i]['limit'] == "unique":
            # 检查输入的数据是否为空
            if values[i] == '' or values[i] == "''":
                print("Insert" + static_string.UNIQUE_LIMIT_NOT_MATCH)
                return False
            # 打开数据表文件，检查是否有重复
            data = load_data_from_file(table_name, dbms_settings, static_string)
            # 检查是否有重复
            for values_in_file in data:
                if values[i] == values_in_file[i]:
                    print("Insert" + static_string.UNIQUE_LIMIT_NOT_MATCH)
                    return False
                else:
                    continue
            break
        else:
            continue
    return True
    
def check_data_is_legal(values, table_name, dbms_settings, static_string):
    ''' 检查数据合法性 '''
    # 检查数据类型是否合法
    if not check_data_type(values, table_name, dbms_settings, static_string):
        return False
    # 检查主键约束
    if not check_primary_key(values, table_name, dbms_settings, static_string):
        return False
    # 检查非空约束
    if not check_not_null(values, table_name, dbms_settings, static_string):
        return False
    # 检查唯一约束
    if not check_unique(values, table_name, dbms_settings, static_string):
        return False
    return True
