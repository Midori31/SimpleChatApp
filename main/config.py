import json
import os

# 配置文件路径
CONFIG_FILE = "config.json"
# 默认配置（首次启动时使用）
DEFAULT_CONFIG = {
    "server_ip": "127.0.0.1",
    "server_port": 9000
}

# 读取配置文件（不存在则创建）
def load_config():
    if not os.path.exists(CONFIG_FILE):
        # 首次启动：生成默认配置文件
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        return DEFAULT_CONFIG
    
    # 读取现有配置文件
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        # 补全缺失的配置项（兼容旧版本）
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config
    except Exception as e:
        print(f"读取配置文件失败，使用默认配置：{e}")
        return DEFAULT_CONFIG

# 保存配置到文件
def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存配置文件失败：{e}")
        return False

# 加载配置
CONFIG = load_config()

# 导出配置项（供其他文件使用）
SERVER_IP = CONFIG["server_ip"]
SERVER_PORT = CONFIG["server_port"]
BUFFER_SIZE = 1024
EXIT_MARKER = "__EXIT__"
CHAT_SEPARATOR = "|||"
SERVER_BIND_ADDR = ("0.0.0.0", SERVER_PORT)