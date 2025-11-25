import socket
import threading
import os
from config import SERVER_BIND_ADDR
from server.connection import handle_single_client

def get_local_ips():
    """获取本机所有可用IP地址"""
    ips = []
    try:
        # 获取主机名
        hostname = socket.gethostname()
        # 获取所有IP地址（包括IPv4和IPv6）
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)
        # 去重并筛选IPv4地址
        for info in addr_info:
            ip = info[4][0]
            if ip not in ips and not ip.startswith("127."):  # 排除本地回环地址
                ips.append(ip)
        # 如果没有外部IP，添加回环地址
        if not ips:
            ips.append("127.0.0.1")
    except Exception as e:
        print(f"获取本机IP失败：{e}")
        ips.append("127.0.0.1")
    return ips

def start_server():
    """启动聊天服务器（监听连接、分配线程）"""
    # 创建TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 允许端口复用（避免重启服务器时端口占用）
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定地址和端口
    server_socket.bind(SERVER_BIND_ADDR)
    # 开始监听（最大等待连接数10）
    server_socket.listen(10)

    # 获取本机IP并显示
    local_ips = get_local_ips()
    print("=" * 50)
    print(f"聊天服务器启动成功！")
    print(f"监听端口：{SERVER_BIND_ADDR[1]}")
    print(f"本机可用IP：")
    for ip in local_ips:
        print(f"  - {ip}")
    print(f"客户端连接格式：IP:{local_ips[0]}, 端口:{SERVER_BIND_ADDR[1]}")
    print("=" * 50)
    print("等待客户端连接...")

    # 循环接收客户端连接
    while True:
        client_socket, client_addr = server_socket.accept()
        print(f"\n新客户端连接：{client_addr}")
        # 为每个客户端创建独立线程处理
        client_thread = threading.Thread(
            target=handle_single_client,
            args=(client_socket, client_addr),
            daemon=True  # 主线程退出时子线程自动退出
        )
        client_thread.start()

if __name__ == "__main__":
    start_server()