class Settings():
    '''存储运行时的所有状态的类'''
    
    def __init__(self):
        '''初始化参数'''
        
        # 数据字典
        self.users = None
        self.dictionary = None
        
        # 状态
        self.is_login = 0
        self.is_root = 0
        self.current_user = None
        self.current_database = None
        
        # 权限
        self.select_permission = 0
        self.insert_permission = 0
        self.delete_permission = 0
        self.update_permission = 0
