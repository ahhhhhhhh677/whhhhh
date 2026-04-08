#!/usr/bin/env python3
"""
清空所有测试数据脚本
用于清空数据库中的所有测试数据，从0开始
"""

import sqlite3
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_proxy_db():
    """清空proxy数据库"""
    logging.info("开始清空proxy数据库")
    
    try:
        conn = sqlite3.connect('proxy.db')
        c = conn.cursor()
        
        # 清空所有表
        c.execute("DELETE FROM users")
        c.execute("DELETE FROM orders")
        c.execute("DELETE FROM requests")
        c.execute("DELETE FROM provider_keys")
        c.execute("DELETE FROM affiliates")
        c.execute("DELETE FROM affiliate_orders")
        
        conn.commit()
        conn.close()
        
        logging.info("✅ 成功清空proxy数据库")
        return True
    except Exception as e:
        logging.error(f"清空proxy数据库失败: {e}")
        return False

def clear_affiliate_db():
    """清空affiliate数据库"""
    logging.info("开始清空affiliate数据库")
    
    try:
        conn = sqlite3.connect('affiliate.db')
        c = conn.cursor()
        
        # 清空所有表
        c.execute("DELETE FROM affiliates")
        c.execute("DELETE FROM affiliate_orders")
        c.execute("DELETE FROM referral_links")
        c.execute("DELETE FROM commission_withdrawals")
        c.execute("DELETE FROM affiliate_trainings")
        c.execute("DELETE FROM affiliate_training_records")
        c.execute("DELETE FROM marketing_materials")
        c.execute("DELETE FROM support_tickets")
        
        conn.commit()
        conn.close()
        
        logging.info("✅ 成功清空affiliate数据库")
        return True
    except Exception as e:
        logging.error(f"清空affiliate数据库失败: {e}")
        return False

def verify_data_cleared():
    """验证数据是否已清空"""
    logging.info("验证数据是否已清空")
    
    try:
        # 验证proxy数据库
        conn = sqlite3.connect('proxy.db')
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM orders")
        order_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM requests")
        request_count = c.fetchone()[0]
        
        conn.close()
        
        # 验证affiliate数据库
        conn = sqlite3.connect('affiliate.db')
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM affiliates")
        affiliate_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM affiliate_orders")
        affiliate_order_count = c.fetchone()[0]
        
        conn.close()
        
        logging.info(f"proxy数据库 - 用户: {user_count}, 订单: {order_count}, 请求: {request_count}")
        logging.info(f"affiliate数据库 - 代理: {affiliate_count}, 代理订单: {affiliate_order_count}")
        
        if user_count == 0 and order_count == 0 and request_count == 0 and affiliate_count == 0 and affiliate_order_count == 0:
            logging.info("✅ 所有数据已清空，数据库为空白状态")
            return True
        else:
            logging.warning("⚠️ 数据库未完全清空")
            return False
    except Exception as e:
        logging.error(f"验证数据清空失败: {e}")
        return False

def main():
    """主函数"""
    logging.info("=" * 60)
    logging.info("开始清空所有测试数据")
    logging.info("=" * 60)
    
    # 清空proxy数据库
    if not clear_proxy_db():
        logging.error("清空proxy数据库失败，停止操作")
        return
    
    # 清空affiliate数据库
    if not clear_affiliate_db():
        logging.error("清空affiliate数据库失败，停止操作")
        return
    
    # 验证数据是否已清空
    if verify_data_cleared():
        logging.info("=" * 60)
        logging.info("✅ 所有测试数据已清空，系统已重置为空白状态")
        logging.info("=" * 60)
    else:
        logging.error("=" * 60)
        logging.error("❌ 数据清空验证失败")
        logging.info("=" * 60)

if __name__ == "__main__":
    main()
