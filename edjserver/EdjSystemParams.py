from typing_extensions import NoExtraItems
import requests
import json
from Crypto.Cipher import AES
import base64
import random
import string
from datetime import datetime
from .EdjSignUtils import EdjSignUtils

class EdjSystemParams:
    """系统级参数类 - 全局静态实现"""
    
    # 类级别的默认配置
    DEFAULT_APPKEY = "61000158"  # 默认合作方标识
    DEFAULT_VER = "3.4.3"       # 固定版本号
    DEFAULT_API_BASE_URL = "http://openapi.d.edaijia.cn"  # 默认API基础URL
    DEFAULT_SECRET = "0031186e-5cc6-45a6-a090-3e88ec220452"  # 默认SECRET
    DEFAULT_FROM_CHANNEL = "01012345"  # 默认业务渠道

    @staticmethod
    def get_system_params():
        """获取完整的系统级参数"""
        
        params = {
            "appkey": EdjSystemParams.DEFAULT_APPKEY,
            "timestamp": EdjSystemParams.get_timestamp(),
            "ver": EdjSystemParams.DEFAULT_VER,
            "from": EdjSystemParams.DEFAULT_FROM_CHANNEL
        }
        return params
    
    @staticmethod
    def get_api_base_url(api_base_url=None):
        """获取API基础URL"""
        return api_base_url or EdjSystemParams.DEFAULT_API_BASE_URL
        
    @staticmethod
    def get_timestamp():
        """获取当前时间戳，格式：2019-01-01 18:00:00"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def generate_sig(params, secret=None):
        """
        生成系统签名
        :param params: 需要签名的参数字典
        :param secret: e代驾分配的SECRET，如果不提供则使用默认值
        :return: 签名字符串
        """
        secret = secret or EdjSystemParams.DEFAULT_SECRET
        return EdjSignUtils.generate_sig(params, secret)
        
   

# 导出类供外部使用
__all__ = ['EdjSystemParams']
