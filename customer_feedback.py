#!/usr/bin/env python3
"""
客户反馈收集脚本
用于收集和分析客户反馈，改进产品和服务
"""

import requests
import json
import time
import logging
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomerFeedback:
    def __init__(self):
        self.feedback_file = "customer_feedback.json"
    
    def generate_feedback(self):
        """生成模拟客户反馈"""
        # 模拟客户反馈数据
        feedbacks = [
            {
                "customer_id": f"customer_{random.randint(1000, 9999)}",
                "name": f"客户{random.randint(1, 100)}",
                "email": f"customer{random.randint(1000, 9999)}@example.com",
                "rating": random.randint(1, 5),
                "feedback": "服务很好，响应速度快，价格合理。",
                "timestamp": time.time(),
                "status": "pending"
            },
            {
                "customer_id": f"customer_{random.randint(1000, 9999)}",
                "name": f"客户{random.randint(1, 100)}",
                "email": f"customer{random.randint(1000, 9999)}@example.com",
                "rating": random.randint(1, 5),
                "feedback": "API接口稳定，文档清晰，使用方便。",
                "timestamp": time.time(),
                "status": "pending"
            },
            {
                "customer_id": f"customer_{random.randint(1000, 9999)}",
                "name": f"客户{random.randint(1, 100)}",
                "email": f"customer{random.randint(1000, 9999)}@example.com",
                "rating": random.randint(1, 5),
                "feedback": "希望能增加更多的AI模型支持。",
                "timestamp": time.time(),
                "status": "pending"
            },
            {
                "customer_id": f"customer_{random.randint(1000, 9999)}",
                "name": f"客户{random.randint(1, 100)}",
                "email": f"customer{random.randint(1000, 9999)}@example.com",
                "rating": random.randint(1, 5),
                "feedback": "客服响应及时，问题解决迅速。",
                "timestamp": time.time(),
                "status": "pending"
            },
            {
                "customer_id": f"customer_{random.randint(1000, 9999)}",
                "name": f"客户{random.randint(1, 100)}",
                "email": f"customer{random.randint(1000, 9999)}@example.com",
                "rating": random.randint(1, 5),
                "feedback": "价格有点贵，希望能有更多优惠活动。",
                "timestamp": time.time(),
                "status": "pending"
            }
        ]
        return feedbacks
    
    def collect_feedback(self):
        """收集客户反馈"""
        logging.info("开始收集客户反馈")
        
        # 生成反馈数据
        feedbacks = self.generate_feedback()
        
        # 保存反馈数据
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedbacks, f, ensure_ascii=False, indent=2)
            logging.info(f"成功收集 {len(feedbacks)} 条客户反馈")
        except Exception as e:
            logging.error(f"保存客户反馈失败: {e}")
        
        return feedbacks
    
    def analyze_feedback(self, feedbacks):
        """分析客户反馈"""
        logging.info("开始分析客户反馈")
        
        if not feedbacks:
            logging.error("没有反馈数据可分析")
            return None
        
        # 计算平均评分
        total_rating = sum(feedback['rating'] for feedback in feedbacks)
        average_rating = round(total_rating / len(feedbacks), 2)
        
        # 分类反馈
        positive_feedbacks = [f for f in feedbacks if f['rating'] >= 4]
        neutral_feedbacks = [f for f in feedbacks if f['rating'] == 3]
        negative_feedbacks = [f for f in feedbacks if f['rating'] <= 2]
        
        # 提取关键词
        keywords = []
        for feedback in feedbacks:
            words = feedback['feedback'].split()
            keywords.extend(words)
        
        # 分析结果
        analysis = {
            "total_feedbacks": len(feedbacks),
            "average_rating": average_rating,
            "positive_feedbacks": len(positive_feedbacks),
            "neutral_feedbacks": len(neutral_feedbacks),
            "negative_feedbacks": len(negative_feedbacks),
            "keywords": keywords[:10]  # 前10个关键词
        }
        
        # 保存分析结果
        try:
            with open("feedback_analysis.json", 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            logging.info("成功保存反馈分析结果")
        except Exception as e:
            logging.error(f"保存反馈分析结果失败: {e}")
        
        return analysis
    
    def run(self):
        """执行客户反馈收集任务"""
        logging.info("开始执行客户反馈收集任务")
        
        # 收集反馈
        feedbacks = self.collect_feedback()
        
        # 分析反馈
        analysis = self.analyze_feedback(feedbacks)
        
        # 输出分析结果
        if analysis:
            logging.info(f"反馈分析结果:")
            logging.info(f"总反馈数: {analysis['total_feedbacks']}")
            logging.info(f"平均评分: {analysis['average_rating']}")
            logging.info(f"正面反馈: {analysis['positive_feedbacks']}")
            logging.info(f"中性反馈: {analysis['neutral_feedbacks']}")
            logging.info(f"负面反馈: {analysis['negative_feedbacks']}")
            logging.info(f"关键词: {', '.join(analysis['keywords'])}")
        
        logging.info("客户反馈收集任务执行完成")
        return analysis

if __name__ == "__main__":
    cf = CustomerFeedback()
    cf.run()
