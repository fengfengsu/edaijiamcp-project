# e代驾 MCP 服务

基于e代驾开放API的MCP (Model Context Protocol) 服务，提供代驾服务的完整功能。

## 功能特性

- **预估费用**: 根据起终点位置预估代驾费用
- **叫代驾下单**: 创建代驾订单，支持自动token管理
- **Token管理**: 智能token获取、存储和刷新机制
- **自动重试**: token过期时自动刷新并重试操作
- **参数验证**: 完善的输入参数验证和错误处理

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

### 1. estimate_cost
预估代驾费用
- **参数**: 
  - `start_address`: 起始地址
  - `start_longitude`: 起始经度
  - `start_latitude`: 起始纬度
  - `end_address`: 目的地地址
  - `end_longitude`: 目的地经度
  - `end_latitude`: 目的地纬度
  - `phone`: 用户手机号（11位数字）
- **返回**: 预估费用信息，包括距离、时间和价格
- **特性**: 自动检查和刷新token，支持token过期重试

### 2. call_driver
叫代驾下单
- **参数**:
  - `start_address`: 起始地址
  - `start_longitude`: 起始经度
  - `start_latitude`: 起始纬度
  - `end_address`: 目的地地址
  - `end_longitude`: 目的地经度
  - `end_latitude`: 目的地纬度
  - `phone`: 用户手机号（11位数字）
  - `contact_phone`: 联系电话（可选，代叫订单必传）
- **返回**: 下单结果，包括订单号和状态
- **特性**: 自动生成唯一订单号，支持token校验失败重试

### 3. refresh_token
刷新用户token
- **参数**:
  - `phone`: 用户手机号（11位数字）
- **返回**: token刷新结果和状态
- **特性**: 手动刷新指定手机号的认证token

## Token管理机制

- **自动检测**: 系统自动检查本地是否存在对应手机号的token
- **智能获取**: 如无本地token，自动调用API获取新token
- **本地存储**: token自动保存到 `edjserver/tokens/` 目录
- **过期处理**: API返回token过期时自动刷新并重试
- **校验重试**: token校验失败时自动刷新token并重新执行操作

## 使用流程

1. **预估费用**: 使用 `estimate_cost` 提供起终点信息和手机号，获取预估价格
2. **确认下单**: 使用 `call_driver` 提供相同信息进行下单
3. **Token管理**: 如需要，使用 `refresh_token` 手动刷新token

## 技术特性

- **智能重试**: token相关错误自动处理，无需手动干预
- **参数验证**: 完善的输入验证，确保数据格式正确
- **错误处理**: 详细的错误信息返回，便于问题定位
- **唯一订单号**: 基于时间戳和UUID生成唯一订单标识

## 运行方式

```bash
python edaijiamcp.py
```

## 依赖项

- **mcp**: Model Context Protocol库
- **requests**: HTTP请求库
- **python-dotenv**: 环境变量管理
- **uuid**: 唯一标识符生成
- **time**: 时间戳生成
- **json**: JSON数据处理
- **os**: 文件系统操作

## 项目结构

```
edaijiamcp/
├── edaijiamcp.py          # MCP服务主文件
├── edjserver/             # e代驾API封装
│   ├── EdjApi.py         # 主要API接口
│   ├── EdjSignUtils.py   # 签名工具
│   ├── EdjSystemParams.py # 系统参数
│   └── tokens/           # token存储目录
├── README.md             # 项目文档
└── pyproject.toml        # 项目配置
```