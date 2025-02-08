import subprocess


def scan_wifi():
    """
    扫描附近的 WiFi 网络并返回列表
    :return: WiFi SSID 列表
    """
    try:
        # 使用 UTF-8 编码运行命令
        result = subprocess.run(
            "chcp 65001 && netsh wlan show networks",
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        networks = result.stdout
        ssid_list = []
        for line in networks.split("\n"):
            line = line.strip()
            if line.startswith("SSID"):
                ssid = line.split(":")[1].strip()
                if ssid:  # 确保 SSID 非空
                    ssid_list.append(ssid)
        return ssid_list
    except subprocess.CalledProcessError as e:
        print(f"扫描 WiFi 网络失败: {e}")
        return []


def connect_to_wifi(ssid, password):
    """
    使用提供的 SSID 和密码连接到 WiFi 网络。
    :param ssid: WiFi 名称
    :param password: WiFi 密码
    """
    try:
        # 创建 WiFi 配置文件
        config = f"""
        <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>{ssid}</name>
            <SSIDConfig>
                <SSID>
                    <name>{ssid}</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>manual</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>WPA2PSK</authentication>
                        <encryption>AES</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                    <sharedKey>
                        <keyType>passPhrase</keyType>
                        <protected>false</protected>
                        <keyMaterial>{password}</keyMaterial>
                    </sharedKey>
                </security>
            </MSM>
        </WLANProfile>
        """
        profile_path = f"{ssid}.xml"

        # 写入配置文件
        with open(profile_path, "w", encoding="utf-8") as file:
            file.write(config.strip())

        # 添加配置文件到 WLAN 配置中
        subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_path}"], check=True)

        # 连接到 WiFi
        subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], check=True)

        print(f"正在连接 WiFi: {ssid} 使用密码: {password}")
    except subprocess.CalledProcessError as e:
        print(f"操作失败: {e}")
    finally:
        # 清理配置文件
        import os
        if os.path.exists(profile_path):
            os.remove(profile_path)


def main():
    print("正在扫描附近的 WiFi 网络，请稍候...")
    ssid_list = scan_wifi()

    if not ssid_list:
        print("未找到任何 WiFi 网络！请确认 WLAN 已开启。")
        return

    print("\n找到以下可用 WiFi 网络：")
    for i, ssid in enumerate(ssid_list, start=1):
        print(f"{i}. {ssid}")

    try:
        choice = int(input("\n请输入要连接的 WiFi 编号："))
        if 1 <= choice <= len(ssid_list):
            ssid = ssid_list[choice - 1]
            # password = input(f"请输入 WiFi [{ssid}] 的密码：")
            with open("passwd_WiFi", "r") as f:
                password = f.readlines()
                print(password)
            for i in password:
                print(i)
                connect_to_wifi(ssid, i)
        else:
            print("输入的编号无效！")
    except ValueError:
        print("请输入有效的编号！")


if __name__ == "__main__":
    main()
