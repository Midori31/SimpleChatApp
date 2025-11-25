"""用户管理模块：维护在线用户列表（线程安全）"""
import threading

online_users = {}
lock = threading.Lock()

def add_user(username, client_socket):
    """添加在线用户"""
    with lock:
        online_users[username] = client_socket

def remove_user(username):
    """移除在线用户"""
    with lock:
        if username in online_users:
            del online_users[username]

def get_user_socket(username):
    """根据用户名获取客户端socket"""
    with lock:
        return online_users.get(username)

def get_all_users():
    """获取所有在线用户名（返回字典，兼容旧代码）"""
    with lock:
        return online_users  # 返回完整字典：{username: socket}

def get_online_list():
    """获取在线用户名列表（仅返回用户名，用于显示）"""
    with lock:
        return list(online_users.keys())

def is_username_exist(username):
    """检查用户名是否已存在"""
    with lock:
        return username in online_users