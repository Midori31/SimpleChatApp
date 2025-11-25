import socket
import threading
from config import SERVER_BIND_ADDR
from server.connection import handle_single_client

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

    print(f"聊天服务器启动成功，监听端口{SERVER_BIND_ADDR[1]}...")
    print("等待客户端连接...")

    # 循环接收客户端连接
    while True:
        client_socket, client_addr = server_socket.accept()
        print(f"新客户端连接：{client_addr}")
        # 为每个客户端创建独立线程处理
        client_thread = threading.Thread(
            target=handle_single_client,
            args=(client_socket, client_addr),
            daemon=True  # 主线程退出时子线程自动退出
        )
        client_thread.start()

if __name__ == "__main__":
    start_server()