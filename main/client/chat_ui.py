from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox)
from PyQt6.QtGui import QFont, QColor, QTextCursor
from client.message_sender import MessageSender
from client.message_receiver import ReceiveThread

class ChatWindow(QMainWindow):
    """聊天主窗口（UI渲染+信号绑定+接收线程管理）"""
    def __init__(self, username, client_socket):
        super().__init__()
        self.username = username
        self.client_socket = client_socket
        self.receive_thread = None  # 后台接收线程
        # 初始化消息发送器（传入UI回调用于本地显示）
        self.sender = MessageSender(client_socket, username, self._display_self_message)
        self.init_ui()
        self.start_receive_thread()  # 启动接收线程

    def init_ui(self):
        """初始化聊天窗口UI"""
        # 窗口基础设置
        self.setWindowTitle(f"聊天客户端 - {self.username}")
        self.setFixedSize(600, 500)
        self.setStyleSheet("background-color: #f5f5f5;")

        # 字体配置
        self.normal_font = QFont("微软雅黑", 10)
        self.bold_font = QFont("微软雅黑", 10, QFont.Weight.Bold)

        # 中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 1. 在线列表标签
        self.online_label = QLabel("当前在线：加载中...")
        self.online_label.setFont(self.bold_font)
        self.online_label.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(self.online_label)

        # 2. 消息显示区域
        self.msg_display = QTextEdit()
        self.msg_display.setReadOnly(True)
        self.msg_display.setFont(self.normal_font)
        self.msg_display.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
        """)
        main_layout.addWidget(self.msg_display, stretch=1)  # 占满剩余空间

        # 3. 消息输入区域（输入框+发送按钮）
        input_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setFont(self.normal_font)
        self.msg_input.setPlaceholderText("输入消息（私聊格式：@用户名 内容），输入 .exit 退出")
        self.msg_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 8px;
        """)
        self.msg_input.returnPressed.connect(self.send_message)  # 回车发送

        self.send_btn = QPushButton("发送")
        self.send_btn.setFont(self.normal_font)
        self.send_btn.setStyleSheet("""
            background-color: #4285f4;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
        """)
        self.send_btn.clicked.connect(self.send_message)  # 点击发送

        input_layout.addWidget(self.msg_input, stretch=1)
        input_layout.addWidget(self.send_btn)
        main_layout.addLayout(input_layout)

    def start_receive_thread(self):
        """启动后台接收消息线程"""
        self.receive_thread = ReceiveThread(self.client_socket)
        # 绑定线程信号到UI回调
        self.receive_thread.normal_msg_signal.connect(self._display_normal_message)
        self.receive_thread.system_msg_signal.connect(self._display_system_message)
        self.receive_thread.error_signal.connect(self._show_error)
        self.receive_thread.login_result_signal.connect(self._handle_login_result)
        # 启动线程
        self.receive_thread.start()

    def send_message(self):
        """处理消息发送（区分群聊/私聊/退出）"""
        msg = self.msg_input.text().strip()
        if not msg:
            return

        # 退出逻辑
        if msg.lower() == ".exit":
            self.close()
            return

        # 私聊逻辑（@开头）
        if msg.startswith("@"):
            if " " not in msg[1:]:
                self._display_self_message(f"[我（私聊）] 格式错误：@用户名 内容")
                self.msg_input.clear()
                return
            target_user, private_msg = msg[1:].split(" ", 1)
            self.sender.send_private_message(target_user, private_msg)
        else:
            # 群聊逻辑
            self.sender.send_group_message(msg)

        # 清空输入框
        self.msg_input.clear()

    def _display_self_message(self, msg):
        """显示自己发送的消息"""
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)
        self.msg_display.setCurrentFont(self.normal_font)
        self.msg_display.setTextColor(QColor(128, 0, 128))  # 紫色
        self.msg_display.insertPlainText(f"\n{msg}")
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)

    def _display_normal_message(self, msg):
        """显示他人发送的普通消息"""
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)
        self.msg_display.setCurrentFont(self.normal_font)
        self.msg_display.setTextColor(QColor(0, 0, 0))  # 黑色
        self.msg_display.insertPlainText(f"\n{msg}")
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)

    def _display_system_message(self, msg):
        """显示系统通知消息"""
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)
        self.msg_display.setCurrentFont(self.bold_font)
        self.msg_display.setTextColor(QColor(66, 133, 244))  # 蓝色
        self.msg_display.insertPlainText(f"\n{msg}")
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)

    def _handle_login_result(self, login_success, online_list):
        """处理登录结果（更新在线列表）"""
        if login_success:
            online_list = online_list or "无"
            online_count = len(online_list.split(',')) if online_list != "无" else 0
            self.online_label.setText(f"当前在线：{online_list}")
            self._display_system_message(f"登录成功，当前在线 {online_count} 人")
        else:
            self.online_label.setText("当前在线：无")
            self._show_error("登录失败，请重试")

    def _show_error(self, error_msg):
        """显示错误提示框"""
        QMessageBox.critical(self, "错误", error_msg)

    def closeEvent(self, event):
        """关闭窗口时：发送退出信号+停止接收线程"""
        # 发送退出信号给服务器
        self.sender.send_exit_signal()
        # 停止接收线程
        if self.receive_thread and self.receive_thread.isRunning():
            self.receive_thread.stop()
            self.receive_thread.wait()
        # 关闭socket
        try:
            self.client_socket.close()
        except:
            pass
        event.accept()