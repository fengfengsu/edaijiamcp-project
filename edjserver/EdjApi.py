import json
import os
import requests

from .EdjSystemParams import EdjSystemParams
from .EdjSignUtils import EdjSignUtils


class EdjApi:
    def __init__(self, appkey=None, secret=None, api_base_url=None):
        """初始化API服务
        Args:
            appkey: str, 合作方标识，不传则使用默认值
            secret: str, e代驾分配的SECRET，不传则使用默认值
            api_base_url: str, API基础URL，不传则使用默认值
        """
        self.appkey = appkey
        self.secret = secret
        self.api_base_url = api_base_url
        
    def get_authen_token(self, phone=None, third_user_id=None, user_os=None, mac=None):
        """获取用户认证token
        Args:
            phone: str, 11位真实用户手机号(非虚拟号必传)
            third_user_id: str, 合作方用户id(虚拟号必传)
            randomkey: str, 16位AES对称密钥,用于解密返回token
            user_os: str, 用户手机系统(可选)
            mac: str, 用户mac地址(可选)
        Returns:
            dict: {
                'code': str,  # 0成功，10授权token已过期
                'message': str,
                'data': {
                    'encrypt_authentoken': str  # AES加密的token
                }
            }
        """
        if not (phone or third_user_id):
            raise ValueError("phone或third_user_id必须传一个")
            
        if phone and len(phone) != 11:
            raise ValueError("phone必须是11位手机号")
            
        params = {
            "randomkey": "1234567890abcdef"
        }
        
        if phone:
            params['phone'] = phone
        if third_user_id:
            params['third_user_id'] = third_user_id
        if user_os:
            params['os'] = user_os
        if mac:
            params['mac'] = mac
        
        params = self._add_system_params_and_sign(params)
        
        # 调用接口获取token
        base_url = EdjSystemParams.get_api_base_url(self.api_base_url)
        url = f"{base_url}/customer/getAuthenToken"
        response = self._post(url, params)
        
        # 打印响应结果
        print(f"API响应: {response}")
        
        # 存储加密token到本地文件
        if response['code'] == '0' and phone:
            encrypt_authentoken = response['data']['encrypt_authentoken']
            # 解密token
            authentoken = EdjSignUtils.decrypt_token(encrypt_authentoken)
            # 打印解密后的token
            print(f"解密后的token: {authentoken}")
            
            # 将加密token存储到本地文件中
            token_dir = os.path.join(os.path.dirname(__file__), 'tokens')
            if not os.path.exists(token_dir):
                os.makedirs(token_dir)
            token_file = os.path.join(token_dir, f"{phone}.token")
            with open(token_file, 'w') as f:
                f.write(authentoken)
            print(f"Token已保存到: {token_file}")
        return response

    def get_city_price_list(self, longitude, latitude, city_name):
        """获取城市价格列表
        Args:
            longitude: float, 经度，例如: 116.476169
            latitude: float, 纬度，例如: 40.018682
            city_name: str, 所在城市名，例如: 北京
        Returns:
            dict: {
                'code': str,  # 接口返回码
                'message': str,  # 接口返回信息
                'data': list  # 价格列表数据
            }
        """
        if not all([longitude, latitude, city_name]):
            raise ValueError("经度、纬度和城市名称都不能为空")
            
        params = {
            'longitude': longitude,
            'latitude': latitude,
            'city_name': city_name
        }

        params = self._add_system_params_and_sign(params)
        
        # 调用接口获取城市价格列表
        base_url = EdjSystemParams.get_api_base_url(self.api_base_url)
        url = f"{base_url}/city/price/list"
        response = self._post(url, params)
        
        return response
    
    def get_cost_estimate_v2(self, token, start_latitude, start_longitude, end_latitude, end_longitude, 
                         channel=None, long_distance_adjust_fee=None, bonus_sn=None, strategyId=None,
                         is_use_bonus=None, estimate_distance=None, estimate_duration=None):
        """获取预估费用V2
        Args:
            token: str, 用户凭证
            start_latitude: float, 起始纬度
            start_longitude: float, 起始经度
            end_latitude: float, 结束纬度
            end_longitude: float, 结束经度
            channel: str, 远程单传01007(可选)
            long_distance_adjust_fee: float, 远程订单补贴费(可选)
            bonus_sn: str, 优惠券码(可选)
            strategyId: str, 权益id(可选)
            is_use_bonus: int, 是否使用优惠券(1:使用 0:不使用,默认0)(可选)
            estimate_distance: int, 合作方预估距离,单位米(可选)
            estimate_duration: int, 合作方预估时长,单位秒(可选)
        Returns:
            dict: 接口返回结果
        """
        # 校验必填参数
        if not all([token, start_latitude, start_longitude, end_latitude, end_longitude]):
            raise ValueError("token和起终点经纬度为必填参数")

        # 构建请求参数
        params = {
            'token': token,
            'start_latitude': start_latitude,
            'start_longitude': start_longitude,
            'end_latitude': end_latitude,
            'end_longitude': end_longitude
        }

        # 添加可选参数
        if channel:
            params['channel'] = channel
        if long_distance_adjust_fee is not None:
            params['long_distance_adjust_fee'] = long_distance_adjust_fee
        if bonus_sn:
            params['bonus_sn'] = bonus_sn
        if strategyId:
            params['strategyId'] = strategyId
        if is_use_bonus is not None:
            params['is_use_bonus'] = is_use_bonus
        if estimate_distance is not None:
            params['estimate_distance'] = estimate_distance
        if estimate_duration is not None:
            params['estimate_duration'] = estimate_duration

        params = self._add_system_params_and_sign(params)
        
        # 调用预估费用接口
        base_url = EdjSystemParams.get_api_base_url(self.api_base_url)
        url = f"{base_url}/order/costestimateV2"
        response = self._post(url, params)
        
        return response



    def commit_order(self, phone, token, start_address, start_longitude, start_latitude,
                     end_address, end_longitude, end_latitude, third_order_id, is_use_bonus=0,
                     contact_phone=None, third_user_id=None, channel='01003', bonus_sn=None,
                     driver_id=None, dynamic_fee=None, dynamic_rate=None, fee_max=None,
                     strategyId=None, strategyServiceSign=None, carNo=None, cash_only=None,
                     callLink=None, prePay=None, multiBizEstimate=None):
        """下单接口
        Args:
            phone: str, 下单用户电话(真实手机号)
            token: str, 用户凭证
            start_address: str, 下单起始地址
            start_longitude: float, 下单起始经度
            start_latitude: float, 下单起始纬度
            end_address: str, 下单目的地地址
            end_longitude: float, 下单目的地经度
            end_latitude: float, 下单目的地纬度
            third_order_id: str, 第三方订单号
            is_use_bonus: int, 是否使用优惠券(1:使用 0:不使用,默认0)
            contact_phone: str, 联系用户电话,代叫订单必传(可选)
            third_user_id: str, 合作商唯一userId(可选)
            channel: str, 渠道号,默认01003一键下单(可选)
            bonus_sn: str, 优惠券码(可选)
            driver_id: str, 司机工号,选司机下单用(可选)
            dynamic_fee: float, 当前动态调价金额(可选)
            dynamic_rate: float, 当前动态调价倍数(可选)
            fee_max: float, 最大动调金额(可选)
            strategyId: str, 权益订单策略id(可选)
            strategyServiceSign: str, 权益订单来源签名(可选)
            carNo: str, 车牌号(可选)
            cash_only: int, 支付方式(代叫订单需要传,0本人支付,1乘客现金支付)(可选)
            callLink: str, 催付短信链接(可选)
            prePay: int, 是否免密或者预付订单(0否,1是)(可选)
            multiBizEstimate: str, 多业务预估信息(可选)
        Returns:
            dict: 接口返回结果
        """
        # 校验必填参数
        if not all([phone, token, start_address, start_longitude, start_latitude,
                    end_address, end_longitude, end_latitude, third_order_id]):
            raise ValueError("必填参数不能为空")

        # 构建请求参数
        params = {
            'phone': phone,
            'token': token,
            'start_address': start_address,
            'start_longitude': start_longitude,
            'start_latitude': start_latitude,
            'end_address': end_address,
            'end_longitude': end_longitude,
            'end_latitude': end_latitude,
            'third_order_id': third_order_id,
            'is_use_bonus': is_use_bonus,
            'channel': channel
        }

        # 添加可选参数
        optional_params = {
            'contact_phone': contact_phone,
            'third_user_id': third_user_id,
            'bonus_sn': bonus_sn,
            'driver_id': driver_id,
            'dynamic_fee': dynamic_fee,
            'dynamic_rate': dynamic_rate,
            'fee_max': fee_max,
            'strategyId': strategyId,
            'strategyServiceSign': strategyServiceSign,
            'carNo': carNo,
            'cash_only': cash_only,
            'callLink': callLink,
            'prePay': prePay,
            'multiBizEstimate': multiBizEstimate
        }

        # 将非None的可选参数添加到请求参数中
        params.update({k: v for k, v in optional_params.items() if v is not None})

        # 添加系统参数和签名
        params = self._add_system_params_and_sign(params)

        # 调用下单接口
        base_url = EdjSystemParams.get_api_base_url(self.api_base_url)
        url = f"{base_url}/order/commit"
        response = self._post(url, params)

        return response

    def _add_system_params_and_sign(self, params):
        """添加系统参数和签名
        Args:
            params: dict, 原始参数字典
        Returns:
            dict: 添加了系统参数和签名后的参数字典
        """
        # 获取系统参数并合并
        system_params = EdjSystemParams.get_system_params()
        params.update(system_params)
        # 获取签名
        sig = EdjSignUtils.generate_sig(params, '0031186e-5cc6-45a6-a090-3e88ec220452')
        params['sig'] = sig
        return params

    def get_token_by_phone(self, phone):
        """根据手机号获取本地存储的token
        Args:
            phone: str, 11位手机号
        Returns:
            str: token字符串,不存在则返回None
        """
        if not phone or len(phone) != 11:
            raise ValueError("phone必须是11位手机号")
            
        # 获取token文件路径
        token_dir = os.path.join(os.path.dirname(__file__), 'tokens')
        token_file = os.path.join(token_dir, f"{phone}.token")
        
        # 如果token文件存在则读取返回
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token = f.read().strip()
                print(f"获取到的token: {token}")
                return token
        return None

    def _post(self, url, params):
        """发送POST请求
        Args:
            url: str, 请求URL
            params: dict, 请求参数
        Returns:
            dict: 响应结果
        """
        try:
            response = requests.post(url, data=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'code': '-1',
                'message': f'请求失败: {str(e)}',
                'data': None
            }
        except json.JSONDecodeError as e:
            return {
                'code': '-2',
                'message': f'响应解析失败: {str(e)}',
                'data': None
            }


# 导出类供外部使用
__all__ = ['EdjApi']
