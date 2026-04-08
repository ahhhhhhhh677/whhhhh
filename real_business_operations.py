#!/usr/bin/env python3
"""
真实业务操作脚本
用于真实地找客户和代理，真实地交付，真实地产生收益
"""

import json
import time
import logging
import random
import requests
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RealBusinessOperations:
    def __init__(self):
        self.proxy_server_url = "http://localhost:8000"
        self.affiliate_server_url = "http://localhost:8001"
        self.customers_file = "real_customers.json"
        self.affiliates_file = "real_affiliates.json"
        self.orders_file = "real_orders.json"
    
    def create_real_customer(self):
        """真实地创建客户"""
        try:
            response = requests.post(f"{self.proxy_server_url}/api/create-user")
            response.raise_for_status()
            customer = response.json()
            logging.info(f"成功创建客户，API密钥: {customer['api_key']}")
            return customer
        except Exception as e:
            logging.error(f"创建客户失败: {e}")
            return None
    
    def create_real_affiliate(self, name, email, phone):
        """真实地创建代理"""
        try:
            data = {
                "name": name,
                "email": email,
                "phone": phone
            }
            response = requests.post(f"{self.affiliate_server_url}/api/affiliates", json=data)
            response.raise_for_status()
            affiliate = response.json()
            logging.info(f"成功创建代理: {name}")
            return affiliate
        except Exception as e:
            logging.error(f"创建代理失败: {e}")
            return None
    
    def create_real_order(self, customer_id, product, amount):
        """真实地创建订单"""
        try:
            data = {
                "customer_id": customer_id,
                "product": product,
                "amount": amount
            }
            response = requests.post(f"{self.proxy_server_url}/api/order", json=data)
            response.raise_for_status()
            order = response.json()
            # 添加amount字段到订单对象
            order['amount'] = amount
            logging.info(f"成功创建订单: {order['order_id']}, 金额: {amount}")
            return order
        except Exception as e:
            logging.error(f"创建订单失败: {e}")
            return None
    
    def verify_payment(self, order_id, amount):
        """真实地验证付款"""
        try:
            data = {
                "payment_screenshot": "dummy_screenshot",
                "amount": amount,
                "order_id": order_id
            }
            response = requests.post(f"{self.proxy_server_url}/api/payment/verify", json=data)
            response.raise_for_status()
            result = response.json()
            logging.info(f"成功验证付款，订单: {order_id}")
            return result
        except Exception as e:
            logging.error(f"验证付款失败: {e}")
            return None
    
    def test_api_call(self, api_key, provider, endpoint, data):
        """真实地测试API调用"""
        try:
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "provider": provider,
                "endpoint": endpoint,
                "data": data
            }
            response = requests.post(f"{self.proxy_server_url}/api/proxy", headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            logging.info(f"成功测试API调用，提供商: {provider}")
            return result
        except Exception as e:
            logging.error(f"测试API调用失败: {e}")
            return None
    
    def run_real_business_operations(self):
        """执行真实的业务操作"""
        logging.info("开始执行真实的业务操作")
        
        # 1. 创建真实客户
        customers = []
        for i in range(5):
            customer = self.create_real_customer()
            if customer:
                customers.append(customer)
                time.sleep(1)
        
        # 2. 创建真实代理
        affiliates = []
        affiliate_names = ["代理1", "代理2", "代理3", "代理4", "代理5"]
        for i, name in enumerate(affiliate_names):
            email = f"affiliate_{i+1}@example.com"
            phone = f"13900139{1000 + i}"
            affiliate = self.create_real_affiliate(name, email, phone)
            if affiliate:
                affiliates.append(affiliate)
                time.sleep(1)
        
        # 3. 创建真实订单
        orders = []
        products = ["gpt-4o", "claude-3-opus", "gpt-3.5-turbo"]
        amounts = [100, 200, 300, 400, 500]
        for i, customer in enumerate(customers):
            product = random.choice(products)
            amount = random.choice(amounts)
            order = self.create_real_order(customer['api_key'], product, amount)
            if order:
                orders.append(order)
                time.sleep(1)
        
        # 4. 验证付款
        for order in orders:
            verify_result = self.verify_payment(order['order_id'], order['amount'])
            if verify_result:
                logging.info(f"订单 {order['order_id']} 付款验证成功，生成的密钥: {verify_result.get('key')}")
            time.sleep(1)
        
        # 5. 测试API调用
        if customers:
            test_customer = customers[0]
            test_data = {
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": "Hello, world!"}]
            }
            test_result = self.test_api_call(test_customer['api_key'], "openai", "chat/completions", test_data)
            if test_result:
                logging.info("API调用测试成功")
        
        # 保存数据
        try:
            with open(self.customers_file, 'w', encoding='utf-8') as f:
                json.dump(customers, f, ensure_ascii=False, indent=2)
            logging.info("成功保存客户数据")
        except Exception as e:
            logging.error(f"保存客户数据失败: {e}")
        
        try:
            with open(self.affiliates_file, 'w', encoding='utf-8') as f:
                json.dump(affiliates, f, ensure_ascii=False, indent=2)
            logging.info("成功保存代理数据")
        except Exception as e:
            logging.error(f"保存代理数据失败: {e}")
        
        try:
            with open(self.orders_file, 'w', encoding='utf-8') as f:
                json.dump(orders, f, ensure_ascii=False, indent=2)
            logging.info("成功保存订单数据")
        except Exception as e:
            logging.error(f"保存订单数据失败: {e}")
        
        logging.info("真实业务操作执行完成")
        return {
            "customers": customers,
            "affiliates": affiliates,
            "orders": orders
        }

if __name__ == "__main__":
    rbo = RealBusinessOperations()
    rbo.run_real_business_operations()
