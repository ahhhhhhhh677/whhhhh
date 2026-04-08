#!/usr/bin/env python3
"""
真实业务数据收集脚本
用于从真实的API和数据库中获取数据，禁止使用任何模拟数据
"""

import json
import time
import logging
import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RealDataCollection:
    def __init__(self):
        self.proxy_server_url = "http://localhost:8000"
        self.affiliate_server_url = "http://localhost:8001"
        self.data_file = "real_business_data.json"
    
    def get_system_status(self):
        """获取系统状态"""
        try:
            response = requests.get(f"{self.proxy_server_url}/status")
            response.raise_for_status()
            status = response.json()
            logging.info("成功获取系统状态")
            return status
        except Exception as e:
            logging.error(f"获取系统状态失败: {e}")
            return None
    
    def get_health_status(self):
        """获取健康状态"""
        try:
            response = requests.get(f"{self.proxy_server_url}/health")
            response.raise_for_status()
            health = response.json()
            logging.info("成功获取健康状态")
            return health
        except Exception as e:
            logging.error(f"获取健康状态失败: {e}")
            return None
    
    def get_affiliates(self):
        """获取代理数据"""
        try:
            response = requests.get(f"{self.affiliate_server_url}/api/affiliates")
            response.raise_for_status()
            affiliates = response.json()
            logging.info("成功获取代理数据")
            return affiliates
        except Exception as e:
            logging.error(f"获取代理数据失败: {e}")
            return None
    
    def get_affiliate_orders(self):
        """获取代理订单数据"""
        try:
            response = requests.get(f"{self.affiliate_server_url}/api/orders")
            response.raise_for_status()
            orders = response.json()
            logging.info("成功获取代理订单数据")
            return orders
        except Exception as e:
            logging.error(f"获取代理订单数据失败: {e}")
            return None
    
    def collect_real_data(self):
        """收集真实业务数据"""
        logging.info("开始收集真实业务数据")
        
        # 获取系统状态
        system_status = self.get_system_status()
        if not system_status:
            logging.error("无法获取系统状态数据")
            return None
        
        # 获取健康状态
        health_status = self.get_health_status()
        if not health_status:
            logging.error("无法获取健康状态数据")
            return None
        
        # 获取代理数据
        affiliates_data = self.get_affiliates()
        if not affiliates_data:
            logging.error("无法获取代理数据")
            return None
        
        # 获取代理订单数据
        affiliate_orders_data = self.get_affiliate_orders()
        if not affiliate_orders_data:
            logging.error("无法获取代理订单数据")
            return None
        
        # 整合数据
        real_data = {
            "system_status": system_status,
            "health_status": health_status,
            "affiliates": affiliates_data,
            "affiliate_orders": affiliate_orders_data,
            "collected_at": time.time()
        }
        
        # 保存数据
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(real_data, f, ensure_ascii=False, indent=2)
            logging.info("成功保存真实业务数据")
        except Exception as e:
            logging.error(f"保存真实业务数据失败: {e}")
            return None
        
        logging.info("真实业务数据收集完成")
        return real_data
    
    def run(self):
        """执行真实数据收集任务"""
        logging.info("开始执行真实数据收集任务")
        
        # 收集真实数据
        real_data = self.collect_real_data()
        
        if real_data:
            # 输出真实数据
            logging.info("真实业务数据:")
            logging.info(f"系统状态: {real_data['system_status']['status']}")
            logging.info(f"已完成订单: {real_data['system_status']['statistics']['orders']['completed']}")
            logging.info(f"总金额: {real_data['system_status']['statistics']['orders']['total_amount']}")
            logging.info(f"总请求: {real_data['system_status']['statistics']['requests']['total']}")
            logging.info(f"总用户: {real_data['system_status']['statistics']['users']}")
            logging.info(f"健康状态: {real_data['health_status']['status']}")
            logging.info(f"代理数量: {len(real_data['affiliates']['affiliates'])}")
            logging.info(f"代理订单数量: {len(real_data['affiliate_orders']['orders'])}")
        else:
            logging.error("无法获取真实数据")
        
        logging.info("真实数据收集任务执行完成")
        return real_data

if __name__ == "__main__":
    rdc = RealDataCollection()
    rdc.run()
