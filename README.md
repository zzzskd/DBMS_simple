## 简介
使用 pyhton 实现的功能简单的 DBMS 系统，主要功能如下：

- 初始化，产生默认 root 用户
- 用户登录功能(login)
- 使用数据库(use 命令)
- 创建用户、数据库、表(create 命令)
- 查询数据表中的数据(select 命令)，支持简单 where 子句、order by，不支持聚集函数等
- 向数据表中插入数据(insert 命令)，支持的数据类型有 int varchar double，支持简单的约束，不支持 where 子句
- 删除数据表中内容(delete 命令)，支持简单的 where 子句
- 更新数据表中的内容(update 命令)，支持简单的 where 子句
- 向用户授权功能(grant 命令)
- 收回权限功能(revoke 命令)
- help 命令

运行平台为：Windows，语言为 Python3，注意的是一定要有 F 盘，因为默认配置文件会建在 F 盘，您也可以修改 static_string.py 中 PATH_ROOT

## 缺陷

- 只能对数据库授权，而不能对数据表授权
- 一个表中只能支持一个约束条件
- 普通用户即使授予了对数据库的使用权限，也没法使用数据库(悲伤...)，这里稍微一改可以实现


## 整体思路

![流程图](https://github.com/zzzskd/pictureandor/blob/master/Untitled%20Diagram.png)

## 使用命令

### 登录 
login root root 

### use
use sdust

### create
create user zzz passwd 1
create database sdust
create table users(id int primary key, name varchar not null)
create view users_view as select * from users

### insert 
insert into users values(1, 'zzz')

### delete 
delete from users
delete from users where id = 1

### update 
update users set name = 'zzz'
update users set id = 3 where name = 'yes'

### select 
select * from users 
select id, name from users 
select * from users order by id
select id, name from users_view

### grant
grant insert, select on test to zzz
grant * on test, sdust to zzz
grant * on test, sdust to zzz, test

### revoke 
revoke insert, select on test from zzz
revoke * on test, sdust from zzz
revoke * on test, sdust from zzz, test

### help
help database
help table users
help view users_view

### 退出
exit

###  存储用户文件结构

./config/users.json:

{ "user_name": {"password": "user_password", "type": 1} }

格式化：
```json
{
    "user_name": {
        "password": "user_password",
        "type": 1
    }
}
```
### 存储数据文件结构
./config/dictionary.json: 

{"sdust": {"views": {"users_view": {"items": [{"nature": "id", "type": "int"}], "content": "select * from users"}}, "permissions": {"root": {"select": 1, "insert": 1, "update": 1, "delete": 1}}, "tables": {"users": {"size": 2, "items": [{"nature": "id", "limit": "primary key", "type": "int"}]}}}}


格式化：
```json
{
    "sdust": {
        "views": {
            "users_view": {
                "items": [
                    {
                        "nature": "id",
                        "type": "int"
                    }
                ],
                "content": "select * from users"
            }
        },
        "permissions": {
            "root": {
                "select": 1,
                "insert": 1,
                "update": 1,
                "delete": 1
            }
        },
        "tables": {
            "users": {
                "size": 2,
                "items": [
                    {
                        "nature": "id",
                        "limit": "primary key",
                        "type": "int"
                    }
                ]
            }
        }
    }
}
```
### 表的文件结构

./databasename/tablename.sql                                   # 本质是个 .txt 文件


> 具体实现解解释见代码注释

