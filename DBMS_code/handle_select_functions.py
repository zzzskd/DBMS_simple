import re
import json
import traceback
import os
from static_string import StaticString
from settings import Settings
from handle_insert_functions import load_data_from_file

def get_table_name_from_view(view):
    ''' 在字典中找出 view 中的表名 '''
    content = view['content']
    pattern = 'select (.+) from (.+)'
    table_name = re.match(pattern, content).group(2)
    return table_name

def get_nature_and_type_from_dictionary(string, name, dbms_settings, static_string):
    ''' 从字典中获取表的字段名和属性 '''
    nature_arr = []
    type_arr = []
    if string == 'view':
        for item in dbms_settings.dictionary[dbms_settings.current_database]['views'][name]['items']:
            nature_arr.append(item['nature'])
            type_arr.append(item['type'])
    else:
        for item in dbms_settings.dictionary[dbms_settings.current_database]['tables'][name]['items']:
            nature_arr.append(item['nature'])
            type_arr.append(item['type'])
    return (nature_arr, type_arr)

def print_select_result(nature_arr, order_arr, data):
    ''' 输出查询结果 '''
    total = len(data)
    for nature in nature_arr:
        print(nature, end = '\t') 
    print()
    for i in range(total):
        for j in order_arr:
            print(data[i][j].rstrip('\n'), end = '\t')
        print() 
    print("Total: " + str(total))
    
def single_table_query(table_name, natures, dbms_settings, static_string):
    ''' 单表查询 '''
    # 判断table or view 是否存在
    flag_one = table_name not in dbms_settings.dictionary[dbms_settings.current_database]['tables']
    flag_two = table_name  not in dbms_settings.dictionary[dbms_settings.current_database]['views']
    if flag_one and flag_two:
       print("Select: " + static_string.TABLE_NOT_EXIST)
       return None
    nature_arr_in_dictionary = []
    type_arr = []
    order_arr = [] # 每个 nature 对应在文件中的次序
    nature_arr = natures.split(',')
    # 去除空格
    for i in range(len(nature_arr)):
        nature_arr[i] = nature_arr[i].strip()

    # 如果 select table 
    if not flag_one:
        (nature_arr_in_dictionary, type_arr) = get_nature_and_type_from_dictionary('table', table_name, dbms_settings, static_string)
    else:
        view_name = table_name
        (nature_arr_in_dictionary, type_arr) = get_nature_and_type_from_dictionary('view', view_name, dbms_settings, static_string)
    # 判断属性列是否存在
    if len(nature_arr) == 1 and nature_arr[0] == '*':
        nature_arr = nature_arr_in_dictionary
        for i in range(len(nature_arr)):
            order_arr.append(i)
    else:
        for i in range(len(nature_arr)):
            if nature_arr[i] not in nature_arr_in_dictionary:
                print("Select: " + static_string.ATTR_NOT_EXIST)
                return None
            else:
                order_arr.append(nature_arr_in_dictionary.index(nature_arr[i]))
    # 如果是 view 的话 order_arr 和 type_arr 还需要更新
    if not flag_two:
        table_name = get_table_name_from_view(dbms_settings.dictionary[dbms_settings.current_database]['views'][table_name])
        (tmp_nature_arr_in_dictionary, type_arr) = get_nature_and_type_from_dictionary('table', table_name, dbms_settings, static_string)
        for i in range(len(nature_arr)):
            order_arr[i] = tmp_nature_arr_in_dictionary.index(nature_arr[i])
    # 读取数据
    data = load_data_from_file(table_name, dbms_settings, static_string)
    return (nature_arr, order_arr, type_arr, data)
        
    
def single_table_order_query(table_name, natures, order_nature, order, dbms_settings, static_string):
    ''' 单表排序查询 '''
    result = single_table_query(table_name, natures, dbms_settings, static_string)
    if not result:
        return None
    (nature_arr, order_arr, type_arr, data) = result
    # 判断 order_nature 是否存在
    flag = table_name not in dbms_settings.dictionary[dbms_settings.current_database]['tables']
    where = ''
    if not flag:
        where = 'table'
    else:
        where = 'view'
    (tmp_nature_arr_in_dictionary, tmp_type_arr) = get_nature_and_type_from_dictionary(where, table_name, dbms_settings, static_string)
    if order_nature not in tmp_nature_arr_in_dictionary:
        print("Select: " + static_string.ATTR_NOT_EXIST)
        return None
    # 排序后输出
    order_attribute_num = tmp_nature_arr_in_dictionary.index(order_nature)
    is_desc = True if order == 'desc' else False
    data = sorted(data, key=lambda x:x[order_attribute_num], reverse=is_desc)
    return (nature_arr, order_arr, type_arr, data)

def single_table_conditional_query(table_name, natures, condition, dbms_settings, static_string):
    ''' 单表条件查询 '''
    # 判断table or view 是否存在
    flag_one = table_name not in dbms_settings.dictionary[dbms_settings.current_database]['tables']
    flag_two = table_name  not in dbms_settings.dictionary[dbms_settings.current_database]['views']
    if flag_one and flag_two:
       print("Select: " + static_string.TABLE_NOT_EXIST)
       return None
    nature_arr_in_dictionary = []
    type_arr = []
    order_arr = [] # 每个 nature 对应在文件中的次序
    nature_arr = natures.split(',')
    # 去除空格
    for i in range(len(nature_arr)):
        nature_arr[i] = nature_arr[i].strip()

    # 如果 select table 
    if not flag_one:
        (nature_arr_in_dictionary, type_arr) = get_nature_and_type_from_dictionary('table', table_name, dbms_settings, static_string)
    else:
        view_name = table_name
        (nature_arr_in_dictionary, type_arr) = get_nature_and_type_from_dictionary('view', view_name, dbms_settings, static_string)
    # 判断属性列是否存在
    if len(nature_arr) == 1 and nature_arr[0] == '*':
        nature_arr = nature_arr_in_dictionary
        for i in range(len(nature_arr)):
            order_arr.append(i)
    else:
        for i in range(len(nature_arr)):
            if nature_arr[i] not in nature_arr_in_dictionary:
                print("Select: " + static_string.ATTR_NOT_EXIST)
                return None
            else:
                order_arr.append(nature_arr_in_dictionary.index(nature_arr[i]))
    # 如果是 view 的话 order_arr 和 type_arr 还需要更新
    if not flag_two:
        table_name = get_table_name_from_view(dbms_settings.dictionary[dbms_settings.current_database]['views'][table_name])
        (tmp_nature_arr_in_dictionary, type_arr) = get_nature_and_type_from_dictionary('table', table_name, dbms_settings, static_string)
        for i in range(len(nature_arr)):
            order_arr[i] = tmp_nature_arr_in_dictionary.index(nature_arr[i])
    # 读取数据
    data = load_data_from_file(table_name, dbms_settings, static_string)
    new_data = []
    # 分析 where 子句
    if re.match('[a-z0-9_]+ ?= ?[a-z0-9_\']+', condition):
        # 处理 =
        condition_nature_value = condition.split('=')
        condition_nature = condition_nature_value[0].strip()           # 条件列
        condition_value = condition_nature_value[1].strip()            # 条件值
        # 检查 nature 是否存在
        if condition_nature not in nature_arr:
            print("Select: Not Found nature")
            return
        condition_order = nature_arr.index(condition_nature)           # 第几列?
        # 检查 value 是否存在
        for values in data:
            if len(values) > condition_order and values[condition_order] == condition_value:
                new_data.append(values)
            else:
                continue
        return (nature_arr, order_arr, type_arr, new_data)
    elif re.match('[a-z0-9_]+ ?> ?[a-z0-9_\']+', condition):
        # 处理 >
        condition_nature_value = condition.split('>')
        condition_nature = condition_nature_value[0].strip()           # 条件列
        condition_value = condition_nature_value[1].strip()            # 条件值
        # 检查 nature 是否存在
        if condition_nature not in nature_arr:
            print("Select: Not Found nature")
            return None
        condition_order = nature_arr.index(condition_nature)           # 第几列? 
        condition_type = type_arr[condition_order]                     # 条件的属性是否可比？
        if condition_type not in ["int", "double"]:
            print("Select: Not Compareable")
            return None
        else:
            for values in data:
                if len(values) > condition_order and values[condition_order] > condition_value:
                    new_data.append(values)
                else:
                    continue
            return (nature_arr, order_arr, type_arr, new_data)
    elif re.match('[a-z0-9_]+ ?< ?[a-z0-9_\']+', condition):
        # 处理 < 
        condition_nature_value = condition.split('<')
        condition_nature = condition_nature_value[0].strip()           # 条件列
        condition_value = condition_nature_value[1].strip()            # 条件值
        # 检查 nature 是否存在
        if condition_nature not in nature_arr:
            print("Select: Not Found nature")
            return None
        condition_order = nature_arr.index(condition_nature)           # 第几列? 
        condition_type = type_arr[condition_order]                     # 条件的属性是否可比？
        if condition_type not in ["int", "double"]:
            print("Select: Not Compareable")
            return None
        else:
            for values in data:
                if len(values) > condition_order and values[condition_order] < condition_value:
                    new_data.append(values)
                else:
                    continue
            return (nature_arr, order_arr, type_arr, new_data)
    else:
        return None
    
def single_table_conditional_order_query(table_name, natures, condition, order_nature, order, dbms_settings, static_string):
    ''' 单表条件排序查询 '''
    
def multi_table_conditional_query(tables_name, natures, condition, dbms_settings, static_string):
    ''' 多表条件查询 连接查询 '''
    
def nested_query(table_name, natures, link_nature, sub_query, dbms_settings, static_string):
    ''' 嵌套查询 '''
    
def collection_query(table_name, natures, identify, table_name2, natures2, dbms_settings, static_string):
    ''' 集合查询 '''

def handle_select_sql(sql, dbms_settings, static_string):
    ''' 分析 select 语法'''
    # 单表查询
    pattern = 'select (.{1,}) from ([a-z0-9_]+)$'
    if re.match(pattern, sql):
        natures = re.search(pattern, sql).group(1).strip() # 这里用 match 也行 
        table_name = re.search(pattern, sql).group(2).strip()
        return single_table_query(table_name, natures, dbms_settings, static_string)
    # 单表排序查询
    pattern = 'select (.{1,}) from ([a-z0-9_]+) order by (.+)( desc|asc)?$'
    if re.match(pattern, sql):
        natures = re.search(pattern, sql).group(1).strip()
        table_name = re.search(pattern, sql).group(2).strip()
        order_nature = re.search(pattern, sql).group(3).strip()
        order = 'asc' # 默认为升序查询
        if re.search(pattern, sql).group(4):
            order = re.search(pattern, sql).group(4).strip()
        return single_table_order_query(table_name, natures, order_nature, order, dbms_settings, static_string)  

    # 单表条件查询
    pattern = 'select (.+) from ([a-z0-9_]+) where (.+)$'
    if re.match(pattern, sql):
        natures = re.search(pattern, sql).group(1).strip()
        table_name = re.search(pattern, sql).group(2).strip()
        condition = re.search(pattern, sql).group(3).strip() 
        return single_table_conditional_query(table_name, natures, condition, dbms_settings, static_string) 

    # 单表条件排序查询
    pattern = 'select (.+) from ([a-z0-9_]+) where (.+) order by (.+)( desc|asc)?$'
    if re.match(pattern, sql):
        natures = re.search(pattern, sql).group(1).strip()
        table_name = re.search(pattern, sql).group(2).strip()
        condition = re.search(pattern, sql).group(3).strip() 
        order_nature = re.search(pattern, sql).group(4).strip()
        order = 'asc' # 默认为升序查询
        if re.search(pattern, sql).group(5):
            order = re.search(pattern, sql).group(5).strip()
        return single_table_conditional_order_query(table_name, natures, condition, order_nature, order, dbms_settings, static_string)

    # 多表条件查询 连接查询
    pattern = 'select (.{1,}) from ([a-z0-9_]+,[a-z0-9_]+) where (.+)$'
    if re.match(pattern, sql):
        print(" --多表未实现-- ")
        return None
        natures = re.search(pattern, sql).group(1).strip()
        tables_name = re.search(pattern, sql).group(2).strip()
        condition = re.search(pattern, sql).group(3).strip() 
        return multi_table_conditional_query(tables_name, natures, condition, dbms_settings, static_string) 
         
    # 嵌套查询
    pattern = 'select (.{1,}?) from ([a-z0-9_]+) where ([a-z0-9_]+) in (.{1,})$'
    if re.match(pattern, sql):
        natures = re.search(pattern, sql).group(1).strip()
        table_name = re.search(pattern, sql).group(2).strip()
        link_nature = re.search(pattern, sql).group(3).strip() 
        sub_query = re.search(pattern, sql).group(4).strip()  # 子查询
        return nested_query(table_name, natures, link_nature, sub_query, dbms_settings, static_string)
    
        
    # 集合查询
    pattern = 'select (.{1,}) from ([a-z0-9_]+) (union|intersect|minus) select (.{1,}) from ([a-z0-9_]+)$'
    if re.match(pattern, sql):
        natures = re.search(pattern, sql).group(1).strip()
        table_name = re.search(pattern, sql).group(2).strip()
        identify = re.search(pattern, sql).group(3).strip() 
        natures2 = re.search(pattern, sql).group(4).strip()
        table_name2 = re.search(pattern, sql).group(5).strip() 
        return collection_query(table_name, natures, identify, table_name2, natures2, dbms_settings, static_string)
        
    # 没有成功匹配到 输出错误提示
    print("Select: " + static_string.COMMAND_ERROR)
    return None
    
