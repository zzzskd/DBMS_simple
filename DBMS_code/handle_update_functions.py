import re
import json
import traceback
import os
from static_string import StaticString
from settings import Settings
from handle_insert_functions import check_is_int, check_is_double,check_is_varchar, check_is_char, no_type_match

def type_is_legal(nature_type, value):
    ''' 判断数据类型是否合法 '''
    commands = {
            'int'    : check_is_int,
            'double' : check_is_double,
            'varchar': check_is_varchar,
            'char'   : check_is_char
            }
    command = commands.get(nature_type, no_type_match)
    return command(value)

def get_nature_and_type_from_dictionary(table_name, dbms_settings):
    ''' 从字典中获取表的字段名和属性 '''
    nature_arr = []
    type_arr = []
    for item in dbms_settings.dictionary[dbms_settings.current_database]['tables'][table_name]['items']:
        nature_arr.append(item['nature'])
        type_arr.append(item['type'])
    return (nature_arr, type_arr)

def update_all(table_name, natures, dbms_settings, static_string):
    ''' 更新全部数据 '''
    # 检查 nature 是否存在，只完成修改一个属性 -_-
    nature_value = natures.split('=')
    nature = nature_value[0].strip()
    value = nature_value[1].strip()
    # 检查 nature 是否存在，存在的话属性是否匹配
    result = get_nature_and_type_from_dictionary(table_name, dbms_settings)
    if result:
        (nature_arr, type_arr) = result
    else:
        return
    if nature not in nature_arr:
        print("Update: " + static_string.ATTR_NOT_EXIST)
        return 
    order = nature_arr.index(nature)
    nature_type = type_arr[order]
    if not type_is_legal(nature_type, value):
        print("Update: " + static_string.DATATYPE_NOT_MATCH)
        return 
    # 检验约束条件
    # 未实现 -_-
    # 替换后写入文件，设计差没有代码复用，insert、delete、update都有写文件操作，
    # 应该把相关函数提取出来
    affected_rows = 0 # 删除的函数
    try:
        # 遍历替换列的值
        data = []
        table_path = static_string.PATH_ROOT + './' + dbms_settings.current_database + './' + table_name + '.sql'
        with open(table_path,'r') as f:
            lines = f.readlines()
            for line in lines:
                affected_rows += 1
                values = line.rstrip('\n').split('\t')
                if len(values) > order:
                    values[order] = value  # 替换
                    data.append(values)
                else:
                    # 插入空值
                    for i in range(order - len(values)):
                        values.append('')
                    values.append(value)
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
        if affected_rows != 0:
            print(static_string.UPDATE_SUCCESS + str(affected_rows) + " rows updated!")
        else:
            print("0 rows updated,The element to be deleted does not exist")
    except Exception:
            traceback.print_exc()
            print("Error")
    
def update_part(table_name, condition, natures, dbms_settings, static_string):
    ''' 更新部分数据，分析 where 字句 '''
    # 判断 set 部分 列是否存在 值得类型是否匹配
    nature_value = natures.split('=')
    nature = nature_value[0].strip()
    value = nature_value[1].strip()
    result = get_nature_and_type_from_dictionary(table_name, dbms_settings)
    if result:
        (nature_arr, type_arr) = result
    else:
        print("Update: " + static_string.ATTR_NOT_EXIST)
        return
    if nature not in nature_arr:
        print("Update: " + static_string.ATTR_NOT_EXIST)
        return 
    # 数据类型是否匹配
    order = nature_arr.index(nature)
    nature_type = type_arr[order]
    if not type_is_legal(nature_type, value):
        print("Update: " + static_string.DATATYPE_NOT_MATCH)
        return 
    # 处理 condition 部分
    # 处理 colomn = value
    if re.match('[a-z0-9_]+ ?= ?[a-z0-9_\']+', condition):
        condition_nature_value = condition.split('=')
        condition_nature = condition_nature_value[0].strip()           # 条件列
        condition_value = condition_nature_value[1].strip()            # 条件值
        # 检查 nature 是否存在
        if nature not in nature_arr:
            print("Update: " + static_string.TABLE_EXIST)
            return
        condition_order = nature_arr.index(condition_nature) # 第几列?
        affected_rows = 0                                    # 修改的行数
        try:
            # 遍历,替换符合conditon_value列的值
            data = []
            table_path = static_string.PATH_ROOT + './' + dbms_settings.current_database + './' + table_name + '.sql'
            with open(table_path,'r') as f:
                lines = f.readlines()
                for line in lines:
                    values = line.rstrip('\n').split('\t')
                    if len(values) > condition_order:
                        if values[condition_order] == condition_value:
                            affected_rows += 1
                            if len(values) > order:
                                values[order] = value  # 替换
                            else:
                                # 插入空值
                                for i in range(order - len(values)):
                                    values.append('')
                                values.append(value)
                        else:
                            pass
                    else:
                        pass
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
            if affected_rows != 0:
                print(static_string.UPDATE_SUCCESS + str(affected_rows) + " rows updated!")
            else:
                print("0 rows updated,The element to be updated does not exist")
        except Exception:
            traceback.print_exc()
            print("Error")
    else:
        # 处理 > 和 < 情况
        return
    

def handle_update_sql(sql, sql_arr, dbms_settings, static_string):
    ''' 分析 update 语法'''
    is_all = False
    table_name = ''
    condition = ''
    natures = ''
    pattern_one = 'update ([a-z0-9_]+) set (.+) where (.+)'
    pattern_two = 'update ([a-z0-9_]+) set (.+)'
    if not re.match(pattern_one, sql):
        if not re.match(pattern_two, sql):
            print("Update: " + static_string.COMMAND_ERROR)
            return
        else:
            is_all = True
            table_name =  re.match(pattern_two, sql).group(1)
            natures = re.match(pattern_two, sql).group(2)
    else:
        table_name = re.match(pattern_one, sql).group(1)
        natures = re.match(pattern_one, sql).group(2)
        condition = re.match(pattern_one, sql).group(3)
    # 判断表是否存在，view 未做处理...
    if table_name not in dbms_settings.dictionary[dbms_settings.current_database]['tables']:
        print("Update: " + static_string.TABLE_NOT_EXIST)
        return
    # 更新全部数据
    if is_all:
        update_all(table_name, natures, dbms_settings, static_string)
    else:
        # where p = q
        update_part(table_name, condition, natures, dbms_settings, static_string)
        return
    
