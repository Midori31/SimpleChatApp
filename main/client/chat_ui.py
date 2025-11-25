from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel, QListWidget,
                             QListWidgetItem, QMessageBox)
from PyQt6.QtGui import QFont, QColor, QTextCursor
from PyQt6.QtCore import Qt
from client.message_sender import MessageSender
from client.message_receiver import ReceiveThread
from client.private_chat_ui import PrivateChatWindow
from datetime import datetime

def get_current_time():
    """获取当前时间，格式：hh:mm:ss"""
    return datetime.now().strftime("%H:%M:%S")

class ChatWindow(QMainWindow):
    """聊天主窗口（含下线按钮+时间戳）"""
    def __init__(self, username, client_socket):
        super().__init__()
        self.username = username
        self.client_socket = client_socket
        self.receive_thread = None
        self.sender = MessageSender(client_socket, username, self._display_self_message)
        self.private_chat_windows = {}
        self.init_ui()
        self.start_receive_thread()

    def init_ui(self):
        """初始化UI（含下线按钮）"""
        self.setWindowTitle(f"EasyChat - {self.username}")
        self.setFixedSize(750, 500)
        self.setStyleSheet("background-color: #f5f5f5;")

        self.normal_font = QFont("微软雅黑", 10)
        self.bold_font = QFont("微软雅黑", 10, QFont.Weight.Bold)
        self.list_font = QFont("微软雅黑", 9)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 左侧在线列表区域
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)

        online_title = QLabel("在线用户")
        online_title.setFont(self.bold_font)
        online_title.setStyleSheet("color: #2c3e50;")
        left_layout.addWidget(online_title)

        self.online_list_widget = QListWidget()
        self.online_list_widget.setFont(self.list_font)
        self.online_list_widget.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 5px;
        """)
        self.online_list_widget.setFixedWidth(150)
        self.online_list_widget.itemDoubleClicked.connect(self.on_item_double_click)
        self._add_online_item("加载中...", is_system=True)
        left_layout.addWidget(self.online_list_widget, stretch=1)

        main_layout.addLayout(left_layout)

        # 右侧聊天区域
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        # 状态提示标签 + 下线按钮
        status_layout = QHBoxLayout()
        self.status_label = QLabel("连接中...")
        self.status_label.setFont(self.normal_font)
        self.status_label.setStyleSheet("color: #666;")
        status_layout.addWidget(self.status_label, stretch=1)

        self.logout_btn = QPushButton("下线")
        self.logout_btn.setFont(self.normal_font)
        self.logout_btn.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 6px 12px;
        """)
        self.logout_btn.clicked.connect(self.do_logout)
        status_layout.addWidget(self.logout_btn)
        right_layout.addLayout(status_layout)

        # 消息显示区域
        self.msg_display = QTextEdit()
        self.msg_display.setReadOnly(True)
        self.msg_display.setFont(self.normal_font)
        self.msg_display.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
        """)
        right_layout.addWidget(self.msg_display, stretch=1)

        # 消息输入区域
        input_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setFont(self.normal_font)
        self.msg_input.setPlaceholderText("输入群聊消息，输入 .exit 退出（私聊请双击左侧用户）")
        self.msg_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 8px;
        """)
        self.msg_input.returnPressed.connect(self.send_group_message)

        self.send_btn = QPushButton("群聊发送")
        self.send_btn.setFont(self.normal_font)
        self.send_btn.setStyleSheet("""
            background-color: #4285f4;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
        """)
        self.send_btn.clicked.connect(self.send_group_message)

        input_layout.addWidget(self.msg_input, stretch=1)
        input_layout.addWidget(self.send_btn)
        right_layout.addLayout(input_layout)

        main_layout.addLayout(right_layout, stretch=1)

    def do_logout(self):
        """执行下线逻辑"""
        reply = QMessageBox.question(
            self,
            "确认下线",
            "确定要下线并关闭窗口吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()

    def on_item_double_click(self, item):
        """双击在线列表触发私聊"""
        item_text = item.text().strip()
        if "加载中..." in item_text or "暂无在线用户" in item_text or "（自己）" in item_text:
            return

        target_user = item_text.replace("（自己）", "").strip()
        if target_user == self.username:
            QMessageBox.information(self, "提示", "不能与自己私聊！")
            return

        if target_user in self.private_chat_windows:
            self.private_chat_windows[target_user].raise_()
            self.private_chat_windows[target_user].activateWindow()
        else:
            chat_window = PrivateChatWindow(
                parent=self,
                username=self.username,
                target_user=target_user,
                message_sender=self.sender
            )
            self.private_chat_windows[target_user] = chat_window
            chat_window.show()

    def remove_private_chat_window(self, target_user):
        """移除私聊窗口引用"""
        if target_user in self.private_chat_windows:
            del self.private_chat_windows[target_user]

    def send_group_message(self):
        """发送群聊消息"""
        msg = self.msg_input.text().strip()
        if not msg:
            return

        if msg.lower() == ".exit":
            self.close()
            return

        self.sender.send_group_message(msg)
        self.msg_input.clear()

    def handle_private_message(self, sender, msg):
        """处理收到的私聊消息"""
        if sender in self.private_chat_windows:
            chat_window = self.private_chat_windows[sender]
            chat_window.display_target_message(msg)
            chat_window.raise_()
            chat_window.activateWindow()
        else:
            reply = QMessageBox.question(
                self,
                "新私聊消息",
                f"收到 {sender} 的私聊消息：\n{msg}\n\n是否打开私聊窗口？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                chat_window = PrivateChatWindow(
                    parent=self,
                    username=self.username,
                    target_user=sender,
                    message_sender=self.sender
                )
                self.private_chat_windows[sender] = chat_window
                chat_window.display_target_message(msg)
                chat_window.show()

    def _add_online_item(self, text, is_system=False, is_self=False):
        """添加在线列表项"""
        item = QListWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFont(self.list_font)

        if is_system:
            item.setForeground(QColor(128, 128, 128))
        elif is_self:
            item.setForeground(QColor(66, 133, 244))
            item.setFont(QFont("微软雅黑", 9, QFont.Weight.Bold))
            item.setBackground(QColor(230, 240, 255))
        else:
            item.setForeground(QColor(0, 0, 0))

        self.online_list_widget.addItem(item)

    def _refresh_online_list(self, online_list):
        """刷新在线列表"""
        self.online_list_widget.clear()

        if not online_list or online_list == "无":
            self._add_online_item("暂无在线用户", is_system=True)
            self.status_label.setText("当前在线：0人")
            return

        usernames = [name.strip() for name in online_list.split(',') if name.strip()]
        self.status_label.setText(f"当前在线：{len(usernames)}人")

        if self.username in usernames:
            self._add_online_item(f"{self.username}（自己）", is_self=True)
            usernames.remove(self.username)

        for name in usernames:
            self._add_online_item(name)

    def start_receive_thread(self):
        """启动接收线程"""
        self.receive_thread = ReceiveThread(self.client_socket)
        self.receive_thread.normal_msg_signal.connect(self._display_normal_message)
        self.receive_thread.system_msg_signal.connect(self._display_system_message)
        self.receive_thread.error_signal.connect(self._show_error)
        self.receive_thread.login_result_signal.connect(self._handle_login_result)
        self.receive_thread.online_list_update_signal.connect(self._refresh_online_list)
        self.receive_thread.private_msg_signal.connect(self.handle_private_message)
        self.receive_thread.start()

    def _display_self_message(self, msg):
        """显示自己的群聊消息（带时间戳）"""
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)
        self.msg_display.setCurrentFont(self.normal_font)
        self.msg_display.setTextColor(QColor(128, 0, 128))
        self.msg_display.insertPlainText(f"\n[我] {get_current_time()}")
        self.msg_display.insertPlainText(f"\n{msg}")
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)

    def _display_normal_message(self, msg):
        """显示他人的群聊消息（带时间戳，服务器已拼接）"""
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)
        self.msg_display.setCurrentFont(self.normal_font)
        self.msg_display.setTextColor(QColor(0, 0, 0))
        self.msg_display.insertPlainText(f"\n{msg}")
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)

    def _display_system_message(self, msg):
        """显示系统通知（带时间戳）"""
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)
        self.msg_display.setCurrentFont(self.bold_font)
        self.msg_display.setTextColor(QColor(66, 133, 244))
        self.msg_display.insertPlainText(f"\n【系统通知】{get_current_time()}")
        self.msg_display.insertPlainText(f"\n{msg}")
        self.msg_display.moveCursor(QTextCursor.MoveOperation.End)

    def _handle_login_result(self, login_success, online_list):
        """处理登录结果"""
        if login_success:
            self._refresh_online_list(online_list)
            online_count = len(online_list.split(',')) if online_list and online_list != "无" else 0
            self._display_system_message(f"登录成功，当前在线 {online_count} 人")
        else:
            self._refresh_online_list("无")
            self.status_label.setText("登录失败")
            self._show_error("登录失败，请重试")

    def _show_error(self, error_msg):
        """显示错误提示"""
        QMessageBox.critical(self, "错误", error_msg)

    def closeEvent(self, event):
        """关闭窗口清理"""
        for chat_window in self.private_chat_windows.values():
            chat_window.close()
        self.sender.send_exit_signal()
        if self.receive_thread and self.receive_thread.isRunning():
            self.receive_thread.stop()
            self.receive_thread.wait()
        try:
            self.client_socket.close()
        except:
            pass
        event.accept()