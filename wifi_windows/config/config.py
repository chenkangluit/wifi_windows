import os

# 目录配置
CONFIG_DIR = "config"
TEMPLATE_PATH = os.path.join(CONFIG_DIR, "wifi_template.xml")
PASSWD_FILE = os.path.join(CONFIG_DIR, "passwd.json")
PASS_DICT_FILE = os.path.join(CONFIG_DIR, "pass.txt")

# 连接配置
MAX_RETRIES = 3  # 最大重试次数
WAIT_TIME = 5  # 连接等待时间（秒）
CHECK_INTERVAL = 2  # 状态检查间隔（秒）
DISCONNECT_WAIT = 2  # 断开连接后的等待时间（秒）

# 加密类型映射
ENCRYPTION_MAP = {
    "WPA3-Personal": ("WPA3SAE", "AES"),
    "WPA2-Personal": ("WPA2PSK", "AES"),
    "WPA-Personal": ("WPAPSK", "TKIP"),
    "Open": ("open", "none"),
    "WEP": ("open", "WEP")
}

# 默认加密设置
DEFAULT_AUTH = "WPA2PSK"
DEFAULT_CIPHER = "AES"

# 网络测试配置
PING_TARGET = "8.8.8.8"  # 用于测试网络连通性的目标
PING_COUNT = 3  # ping测试次数

# 密码生成设置
length_range = (8, 8)  # 设置密码长度区间
number = 10  # 设置生成密码的数量
