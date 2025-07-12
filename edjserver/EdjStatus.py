# 订单状态码定义
ORDER_STATUS = {
    102: "开始系统派单",
    180: "系统派单中", 
    301: "司机接单",
    302: "司机就位（到达用户地点）",
    303: "司机开车",
    304: "代驾结束",
    403: "客户取消",
    404: "司机取消",
    501: "司机报单",
    506: "系统派单失败"  # 下单接口返回timeout秒内，未派到司机，无响应订单
}


# API返回码定义
API_RESPONSE_CODE = {
    0: "成功",
    1: "ip已被拉黑",
    2: "您最多可以同时用1名代驾司机",
    3: "系统参数缺失或非法",
    4: "系统参数timestamp已超过10分钟",
    5: "appkey未在配置中心配置",
    6: "该appkey已被禁用",
    7: "sig错误，接口签名失败",
    8: "业务参数缺失或非法",
    9: "接口请求失败",
    10: "授权token已过期，请重新获取",
    11: "附近暂无空闲司机",
    12: "该城市未开通，获取城市价格表失败",
    14: "这位司机刚被别人选走了，请重选一位",
    20: "订单正在进行中,请稍后重试!",
    -1: "未到报单,暂不支持查询订单费用"
}

# 订单状态分类
PENDING_STATUS = [102, 180]  # 待处理状态
ACTIVE_STATUS = [301, 302, 303]  # 进行中状态
COMPLETED_STATUS = [304]  # 已完成状态
CANCELLED_STATUS = [403, 404]  # 已取消状态
FAILED_STATUS = [501, 506]  # 失败状态

def get_order_status_desc(status_code):
    """
    获取订单状态描述
    :param status_code: 状态码
    :return: 状态描述
    """
    return ORDER_STATUS.get(status_code, "未知状态")


def get_api_response_desc(code):
    """
    获取API返回码描述
    :param code: API返回码
    :return: 返回码描述
    """
    return API_RESPONSE_CODE.get(code, "未知错误")
