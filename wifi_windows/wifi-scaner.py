import argparse
import json
import os
import subprocess
import time
import urllib.parse
from config.config import *  # 导入所有配置


def init_environment():
    """初始化必要目录和文件"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(PASS_DICT_FILE), exist_ok=True)

    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"必须创建配置文件: {TEMPLATE_PATH}")


def scan_wifi():
    """扫描可用WiFi网络"""
    try:
        result = subprocess.run(
            "chcp 65001 && netsh wlan show networks mode=bssid",
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        networks = result.stdout.split("\n")

        wifi_list = []
        current_ssid = None

        for line in networks:
            line = line.strip()
            if line.startswith("SSID"):
                current_ssid = line.split(":")[1].strip()
            elif line.startswith("Authentication"):
                encryption = line.split(":")[1].strip()
                if current_ssid:
                    wifi_list.append((current_ssid, encryption))
                    current_ssid = None
        return wifi_list

    except Exception as e:
        print(f"扫描失败: {str(e)}")
        return []


def generate_config(ssid, password, encryption):
    """生成WiFi配置文件"""
    auth, cipher = DEFAULT_AUTH, DEFAULT_CIPHER  # 使用默认值
    for key in ENCRYPTION_MAP:
        if key in encryption:
            auth, cipher = ENCRYPTION_MAP[key]
            break

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    # 确保SSID中的特殊字符被正确处理
    config = template.format(
        ssid=ssid.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;").replace('"',
                                                                                                                 "&quot;"),
        auth=auth,
        cipher=cipher,
        password=password
    )
    return config


def check_connection(target_ssid):
    """检查连接状态
    返回: (是否连接, 状态信息)
    """
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        if result.returncode != 0:
            return False, "获取网络接口信息失败"

        output = result.stdout
        lines = output.split('\n')

        # 解析接口信息
        current_state = None
        current_ssid = None

        for line in lines:
            line = line.strip()
            if "状态" in line or "State" in line:
                current_state = line.split(':')[1].strip()
            elif "SSID" in line and "BSSID" not in line:
                current_ssid = line.split(':')[1].strip()

            # 如果找到了目标网络的信息
            if current_ssid == target_ssid:
                # 检查连接状态
                if current_state and ("已连接" in current_state or "connected" in current_state.lower()):
                    # 检查IP地址
                    ip_result = subprocess.run(
                        ["ipconfig"],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore'
                    )

                    if "IPv4" in ip_result.stdout:
                        return True, "连接成功且已获取IP地址"
                    else:
                        return False, "已连接但未获取IP地址"
                else:
                    return False, f"未完全连接，当前状态: {current_state}"

        return False, "未找到目标网络连接"

    except Exception as e:
        return False, f"检查连接状态时出错: {str(e)}"


def test_network():
    """测试网络连通性"""
    try:
        result = subprocess.run(
            ["ping", "-n", str(PING_COUNT), PING_TARGET],
            capture_output=True,
            text=True
        )
        return "TTL=" in result.stdout
    except:
        return False


def disconnect_wifi():
    """断开当前WiFi连接"""
    try:
        subprocess.run(
            ["netsh", "wlan", "disconnect"],
            capture_output=True,
            text=True,
            check=True
        )
        # 给一点时间确保完全断开
        time.sleep(DISCONNECT_WAIT)
        return True
    except Exception as e:
        print(f"断开连接时出错: {str(e)}")
        return False


def connect_wifi(ssid, password, encryption):
    """执行连接操作（优化版）"""
    profile_file = f"{ssid.replace(' ', '_')}.xml"
    try:
        # 先断开现有连接
        print("断开现有连接...")
        disconnect_wifi()

        # 生成配置文件（增加错误处理）
        config = generate_config(ssid, password, encryption)
        if not config:
            print("⚠️ 配置文件生成失败，请检查加密方式")
            return False

        # 写入配置文件（处理特殊字符）
        with open(profile_file, "w", encoding="utf-8") as f:
            f.write(config)
        print(f"🔧 临时配置文件生成成功：{os.path.abspath(profile_file)}")

        # 添加配置文件（显示完整命令）
        try:
            add_result = subprocess.run(
                ["netsh", "wlan", "add", "profile", f"filename={profile_file}"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"✅ 配置加载成功：{add_result.stdout}")
        except subprocess.TimeoutExpired:
            print("⌛ 添加配置文件超时，请重试")
            return False

        # 执行连接（增加重试机制）
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"🔗 尝试连接第 {attempt}/{MAX_RETRIES} 次...")
            connect_result = subprocess.run(
                ["netsh", "wlan", "connect", f"name={ssid}"],
                capture_output=True,
                text=True
            )

            # 显示完整输出
            if connect_result.stdout:
                print(f"📡 连接输出：{connect_result.stdout.strip()}")
            if connect_result.stderr:
                print(f"❌ 连接错误：{connect_result.stderr.strip()}")

            # 渐进式等待和检查
            total_waited = 0

            while total_waited < WAIT_TIME:
                print(f"⏳ 等待连接建立 ({total_waited}/{WAIT_TIME} 秒)...")
                time.sleep(CHECK_INTERVAL)
                total_waited += CHECK_INTERVAL

                # 检查连接状态
                is_connected, status = check_connection(ssid)
                print(f"📡 连接状态: {status}")

                if is_connected:
                    print("✅ WiFi已连接，正在验证网络...")
                    # 给网络一点时间来稳定连接
                    time.sleep(CHECK_INTERVAL)
                    if test_network():
                        print("🌐 网络连接验证成功！")
                        # 保存密码（原子化写入）
                        try:
                            data = {}
                            if os.path.exists(PASSWD_FILE):
                                try:
                                    with open(PASSWD_FILE, "r", encoding="utf-8") as f:
                                        content = f.read().strip()
                                        if content:  # 只有当文件不为空时才解析JSON
                                            data = json.loads(content)
                                except json.JSONDecodeError:
                                    print("⚠️ 密码文件格式错误，将重新创建")
                                    data = {}

                            data[ssid] = password
                            # 确保目录存在
                            os.makedirs(os.path.dirname(PASSWD_FILE), exist_ok=True)
                            # 原子写入
                            temp_file = PASSWD_FILE + ".tmp"
                            with open(temp_file, "w", encoding="utf-8") as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            os.replace(temp_file, PASSWD_FILE)
                            print("🔐 密码保存成功")
                        except Exception as e:
                            print(f"⚠️ 密码保存失败：{str(e)}")
                        return True
                    else:
                        print("❌ 已连接但无法访问互联网")
                        # 确保断开连接后再继续
                        disconnect_wifi()
                        break  # 跳出等待循环，尝试下一次重试

            if total_waited >= WAIT_TIME:
                print("❌ 连接超时")
                # 确保断开连接后再继续
                disconnect_wifi()

        print("⛔ 所有连接尝试失败")
        return False

    except subprocess.CalledProcessError as e:
        print(f"🔥 关键错误：{e.stderr if hasattr(e, 'stderr') else str(e)}")
        print(f"完整错误信息：{vars(e)}")
        return False
    except Exception as e:
        print(f"⚠️ 未处理异常：{str(e)}")
        return False
    finally:
        # 确保清理文件
        if os.path.exists(profile_file):
            try:
                os.remove(profile_file)
                print(f"🧹 已清理临时文件：{profile_file}")
            except Exception as e:
                print(f"⚠️ 文件清理失败：{str(e)}")


def main():
    init_environment()

    parser = argparse.ArgumentParser(description="WiFi自动化连接工具")
    parser.add_argument("-m", required=True, choices=["scan", "conn"], help="操作模式")
    parser.add_argument("-s", help="目标SSID（连接模式需要）")
    args = parser.parse_args()

    if args.m == "scan":
        print("正在扫描WiFi...")
        networks = scan_wifi()
        print("\n发现网络：")
        for idx, (ssid, enc) in enumerate(networks, 1):
            print(f"{idx}. {ssid.ljust(20)} [{enc}]")

    elif args.m == "conn":
        if not args.s:
            print("必须使用 -s 指定SSID")
            return

        ssid = urllib.parse.unquote(args.s.replace("+", " "))
        print(f"开始连接: {ssid}")

        try:
            with open(PASS_DICT_FILE, "r") as f:
                passwords = [p.strip() for p in f.readlines()]
        except FileNotFoundError:
            print(f"密码文件不存在: {PASS_DICT_FILE}")
            return

        # 确保开始前断开任何现有连接
        disconnect_wifi()

        for pwd in passwords:
            print(f"尝试密码: {pwd}")
            wifi_list = scan_wifi()
            for scan_ssid, enc in wifi_list:
                if scan_ssid == ssid:
                    if connect_wifi(ssid, pwd, enc):
                        print(f"\n连接成功！\nSSID: {ssid}\nPassword: {pwd}")
                        return
            print("密码错误，尝试下一个...")
            # 确保在尝试下一个密码前断开连接
            disconnect_wifi()

        print("所有密码尝试失败")


if __name__ == "__main__":
    main()
