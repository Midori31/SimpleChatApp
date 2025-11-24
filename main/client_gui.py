import sys
import socket
import threading
from queue import Queue
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QTextCursor  # 导入 QTextCursor

# 配置参数（和服务器一致）
SERVER_IP = "101.76.246.151"
SERVER_PORT = 9000
BUFFER_SIZE = 1024
EXIT_MARKER = "__EXIT__"
CHAT_SEPARATOR = "|||"

class ReceiveThread(QThread):
    """后台接收消息线程（不阻塞UI）"""
    message_signal = pyqtSignal(str)  # 传递消息到UI的信号
    error_signal = pyqtSignal(str)    # 传递错误信息的信号
    login_signal = pyqtSignal(bool, str)  # 登录结果信号（成功/失败，在线列表）

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.running = True

    def run(self):
        """线程运行逻辑：持续接收服务器消息"""
        try:
            # 登录阶段：接收登录响应和初始在线列表
            login_data = b""
            while len(login_data.split(CHAT_SEPARATOR.encode("utf-8"))) < 3 and self.running:
                chunk = self.client_socket.recv(BUFFER_SIZE)
                if not chunk:
                    self.error_signal.emit("服务器断开连接")
                    return
                login_data += chunk

            # 解析登录响应
            responses = [m.strip() for m in login_data.decode("utf-8").split(CHAT_SEPARATOR) if m.strip()]
            login_success = False
            online_list = ""
            for resp in responses:
                if resp.startswith("【成功】"):
                    login_success = True
                elif resp.startswith("【当前在线】"):
                    online_list = resp.replace("【当前在线】", "")
                elif resp.startswith("【错误】"):
                    self.error_signal.emit(resp)

            self.login_signal.emit(login_success, online_list)
            if not login_success:
                self.client_socket.close()
                return

            # 聊天阶段：持续接收消息
            while self.running:
                data = self.client_socket.recv(BUFFER_SIZE).decode("utf-8", errors="ignore")
                if not data:
                    break
                msgs = [m.strip() for m in data.split(CHAT_SEPARATOR) if m.strip()]
                for msg in msgs:
                    if msg:
                        self.message_signal.emit(msg)

        except Exception as e:
            self.error_signal.emit(f"接收消息失败：{str(e)}")
        finally:
            self.client_socket.close()

    def stop(self):
        """停止线程"""
        self.running = False

class ChatWindow(QMainWindow):
    """主聊天窗口"""
    def __init__(self, username, client_socket):
        super().__init__()
        self.username = username
        self.client_socket = client_socket
        self.init_ui()
        self.start_receive_thread()

    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle(f"聊天客户端 - {self.username}")
        self.setFixedSize(600, 500)  # 固定窗口大小
        self.setStyleSheet("background-color: #f5f5f5;")

        # 字体设置（修复：Weight.Bold 首字母大写）
        self.font = QFont("微软雅黑", 10)
        self.bold_font = QFont("微软雅黑", 10, QFont.Weight.Bold)

        # 中心部件和布局
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

        # 2. 消息显示区域（不可编辑）
        self.msg_display = QTextEdit()
        self.msg_display.setReadOnly(True)
        self.msg_display.setFont(self.font)
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
        self.msg_input.setFont(self.font)
        self.msg_input.setPlaceholderText("输入消息（私聊格式：@用户名 内容），输入 .exit 退出")
        self.msg_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 8px;
        """)
        self.msg_input.returnPressed.connect(self.send_message)  # 回车发送

        self.send_btn = QPushButton("发送")
        self.send_btn.setFont(self.font)
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
        """启动接收消息线程"""
        self.receive_thread = ReceiveThread(self.client_socket)
        self.receive_thread.message_signal.connect(self.display_message)
        self.receive_thread.error_signal.connect(self.show_error)
        self.receive_thread.login_signal.connect(self.update_online_list)
        self.receive_thread.start()

    def display_message(self, msg):
        """在消息区域显示消息（区分系统通知和聊天消息）"""
        # 修复：光标移到末尾（使用 QTextCursor.MoveOperation.End）
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)
        if msg.startswith("【系统通知】"):
            # 系统通知：蓝色加粗
            self.msg_display.setCurrentFont(self.bold_font)
            self.msg_display.setTextColor(QColor(66, 133, 244))  # 蓝色
            self.msg_display.insertPlainText(f"\n{msg}")
        else:
            # 聊天消息：黑色常规
            self.msg_display.setCurrentFont(self.font)
            self.msg_display.setTextColor(QColor(0, 0, 0))
            self.msg_display.insertPlainText(f"\n{msg}")
        # 修复：自动滚动到底部
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)

    def update_online_list(self, login_success, online_list):
        """更新在线列表标签"""
        if login_success:
            # 处理在线列表为空的情况（避免 split 报错）
            online_list = online_list.strip()
            if not online_list:
                online_count = 0
                online_list = "无"
            else:
                online_count = len(online_list.split(','))
            self.online_label.setText(f"当前在线：{online_list}")
            self.display_message(f"【系统通知】登录成功，当前在线 {online_count} 人")
        else:
            self.online_label.setText("当前在线：无")

    def send_message(self):
        """发送消息到服务器"""
        msg = self.msg_input.text().strip()
        if not msg:
            return

        # 退出逻辑
        if msg.lower() == ".exit":
            self.close()
            return

        try:
            # 发送消息（带分隔符）
            self.client_socket.send(f"{msg}{CHAT_SEPARATOR}".encode("utf-8"))
            # 自己发送的消息也显示在界面上
            if msg.startswith("@"):
                # 私聊消息（处理无空格的情况）
                if " " in msg:
                    self.display_message(f"[我（私聊）] {msg.split(' ', 1)[1]}")
                else:
                    self.display_message(f"[我（私聊）] 格式错误：@用户名 内容")
            else:
                # 群聊消息
                self.display_message(f"[我] {msg}")
            self.msg_input.clear()  # 清空输入框
        except Exception as e:
            self.show_error(f"发送消息失败：{str(e)}")

    def show_error(self, error_msg):
        """显示错误提示框"""
        QMessageBox.critical(self, "错误", error_msg)

    def closeEvent(self, event):
        """窗口关闭时执行（发送退出标记）"""
        try:
            self.client_socket.send(EXIT_MARKER.encode("utf-8"))
            self.receive_thread.stop()
            self.receive_thread.wait()
            self.client_socket.close()
        except:
            pass
        event.accept()

class LoginWindow(QMainWindow):
    """登录窗口"""
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.init_ui()

    def init_ui(self):
        """初始化登录界面"""
        self.setWindowTitle("聊天客户端 - 登录")
        self.setFixedSize(400, 200)
        self.setStyleSheet("background-color: #f5f5f5;")

        # 字体设置
        self.font = QFont("微软雅黑", 11)

        # 中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(50, 50, 50, 50)

        # 1. 用户名输入
        self.username_input = QLineEdit()
        self.username_input.setFont(self.font)
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 8px;
        """)
        self.username_input.returnPressed.connect(self.login)  # 回车登录

        # 2. 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setFont(self.font)
        self.login_btn.setStyleSheet("""
            background-color: #4285f4;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
        """)
        self.login_btn.clicked.connect(self.login)  # 点击登录

        main_layout.addWidget(self.username_input)
        main_layout.addWidget(self.login_btn)

    def login(self):
        """登录逻辑：连接服务器并发送用户名"""
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "警告", "用户名不能为空！")
            return

        # 连接服务器
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            # 发送用户名
            self.client_socket.sendall(username.encode("utf-8"))
        except Exception as e:
            QMessageBox.critical(self, "登录失败", f"连接服务器失败：{str(e)}")
            return

        # 隐藏登录窗口，打开聊天窗口
        self.chat_window = ChatWindow(username, self.client_socket)
        self.chat_window.show()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())