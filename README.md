# e代驾 MCP 服务

基于e代驾开放API的MCP (Model Context Protocol) 服务，提供代驾服务的完整功能。

## 功能特性

- **用户叫代驾**: 收集用户手机号和出发地信息
- **距离计算**: 计算出发地到目的地的距离和预估价格
- **订单创建**: 创建代驾订单
- **状态跟踪**: 实时查询订单状态（等待接单、司机接单、司机就位、行程中、订单完成等）
- **订单取消**: 取消已创建的订单

## 环境配置

### 1. 创建环境变量文件
复制 `.env.example` 文件为 `.env`：
```bash
cp .env.example .env
```

### 2. 配置API密钥
在 `.env` 文件中设置您的API密钥：
```
APP_KEY=your_app_key_here
SECRET=your_secret_here
API_BASE_URL=https://openapi.d.edaijia.cn
```

**注意**: `.env` 文件包含敏感信息，已被添加到 `.gitignore` 中，不会被提交到版本控制系统。

## 可用工具

### 1. call_driver
用户叫代驾服务
- **参数**: 
  - `phone`: 用户手机号（11位数字）
  - `departure`: 出发地地址
- **返回**: 提示信息，引导用户提供目的地以获取价格预估

### 2. calculate_distance_and_price
计算两地距离并显示代驾预估价格
- **参数**:
  - `departure`: 出发地地址
  - `destination`: 目的地地址
- **返回**: 距离、预估时间和价格信息

### 3. create_order
创建代驾订单
- **参数**:
  - `phone`: 用户手机号（11位数字）
  - `departure`: 出发地地址
  - `destination`: 目的地地址（可选）
- **返回**: 订单创建结果和订单号

### 4. check_order_status
查询订单实时状态
- **参数**:
  - `order_id`: 订单号
- **返回**: 订单详细状态信息，包括司机信息（如有）

### 5. cancel_order
取消订单
- **参数**:
  - `order_id`: 订单号
  - `reason`: 取消原因（可选）
- **返回**: 取消结果

## 订单状态说明

- **等待接单**: 订单已创建，等待司机接单
- **司机已接单**: 司机已接受订单，正在前往出发地
- **司机已就位**: 司机已到达出发地，等待用户上车
- **行程中**: 代驾服务进行中
- **订单完成**: 代驾服务已完成
- **订单取消**: 订单已被取消

## 使用流程

1. **叫代驾**: 使用 `call_driver` 提供手机号和出发地
2. **查看价格**: 使用 `calculate_distance_and_price` 查看距离和预估价格
3. **创建订单**: 使用 `create_order` 创建正式订单
4. **跟踪状态**: 使用 `check_order_status` 实时查询订单状态
5. **取消订单**: 如需取消，使用 `cancel_order`

## 运行方式

```bash
python edaijiamcp.py
```

## 依赖项

- httpx: HTTP客户端库
- mcp: Model Context Protocol库
- python-dotenv: 环境变量管理
- hashlib: 用于生成API签名
- time: 用于时间戳生成