from typing import Any, Dict, Optional
import httpx
import hashlib
import time
import json
import os
try:
    from mcp.server import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("edaijiamcp")

# e代驾API配置
API_BASE_URL = os.getenv("API_BASE_URL", "https://openapi.d.edaijia.cn")
APP_KEY = os.getenv("APP_KEY")
SECRET = os.getenv("SECRET")

# 检查必要的环境变量
if not APP_KEY or not SECRET:
    raise ValueError("请在.env文件中设置APP_KEY和SECRET环境变量")

def generate_signature(params: Dict[str, Any]) -> str:
    """生成API签名"""
    # 添加公共参数
    params['appkey'] = APP_KEY
    params['timestamp'] = str(int(time.time()))
    
    # 按key排序并拼接
    sorted_params = sorted(params.items())
    param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
    
    # 添加secret并生成MD5签名
    # 使用字符串格式化避免None类型的拼接问题
    sign_str = f"{param_str}&secret={SECRET}"
    signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    return signature

async def make_api_request(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """发送API请求"""
    signature = generate_signature(params.copy())
    params['appkey'] = APP_KEY
    params['timestamp'] = str(int(time.time()))
    params['sign'] = signature
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}{endpoint}", data=params)
        return response.json()

@mcp.tool()
async def call_driver(phone: str, departure: str) -> str:
    """用户叫代驾服务
    
    Args:
        phone: 用户手机号
        departure: 出发地地址
    
    Returns:
        提示信息，引导用户提供目的地以获取价格预估
    """
    if not phone or not departure:
        return "你好e代驾客服，请提供完整的手机号和出发地信息"
    
    # 验证手机号格式
    if len(phone) != 11 or not phone.isdigit():
        return "你好e代驾客服，请输入正确的11位手机号"
    
    return f"你好e代驾客服，已收到您的代驾需求：\n手机号：{phone}\n出发地：{departure}\n\n如需查看价格预估，请提供目的地地址。如需直接下单，请使用创建订单功能。"

@mcp.tool()
async def calculate_distance_and_price(departure: str, destination: str) -> str:
    """计算两地距离并显示代驾预估价格
    
    Args:
        departure: 出发地地址
        destination: 目的地地址
    
    Returns:
        距离和价格预估信息
    """
    if not departure or not destination:
        return "你好e代驾客服，请提供完整的出发地和目的地信息"
    
    try:
        # 调用距离计算API
        params = {
            'from_address': departure,
            'to_address': destination
        }
        
        result = await make_api_request('/api/distance', params)
        
        if result.get('code') == 200:
            data = result.get('data', {})
            distance = data.get('distance', 0)  # 距离（公里）
            duration = data.get('duration', 0)  # 预估时间（分钟）
            price = data.get('estimated_price', 0)  # 预估价格（元）
            
            return f"你好e代驾客服，路线信息：\n出发地：{departure}\n目的地：{destination}\n距离：{distance}公里\n预估时间：{duration}分钟\n预估价格：¥{price}元\n\n如需下单，请使用创建订单功能。"
        else:
            return f"你好e代驾客服，计算失败：{result.get('message', '未知错误')}"
            
    except Exception as e:
        return f"你好e代驾客服，计算距离时发生错误：{str(e)}"

@mcp.tool()
async def create_order(phone: str, departure: str, destination: str = "") -> str:
    """创建代驾订单
    
    Args:
        phone: 用户手机号
        departure: 出发地地址
        destination: 目的地地址（可选）
    
    Returns:
        订单创建结果和订单号
    """
    if not phone or not departure:
        return "你好e代驾客服，请提供完整的手机号和出发地信息"
    
    # 验证手机号格式
    if len(phone) != 11 or not phone.isdigit():
        return "你好e代驾客服，请输入正确的11位手机号"
    
    try:
        # 调用创建订单API
        params = {
            'phone': phone,
            'from_address': departure,
            'to_address': destination,
            'service_type': 'driver'  # 代驾服务
        }
        
        result = await make_api_request('/api/order/create', params)
        
        if result.get('code') == 200:
            data = result.get('data', {})
            order_id = data.get('order_id')
            order_status = data.get('status', '待接单')
            
            return f"你好e代驾客服，订单创建成功！\n订单号：{order_id}\n手机号：{phone}\n出发地：{departure}\n目的地：{destination if destination else '待确定'}\n订单状态：{order_status}\n\n请使用订单号查询实时状态。"
        else:
            return f"你好e代驾客服，订单创建失败：{result.get('message', '未知错误')}"
            
    except Exception as e:
        return f"你好e代驾客服，创建订单时发生错误：{str(e)}"

@mcp.tool()
async def check_order_status(order_id: str) -> str:
    """查询订单实时状态
    
    Args:
        order_id: 订单号
    
    Returns:
        订单详细状态信息
    """
    if not order_id:
        return "你好e代驾客服，请提供订单号"
    
    try:
        # 调用订单状态查询API
        params = {
            'order_id': order_id
        }
        
        result = await make_api_request('/api/order/status', params)
        
        if result.get('code') == 200:
            data = result.get('data', {})
            status = data.get('status')
            driver_info = data.get('driver_info', {})
            
            status_map = {
                'waiting': '等待接单',
                'accepted': '司机已接单',
                'arrived': '司机已就位',
                'driving': '行程中',
                'completed': '订单完成',
                'cancelled': '订单取消'
            }
            
            status_text = status_map.get(status, status)
            
            response = f"你好e代驾客服，订单状态：{status_text}\n订单号：{order_id}\n"
            
            if driver_info:
                driver_name = driver_info.get('name', '')
                driver_phone = driver_info.get('phone', '')
                driver_car = driver_info.get('car_info', '')
                driver_location = driver_info.get('location', '')
                
                if driver_name:
                    response += f"\n司机信息：\n姓名：{driver_name}\n电话：{driver_phone}\n车辆：{driver_car}\n"
                    
                if driver_location and status in ['accepted', 'arrived']:
                    response += f"司机位置：{driver_location}\n"
            
            # 根据状态提供相应提示
            if status == 'waiting':
                response += "\n正在为您匹配司机，请稍候..."
            elif status == 'accepted':
                response += "\n司机正在前往您的位置，请耐心等待"
            elif status == 'arrived':
                response += "\n司机已到达，请尽快上车"
            elif status == 'driving':
                response += "\n行程进行中，请系好安全带"
            elif status == 'completed':
                response += "\n订单已完成，感谢使用e代驾服务！"
            elif status == 'cancelled':
                response += "\n订单已取消"
            
            return response
        else:
            return f"你好e代驾客服，查询失败：{result.get('message', '未知错误')}"
            
    except Exception as e:
        return f"你好e代驾客服，查询订单状态时发生错误：{str(e)}"

@mcp.tool()
async def cancel_order(order_id: str, reason: str = "") -> str:
    """取消代驾订单
    
    Args:
        order_id: 订单号
        reason: 取消原因（可选）
    
    Returns:
        取消结果
    """
    if not order_id:
        return "你好e代驾客服，请提供订单号"
    
    try:
        # 调用取消订单API
        params = {
            'order_id': order_id,
            'cancel_reason': reason
        }
        
        result = await make_api_request('/api/order/cancel', params)
        
        if result.get('code') == 200:
            return f"你好e代驾客服，订单 {order_id} 已成功取消"
        else:
            return f"你好e代驾客服，取消订单失败：{result.get('message', '未知错误')}"
            
    except Exception as e:
        return f"你好e代驾客服，取消订单时发生错误：{str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()