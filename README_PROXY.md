# AI服务中转代理系统

## 项目简介

这是一个AI服务中转代理系统，支持多个AI服务提供商，包括：
- 海外：OpenAI、Anthropic、Groq、Together
- 国内：阿里通义、百度文心、字节豆包、MiniMax、DeepSeek

系统功能包括：
- API密钥管理
- 请求转发
- 负载均衡（多Key轮询）
- 限流控制
- 费用计算和余额管理
- 使用统计

## 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn requests
```

### 2. 启动服务

```bash
python app_proxy.py
```

服务将在 `http://0.0.0.0:8000` 上运行。

### 3. 访问管理页面

打开浏览器访问 `http://localhost:8000/proxy_admin.html`，进入管理界面。

## API文档

### 1. 创建用户

**请求**：
```bash
POST /api/create-user
```

**响应**：
```json
{
  "api_key": "6bc7e63e7eb48de1f346585095c70a8518f4db233a6058708a68bdce928153f8",
  "balance": 0
}
```

### 2. 充值余额

**请求**：
```bash
POST /api/topup
Headers: x-api-key: YOUR_API_KEY
Body: {"amount": 100}
```

**响应**：
```json
{
  "message": "Successfully topped up 100.0 yuan",
  "new_balance": 100.0
}
```

### 3. 添加提供商API密钥

**请求**：
```bash
POST /api/add-provider-key
Body: {"provider": "openai", "api_key": "YOUR_OPENAI_KEY"}
```

**响应**：
```json
{
  "message": "Successfully added API key for openai"
}
```

### 4. 代理请求

**请求**：
```bash
POST /api/proxy
Headers: x-api-key: YOUR_API_KEY
Body: {
  "provider": "openai",
  "endpoint": "chat/completions",
  "data": {
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }
}
```

**响应**：
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "gpt-3.5-turbo-0613",
  "usage": {
    "prompt_tokens": 13,
    "completion_tokens": 7,
    "total_tokens": 20
  },
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "你好！我是一个AI助手，有什么可以帮助你的吗？"
      },
      "finish_reason": "stop",
      "index": 0
    }
  ]
}
```

### 5. 查询余额

**请求**：
```bash
GET /api/balance
Headers: x-api-key: YOUR_API_KEY
```

**响应**：
```json
{
  "balance": 99.99
}
```

### 6. 查询统计

**请求**：
```bash
GET /api/stats
Headers: x-api-key: YOUR_API_KEY
```

**响应**：
```json
{
  "stats": [
    {
      "provider": "openai",
      "requests": 5,
      "tokens": 100,
      "cost": 0.01
    }
  ]
}
```

## 定价策略

根据2026年市场行情，建议采用以下定价策略：

- 零售价比官方低20%-30%
- 套餐：10元/万Token、50元/5万Token、200元/25万Token
- 企业客户：阶梯价、专属客服、SLA保障

## 获客渠道

- 线上：GitHub、开发者社区、AI交流群、闲鱼、小红书、知识星球
- 线下：技术沙龙、创业孵化器、中小企业服务

## 技术特点

1. **多提供商支持**：集成了9个主流AI服务提供商
2. **负载均衡**：多Key轮询，提高可用性
3. **限流控制**：防止API滥用
4. **费用计算**：自动计算Token使用量和费用
5. **实时统计**：详细的使用统计和分析
6. **简单易用**：提供Web管理界面，操作简单

## 部署建议

1. **新手方案**：使用现成中转面板（如本系统），部署在一台电脑或轻量服务器上，添加域名和SSL，生成子密钥售卖

2. **放大方案**：
   - API服务池
   - 负载均衡
   - 多Key轮询
   - 限流控制
   - 监控系统

## 注意事项

1. 请确保添加真实的API密钥，否则代理请求会失败
2. 定期检查API密钥的使用情况，避免密钥过期
3. 根据实际需求调整限流参数
4. 建议使用HTTPS协议，保障API密钥安全

## 故障排除

1. **代理请求失败**：检查提供商API密钥是否正确，网络连接是否正常
2. **余额不足**：及时充值
3. **限流错误**：减少请求频率，或联系管理员调整限流参数
4. **数据库错误**：检查proxy.db文件权限，确保可读写

## 联系方式

如有问题或建议，欢迎联系我们。