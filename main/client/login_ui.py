import socket
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLineEdit,
                             QPushButton, QMessageBox)
from PyQt6.QtGui import QFont
from config import SERVER_IP, SERVER_PORT
from client.chat_ui import ChatWindow

class LoginWindow(QMainWindow):
    """登录窗口（独立UI+登录逻辑）"""
    def __init__(self):
        super().__init__()
        self.client_socket = None  # 登录成功后创建的socket
        self.init_ui()

    def init_ui(self):
        """初始化登录窗口UI"""
        # 窗口基础设置
        self.setWindowTitle("聊天客户端 - 登录")
        self.setFixedSize(400, 200)
        self.setStyleSheet("background-color: #f5f5f5;")

        # 字体配置
        self.font = QFont("微软雅黑", 11)

        # 中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(50, 50, 50, 50)

        # 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setFont(self.font)
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 8px;
        """)
        self.username_input.returnPressed.connect(self.do_login)  # 回车登录

        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setFont(self.font)
        self.login_btn.setStyleSheet("""
            background-color: #4285f4;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
        """)
        self.login_btn.clicked.connect(self.do_login)  # 点击登录

        # 添加组件到布局
        main_layout.addWidget(self.username_input)
        main_layout.addWidget(self.login_btn)

    def do_login(self):
        """执行登录逻辑：连接服务器+发送用户名"""
        username = self.username_input.text().strip()
        # 验证用户名非空
        if not username:
            QMessageBox.warning(self, "警告", "用户名不能为空！")
            return

        # 连接服务器
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            # 发送用户名到服务器
            self.client_socket.sendall(username.encode("utf-8"))
        except Exception as e:
            QMessageBox.critical(self, "登录失败", f"连接服务器失败：{str(e)}")
            return

        # 登录成功：打开聊天窗口，隐藏登录窗口
        self.chat_window = ChatWindow(username, self.client_socket)
        self.chat_window.show()
        self.hide()

    def closeEvent(self, event):
        """关闭登录窗口时关闭socket（如果已创建）"""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        event.accept()