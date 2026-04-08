#!/usr/bin/env python3
"""
提供商评估脚本
用于评估现有和潜在的上游AI服务提供商
"""

import json
import time
import logging
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProviderEvaluation:
    def __init__(self):
        self.evaluation_file = "provider_evaluation.json"
        self.evaluated_providers_file = "real_evaluated_providers.json"
    
    def load_evaluated_providers(self):
        """加载已评估的提供商"""
        try:
            with open(self.evaluated_providers_file, 'r', encoding='utf-8') as f:
                providers = json.load(f)
            logging.info("成功加载已评估的提供商")
            return providers
        except Exception as e:
            logging.error(f"加载已评估的提供商失败: {e}")
            return []
    
    def evaluate_provider(self, provider):
        """评估提供商"""
        logging.info(f"开始评估提供商: {provider['provider']}")
        
        # 评估指标
        evaluation = {
            "provider": provider['provider'],
            "base_url": provider['base_url'],
            "response_time": provider['response_time'],
            "success_rate": provider['success_rate'],
            "cost_per_token": provider['cost_per_token'],
            "status": provider['status'],
            "evaluation": {
                "performance": self.calculate_performance_score(provider),
                "reliability": self.calculate_reliability_score(provider),
                "cost_efficiency": self.calculate_cost_efficiency_score(provider),
                "overall_score": 0
            },
            "recommendation": ""
        }
        
        # 计算总体评分
        evaluation["evaluation"]["overall_score"] = (
            evaluation["evaluation"]["performance"] * 0.4 +
            evaluation["evaluation"]["reliability"] * 0.3 +
            evaluation["evaluation"]["cost_efficiency"] * 0.3
        )
        
        # 生成推荐意见
        if evaluation["evaluation"]["overall_score"] >= 8:
            evaluation["recommendation"] = "强烈推荐"
        elif evaluation["evaluation"]["overall_score"] >= 6:
            evaluation["recommendation"] = "推荐"
        elif evaluation["evaluation"]["overall_score"] >= 4:
            evaluation["recommendation"] = "谨慎推荐"
        else:
            evaluation["recommendation"] = "不推荐"
        
        logging.info(f"提供商 {provider['provider']} 评估完成，总体评分: {evaluation['evaluation']['overall_score']:.2f}")
        return evaluation
    
    def calculate_performance_score(self, provider):
        """计算性能评分"""
        # 响应时间越短，评分越高
        response_time_score = max(0, 10 - (provider['response_time'] * 10))
        return response_time_score
    
    def calculate_reliability_score(self, provider):
        """计算可靠性评分"""
        # 成功率越高，评分越高
        return provider['success_rate'] * 10
    
    def calculate_cost_efficiency_score(self, provider):
        """计算成本效益评分"""
        # 成本越低，评分越高
        # 假设每token成本低于0.00005为优秀，高于0.0001为差
        if provider['cost_per_token'] <= 0.00005:
            return 10
        elif provider['cost_per_token'] <= 0.00008:
            return 8
        elif provider['cost_per_token'] <= 0.0001:
            return 6
        else:
            return 4
    
    def run(self):
        """执行提供商评估任务"""
        logging.info("开始执行提供商评估任务")
        
        # 加载已评估的提供商
        providers = self.load_evaluated_providers()
        
        # 评估每个提供商
        evaluations = []
        for provider in providers:
            evaluation = self.evaluate_provider(provider)
            evaluations.append(evaluation)
        
        # 按总体评分排序
        evaluations.sort(key=lambda x: x['evaluation']['overall_score'], reverse=True)
        
        # 保存评估结果
        try:
            with open(self.evaluation_file, 'w', encoding='utf-8') as f:
                json.dump(evaluations, f, ensure_ascii=False, indent=2)
            logging.info("成功保存提供商评估结果")
        except Exception as e:
            logging.error(f"保存提供商评估结果失败: {e}")
        
        # 输出评估结果
        logging.info("提供商评估结果:")
        for i, evaluation in enumerate(evaluations, 1):
            logging.info(f"{i}. {evaluation['provider']}")
            logging.info(f"   总体评分: {evaluation['evaluation']['overall_score']:.2f}")
            logging.info(f"   性能评分: {evaluation['evaluation']['performance']:.2f}")
            logging.info(f"   可靠性评分: {evaluation['evaluation']['reliability']:.2f}")
            logging.info(f"   成本效益评分: {evaluation['evaluation']['cost_efficiency']:.2f}")
            logging.info(f"   推荐意见: {evaluation['recommendation']}")
            logging.info("")
        
        logging.info("提供商评估任务执行完成")
        return evaluations

if __name__ == "__main__":
    pe = ProviderEvaluation()
    pe.run()
