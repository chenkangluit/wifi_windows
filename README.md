# WiFi 自动化连接工具

![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)![License](https://img.shields.io/badge/License-MIT-green)

这是一个用 Python 编写的 WiFi 自动化连接工具，可以自动扫描可用的 WiFi 网络，并尝试使用预设的密码字典进行连接。

## 功能特点

- 🔍 扫描并显示周围可用的 WiFi 网络
- 🔑 支持多种加密类型（WPA3/WPA2/WPA/WEP/Open）
- 📚 支持密码字典批量尝试
- 💾 自动保存成功连接的密码
- 🔄 智能重试机制
- ⚡ 连接状态实时反馈
- 🛡️ 安全的配置文件处理

## 系统要求

- Windows 11 
- Python 3.11+

## 安装说明

1. 克隆或下载本项目到本地：
```bash
git clone <repository_url>
cd wifi-windows
```

2. 创建必要的配置文件：

在 `config` 目录下创建以下文件：
- `wifi_template.xml`：WiFi 配置模板
- `pass.txt`：密码字典文件

3. 配置密码字典：
在 `config/pass.txt` 中添加要尝试的密码，每行一个密码。

## 使用方法

### 扫描 WiFi 网络

```bash
python wifi-scaner.py -m scan
```

这将显示周围可用的 WiFi 网络列表。

### 连接 WiFi

```bash
python wifi-scaner.py -m conn -s "WIFI名称"
```

注意：如果 WiFi 名称中包含空格，请使用引号包围。

## 配置说明

配置文件位于 `config/config.py`，可以根据需要修改以下参数：

### 连接配置
```python
FAST_WAIT_TIME = 5            # 快速检测窗口(秒)
MAX_RETRIES = 2               # 最大重试次数
FAST_CHECK_INTERVAL = 0.3     # 快速检测间隔(秒)
DISCONNECT_WAIT = 0.5         # 断开等待时间(秒)
CONNECT_TIMEOUT = 5           # 连接超时(秒)
```

### 网络测试配置
```python
PING_TARGET = "8.8.8.8"       # Google DNS(响应最快)
PING_COUNT = 2                # Ping次数
```

### 文件路径配置
```python
CONFIG_DIR = "config"
TEMPLATE_PATH = "config/wifi_template.xml"
PASSWD_FILE = "config/saved_passwords.json"
PASS_DICT_FILE = "config/password_dict.txt"
```

## 注意事项

1. 请确保以管理员权限运行程序
2. 使用工具时请遵守当地法律法规
3. 不要在未经授权的网络上使用此工具
4. 建议在测试环境中使用

## 文件说明

- `wifi-scaner.py`：主程序文件
- `config/config.py`：配置文件
- `config/wifi_template.xml`：WiFi配置模板
- `config/password_dict.txt`：密码字典
- `config/saved_passwords.json`：已保存的密码文件

## 常见问题

1. **连接失败**
   - 检查密码是否正确
   - 确认网络信号强度
   - 验证加密类型是否支持

2. **权限问题**
   - 确保以管理员权限运行
   - 检查防火墙设置

3. **配置文件错误**
   - 确认 config 目录下所有必要文件都存在
   - 检查文件格式是否正确

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的 WiFi 扫描和连接功能
- 添加配置文件支持
- 实现密码保存功能
### v1.0.1
- 优化连接效率(默认配置，一次大约6秒)

## 许可证

本项目采用 [MIT License](LICENSE)