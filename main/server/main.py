import socket
import threading
from config import SERVER_BIND_ADDR, SERVER_PORT  # 适配你的配置项

def get_local_ip():
    """自动获取本机局域网IP（优先返回非127.0.0.1的IP）"""
    try:
        # 创建临时UDP socket，不实际连接
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # 连接公网服务器获取出口IP
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"  # 异常时返回本地回环IP

def main():
    """服务器主函数（适配JSON配置+自动显示IP）"""
    local_ip = get_local_ip()
    
    # 创建TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 端口复用（避免重启时端口占用）
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定地址（使用 config.py 中的 SERVER_BIND_ADDR = ("0.0.0.0", 9000)）
    server_socket.bind(SERVER_BIND_ADDR)
    server_socket.listen(5)  # 最大连接数5
    
    # 启动成功提示（显示关键信息）
    print("=" * 60)
    print(f"📡 服务器已启动成功！")
    print(f"🔌 绑定地址：{SERVER_BIND_ADDR}（监听所有网卡）")
    print(f"🌐 本机局域网IP：{local_ip}:{SERVER_PORT}（局域网客户端连接）")
    print(f"💻 本地测试IP：127.0.0.1:{SERVER_PORT}（本机客户端连接）")
    print(f"⚠️  按 Ctrl+C 关闭服务器")
    print("=" * 60)
    print("等待客户端连接...")

    try:
        while True:
            # 接受客户端连接
            client_socket, client_address = server_socket.accept()
            # 为每个客户端创建独立线程
            client_thread = threading.Thread(
                target=handle_single_client,
                args=(client_socket, client_address),
                daemon=True  # 主线程退出时子线程自动退出
            )
            client_thread.start()
            print(f"\n✅ 新连接：{client_address}")
            print(f"📊 当前在线：{threading.active_count() - 1} 人")
    except KeyboardInterrupt:
        print("\n\n⚠️  正在关闭服务器...")
    finally:
        server_socket.close()
        print("✅ 服务器已完全关闭")

if __name__ == "__main__":
    # 延迟导入，避免循环依赖
    from server.connection import handle_single_client
    main()