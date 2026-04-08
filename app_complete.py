from fastapi import FastAPI, HTTPException, Header, Depends, Request
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
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_complete.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI聊天平台 - 类似rsk.cn")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="."), name="static")

# 根路径重定向到主页面
@app.get("/")
def root():
    return RedirectResponse(url="/static/index_complete.html")

# 配置类
class Config:
    # 产品配置
    PRODUCTS = {
        "GPT-4o": {
            "100万token": 30,
            "500万token": 120,
            "无限包月": 199
        },
        "Claude-3.5": {
            "100万token": 25,
            "500万token": 100,
            "无限包月": 168
        },
        "Llama-3.3": {
            "100万token": 15,
            "500万token": 60,
            "无限包月": 99
        }
    }
    
    # 会员配置
    MEMBERSHIP_TIERS = {
        "free": {
            "name": "免费版",
            "daily_limit": 10,
            "models": ["Qwen/Qwen2.5-7B-Instruct"],
            "features": ["基础聊天"]
        },
        "pro": {
            "name": "Pro会员",
            "daily_limit": 100,
            "models": ["Qwen/Qwen2.5-7B-Instruct", "deepseek-ai/DeepSeek-R1"],
            "features": ["高级聊天", "画图", "写作"],
            "price_monthly": 29,
            "price_yearly": 299
        },
        "ultimate": {
            "name": "Ultimate会员",
            "daily_limit": -1,
            "models": ["Qwen/Qwen2.5-7B-Instruct", "deepseek-ai/DeepSeek-R1", "meta-llama/Llama-3.3-70B-Instruct"],
            "features": ["全部功能", "视频", "思维导图", "翻译"],
            "price_monthly": 99,
            "price_yearly": 999
        }
    }
    
    # 任务配置
    TASKS = [
        {"id": "daily_login", "name": "每日登录", "reward": 10, "type": "points"},
        {"id": "share", "name": "分享给好友", "reward": 50, "type": "points"},
        {"id": "complete_5_chats", "name": "完成5次对话", "reward": 100, "type": "points"},
        {"id": "invite_friend", "name": "邀请好友注册", "reward": 200, "type": "points"}
    ]

# 提供商配置
PROVIDERS = {
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "endpoints": ["chat/completions", "completions", "embeddings"]
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "endpoints": ["chat/completions", "completions", "embeddings"]
    }
}

# 数据库初始化
def init_db():
    conn = sqlite3.connect('platform.db')
    c = conn.cursor()
    
    # 用户表
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password TEXT NOT NULL,
        api_key TEXT UNIQUE NOT NULL,
        balance REAL DEFAULT 0,
        points INTEGER DEFAULT 0,
        membership_tier TEXT DEFAULT 'free',
        membership_expiry TIMESTAMP,
        daily_usage INTEGER DEFAULT 0,
        last_login_date TEXT,
        invite_code TEXT UNIQUE,
        invited_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 订单表
    c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        product TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        payment_method TEXT,
        payment_time TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 任务完成表
    c.execute('''
    CREATE TABLE IF NOT EXISTS task_completions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task_id TEXT NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 邀请记录表
    c.execute('''
    CREATE TABLE IF NOT EXISTS invitations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inviter_id INTEGER NOT NULL,
        invitee_id INTEGER NOT NULL,
        reward_given INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 对话记录表
    c.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT,
        model TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 消息表
    c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        tokens INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

init_db()

# 数据模型
class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    invite_code: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class OrderCreate(BaseModel):
    product: str
    amount: float
    payment_method: str = "wechat"

class ChatMessage(BaseModel):
    conversation_id: Optional[int] = None
    model: str
    messages: List[Dict[str, str]]

class TaskComplete(BaseModel):
    task_id: str

# 工具函数
def generate_api_key():
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

def generate_invite_code():
    return ''.join([str(uuid.uuid4().hex[:8]).upper()])

def get_db_connection():
    return sqlite3.connect('platform.db')

def get_user_by_api_key(api_key: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE api_key = ?", (api_key,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def check_daily_limit(user):
    if user[7] == 'ultimate':
        return True
    if user[7] == 'pro' and user[8] < 100:
        return True
    if user[7] == 'free' and user[8] < 10:
        return True
    today = datetime.now().strftime('%Y-%m-%d')
    if user[9] != today:
        return True
    return False

def update_daily_usage(user_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("UPDATE users SET daily_usage = daily_usage + 1, last_login_date = ? WHERE id = ?", (today, user_id))
    conn.commit()
    conn.close()

# 路由
@app.post("/api/register")
def register(user_data: UserRegister):
    conn = get_db_connection()
    c = conn.cursor()
    
    # 检查用户名是否存在
    c.execute("SELECT id FROM users WHERE username = ?", (user_data.username,))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    api_key = generate_api_key()
    invite_code = generate_invite_code()
    hashed_pwd = hash_password(user_data.password)
    
    inviter_id = None
    if user_data.invite_code:
        c.execute("SELECT id FROM users WHERE invite_code = ?", (user_data.invite_code,))
        inviter = c.fetchone()
        if inviter:
            inviter_id = inviter[0]
    
    c.execute(
        "INSERT INTO users (username, email, password, api_key, invite_code, invited_by) VALUES (?, ?, ?, ?, ?, ?)",
        (user_data.username, user_data.email, hashed_pwd, api_key, invite_code, inviter_id)
    )
    
    user_id = c.lastrowid
    
    if inviter_id:
        c.execute("INSERT INTO invitations (inviter_id, invitee_id) VALUES (?, ?)", (inviter_id, user_id))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "api_key": api_key, "invite_code": invite_code}

@app.post("/api/login")
def login(user_data: UserLogin):
    conn = get_db_connection()
    c = conn.cursor()
    
    hashed_pwd = hash_password(user_data.password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user_data.username, hashed_pwd))
    user = c.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    today = datetime.now().strftime('%Y-%m-%d')
    if user[9] != today:
        c.execute("UPDATE users SET daily_usage = 0, last_login_date = ? WHERE id = ?", (today, user[0]))
        
        try:
            c.execute("INSERT INTO task_completions (user_id, task_id) VALUES (?, ?)", (user[0], "daily_login"))
            c.execute("UPDATE users SET points = points + 10 WHERE id = ?", (user[0],))
        except:
            pass
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "api_key": user[4],
        "user": {
            "id": user[0],
            "username": user[1],
            "balance": user[5],
            "points": user[6],
            "membership_tier": user[7],
            "daily_usage": user[8]
        }
    }

@app.get("/api/user/profile")
def get_profile(api_key: str = Header(..., alias="X-API-Key")):
    user = get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "balance": user[5],
        "points": user[6],
        "membership_tier": user[7],
        "membership_expiry": user[8],
        "daily_usage": user[9],
        "invite_code": user[10]
    }

@app.post("/api/order/create")
def create_order(order_data: OrderCreate, api_key: str = Header(..., alias="X-API-Key")):
    user = get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    order_id = str(uuid.uuid4())
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (order_id, user_id, product, amount, payment_method) VALUES (?, ?, ?, ?, ?)",
        (order_id, user[0], order_data.product, order_data.amount, order_data.payment_method)
    )
    conn.commit()
    conn.close()
    
    return {"success": True, "order_id": order_id}

@app.get("/api/order/{order_id}")
def get_order(order_id: str, api_key: str = Header(..., alias="X-API-Key")):
    user = get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE order_id = ? AND user_id = ?", (order_id, user[0]))
    order = c.fetchone()
    conn.close()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    return {
        "order_id": order[1],
        "product": order[3],
        "amount": order[4],
        "status": order[5],
        "created_at": order[7]
    }

@app.get("/api/membership/tiers")
def get_membership_tiers():
    return Config.MEMBERSHIP_TIERS

@app.get("/api/tasks")
def get_tasks(api_key: str = Header(..., alias="X-API-Key")):
    user = get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT task_id FROM task_completions WHERE user_id = ? AND date(completed_at) = ?", (user[0], today))
    completed = [row[0] for row in c.fetchall()]
    conn.close()
    
    tasks = []
    for task in Config.TASKS:
        tasks.append({
            **task,
            "completed": task["id"] in completed
        })
    
    return tasks

@app.post("/api/tasks/complete")
def complete_task(task_data: TaskComplete, api_key: str = Header(..., alias="X-API-Key")):
    user = get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    task = next((t for t in Config.TASKS if t["id"] == task_data.task_id), None)
    if not task:
        raise HTTPException(status_code=400, detail="任务不存在")
    
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO task_completions (user_id, task_id) VALUES (?, ?)", (user[0], task["id"]))
        c.execute("UPDATE users SET points = points + ? WHERE id = ?", (task["reward"], user[0]))
        conn.commit()
        conn.close()
        return {"success": True, "reward": task["reward"]}
    except:
        conn.close()
        raise HTTPException(status_code=400, detail="今天已完成此任务")

@app.get("/api/conversations")
def get_conversations(api_key: str = Header(..., alias="X-API-Key")):
    user = get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM conversations WHERE user_id = ? ORDER BY created_at DESC", (user[0],))
    conversations = c.fetchall()
    conn.close()
    
    return [
        {
            "id": conv[0],
            "title": conv[2],
            "model": conv[3],
            "created_at": conv[4]
        }
        for conv in conversations
    ]

@app.post("/api/chat")
def chat(chat_data: ChatMessage, api_key: str = Header(..., alias="X-API-Key")):
    user = get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    if not check_daily_limit(user):
        raise HTTPException(status_code=429, detail="今日使用次数已达上限")
    
    membership = Config.MEMBERSHIP_TIERS.get(user[7], Config.MEMBERSHIP_TIERS["free"])
    if chat_data.model not in membership["models"]:
        raise HTTPException(status_code=403, detail="您的会员等级不支持此模型")
    
    conversation_id = chat_data.conversation_id
    if not conversation_id:
        conn = get_db_connection()
        c = conn.cursor()
        title = chat_data.messages[0]["content"][:30] if chat_data.messages else "新对话"
        c.execute("INSERT INTO conversations (user_id, title, model) VALUES (?, ?, ?)", (user[0], title, chat_data.model))
        conversation_id = c.lastrowid
        conn.commit()
        conn.close()
    
    conn = get_db_connection()
    c = conn.cursor()
    for msg in chat_data.messages:
        c.execute("INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)", (conversation_id, msg["role"], msg["content"]))
    conn.commit()
    conn.close()
    
    update_daily_usage(user[0])
    
    return {
        "success": True,
        "conversation_id": conversation_id,
        "message": "模拟响应（需要配置真实API密钥）"
    }

@app.get("/api/conversation/{conv_id}")
def get_conversation(conv_id: int, api_key: str = Header(..., alias="X-API-Key")):
    user = get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at", (conv_id,))
    messages = c.fetchall()
    conn.close()
    
    return [
        {
            "id": msg[0],
            "role": msg[2],
            "content": msg[3],
            "tokens": msg[4],
            "created_at": msg[5]
        }
        for msg in messages
    ]

@app.get("/api/status")
def system_status():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM conversations")
    conv_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM orders WHERE status = 'completed'")
    order_count = c.fetchone()[0]
    
    conn.close()
    
    return {
        "status": "running",
        "user_count": user_count,
        "conversation_count": conv_count,
        "order_count": order_count
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
