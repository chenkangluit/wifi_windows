import os

# 路径配置
CONFIG_DIR = "config"
TEMPLATE_PATH = os.path.join(CONFIG_DIR, "wifi_template.xml")
PASSWD_FILE = os.path.join(CONFIG_DIR, "saved_passwords.json")
PASS_DICT_FILE = os.path.join(CONFIG_DIR, "password_dict.txt")

# 加密类型映射
ENCRYPTION_MAP = {
    "WPA2-Personal": ("WPA2PSK", "AES"),
    "WPA2-Enterprise": ("WPA2", "AES"),
    "WPA-Personal": ("WPAPSK", "AES"),
    "WPA-Enterprise": ("WPA", "AES"),
    "WEP": ("open", "WEP")
}

# 默认加密方式
DEFAULT_AUTH = "WPA2PSK"
DEFAULT_CIPHER = "AES"

# 超时参数（极致优化）
FAST_WAIT_TIME = 5            # 快速检测窗口(秒)
MAX_RETRIES = 2               # 最大重试次数
FAST_CHECK_INTERVAL = 0.3     # 快速检测间隔(秒)
DISCONNECT_WAIT = 0.5         # 断开等待时间(秒)
CONNECT_TIMEOUT = 5           # 连接超时(秒)

# 网络测试
PING_TARGET = "8.8.8.8"       # Google DNS(响应最快)
PING_COUNT = 2                # Ping次数

# 密码生成设置
length_range = (8, 8)  # 设置密码长度区间
number = 10  # 设置生成密码的数量
