from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse, RedirectResponse
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
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('affiliate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI服务代理管理系统")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="."), name="static")

# 数据库初始化
def init_db():
    conn = sqlite3.connect('affiliate.db')
    c = conn.cursor()
    
    # 创建代理表
    c.execute('''
    CREATE TABLE IF NOT EXISTS affiliates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        affiliate_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        level TEXT DEFAULT '初级',
        commission_rate REAL DEFAULT 0.15,
        total_commission REAL DEFAULT 0,
        total_sales REAL DEFAULT 0,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建代理订单表
    c.execute('''
    CREATE TABLE IF NOT EXISTS affiliate_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        affiliate_id TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        product TEXT NOT NULL,
        amount REAL NOT NULL,
        commission REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建推广链接表
    c.execute('''
    CREATE TABLE IF NOT EXISTS referral_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_id TEXT UNIQUE NOT NULL,
        affiliate_id TEXT NOT NULL,
        url TEXT NOT NULL,
        clicks INTEGER DEFAULT 0,
        conversions INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建佣金结算表
    c.execute('''
    CREATE TABLE IF NOT EXISTS commission_withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        withdrawal_id TEXT UNIQUE NOT NULL,
        affiliate_id TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP
    )''')
    
    # 创建代理培训表
    c.execute('''
    CREATE TABLE IF NOT EXISTS affiliate_trainings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        training_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        type TEXT DEFAULT 'online',
        duration INTEGER DEFAULT 60,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建代理培训记录表
    c.execute('''
    CREATE TABLE IF NOT EXISTS affiliate_training_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id TEXT UNIQUE NOT NULL,
        affiliate_id TEXT NOT NULL,
        training_id TEXT NOT NULL,
        status TEXT DEFAULT 'completed',
        score INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建营销材料表
    c.execute('''
    CREATE TABLE IF NOT EXISTS marketing_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        type TEXT DEFAULT 'image',
        url TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建技术支持表
    c.execute('''
    CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT UNIQUE NOT NULL,
        affiliate_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        status TEXT DEFAULT 'open',
        priority TEXT DEFAULT 'medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

init_db()

# 数据模型
class AffiliateCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class AffiliateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    level: Optional[str] = None
    commission_rate: Optional[float] = Field(None, ge=0, le=1)
    status: Optional[str] = None

class ReferralLinkCreate(BaseModel):
    affiliate_id: str
    url: str

class OrderCreate(BaseModel):
    affiliate_id: str
    customer_id: str
    product: str
    amount: float = Field(gt=0)

class WithdrawalCreate(BaseModel):
    affiliate_id: str
    amount: float = Field(gt=0)

class TrainingCreate(BaseModel):
    title: str
    content: str
    type: Optional[str] = "online"
    duration: Optional[int] = 60

class TrainingRecordCreate(BaseModel):
    affiliate_id: str
    training_id: str
    score: Optional[int] = 0

class MarketingMaterialCreate(BaseModel):
    title: str
    type: Optional[str] = "image"
    url: str
    description: Optional[str] = None

class SupportTicketCreate(BaseModel):
    affiliate_id: str
    title: str
    content: str
    priority: Optional[str] = "medium"

# 工具函数
def generate_affiliate_id():
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]

def generate_link_id():
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:12]

def generate_withdrawal_id():
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]

def generate_training_id():
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]

def generate_record_id():
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]

def generate_material_id():
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]

def generate_ticket_id():
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]

def get_db_connection():
    return sqlite3.connect('affiliate.db')

def create_affiliate(name: str, email: str, phone: Optional[str] = None):
    affiliate_id = generate_affiliate_id()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO affiliates (affiliate_id, name, email, phone) VALUES (?, ?, ?, ?)",
        (affiliate_id, name, email, phone)
    )
    conn.commit()
    conn.close()
    return affiliate_id

def get_affiliate(affiliate_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM affiliates WHERE affiliate_id = ?", (affiliate_id,))
    affiliate = c.fetchone()
    conn.close()
    return affiliate

def update_affiliate(affiliate_id: str, updates: Dict[str, Any]):
    conn = get_db_connection()
    c = conn.cursor()
    
    set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
    values = list(updates.values()) + [affiliate_id]
    
    c.execute(f"UPDATE affiliates SET {set_clause} WHERE affiliate_id = ?", values)
    conn.commit()
    conn.close()

def create_referral_link(affiliate_id: str, url: str):
    link_id = generate_link_id()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO referral_links (link_id, affiliate_id, url) VALUES (?, ?, ?)",
        (link_id, affiliate_id, url)
    )
    conn.commit()
    conn.close()
    return link_id

def create_affiliate_order(affiliate_id: str, customer_id: str, product: str, amount: float):
    affiliate = get_affiliate(affiliate_id)
    if not affiliate:
        return None
    
    commission_rate = affiliate[6]
    commission = amount * commission_rate
    
    order_id = str(uuid.uuid4())
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO affiliate_orders (order_id, affiliate_id, customer_id, product, amount, commission) VALUES (?, ?, ?, ?, ?, ?)",
        (order_id, affiliate_id, customer_id, product, amount, commission)
    )
    
    # 更新代理的总佣金和总销售额
    c.execute(
        "UPDATE affiliates SET total_commission = total_commission + ?, total_sales = total_sales + ? WHERE affiliate_id = ?",
        (commission, amount, affiliate_id)
    )
    
    conn.commit()
    conn.close()
    return order_id

def get_affiliate_orders(affiliate_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM affiliate_orders WHERE affiliate_id = ? ORDER BY created_at DESC", (affiliate_id,))
    orders = c.fetchall()
    conn.close()
    return orders

def get_affiliate_stats(affiliate_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT total_commission, total_sales FROM affiliates WHERE affiliate_id = ?", (affiliate_id,))
    stats = c.fetchone()
    conn.close()
    return stats

def create_withdrawal(affiliate_id: str, amount: float):
    affiliate = get_affiliate(affiliate_id)
    if not affiliate:
        return None
    
    total_commission = affiliate[7]
    if amount > total_commission:
        return None
    
    withdrawal_id = generate_withdrawal_id()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO commission_withdrawals (withdrawal_id, affiliate_id, amount) VALUES (?, ?, ?)",
        (withdrawal_id, affiliate_id, amount)
    )
    
    # 更新代理的总佣金
    c.execute(
        "UPDATE affiliates SET total_commission = total_commission - ? WHERE affiliate_id = ?",
        (amount, affiliate_id)
    )
    
    conn.commit()
    conn.close()
    return withdrawal_id

def get_affiliate_withdrawals(affiliate_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM commission_withdrawals WHERE affiliate_id = ? ORDER BY created_at DESC", (affiliate_id,))
    withdrawals = c.fetchall()
    conn.close()
    return withdrawals

def create_training(title: str, content: str, training_type: str = "online", duration: int = 60):
    training_id = generate_training_id()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO affiliate_trainings (training_id, title, content, type, duration) VALUES (?, ?, ?, ?, ?)",
        (training_id, title, content, training_type, duration)
    )
    conn.commit()
    conn.close()
    return training_id

def get_trainings():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM affiliate_trainings ORDER BY created_at DESC")
    trainings = c.fetchall()
    conn.close()
    return trainings

def create_training_record(affiliate_id: str, training_id: str, score: int = 0):
    record_id = generate_record_id()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO affiliate_training_records (record_id, affiliate_id, training_id, score) VALUES (?, ?, ?, ?)",
        (record_id, affiliate_id, training_id, score)
    )
    conn.commit()
    conn.close()
    return record_id

def get_affiliate_training_records(affiliate_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM affiliate_training_records WHERE affiliate_id = ? ORDER BY created_at DESC", (affiliate_id,))
    records = c.fetchall()
    conn.close()
    return records

def create_marketing_material(title: str, material_type: str = "image", url: str = "", description: str = None):
    material_id = generate_material_id()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO marketing_materials (material_id, title, type, url, description) VALUES (?, ?, ?, ?, ?)",
        (material_id, title, material_type, url, description)
    )
    conn.commit()
    conn.close()
    return material_id

def get_marketing_materials():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM marketing_materials ORDER BY created_at DESC")
    materials = c.fetchall()
    conn.close()
    return materials

def create_support_ticket(affiliate_id: str, title: str, content: str, priority: str = "medium"):
    ticket_id = generate_ticket_id()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO support_tickets (ticket_id, affiliate_id, title, content, priority) VALUES (?, ?, ?, ?, ?)",
        (ticket_id, affiliate_id, title, content, priority)
    )
    conn.commit()
    conn.close()
    return ticket_id

def get_affiliate_support_tickets(affiliate_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM support_tickets WHERE affiliate_id = ? ORDER BY created_at DESC", (affiliate_id,))
    tickets = c.fetchall()
    conn.close()
    return tickets

def update_support_ticket(ticket_id: str, status: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE support_tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?",
        (status, ticket_id)
    )
    conn.commit()
    conn.close()

def get_all_affiliates():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM affiliates ORDER BY created_at DESC")
    affiliates = c.fetchall()
    conn.close()
    return affiliates

def get_all_orders():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM affiliate_orders ORDER BY created_at DESC")
    orders = c.fetchall()
    conn.close()
    return orders

def get_all_withdrawals():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM commission_withdrawals ORDER BY created_at DESC")
    withdrawals = c.fetchall()
    conn.close()
    return withdrawals

def get_all_support_tickets():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM support_tickets ORDER BY created_at DESC")
    tickets = c.fetchall()
    conn.close()
    return tickets

# 路由
@app.get("/")
def root():
    return RedirectResponse(url="/static/affiliate_admin.html")

@app.post("/api/affiliates")
def create_affiliate_endpoint(affiliate: AffiliateCreate):
    affiliate_id = create_affiliate(affiliate.name, affiliate.email, affiliate.phone)
    return {"affiliate_id": affiliate_id, "status": "created"}

@app.get("/api/affiliates/{affiliate_id}")
def get_affiliate_endpoint(affiliate_id: str):
    affiliate = get_affiliate(affiliate_id)
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    return {
        "affiliate_id": affiliate[1],
        "name": affiliate[2],
        "email": affiliate[3],
        "phone": affiliate[4],
        "level": affiliate[5],
        "commission_rate": affiliate[6],
        "total_commission": affiliate[7],
        "total_sales": affiliate[8],
        "status": affiliate[9],
        "created_at": affiliate[10],
        "last_login": affiliate[11]
    }

@app.put("/api/affiliates/{affiliate_id}")
def update_affiliate_endpoint(affiliate_id: str, affiliate: AffiliateUpdate):
    updates = {}
    if affiliate.name:
        updates["name"] = affiliate.name
    if affiliate.email:
        updates["email"] = affiliate.email
    if affiliate.phone:
        updates["phone"] = affiliate.phone
    if affiliate.level:
        updates["level"] = affiliate.level
    if affiliate.commission_rate is not None:
        updates["commission_rate"] = affiliate.commission_rate
    if affiliate.status:
        updates["status"] = affiliate.status
    
    if updates:
        update_affiliate(affiliate_id, updates)
    
    return {"message": "Affiliate updated successfully"}

@app.get("/api/affiliates")
def get_all_affiliates_endpoint():
    affiliates = get_all_affiliates()
    return {
        "affiliates": [
            {
                "affiliate_id": affiliate[1],
                "name": affiliate[2],
                "email": affiliate[3],
                "phone": affiliate[4],
                "level": affiliate[5],
                "commission_rate": affiliate[6],
                "total_commission": affiliate[7],
                "total_sales": affiliate[8],
                "status": affiliate[9],
                "created_at": affiliate[10],
                "last_login": affiliate[11]
            }
            for affiliate in affiliates
        ]
    }

@app.post("/api/referral-links")
def create_referral_link_endpoint(link: ReferralLinkCreate):
    link_id = create_referral_link(link.affiliate_id, link.url)
    referral_url = f"http://localhost:8000/r/{link_id}"
    return {"link_id": link_id, "referral_url": referral_url}

@app.post("/api/orders")
def create_order_endpoint(order: OrderCreate):
    order_id = create_affiliate_order(order.affiliate_id, order.customer_id, order.product, order.amount)
    if not order_id:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    return {"order_id": order_id, "status": "created"}

@app.get("/api/affiliates/{affiliate_id}/orders")
def get_affiliate_orders_endpoint(affiliate_id: str):
    orders = get_affiliate_orders(affiliate_id)
    return {
        "orders": [
            {
                "order_id": order[1],
                "customer_id": order[3],
                "product": order[4],
                "amount": order[5],
                "commission": order[6],
                "status": order[7],
                "created_at": order[8]
            }
            for order in orders
        ]
    }

@app.get("/api/orders")
def get_all_orders_endpoint():
    orders = get_all_orders()
    return {
        "orders": [
            {
                "order_id": order[1],
                "affiliate_id": order[2],
                "customer_id": order[3],
                "product": order[4],
                "amount": order[5],
                "commission": order[6],
                "status": order[7],
                "created_at": order[8]
            }
            for order in orders
        ]
    }

@app.get("/api/affiliates/{affiliate_id}/stats")
def get_affiliate_stats_endpoint(affiliate_id: str):
    stats = get_affiliate_stats(affiliate_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    return {
        "total_commission": stats[0],
        "total_sales": stats[1]
    }

@app.post("/api/withdrawals")
def create_withdrawal_endpoint(withdrawal: WithdrawalCreate):
    withdrawal_id = create_withdrawal(withdrawal.affiliate_id, withdrawal.amount)
    if not withdrawal_id:
        raise HTTPException(status_code=400, detail="Affiliate not found or insufficient commission")
    return {"withdrawal_id": withdrawal_id, "status": "created"}

@app.get("/api/affiliates/{affiliate_id}/withdrawals")
def get_affiliate_withdrawals_endpoint(affiliate_id: str):
    withdrawals = get_affiliate_withdrawals(affiliate_id)
    return {
        "withdrawals": [
            {
                "withdrawal_id": withdrawal[1],
                "amount": withdrawal[3],
                "status": withdrawal[4],
                "created_at": withdrawal[5],
                "processed_at": withdrawal[6]
            }
            for withdrawal in withdrawals
        ]
    }

@app.get("/api/withdrawals")
def get_all_withdrawals_endpoint():
    withdrawals = get_all_withdrawals()
    return {
        "withdrawals": [
            {
                "withdrawal_id": withdrawal[1],
                "affiliate_id": withdrawal[2],
                "amount": withdrawal[3],
                "status": withdrawal[4],
                "created_at": withdrawal[5],
                "processed_at": withdrawal[6]
            }
            for withdrawal in withdrawals
        ]
    }

@app.post("/api/trainings")
def create_training_endpoint(training: TrainingCreate):
    training_id = create_training(training.title, training.content, training.type, training.duration)
    return {"training_id": training_id, "status": "created"}

@app.get("/api/trainings")
def get_trainings_endpoint():
    trainings = get_trainings()
    return {
        "trainings": [
            {
                "training_id": training[1],
                "title": training[2],
                "content": training[3],
                "type": training[4],
                "duration": training[5],
                "created_at": training[6]
            }
            for training in trainings
        ]
    }

@app.post("/api/training-records")
def create_training_record_endpoint(record: TrainingRecordCreate):
    record_id = create_training_record(record.affiliate_id, record.training_id, record.score)
    return {"record_id": record_id, "status": "created"}

@app.get("/api/affiliates/{affiliate_id}/training-records")
def get_affiliate_training_records_endpoint(affiliate_id: str):
    records = get_affiliate_training_records(affiliate_id)
    return {
        "records": [
            {
                "record_id": record[1],
                "training_id": record[3],
                "status": record[4],
                "score": record[5],
                "created_at": record[6]
            }
            for record in records
        ]
    }

@app.post("/api/marketing-materials")
def create_marketing_material_endpoint(material: MarketingMaterialCreate):
    material_id = create_marketing_material(material.title, material.type, material.url, material.description)
    return {"material_id": material_id, "status": "created"}

@app.get("/api/marketing-materials")
def get_marketing_materials_endpoint():
    materials = get_marketing_materials()
    return {
        "materials": [
            {
                "material_id": material[1],
                "title": material[2],
                "type": material[3],
                "url": material[4],
                "description": material[5],
                "created_at": material[6]
            }
            for material in materials
        ]
    }

@app.post("/api/support-tickets")
def create_support_ticket_endpoint(ticket: SupportTicketCreate):
    ticket_id = create_support_ticket(ticket.affiliate_id, ticket.title, ticket.content, ticket.priority)
    return {"ticket_id": ticket_id, "status": "created"}

@app.get("/api/affiliates/{affiliate_id}/support-tickets")
def get_affiliate_support_tickets_endpoint(affiliate_id: str):
    tickets = get_affiliate_support_tickets(affiliate_id)
    return {
        "tickets": [
            {
                "ticket_id": ticket[1],
                "title": ticket[3],
                "content": ticket[4],
                "status": ticket[5],
                "priority": ticket[6],
                "created_at": ticket[7],
                "updated_at": ticket[8]
            }
            for ticket in tickets
        ]
    }

@app.get("/api/support-tickets")
def get_all_support_tickets_endpoint():
    tickets = get_all_support_tickets()
    return {
        "tickets": [
            {
                "ticket_id": ticket[1],
                "affiliate_id": ticket[2],
                "title": ticket[3],
                "content": ticket[4],
                "status": ticket[5],
                "priority": ticket[6],
                "created_at": ticket[7],
                "updated_at": ticket[8]
            }
            for ticket in tickets
        ]
    }

@app.put("/api/support-tickets/{ticket_id}")
def update_support_ticket_endpoint(ticket_id: str, status: str):
    update_support_ticket(ticket_id, status)
    return {"message": "Support ticket updated successfully"}

@app.get("/r/{link_id}")
def redirect_referral(link_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT affiliate_id, url FROM referral_links WHERE link_id = ?", (link_id,))
    link = c.fetchone()
    if not link:
        return RedirectResponse(url="/")
    
    # 更新点击次数
    c.execute("UPDATE referral_links SET clicks = clicks + 1 WHERE link_id = ?", (link_id,))
    conn.commit()
    conn.close()
    
    return RedirectResponse(url=link[1])

# 健康检查
@app.get("/health")
def health_check():
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting AI service affiliate management system")
    uvicorn.run(app, host="0.0.0.0", port=8001)