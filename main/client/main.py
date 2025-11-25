import sys
from PyQt6.QtWidgets import QApplication
from client.login_ui import LoginWindow

def main():
    """客户端入口函数：启动QT应用+显示登录窗口"""
    # 创建QT应用实例
    app = QApplication(sys.argv)
    # 创建并显示登录窗口
    login_window = LoginWindow()
    login_window.show()
    # 运行应用事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()