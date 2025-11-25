import socket
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox)
from PyQt6.QtGui import QFont
from config import load_config, save_config, DEFAULT_CONFIG
from client.chat_ui import ChatWindow

class LoginWindow(QMainWindow):
    """登录窗口（独立UI+登录逻辑+IP/端口配置）"""
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.config = load_config()  # 加载配置
        self.init_ui()

    def init_ui(self):
        """初始化登录窗口UI（新增IP/端口输入框）"""
        # 窗口基础设置
        self.setWindowTitle("聊天客户端 - 登录")
        self.setFixedSize(450, 280)
        self.setStyleSheet("background-color: #f5f5f5;")

        # 字体配置
        self.font = QFont("微软雅黑", 11)
        self.label_font = QFont("微软雅黑", 10, QFont.Weight.Bold)

        # 中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(50, 40, 50, 30)

        # 1. 服务器配置区域（IP+端口）
        config_layout = QVBoxLayout()
        
        # IP输入行
        ip_layout = QHBoxLayout()
        ip_label = QLabel("服务器IP：")
        ip_label.setFont(self.label_font)
        ip_label.setStyleSheet("color: #2c3e50;")
        self.ip_input = QLineEdit()
        self.ip_input.setFont(self.font)
        self.ip_input.setText(self.config["server_ip"])  # 从配置读取默认值
        self.ip_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 8px;
        """)
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(self.ip_input, stretch=1)

        # 端口输入行
        port_layout = QHBoxLayout()
        port_label = QLabel("服务器端口：")
        port_label.setFont(self.label_font)
        port_label.setStyleSheet("color: #2c3e50;")
        self.port_input = QLineEdit()
        self.port_input.setFont(self.font)
        self.port_input.setText(str(self.config["server_port"]))  # 从配置读取默认值
        self.port_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 8px;
        """)
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)

        config_layout.addLayout(ip_layout)
        config_layout.addLayout(port_layout)
        main_layout.addLayout(config_layout)

        # 2. 用户名输入框
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
        main_layout.addWidget(self.username_input)

        # 3. 登录按钮
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
        main_layout.addWidget(self.login_btn)

    def do_login(self):
        """执行登录逻辑（验证IP/端口+连接服务器）"""
        # 1. 获取并验证输入
        username = self.username_input.text().strip()
        server_ip = self.ip_input.text().strip()
        server_port_str = self.port_input.text().strip()

        # 验证用户名
        if not username:
            QMessageBox.warning(self, "警告", "用户名不能为空！")
            return

        # 验证IP
        if not server_ip:
            QMessageBox.warning(self, "警告", "服务器IP不能为空！")
            return

        # 验证端口
        try:
            server_port = int(server_port_str)
            if not (1 <= server_port <= 65535):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "警告", "端口必须是1-65535之间的整数！")
            return

        # 2. 保存配置（更新最后输入的IP和端口）
        new_config = {
            "server_ip": server_ip,
            "server_port": server_port
        }
        save_config(new_config)

        # 3. 连接服务器
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, server_port))
            # 发送用户名到服务器
            self.client_socket.sendall(username.encode("utf-8"))
        except Exception as e:
            QMessageBox.critical(self, "登录失败", f"连接服务器失败：{str(e)}")
            return

        # 4. 登录成功：打开聊天窗口，隐藏登录窗口
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