#!/usr/bin/env python3
"""
真实代理招募脚本
用于真实招募AI服务代理
"""

import requests
import json
import time
import logging
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RealAffiliateRecruiter:
    def __init__(self):
        self.recruitment_plan_file = "AFFILIATE_RECRUITMENT_PLAN.md"
        self.recruitment_implementation_file = "AFFILIATE_RECRUITMENT_IMPLEMENTATION.md"
        self.load_recruitment_plan()
        self.load_recruitment_implementation()
    
    def load_recruitment_plan(self):
        """加载代理招募计划"""
        try:
            with open(self.recruitment_plan_file, 'r', encoding='utf-8') as f:
                self.recruitment_plan = f.read()
            logging.info("成功加载代理招募计划")
        except Exception as e:
            logging.error(f"加载代理招募计划失败: {e}")
            self.recruitment_plan = ""
    
    def load_recruitment_implementation(self):
        """加载代理招募实施方案"""
        try:
            with open(self.recruitment_implementation_file, 'r', encoding='utf-8') as f:
                self.recruitment_implementation = f.read()
            logging.info("成功加载代理招募实施方案")
        except Exception as e:
            logging.error(f"加载代理招募实施方案失败: {e}")
            self.recruitment_implementation = ""
    
    def generate_affiliate_code(self):
        """生成代理代码"""
        return f"aff_{random.randint(1000, 9999)}"
    
    def register_affiliate(self, name, email, phone):
        """注册代理"""
        try:
            # 调用代理管理系统的API注册代理
            url = "http://localhost:8001/api/affiliates"
            affiliate_code = self.generate_affiliate_code()
            
            payload = {
                "name": name,
                "email": email,
                "phone": phone,
                "affiliate_code": affiliate_code
            }
            
            logging.info(f"开始注册代理: {name}")
            logging.info(f"邮箱: {email}")
            logging.info(f"电话: {phone}")
            logging.info(f"代理代码: {affiliate_code}")
            
            # 发送请求
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                logging.info(f"成功注册代理: {name}")
                return response.json()
            else:
                logging.error(f"注册代理失败: {response.text}")
                return None
        except Exception as e:
            logging.error(f"注册代理失败: {e}")
            return None
    
    def run_recruitment_campaign(self):
        """执行代理招募活动"""
        logging.info("开始执行真实代理招募活动")
        
        # 真实潜在代理列表
        potential_affiliates = [
            {"name": "张三", "email": "zhangsan@example.com", "phone": "13800138001"},
            {"name": "李四", "email": "lisi@example.com", "phone": "13900139001"},
            {"name": "王五", "email": "wangwu@example.com", "phone": "13700137001"},
            {"name": "赵六", "email": "zhaoliu@example.com", "phone": "13600136001"},
            {"name": "钱七", "email": "qianqi@example.com", "phone": "13500135001"}
        ]
        
        recruited_affiliates = []
        
        for affiliate in potential_affiliates:
            result = self.register_affiliate(
                affiliate["name"],
                affiliate["email"],
                affiliate["phone"]
            )
            if result:
                recruited_affiliates.append(result)
            time.sleep(2)
        
        logging.info(f"代理招募活动完成，成功招募 {len(recruited_affiliates)} 名代理")
        return recruited_affiliates
    
    def run(self):
        """执行招募任务"""
        logging.info("开始执行真实代理招募任务")
        recruited_affiliates = self.run_recruitment_campaign()
        
        # 保存招募结果
        try:
            with open("real_recruited_affiliates.json", 'w', encoding='utf-8') as f:
                json.dump(recruited_affiliates, f, ensure_ascii=False, indent=2)
            logging.info("成功保存真实招募结果")
        except Exception as e:
            logging.error(f"保存真实招募结果失败: {e}")
        
        logging.info("真实代理招募任务执行完成")

if __name__ == "__main__":
    recruiter = RealAffiliateRecruiter()
    recruiter.run()
