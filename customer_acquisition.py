#!/usr/bin/env python3
"""
客户获取系统
用于寻找真实用户和订单，管理客户关系
"""

import json
import time
import logging
import requests
import sqlite3
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomerAcquisition:
    def __init__(self):
        self.proxy_url = "http://localhost:8000"
        self.affiliate_url = "http://localhost:8001"
        self.db_name = "customer_acquisition.db"
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # 创建潜在线索表
        c.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                contact_info TEXT,
                status TEXT DEFAULT 'new',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建营销活动表
        c.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                channel TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                leads_generated INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("客户获取数据库初始化完成")
    
    def get_system_status(self):
        """获取系统状态"""
        try:
            response = requests.get(f"{self.proxy_url}/status")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"获取系统状态失败: {e}")
            return None
    
    def create_lead(self, source, contact_info, notes=""):
        """创建潜在线索"""
        lead_id = f"lead_{int(time.time())}_{hash(contact_info) % 10000}"
        
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(
            "INSERT INTO leads (lead_id, source, contact_info, notes) VALUES (?, ?, ?, ?)",
            (lead_id, source, contact_info, notes)
        )
        conn.commit()
        conn.close()
        
        logging.info(f"创建潜在线索: {lead_id}, 来源: {source}")
        return lead_id
    
    def get_leads(self, status=None):
        """获取潜在线索列表"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        if status:
            c.execute("SELECT * FROM leads WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            c.execute("SELECT * FROM leads ORDER BY created_at DESC")
        
        leads = c.fetchall()
        conn.close()
        return leads
    
    def update_lead_status(self, lead_id, status):
        """更新线索状态"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(
            "UPDATE leads SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE lead_id = ?",
            (status, lead_id)
        )
        conn.commit()
        conn.close()
        logging.info(f"更新线索状态: {lead_id} -> {status}")
    
    def create_campaign(self, name, channel):
        """创建营销活动"""
        import uuid
        campaign_id = f"camp_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(
            "INSERT INTO campaigns (campaign_id, name, channel) VALUES (?, ?, ?)",
            (campaign_id, name, channel)
        )
        conn.commit()
        conn.close()
        
        logging.info(f"创建营销活动: {campaign_id}, 名称: {name}, 渠道: {channel}")
        return campaign_id
    
    def get_campaigns(self):
        """获取营销活动列表"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT * FROM campaigns ORDER BY created_at DESC")
        campaigns = c.fetchall()
        conn.close()
        return campaigns
    
    def generate_acquisition_report(self):
        """生成获客报告"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # 统计线索
        c.execute("SELECT COUNT(*) FROM leads")
        total_leads = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM leads WHERE status = 'new'")
        new_leads = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM leads WHERE status = 'contacted'")
        contacted_leads = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM leads WHERE status = 'converted'")
        converted_leads = c.fetchone()[0]
        
        # 统计活动
        c.execute("SELECT COUNT(*) FROM campaigns")
        total_campaigns = c.fetchone()[0]
        
        c.execute("SELECT SUM(leads_generated) FROM campaigns")
        campaign_leads = c.fetchone()[0] or 0
        
        conn.close()
        
        report = {
            "total_leads": total_leads,
            "new_leads": new_leads,
            "contacted_leads": contacted_leads,
            "converted_leads": converted_leads,
            "total_campaigns": total_campaigns,
            "campaign_leads": campaign_leads,
            "conversion_rate": (converted_leads / total_leads * 100) if total_leads > 0 else 0
        }
        
        return report
    
    def run_acquisition_strategy(self):
        """执行获客策略"""
        logging.info("开始执行获客策略")
        
        # 1. 检查系统状态
        system_status = self.get_system_status()
        if not system_status:
            logging.error("系统未运行，无法执行获客策略")
            return False
        
        logging.info(f"系统状态: {system_status.get('status', 'unknown')}")
        
        # 2. 创建获客活动
        campaigns = [
            ("GitHub技术社区推广", "github"),
            ("开发者论坛推广", "forum"),
            ("社交媒体营销", "social_media"),
            ("技术沙龙活动", "offline_event")
        ]
        
        for name, channel in campaigns:
            self.create_campaign(name, channel)
        
        # 3. 生成示例线索（模拟真实获客）
        sample_leads = [
            ("github", "contact1@example.com", "GitHub上看到项目，对AI API感兴趣"),
            ("forum", "contact2@example.com", "开发者论坛咨询价格"),
            ("social_media", "contact3@example.com", "小红书看到推广"),
            ("referral", "contact4@example.com", "朋友推荐")
        ]
        
        for source, contact, notes in sample_leads:
            self.create_lead(source, contact, notes)
        
        # 4. 生成报告
        report = self.generate_acquisition_report()
        
        logging.info("获客策略执行完成")
        logging.info(f"总线索数: {report['total_leads']}")
        logging.info(f"新线索: {report['new_leads']}")
        logging.info(f"已联系: {report['contacted_leads']}")
        logging.info(f"已转化: {report['converted_leads']}")
        logging.info(f"转化率: {report['conversion_rate']:.2f}%")
        
        return report
    
    def monitor_real_time(self):
        """实时监控获客数据"""
        logging.info("开始实时监控获客数据")
        
        while True:
            try:
                # 获取系统状态
                system_status = self.get_system_status()
                if system_status:
                    stats = system_status.get('statistics', {})
                    orders = stats.get('orders', {})
                    users = stats.get('users', 0)
                    
                    logging.info(f"实时监控 - 用户: {users}, 完成订单: {orders.get('completed', 0)}, 总金额: {orders.get('total_amount', 0)}")
                
                # 获取获客报告
                report = self.generate_acquisition_report()
                logging.info(f"线索统计 - 总线索: {report['total_leads']}, 新线索: {report['new_leads']}, 转化率: {report['conversion_rate']:.2f}%")
                
                # 每30秒检查一次
                time.sleep(30)
                
            except KeyboardInterrupt:
                logging.info("停止实时监控")
                break
            except Exception as e:
                logging.error(f"监控出错: {e}")
                time.sleep(30)

def main():
    """主函数"""
    acquisition = CustomerAcquisition()
    
    # 执行获客策略
    acquisition.run_acquisition_strategy()
    
    # 开始实时监控
    logging.info("开始实时监控，按Ctrl+C停止")
    acquisition.monitor_real_time()

if __name__ == "__main__":
    main()
