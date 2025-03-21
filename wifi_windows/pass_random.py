import random
import string
from config.config import *  # 导入所有配置

class PassRandom:
    def __init__(self, length_range, number):
        self.length_range = length_range
        self.number = number

    def generate_random_length(self):
        """生成一个在指定区间内的随机长度"""
        return random.randint(self.length_range[0], self.length_range[1])

    def generate_random_string(self, length):
        """生成一个指定长度的随机字符串，包括字母和数字"""
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choices(characters, k=length))
        return random_string

    def write_pass(self):
        """生成多个随机密码并写入文件"""
        try:
            with open(PASS_DICT_FILE, "a+") as f:
                for _ in range(self.number):
                    length = self.generate_random_length()
                    password = self.generate_random_string(length)
                    f.write(password + '\n')  # 每个密码占一行
            print(f"Successfully wrote {self.number} passwords to {PASS_DICT_FILE}.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    wifi_pass = PassRandom(length_range, number)
    wifi_pass.write_pass()
