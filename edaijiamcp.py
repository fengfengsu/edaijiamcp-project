from typing import Any, Dict, Optional
import httpx
import hashlib
import time
import json
import os
import uuid
from fastmcp import FastMCP
from dotenv import load_dotenv
from edjserver.EdjApi import EdjApi

# 加载环境变量
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("edaijiamcp")

# 初始化EdjApi实例
api = EdjApi()

@mcp.tool()
def estimate_cost(start_address: str, start_longitude: float, start_latitude: float,
                 end_address: str, end_longitude: float, end_latitude: float, phone: str) -> Dict[str, Any]:
    """预估代驾费用
    
    Args:
        start_address: 起始地址
        start_longitude: 起始经度
        start_latitude: 起始纬度
        end_address: 目的地地址
        end_longitude: 目的地经度
        end_latitude: 目的地纬度
        phone: 用户手机号(11位)
    
    Returns:
        预估费用信息
    """
    try:
        # 验证手机号格式
        if not phone or len(phone) != 11:
            return {"error": "手机号必须是11位数字"}
        
        # 获取或刷新token
        token = api.get_token_by_phone(phone)
        if not token:
            print(f"本地未找到手机号 {phone} 的token，正在获取新token...")
            token_response = api.get_authen_token(phone)
            if token_response['code'] != '0':
                return {"error": f"获取token失败: {token_response['message']}"}
            token = api.get_token_by_phone(phone)
        
        # 调用预估费用接口
        result = api.get_cost_estimate_v2(
            token=token,
            start_latitude=start_latitude,
            start_longitude=start_longitude,
            end_latitude=end_latitude,
            end_longitude=end_longitude
        )
        
        # 如果token过期，重新获取token并重试
        if result['code'] == '10':  # token过期
            print(f"Token已过期，正在刷新token...")
            token_response = api.get_authen_token(phone)
            if token_response['code'] != '0':
                return {"error": f"刷新token失败: {token_response['message']}"}
            token = api.get_token_by_phone(phone)
            
            # 重新调用预估费用接口
            result = api.get_cost_estimate_v2(
                token=token,
                start_latitude=start_latitude,
                start_longitude=start_longitude,
                end_latitude=end_latitude,
                end_longitude=end_longitude
            )
        
        return {
            "start_address": start_address,
            "end_address": end_address,
            "phone": phone,
            "estimate_result": result
        }
        
    except Exception as e:
        return {"error": f"预估费用失败: {str(e)}"}

@mcp.tool()
def call_driver(start_address: str, start_longitude: float, start_latitude: float,
               end_address: str, end_longitude: float, end_latitude: float, phone: str,
               contact_phone: Optional[str] = None) -> Dict[str, Any]:
    """叫代驾下单
    
    Args:
        start_address: 起始地址
        start_longitude: 起始经度
        start_latitude: 起始纬度
        end_address: 目的地地址
        end_longitude: 目的地经度
        end_latitude: 目的地纬度
        phone: 用户手机号(11位)
        contact_phone: 联系电话(代叫订单必传)
    
    Returns:
        下单结果信息
    """
    try:
        # 验证手机号格式
        if not phone or len(phone) != 11:
            return {"error": "手机号必须是11位数字"}
        
        # 获取或刷新token
        token = api.get_token_by_phone(phone)
        if not token:
            print(f"本地未找到手机号 {phone} 的token，正在获取新token...")
            token_response = api.get_authen_token(phone)
            if token_response['code'] != '0':
                return {"error": f"获取token失败: {token_response['message']}"}
            token = api.get_token_by_phone(phone)
        
        # 生成唯一订单号
        third_order_id = f"MCP_ORDER_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        # 调用下单接口
        result = api.commit_order(
            phone=phone,
            token=token,
            start_address=start_address,
            start_longitude=start_longitude,
            start_latitude=start_latitude,
            end_address=end_address,
            end_longitude=end_longitude,
            end_latitude=end_latitude,
            third_order_id=third_order_id,
            contact_phone=contact_phone
        )
        
        # 如果token过期，重新获取token并重试
        if result['code'] == '1' and 'token' in result.get('message', '').lower():
            print(f"Token校验失败，正在刷新token...")
            token_response = api.get_authen_token(phone)
            if token_response['code'] != '0':
                return {"error": f"刷新token失败: {token_response['message']}"}
            token = api.get_token_by_phone(phone)
            
            # 重新调用下单接口
            result = api.commit_order(
                phone=phone,
                token=token,
                start_address=start_address,
                start_longitude=start_longitude,
                start_latitude=start_latitude,
                end_address=end_address,
                end_longitude=end_longitude,
                end_latitude=end_latitude,
                third_order_id=third_order_id,
                contact_phone=contact_phone
            )
        
        return {
            "start_address": start_address,
            "end_address": end_address,
            "phone": phone,
            "third_order_id": third_order_id,
            "contact_phone": contact_phone,
            "order_result": result
        }
        
    except Exception as e:
        return {"error": f"下单失败: {str(e)}"}

@mcp.tool()
def refresh_token(phone: str) -> Dict[str, Any]:
    """刷新用户token
    
    Args:
        phone: 用户手机号(11位)
    
    Returns:
        token刷新结果
    """
    try:
        # 验证手机号格式
        if not phone or len(phone) != 11:
            return {"error": "手机号必须是11位数字"}
        
        # 获取新token
        result = api.get_authen_token(phone)
        
        if result['code'] == '0':
            token = api.get_token_by_phone(phone)
            return {
                "phone": phone,
                "status": "success",
                "message": "Token刷新成功",
                "token_length": len(token) if token else 0
            }
        else:
            return {
                "phone": phone,
                "status": "failed",
                "error": result['message']
            }
            
    except Exception as e:
        return {"error": f"刷新token失败: {str(e)}"}

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')
