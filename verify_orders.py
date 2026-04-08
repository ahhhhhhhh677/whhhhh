#!/usr/bin/env python3
"""
订单验证脚本
用于真实调用数据库查询语句，获取真实的已完成订单数量
"""

import sqlite3
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect('proxy.db')

def verify_completed_orders():
    """验证已完成订单数量"""
    logging.info("开始验证已完成订单数量")
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # 执行数据库查询，获取已完成订单数量
        c.execute("SELECT COUNT(*), SUM(amount) FROM orders WHERE status = 'completed'")
        order_stats = c.fetchone()
        
        conn.close()
        
        completed_orders = order_stats[0] or 0
        total_amount = order_stats[1] or 0
        
        logging.info(f"数据库查询结果：已完成订单 {completed_orders}，总金额 {total_amount}")
        return completed_orders, total_amount
    except Exception as e:
        logging.error(f"数据库查询失败: {e}")
        return None, None

if __name__ == "__main__":
    completed_orders, total_amount = verify_completed_orders()
    if completed_orders is not None:
        logging.info(f"验证完成：已完成订单 {completed_orders}，总金额 {total_amount}")
    else:
        logging.error("无法获取真实数据")
