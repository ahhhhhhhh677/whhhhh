#!/usr/bin/env python3
"""
质量控制机制脚本
用于建立和执行质量控制措施，确保AI服务代理系统的服务质量
"""

import requests
import json
import time
import logging
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QualityControl:
    def __init__(self):
        self.service_url = "http://localhost:8000"
        self.affiliate_url = "http://localhost:8001"
    
    def check_service_health(self):
        """检查服务健康状态"""
        try:
            logging.info("开始检查服务健康状态")
            response = requests.get(f"{self.service_url}/health")
            if response.status_code == 200:
                health_status = response.json()
                logging.info(f"服务健康状态: {health_status['status']}")
                logging.info(f"提供商状态: {health_status['providers']}")
                return health_status
            else:
                logging.error(f"服务健康检查失败: {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"服务健康检查失败: {e}")
            return None
    
    def test_api_performance(self):
        """测试API性能"""
        try:
            logging.info("开始测试API性能")
            
            # 测试请求
            test_payload = {
                "provider": "openai",
                "endpoint": "chat/completions",
                "data": {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "user", "content": "Hello, how are you?"}
                    ],
                    "max_tokens": 50
                }
            }
            
            start_time = time.time()
            response = requests.post(f"{self.service_url}/api/proxy", json=test_payload, headers={"X-API-Key": "d94942d1a629c1ab5f951f3172dabd74d437899254a9083d4db47cf0b4092068"})
            end_time = time.time()
            
            response_time = round(end_time - start_time, 2)
            
            if response.status_code == 200:
                logging.info(f"API性能测试成功")
                logging.info(f"响应时间: {response_time}秒")
                return {
                    "status": "success",
                    "response_time": response_time,
                    "status_code": response.status_code
                }
            else:
                logging.error(f"API性能测试失败: {response.status_code}")
                return {
                    "status": "failed",
                    "response_time": response_time,
                    "status_code": response.status_code
                }
        except Exception as e:
            logging.error(f"API性能测试失败: {e}")
            return {
                "status": "error",
                "response_time": 0,
                "status_code": 500
            }
    
    def check_affiliate_system(self):
        """检查代理系统状态"""
        try:
            logging.info("开始检查代理系统状态")
            response = requests.get(f"{self.affiliate_url}/health")
            if response.status_code == 200:
                health_status = response.json()
                logging.info(f"代理系统健康状态: {health_status['status']}")
                return health_status
            else:
                logging.error(f"代理系统健康检查失败: {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"代理系统健康检查失败: {e}")
            return None
    
    def generate_quality_report(self):
        """生成质量报告"""
        logging.info("开始生成质量报告")
        
        # 检查服务健康状态
        service_health = self.check_service_health()
        
        # 测试API性能
        api_performance = self.test_api_performance()
        
        # 检查代理系统状态
        affiliate_health = self.check_affiliate_system()
        
        # 生成报告
        report = {
            "timestamp": time.time(),
            "service_health": service_health,
            "api_performance": api_performance,
            "affiliate_health": affiliate_health,
            "overall_status": "healthy" if service_health and api_performance["status"] == "success" and affiliate_health else "unhealthy"
        }
        
        # 保存报告
        try:
            with open("quality_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logging.info("成功保存质量报告")
        except Exception as e:
            logging.error(f"保存质量报告失败: {e}")
        
        logging.info("质量报告生成完成")
        return report
    
    def run(self):
        """执行质量控制任务"""
        logging.info("开始执行质量控制任务")
        
        # 生成质量报告
        report = self.generate_quality_report()
        
        # 分析报告
        if report["overall_status"] == "healthy":
            logging.info("系统质量检查通过")
        else:
            logging.error("系统质量检查失败")
        
        logging.info("质量控制任务执行完成")
        return report

if __name__ == "__main__":
    qc = QualityControl()
    qc.run()
