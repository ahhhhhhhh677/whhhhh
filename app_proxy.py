from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import requests
import time
import os
import uuid
import hashlib
import sqlite3
import threading
import json
import logging
from typing import Optional, Dict, Any, List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proxy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI服务中转代理")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="."), name="static")

# 添加根路径重定向到客户页面
@app.get("/")
def root():
    return RedirectResponse(url="/static/customer_portal.html")

# 系统信息端点
@app.get("/info")
def system_info():
    return {
        "name": "AI服务中转代理",
        "version": "1.0.0",
        "environment": "production" if os.environ.get("ENVIRONMENT") == "production" else "development",
        "providers": list(PROVIDERS.keys()),
        "products": Config.PRODUCTS
    }

# 数据库初始化
def init_db():
    conn = sqlite3.connect('proxy.db')
    c = conn.cursor()
    
    # 创建用户表
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_key TEXT UNIQUE NOT NULL,
        balance REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建API密钥表
    c.execute('''
    CREATE TABLE IF NOT EXISTS provider_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT NOT NULL,
        api_key TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建请求记录表
    c.execute('''
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_api_key TEXT NOT NULL,
        provider TEXT NOT NULL,
        endpoint TEXT NOT NULL,
        tokens INTEGER DEFAULT 0,
        cost REAL DEFAULT 0,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建订单表
    c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT UNIQUE NOT NULL,
        customer_id TEXT NOT NULL,
        product TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        key_sent TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建分销表
    c.execute('''
    CREATE TABLE IF NOT EXISTS affiliates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        affiliate_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        link TEXT NOT NULL,
        commission_rate REAL DEFAULT 0.2,
        total_commission REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建分销订单表
    c.execute('''
    CREATE TABLE IF NOT EXISTS affiliate_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        affiliate_id TEXT NOT NULL,
        amount REAL NOT NULL,
        commission REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

init_db()

# 导入配置
from config import Config

# 提供商配置
PROVIDERS = {
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "endpoints": ["chat/completions", "completions", "embeddings"]
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "endpoints": ["chat/completions", "completions", "embeddings"]
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "endpoints": ["messages"]
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "endpoints": ["chat/completions"]
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "endpoints": ["chat/completions"]
    },
    "ali": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "endpoints": ["chat/completions"]
    },
    "baidu": {
        "base_url": "https://api.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
        "endpoints": ["completions"]
    },
    "bytedance": {
        "base_url": "https://api.doubao.com/v1",
        "endpoints": ["chat/completions"]
    },
    "minimax": {
        "base_url": "https://api.minimax.chat/v1",
        "endpoints": ["chat/completions"]
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "endpoints": ["chat/completions"]
    }
}

# 定价策略
PRICING = {
    "openai": {
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
    },
    "anthropic": {
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075}
    }
}

# 数据模型
class ProxyRequest(BaseModel):
    provider: str
    endpoint: str
    data: Dict[str, Any]

class UserCreate(BaseModel):
    pass

class BalanceTopup(BaseModel):
    amount: float = Field(gt=0)

class ProviderKeyAdd(BaseModel):
    provider: str
    api_key: str

class OrderCreate(BaseModel):
    customer_id: str
    product: str
    amount: float = Field(gt=0)

class OrderUpdate(BaseModel):
    status: str
    key_sent: Optional[str] = None

class AffiliateCreate(BaseModel):
    name: str
    link: str
    commission_rate: float = Field(gt=0, le=1)

class SalesBotRequest(BaseModel):
    message: str
    customer_id: str

class PaymentVerification(BaseModel):
    payment_screenshot: str
    amount: float = Field(gt=0)
    order_id: str

# 工具函数
def generate_api_key():
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

def get_db_connection():
    return sqlite3.connect('proxy.db')

def get_user_by_api_key(api_key: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE api_key = ?", (api_key,))
    user = c.fetchone()
    conn.close()
    return user

def get_active_provider_keys(provider: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT api_key FROM provider_keys WHERE provider = ? AND status = 'active'", (provider,))
    keys = [row[0] for row in c.fetchall()]
    conn.close()
    return keys

def record_request(user_api_key: str, provider: str, endpoint: str, tokens: int, cost: float, status: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO requests (user_api_key, provider, endpoint, tokens, cost, status) VALUES (?, ?, ?, ?, ?, ?)",
        (user_api_key, provider, endpoint, tokens, cost, status)
    )
    conn.commit()
    conn.close()

def update_balance(api_key: str, amount: float):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE api_key = ?", (amount, api_key))
    conn.commit()
    conn.close()

def create_order(customer_id: str, product: str, amount: float):
    order_id = str(uuid.uuid4())
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (order_id, customer_id, product, amount, status) VALUES (?, ?, ?, ?, ?)",
        (order_id, customer_id, product, amount, "pending")
    )
    conn.commit()
    conn.close()
    return order_id

def update_order(order_id: str, status: str, key_sent: Optional[str] = None):
    conn = get_db_connection()
    c = conn.cursor()
    if key_sent:
        c.execute(
            "UPDATE orders SET status = ?, key_sent = ? WHERE order_id = ?",
            (status, key_sent, order_id)
        )
    else:
        c.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?",
            (status, order_id)
        )
    conn.commit()
    conn.close()

def get_order(order_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    order = c.fetchone()
    conn.close()
    return order

def create_affiliate(name: str, link: str, commission_rate: float):
    affiliate_id = str(uuid.uuid4())
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO affiliates (affiliate_id, name, link, commission_rate) VALUES (?, ?, ?, ?)",
        (affiliate_id, name, link, commission_rate)
    )
    conn.commit()
    conn.close()
    return affiliate_id

def create_affiliate_order(order_id: str, affiliate_id: str, amount: float, commission: float):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO affiliate_orders (order_id, affiliate_id, amount, commission, status) VALUES (?, ?, ?, ?, ?)",
        (order_id, affiliate_id, amount, commission, "pending")
    )
    # 更新分销总佣金
    c.execute(
        "UPDATE affiliates SET total_commission = total_commission + ? WHERE affiliate_id = ?",
        (commission, affiliate_id)
    )
    conn.commit()
    conn.close()

def get_sales_bot_response(message: str):
    # 销售机器人响应逻辑
    message_lower = message.lower()
    
    # 价格表回复
    if any(keyword in message_lower for keyword in ["价格", "多少钱", "报价", "费用"]):
        response = "价格表：\n"
        for product, options in Config.PRODUCTS.items():
            response += f"\n{product}:\n"
            for option, price in options.items():
                response += f"  - {option}: {price}元\n"
        response += "\n付款后发送截图，我自动发卡。"
        return response
    
    # 付款相关回复
    if any(keyword in message_lower for keyword in ["付款", "支付", "转账", "截图"]):
        return "请发送付款截图，我会自动识别并发卡。"
    
    # 其他问题回复
    response = "您好！我是AI API额度自动销售客服。\n\n价格表：\n"
    for product, options in Config.PRODUCTS.items():
        for option, price in options.items():
            response += f"- {product} {option} = {price}元\n"
    response += "\n付款后发送截图，我自动发卡。"
    return response

def process_payment(amount: float, order_id: str):
    # 处理付款逻辑
    order = get_order(order_id)
    if not order:
        return False, "订单不存在"
    
    if order[5] != "pending":
        return False, "订单状态错误"
    
    if abs(order[4] - amount) > 0.01:
        return False, "金额不匹配"
    
    # 模拟向上游购买
    # 实际应用中，这里应该调用上游API购买额度
    key = generate_api_key()
    
    # 更新订单状态
    update_order(order_id, "completed", key)
    
    return True, key

# 限流管理
class RateLimiter:
    def __init__(self):
        self.limits = {}
        self.lock = threading.Lock()
    
    def check_limit(self, api_key: str, max_requests: int = 60, window: int = 60):
        with self.lock:
            current_time = time.time()
            if api_key not in self.limits:
                self.limits[api_key] = []
            
            # 清理过期的请求
            self.limits[api_key] = [t for t in self.limits[api_key] if current_time - t < window]
            
            if len(self.limits[api_key]) >= max_requests:
                return False
            
            self.limits[api_key].append(current_time)
            return True

rate_limiter = RateLimiter()

# 依赖项
def get_current_user(x_api_key: str = Header(...)):
    user = get_user_by_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

# 路由
@app.post("/api/create-user")
def create_user():
    api_key = generate_api_key()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (api_key, balance) VALUES (?, ?)", (api_key, 0))
    conn.commit()
    conn.close()
    return {"api_key": api_key, "balance": 0}

@app.post("/api/topup")
def topup(balance: BalanceTopup, user: tuple = Depends(get_current_user)):
    update_balance(user[1], balance.amount)
    return {"message": f"Successfully topped up {balance.amount} yuan", "new_balance": user[2] + balance.amount}

@app.post("/api/add-provider-key")
def add_provider_key(key: ProviderKeyAdd):
    if key.provider not in Config.PROVIDERS:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO provider_keys (provider, api_key) VALUES (?, ?)", (key.provider, key.api_key))
    conn.commit()
    conn.close()
    
    return {"message": f"Successfully added API key for {key.provider}"}

@app.post("/api/proxy")
async def proxy_request(request: ProxyRequest, user: tuple = Depends(get_current_user)):
    # 检查限流
    if not rate_limiter.check_limit(user[1]):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # 检查提供商
    if request.provider not in PROVIDERS:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    # 检查端点
    if request.endpoint not in PROVIDERS[request.provider]["endpoints"]:
        raise HTTPException(status_code=400, detail="Invalid endpoint")
    
    # 获取提供商API密钥
    provider_keys = get_active_provider_keys(request.provider)
    if not provider_keys:
        raise HTTPException(status_code=503, detail=f"No active API keys for {request.provider}")
    
    # 简单轮询选择API密钥
    key_index = int(time.time() % len(provider_keys))
    provider_key = provider_keys[key_index]
    
    # 构建请求
    base_url = PROVIDERS[request.provider]["base_url"]
    url = f"{base_url}/{request.endpoint}"
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json"
    }
    
    # 根据提供商设置认证头
    if request.provider == "openai" or request.provider == "groq" or request.provider == "together" or request.provider == "deepseek":
        headers["Authorization"] = f"Bearer {provider_key}"
    elif request.provider == "anthropic":
        headers["x-api-key"] = provider_key
        headers["anthropic-version"] = "2023-06-01"
    elif request.provider == "ali":
        headers["Authorization"] = f"Bearer {provider_key}"
    elif request.provider == "baidu":
        # 百度需要特殊处理
        pass
    elif request.provider == "bytedance":
        headers["Authorization"] = f"Bearer {provider_key}"
    elif request.provider == "minimax":
        headers["Authorization"] = f"Bearer {provider_key}"
    
    # 发送请求
    try:
        response = requests.post(url, headers=headers, json=request.data, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 计算token使用量和费用
        tokens = 0
        cost = 0
        
        if request.provider == "openai" and "usage" in result:
            tokens = result["usage"].get("total_tokens", 0)
            model = request.data.get("model", "gpt-3.5-turbo")
            if model in Config.PRICING.get("openai", {}):
                pricing = Config.PRICING["openai"][model]
                cost = (result["usage"].get("prompt_tokens", 0) * pricing["input"] + 
                        result["usage"].get("completion_tokens", 0) * pricing["output"]) / 1000
        
        # 记录请求
        record_request(user[1], request.provider, request.endpoint, tokens, cost, "success")
        
        # 扣除余额
        if cost > 0:
            update_balance(user[1], -cost)
        
        return result
        
    except Exception as e:
        # 记录失败请求
        record_request(user[1], request.provider, request.endpoint, 0, 0, "failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/balance")
def get_balance(user: tuple = Depends(get_current_user)):
    return {"balance": user[2]}

@app.get("/api/stats")
def get_stats(user: tuple = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT provider, COUNT(*), SUM(tokens), SUM(cost) FROM requests WHERE user_api_key = ? GROUP BY provider",
        (user[1],)
    )
    stats = []
    for row in c.fetchall():
        stats.append({
            "provider": row[0],
            "requests": row[1],
            "tokens": row[2] or 0,
            "cost": row[3] or 0
        })
    conn.close()
    return {"stats": stats}

@app.post("/api/order")
def create_order_endpoint(order: OrderCreate):
    order_id = create_order(order.customer_id, order.product, order.amount)
    return {"order_id": order_id, "status": "pending"}

@app.get("/api/order/{order_id}")
def get_order_endpoint(order_id: str):
    order = get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order_id": order[1],
        "customer_id": order[2],
        "product": order[3],
        "amount": order[4],
        "status": order[5],
        "key_sent": order[6],
        "created_at": order[7]
    }

@app.put("/api/order/{order_id}/update")
def update_order_endpoint(order_id: str, update: OrderUpdate):
    order = get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    update_order(order_id, update.status, update.key_sent)
    return {"message": "Order updated successfully"}

@app.post("/api/affiliate")
def create_affiliate_endpoint(affiliate: AffiliateCreate):
    affiliate_id = create_affiliate(affiliate.name, affiliate.link, affiliate.commission_rate)
    return {"affiliate_id": affiliate_id, "link": affiliate.link}

@app.post("/api/sales-bot")
def sales_bot_endpoint(request: SalesBotRequest):
    response = get_sales_bot_response(request.message)
    return {"response": response}

@app.post("/api/payment/verify")
def verify_payment_endpoint(verification: PaymentVerification):
    try:
        success, result = process_payment(verification.amount, verification.order_id)
        if success:
            logger.info(f"Payment verified successfully for order {verification.order_id}")
            return {"success": True, "key": result, "message": "Payment verified successfully"}
        else:
            logger.warning(f"Payment verification failed for order {verification.order_id}: {result}")
            raise HTTPException(status_code=400, detail=result)
    except Exception as e:
        logger.error(f"Error in payment verification: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# 健康检查端点
@app.get("/health")
def health_check():
    try:
        # 检查数据库连接
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        
        # 检查API密钥
        providers = get_active_provider_keys("openai")
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "providers": {
                "openai": len(providers) > 0
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        }

# 系统状态端点
@app.get("/status")
def system_status():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # 获取订单统计
        c.execute("SELECT COUNT(*), SUM(amount) FROM orders WHERE status = 'completed'")
        order_stats = c.fetchone()
        
        # 获取请求统计
        c.execute("SELECT COUNT(*), SUM(tokens), SUM(cost) FROM requests")
        request_stats = c.fetchone()
        
        # 获取用户统计
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "running",
            "timestamp": time.time(),
            "statistics": {
                "orders": {
                    "completed": order_stats[0] or 0,
                    "total_amount": order_stats[1] or 0
                },
                "requests": {
                    "total": request_stats[0] or 0,
                    "tokens": request_stats[1] or 0,
                    "cost": request_stats[2] or 0
                },
                "users": user_count
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return {
            "status": "error",
            "timestamp": time.time(),
            "error": str(e)
        }

# 监控线程
class MonitorThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.error_count = 0
    
    def run(self):
        while Config.MONITORING_ENABLED:
            try:
                # 检查健康状态
                response = requests.get("http://localhost:8000/health", timeout=5)
                status = response.json()
                
                if status.get("status") == "healthy":
                    self.error_count = 0
                    logger.info("System health check passed")
                else:
                    self.error_count += 1
                    logger.warning(f"System health check failed: {status.get('error')}")
                    
                    # 如果错误次数超过阈值，发送警报
                    if self.error_count >= Config.ALERT_THRESHOLD:
                        logger.error("Alert: System health check failed multiple times")
                        # 这里可以添加发送邮件或短信警报的代码
            except Exception as e:
                self.error_count += 1
                logger.error(f"Error during health check: {str(e)}")
                
                # 如果错误次数超过阈值，发送警报
                if self.error_count >= Config.ALERT_THRESHOLD:
                    logger.error("Alert: System health check failed multiple times")
            
            # 等待下一次检查
            time.sleep(Config.CHECK_INTERVAL)

if __name__ == "__main__":
    # 启动监控线程
    monitor = MonitorThread()
    monitor.start()
    logger.info("Monitoring thread started")
    
    # 启动服务
    import uvicorn
    logger.info(f"Starting AI service proxy server on {Config.HOST}:{Config.PORT}")
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)