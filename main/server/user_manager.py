import threading

# 全局在线用户字典（用户名: 客户端socket）
online_users = {}
# 线程锁（保证用户操作线程安全）
user_lock = threading.Lock()

def add_user(username, client_socket):
    """添加在线用户（线程安全）"""
    with user_lock:
        online_users[username] = client_socket

def remove_user(username):
    """移除在线用户（线程安全）"""
    with user_lock:
        if username in online_users:
            del online_users[username]

def is_username_exist(username):
    """检查用户名是否已存在（线程安全）"""
    with user_lock:
        return username in online_users

def get_online_list():
    """获取在线用户名列表（线程安全）"""
    with user_lock:
        return list(online_users.keys())

def get_user_socket(username):
    """获取指定用户的socket（线程安全）"""
    with user_lock:
        return online_users.get(username)

def get_online_list_str():
    """获取在线列表字符串（逗号分隔）"""
    online_list = get_online_list()
    return ",".join(online_list) if online_list else "无"