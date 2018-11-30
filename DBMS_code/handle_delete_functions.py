import os
import json
import re
import traceback
from static_string import StaticString
from settings import Settings

def get_nature_from_dictionary(table_name, dbms_settings):
    ''' 从字典中获取表的字段名和属性 '''
    nature_arr = []
    for item in dbms_settings.dictionary[dbms_settings.current_database]['tables'][table_name]['items']:
        nature_arr.append(item['nature'])
    return nature_arr
    
def delete_all(table_name, dbms_settings, static_string):
    ''' 删除表中所有数据 '''
    try:
        # 将文件删除，在创建一个空文件
        # 同步更改 dictionary 中的数据
        file_path = static_string.PATH_ROOT + './' + dbms_settings.current_database + './' + table_name + '.sql'
        f = open(file_path, 'w')
        f.close()
        affected_rows =  dbms_settings.dictionary[dbms_settings.current_database]['tables'][table_name]['size']
        dbms_settings.dictionary[dbms_settings.current_database]['tables'][table_name]['size'] = 0
        with open(static_string.PATH_DICTIONARY, 'w') as f:
            json.dump(dbms_settings.dictionary, f)
        print(static_string.DELETE_SUCCESS + str(affected_rows) + " rows deleted!")
    except Exception:
        traceback.print_exc()
        print(static_string.INTTERNAL_ERROR)

def delete_part(table_name, condition, dbms_settings, static_string):
    ''' 按照 where 子句删除 '''
    # 处理 colomn = value
    if re.match('[a-z0-9_]+ ?= ?[a-z0-9_\']+', condition):
        nature_value = condition.split('=')
        nature = nature_value[0].strip()
        value = nature_value[1].strip()
        # 检查 nature 是否存在
        nature_arr = get_nature_from_dictionary(table_name, dbms_settings)
        if nature not in nature_arr:
            print("Delete: " + static_string.ATTR_NOT_EXIST)
            return
        order = nature_arr.index(nature) # 第几列?
        nature_num = len(nature_arr)     # 一共有多少列
        affected_rows = 0                # 删除的行数
        try:
            # 遍历如果相同则删除
            data = []
            table_path = static_string.PATH_ROOT + './' + dbms_settings.current_database + './' + table_name + '.sql'
            with open(table_path,'r') as f:
                lines = f.readlines()
                for line in lines:
                    values = line.rstrip('\n').split('\t')
                    if len(values) > order:
                        if values[order] != value:
                            data.append(values)
                        else:
                            affected_rows += 1
                    else:
                        data.append(values)
            # 重新写入的数据
            values_str = ''
            for values in data:
                values_str += values[0]
                for i in range(1,len(values)):
                    values_str += '\t' + values[i]
                values_str += '\n'
            # 重新写入
            with open(table_path,'w') as f:
                f.write(values_str)
            # 修改字典的 size
            dbms_settings.dictionary[dbms_settings.current_database]['tables'][table_name]['size'] -= affected_rows
            with open(static_string.PATH_DICTIONARY, 'w') as f:
                json.dump(dbms_settings.dictionary, f)
            if affected_rows != 0:
                print(static_string.DELETE_SUCCESS + str(affected_rows) + " rows deleted!")
            else:
                print("0 rows deleted,The element to be deleted does not exist")
        except Exception:
            traceback.print_exc()
            print("Error")
    else:
        # 处理 > 和 < 情况
        return

def handle_delete_sql(sql, sql_arr, dbms_settings, static_string):
    ''' 分析 delete 语法 '''
    is_all = False
    table_name = ''
    condition = ''
    pattern_one = 'delete from ([a-z0-9_]+) where (.+)'
    pattern_two = 'delete from ([a-z0-9_]+)'
    if not re.match(pattern_one, sql):
        if not re.match(pattern_two, sql):
            print("Delete: " + static_string.COMMAND_ERROR)
            return
        else:
            is_all = True
            table_name =  re.match(pattern_two, sql).group(1)
    else:
        table_name = re.match(pattern_one, sql).group(1)
        condition = re.match(pattern_one, sql).group(2)
    # 判断表是否存在，view 未做处理...
    if table_name not in dbms_settings.dictionary[dbms_settings.current_database]['tables']:
        print("Delete: " + static_string.TABLE_NOT_EXIST)
        return
    # 删除全部数据
    if is_all:
        delete_all(table_name, dbms_settings, static_string)
    else:
        # where p = q
        delete_part(table_name, condition, dbms_settings, static_string)
        return
        
