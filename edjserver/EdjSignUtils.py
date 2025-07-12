import hashlib
from typing import Dict, List
import collections
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

class EdjSignUtils:
    """
    e代驾签名工具类
    """
    DEFAULT_RANDOMKEY = "1234567890abcdef"
    
    @staticmethod
    def generate_sig(params: Dict[str, str], secret: str) -> str:
        """
        生成签名的方法
        :param params: 本次请求的所有参数都放在此dict中
        :param secret: e代驾分配的SECRET
        :return: 签名字符串
        """
        params_list = EdjSignUtils.sort(params)
        query_str = EdjSignUtils.create_query_str(params_list)
        md_str = secret + query_str + secret
        sig = EdjSignUtils.md5(md_str)[:30]
        return sig
    
    @staticmethod
    def decrypt_token(encrypt_token: str) -> str:
        """
        AES解密token
        :param encrypt_token: 加密的token字符串
        :param random_key: 解密密钥(randomkey参数值)
        :return: 解密后的token
        """
        
        # 使用randomkey作为密钥进行AES解密
        cipher = AES.new(EdjSignUtils.DEFAULT_RANDOMKEY.encode(), AES.MODE_ECB)
        # base64解码后进行AES解密
        encrypted_data = base64.b64decode(encrypt_token)
        decrypted_data = cipher.decrypt(encrypted_data)
        # 去除填充
        token = unpad(decrypted_data, AES.block_size).decode()
        return token

    @staticmethod
    def sort(params: Dict[str, str]) -> List:
        """
        对参数字典按key排序
        """
        return sorted(params.items(), key=lambda x: x[0])

    @staticmethod
    def create_query_str(params: List) -> str:
        """
        创建查询字符串
        """
        sb = []
        for key, value in params:
            if key not in ['gpsstring', 'callback', '_', 'sig']:
                sb.append(str(key))
                if value is not None and value != '':
                    sb.append(str(value))
        return ''.join(sb)

    @staticmethod
    def md5(plain_text: str) -> str:
        """
        MD5加密
        :param plain_text: 明文
        :return: 32位密文
        """
        md5_hash = hashlib.md5()
        md5_hash.update(plain_text.encode())
        return md5_hash.hexdigest()

def test_generate_sig():
    """
    测试签名生成方法
    """
    # 测试参数
    params = {
        'appkey': '61000158',
        'timestamp': '2019-06-15 11:57:11',
        'from': '01012345',
        'ver': '3.4.3',
        'longitude': '116.476169',
        'latitude': '40.018682',
        'city_name': '北京'
    }
    
    # e代驾分配的secret
    secret = '0031186e-5cc6-45a6-a090-3e88ec220452'
    
    # 生成签名
    sig = EdjSignUtils.generate_sig(params, secret)
    
    # 预期的签名结果
    expected_sig = '7bebf0fe6453861c9d304a83bc0eed'
    # 验证签名是否正确
    assert sig == expected_sig, f'签名验证失败: 期望值={expected_sig}, 实际值={sig}'
    # 打印生成的签名值
    print(f'生成的签名值: {sig}')
    print('签名验证通过!')

if __name__ == '__main__':
    test_generate_sig()
# 导出类供外部使用
__all__ = ['EdjSignUtils']
