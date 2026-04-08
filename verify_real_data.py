#!/usr/bin/env python3
"""
验证数据真实性脚本
用于验证数据库中的数据是否为真实业务产生，而非测试数据
"""

import sqlite3
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection(db_name):
    """获取数据库连接"""
    return sqlite3.connect(db_name)

def verify_orders_realness():
    """验证订单的真实性 - 方法1"""
    logging.info("=" * 60)
    logging.info("方法1：验证订单的真实创建时间和来源")
    logging.info("=" * 60)
    
    try:
        conn = get_db_connection('proxy.db')
        c = conn.cursor()
        
        # 查询所有已完成订单的详细信息
        c.execute("""
            SELECT id, customer_id, product, amount, status, created_at, key_sent 
            FROM orders 
            WHERE status = 'completed'
            ORDER BY created_at
        """)
        orders = c.fetchall()
        conn.close()
        
        if not orders:
            logging.warning("没有找到已完成订单")
            return False
        
        logging.info(f"找到 {len(orders)} 个已完成订单")
        
        # 分析订单特征
        created_times = []
        amounts = []
        customer_ids = []
        
        for order in orders:
            order_id, customer_id, product, amount, status, created_at, key_sent = order
            created_times.append(created_at)
            amounts.append(amount)
            customer_ids.append(customer_id)
            logging.info(f"订单ID: {order_id}, 客户ID: {customer_id}, 产品: {product}, 金额: {amount}, 创建时间: {created_at}")
        
        # 检查是否为假数据特征
        logging.info("\n--- 假数据特征检查 ---")
        
        # 检查1：创建时间是否几乎一致
        if len(set(created_times)) == 1:
            logging.error("❌ 假数据特征：所有订单创建时间完全一致，疑似批量生成")
        elif len(set(created_times)) <= 3:
            logging.warning("⚠️ 可疑：订单创建时间高度集中，可能为批量生成")
        else:
            logging.info("✅ 创建时间分布正常")
        
        # 检查2：金额是否为凑好的整数
        amount_set = set(amounts)
        if len(amount_set) <= 3:
            logging.error(f"❌ 假数据特征：金额高度重复，只有 {len(amount_set)} 种金额: {amount_set}")
        else:
            logging.info("✅ 金额分布正常")
        
        # 检查3：客户ID是否连续
        try:
            # 尝试解析客户ID是否为连续数字
            numeric_ids = [int(cid.replace('customer_', '')) for cid in customer_ids if 'customer_' in cid]
            if numeric_ids:
                is_sequential = all(numeric_ids[i] + 1 == numeric_ids[i+1] for i in range(len(numeric_ids)-1))
                if is_sequential:
                    logging.error("❌ 假数据特征：客户ID完全连续，疑似测试数据")
                else:
                    logging.info("✅ 客户ID分布正常")
        except:
            logging.info("✅ 客户ID格式正常")
        
        return True
    except Exception as e:
        logging.error(f"验证订单失败: {e}")
        return False

def verify_users_realness():
    """验证用户的真实性 - 方法2"""
    logging.info("\n" + "=" * 60)
    logging.info("方法2：验证用户表的真实性")
    logging.info("=" * 60)
    
    try:
        conn = get_db_connection('proxy.db')
        c = conn.cursor()
        
        # 查询所有用户
        c.execute("SELECT id, api_key, balance, created_at FROM users ORDER BY created_at")
        users = c.fetchall()
        conn.close()
        
        if not users:
            logging.warning("没有找到用户")
            return False
        
        logging.info(f"找到 {len(users)} 个用户")
        
        created_times = []
        for user in users:
            user_id, api_key, balance, created_at = user
            created_times.append(created_at)
            logging.info(f"用户ID: {user_id}, API密钥: {api_key[:20]}..., 余额: {balance}, 创建时间: {created_at}")
        
        # 检查是否为假数据特征
        logging.info("\n--- 假数据特征检查 ---")
        
        # 检查1：创建时间是否同一时间生成
        if len(set(created_times)) == 1:
            logging.error("❌ 假数据特征：所有用户创建时间完全一致，疑似批量生成")
        elif len(set(created_times)) <= 5:
            logging.warning("⚠️ 可疑：用户创建时间高度集中，可能为批量生成")
        else:
            logging.info("✅ 用户创建时间分布正常")
        
        return True
    except Exception as e:
        logging.error(f"验证用户失败: {e}")
        return False

def verify_api_usage_realness():
    """验证API请求日志的真实性 - 方法3"""
    logging.info("\n" + "=" * 60)
    logging.info("方法3：验证API请求日志的真实性")
    logging.info("=" * 60)
    
    try:
        conn = get_db_connection('proxy.db')
        c = conn.cursor()
        
        # 查询请求记录
        c.execute("SELECT COUNT(*) FROM requests")
        request_count = c.fetchone()[0]
        
        # 查询详细请求记录
        c.execute("""
            SELECT id, user_api_key, provider, endpoint, tokens, cost, status, created_at 
            FROM requests 
            ORDER BY created_at
        """)
        requests_data = c.fetchall()
        conn.close()
        
        logging.info(f"总请求数: {request_count}")
        
        if requests_data:
            for req in requests_data:
                req_id, user_api_key, provider, endpoint, tokens, cost, status, created_at = req
                logging.info(f"请求ID: {req_id}, 用户: {user_api_key[:20]}..., 提供商: {provider}, 端点: {endpoint}, Token: {tokens}, 成本: {cost}, 状态: {status}, 时间: {created_at}")
        
        # 关键验证：订单与请求的比例
        conn = get_db_connection('proxy.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM orders WHERE status = 'completed'")
        completed_orders = c.fetchone()[0]
        conn.close()
        
        logging.info("\n--- 关键验证：订单与请求的比例 ---")
        logging.info(f"已完成订单: {completed_orders}")
        logging.info(f"API请求数: {request_count}")
        
        if completed_orders > 0 and request_count == 0:
            logging.error("❌ 假数据铁证：有完成订单但API请求为0，真实业务不可能出现这种情况")
        elif completed_orders > request_count * 10:
            logging.warning("⚠️ 可疑：订单数远多于请求数，可能为假数据")
        else:
            logging.info("✅ 订单与请求比例正常")
        
        return True
    except Exception as e:
        logging.error(f"验证API请求失败: {e}")
        return False

def verify_affiliate_db_realness():
    """验证代理数据库的真实性"""
    logging.info("\n" + "=" * 60)
    logging.info("方法4：验证代理数据库的真实性")
    logging.info("=" * 60)
    
    try:
        conn = get_db_connection('affiliate.db')
        c = conn.cursor()
        
        # 查询代理
        c.execute("SELECT affiliate_id, name, email, created_at FROM affiliates ORDER BY created_at")
        affiliates = c.fetchall()
        
        # 查询代理订单
        c.execute("SELECT COUNT(*) FROM affiliate_orders")
        affiliate_orders_count = c.fetchone()[0]
        
        conn.close()
        
        logging.info(f"代理数量: {len(affiliates)}")
        logging.info(f"代理订单数量: {affiliate_orders_count}")
        
        if affiliates:
            created_times = []
            for affiliate in affiliates:
                affiliate_id, name, email, created_at = affiliate
                created_times.append(created_at)
                logging.info(f"代理ID: {affiliate_id}, 名称: {name}, 邮箱: {email}, 创建时间: {created_at}")
            
            # 检查创建时间
            if len(set(created_times)) == 1:
                logging.error("❌ 假数据特征：所有代理创建时间完全一致，疑似批量生成")
            elif len(set(created_times)) <= 5:
                logging.warning("⚠️ 可疑：代理创建时间高度集中，可能为批量生成")
            else:
                logging.info("✅ 代理创建时间分布正常")
        
        return True
    except Exception as e:
        logging.error(f"验证代理数据库失败: {e}")
        return False

def main():
    """主函数"""
    logging.info("开始验证数据真实性")
    logging.info("=" * 60)
    
    # 执行3个验证方法
    verify_orders_realness()
    verify_users_realness()
    verify_api_usage_realness()
    verify_affiliate_db_realness()
    
    logging.info("\n" + "=" * 60)
    logging.info("验证完成")
    logging.info("=" * 60)
    logging.info("结论：请根据上述检查结果判断数据是否为真实业务产生")

if __name__ == "__main__":
    main()
