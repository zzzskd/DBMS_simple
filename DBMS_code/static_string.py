class StaticString():
    ''' 存储静态变量 '''
    
    def __init__(self):
        
        # 错误提示信息
        self.INIT_FAILED = "Init failed!"
        self.LOGIN_AGANIN = "Faield, you have logined, please logout first!"
        self.LOGIN_FIRST = "Failed, please login first!"
        self.USER_NOT_EXIST = "Failed, user not exsists!"
        self.COMMAND_ERROR = "Failed, command error!"
        self.PASSWORD_WRONG = "Failed, the password is wrong!"
        self.DATABASE_EXIST = "Failed, database has exsisted!"
        self.ACCESS_DENIED = "Failed, permission is not enough!"
        self.NO_DATABASE_SELECT = "Failed, no database select!"
        self.TABLE_EXIST = "Failed, table has exsisted!"
        self.DATABASE_NOT_EXIST = "Failed, database not exsists!"
        self.USER_EXIST = "Failed, user has exsit!"
        self.TABLE_NOT_EXIST = "Failed, table not exsits!"
        self.DATATYPE_NOT_MATCH = "Faield, data type not match!"
        self.ATTR_NOT_EXIST = "Failed, attribute not exists!"
        self.DATA_EXIST = "Failed, data already exists!"
        self.COLUMN_NOT_EXSIT = "Faild, column not exsits!"
        self.PRIMARY_KEY_LIMIT_NOT_MATCH = "Faild, not match primary key limit!"
        self.NOT_NULL_LIMIT_NOT_MATCH = "Failed, not match not null limit!"
        self.UNIQUE_LIMIT_NOT_MATCH = "Failed, not match unique limit!"
        self.VIEW_NOT_EXSIT =  "Failed, view not exsit!"
        self.VIEW_EXSIT = "Failed, view has exsit!"
        self.REVOKE_USER_NOT_EXSIT = "Failed, user not exsits in permission table!"
        self.REVOKE_USER_PERMISSION_NOT_EXSIT = "Failed, delete permissions that the user does not have!"
        self.INTTERNAL_ERROR = "Sorry, internal error!"
        
        # 正确提示信息
        self.LOGIN_SUCCESS = "ok, login is successful!"
        self.EXIT_DATABASE = "ok, exit database is successful!"
        self.EXIT_SYSTEM = "bye-bye!"
        self.CREATE_DATABASE_SUCCESS = "ok, a database is created successfully!"
        self.USE_DATABASE_SUCCESS = "ok, database is changed!"
        self.CREATE_TABLE_SUCCESS = "ok, a table is created successfully!"
        self.CREATE_USER_SUCCESS = "ok, an user is created successfully!"
        self.CREATE_VIEW_SUCCESS = "ok, an view is created successfully!"
        self.INSERT_DATA_SUCCESS = "ok, a record is insert into "
        self.DELETE_SUCCESS = "ok, delete successfully!"
        self.RECORD_DELETE_SUCCESS = "ok, a record is deleted successfully!"
        self.UPDATE_SUCCESS = "ok, update successfully!"
        self.GRANT_SUCCESS = "ok, grant successfully!"
        self.REVOKE_SUCCESS = "ok, revoke successfully!";
        
        # 存储路径
        self.PATH_ROOT = "F:/DBMS/"
        self.PATH_CONFIG = self.PATH_ROOT + "./config/"
        self.PATH_USERS = self.PATH_CONFIG + "./users.json"
        self.PATH_DICTIONARY = self.PATH_CONFIG + "./dictionary.json"
        
        # 程序开始提示信息
        self.WELCOME_INFO = '''
                                    欢迎使用 zzz 的DBMS !
                        ***********************************************
                        /                                             \\
                        \\               数据库课程设计                /
                        /                                             \\
                        \\                    DBMS                     /
                        /                                             \\
                        \\                                             /
                        /        zzz          学号：20160106xxxx        \\
                        \\                                             /
                        ***********************************************
                        
                        '''
                        
