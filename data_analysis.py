#!/usr/bin/env python3
"""
数据分析脚本
用于分析业务数据，提供数据驱动的决策支持
"""

import json
import time
import logging
import random
import statistics

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataAnalysis:
    def __init__(self):
        self.analysis_file = "data_analysis.json"
        self.customer_file = "customers.json"
        self.affiliate_file = "affiliates.json"
        self.brand_file = "brand_building.json"
    
    def load_data(self):
        """加载业务数据"""
        data = {}
        
        # 加载客户数据
        try:
            with open(self.customer_file, 'r', encoding='utf-8') as f:
                data['customers'] = json.load(f)
            logging.info("成功加载客户数据")
        except Exception as e:
            logging.error(f"加载客户数据失败: {e}")
            data['customers'] = []
        
        # 加载代理数据
        try:
            with open(self.affiliate_file, 'r', encoding='utf-8') as f:
                data['affiliates'] = json.load(f)
            logging.info("成功加载代理数据")
        except Exception as e:
            logging.error(f"加载代理数据失败: {e}")
            data['affiliates'] = []
        
        # 加载品牌建设数据
        try:
            with open(self.brand_file, 'r', encoding='utf-8') as f:
                data['brand'] = json.load(f)
            logging.info("成功加载品牌建设数据")
        except Exception as e:
            logging.error(f"加载品牌建设数据失败: {e}")
            data['brand'] = {"activities": [], "total_impact": 0}
        
        return data
    
    def analyze_data(self, data):
        """分析业务数据"""
        logging.info("开始数据分析")
        
        # 客户分析
        customer_analysis = {
            "total_customers": len(data['customers']),
            "active_customers": len([c for c in data['customers'] if c.get('status') == 'active']),
            "total_spending": sum(c.get('spending', 0) for c in data['customers']),
            "average_spending": statistics.mean([c.get('spending', 0) for c in data['customers']]) if data['customers'] else 0,
            "customer_types": {}
        }
        
        # 按客户类型分析
        for customer in data['customers']:
            customer_type = customer.get('type', '未知')
            if customer_type not in customer_analysis['customer_types']:
                customer_analysis['customer_types'][customer_type] = 0
            customer_analysis['customer_types'][customer_type] += 1
        
        # 代理分析
        affiliate_analysis = {
            "total_affiliates": len(data['affiliates']),
            "active_affiliates": len([a for a in data['affiliates'] if a.get('status') == 'active']),
            "total_sales": sum(a.get('total_sales', 0) for a in data['affiliates']),
            "total_commission": sum(a.get('total_commission', 0) for a in data['affiliates']),
            "average_commission_rate": statistics.mean([a.get('commission_rate', 0) for a in data['affiliates']]) if data['affiliates'] else 0,
            "affiliate_types": {}
        }
        
        # 按代理类型分析
        for affiliate in data['affiliates']:
            affiliate_type = affiliate.get('type', '未知')
            if affiliate_type not in affiliate_analysis['affiliate_types']:
                affiliate_analysis['affiliate_types'][affiliate_type] = 0
            affiliate_analysis['affiliate_types'][affiliate_type] += 1
        
        # 品牌分析
        brand_analysis = {
            "total_activities": len(data['brand'].get('activities', [])),
            "total_impact": data['brand'].get('total_impact', 0),
            "average_impact": statistics.mean([a.get('impact', 0) for a in data['brand'].get('activities', [])]) if data['brand'].get('activities', []) else 0
        }
        
        # 综合分析
        total_revenue = customer_analysis['total_spending'] + affiliate_analysis['total_sales']
        total_cost = affiliate_analysis['total_commission']
        profit = total_revenue - total_cost
        
        overall_analysis = {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "profit": profit,
            "profit_margin": (profit / total_revenue * 100) if total_revenue > 0 else 0,
            "customer_acquisition_cost": (total_cost / customer_analysis['total_customers']) if customer_analysis['total_customers'] > 0 else 0
        }
        
        # 分析结果
        analysis_result = {
            "customer_analysis": customer_analysis,
            "affiliate_analysis": affiliate_analysis,
            "brand_analysis": brand_analysis,
            "overall_analysis": overall_analysis,
            "created_at": time.time()
        }
        
        # 保存分析结果
        try:
            with open(self.analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            logging.info("成功保存数据分析结果")
        except Exception as e:
            logging.error(f"保存数据分析结果失败: {e}")
        
        logging.info("成功完成数据分析")
        return analysis_result
    
    def run(self):
        """执行数据分析任务"""
        logging.info("开始执行数据分析任务")
        
        # 加载业务数据
        data = self.load_data()
        
        # 分析业务数据
        analysis_result = self.analyze_data(data)
        
        # 输出分析结果
        logging.info("数据分析结果:")
        logging.info("\n客户分析:")
        logging.info(f"总客户数: {analysis_result['customer_analysis']['total_customers']}")
        logging.info(f"活跃客户数: {analysis_result['customer_analysis']['active_customers']}")
        logging.info(f"总消费: {analysis_result['customer_analysis']['total_spending']}")
        logging.info(f"平均消费: {analysis_result['customer_analysis']['average_spending']:.2f}")
        logging.info("客户类型分布:")
        for customer_type, count in analysis_result['customer_analysis']['customer_types'].items():
            logging.info(f"- {customer_type}: {count}")
        
        logging.info("\n代理分析:")
        logging.info(f"总代理数: {analysis_result['affiliate_analysis']['total_affiliates']}")
        logging.info(f"活跃代理数: {analysis_result['affiliate_analysis']['active_affiliates']}")
        logging.info(f"总销售额: {analysis_result['affiliate_analysis']['total_sales']}")
        logging.info(f"总佣金: {analysis_result['affiliate_analysis']['total_commission']}")
        logging.info(f"平均佣金率: {analysis_result['affiliate_analysis']['average_commission_rate']:.2f}")
        logging.info("代理类型分布:")
        for affiliate_type, count in analysis_result['affiliate_analysis']['affiliate_types'].items():
            logging.info(f"- {affiliate_type}: {count}")
        
        logging.info("\n品牌分析:")
        logging.info(f"总活动数: {analysis_result['brand_analysis']['total_activities']}")
        logging.info(f"总影响力: {analysis_result['brand_analysis']['total_impact']}")
        logging.info(f"平均影响力: {analysis_result['brand_analysis']['average_impact']:.2f}")
        
        logging.info("\n综合分析:")
        logging.info(f"总收入: {analysis_result['overall_analysis']['total_revenue']}")
        logging.info(f"总成本: {analysis_result['overall_analysis']['total_cost']}")
        logging.info(f"利润: {analysis_result['overall_analysis']['profit']}")
        logging.info(f"利润率: {analysis_result['overall_analysis']['profit_margin']:.2f}%")
        logging.info(f"客户获取成本: {analysis_result['overall_analysis']['customer_acquisition_cost']:.2f}")
        
        logging.info("数据分析任务执行完成")
        return analysis_result

if __name__ == "__main__":
    da = DataAnalysis()
    da.run()
