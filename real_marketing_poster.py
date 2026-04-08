#!/usr/bin/env python3
"""
真实营销发布脚本
用于在真实平台发布营销内容，获取真实用户
"""

import json
import time
import logging
import requests
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RealMarketingPoster:
    def __init__(self):
        self.service_url = "http://localhost:8000"
        self.marketing_log = "marketing_posts.json"
    
    def generate_marketing_content(self):
        """生成营销内容"""
        content = {
            "title": "AI API中转服务 - 稳定、便宜、国内直连",
            "body": """
🚀 AI API中转服务正式上线！

✅ 支持模型：
- Llama 3.3 70B
- Qwen 2.5
- DeepSeek V3
- 更多模型陆续接入

✅ 服务优势：
- 国内直连，无需翻墙
- 价格便宜，比官方低20-30%
- 稳定可靠，7×24小时服务
- 支持OpenAI格式API

✅ 价格表：
- 100万 Token：30元
- 500万 Token：140元
- 1000万 Token：270元

✅ 使用方式：
1. 访问 http://localhost:8000
2. 注册获取API密钥
3. 开始调用API

📞 联系方式：
- 微信：xxx
- 邮箱：xxx@example.com

欢迎试用！
            """.strip(),
            "tags": ["AI", "API", "大模型", "Llama", "DeepSeek", "Qwen"],
            "created_at": datetime.now().isoformat()
        }
        return content
    
    def save_marketing_plan(self, content):
        """保存营销计划"""
        try:
            with open(self.marketing_log, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            logging.info("营销内容已保存到 marketing_posts.json")
        except Exception as e:
            logging.error(f"保存营销内容失败: {e}")
    
    def print_publish_guide(self):
        """打印发布指南"""
        content = self.generate_marketing_content()
        
        print("\n" + "="*60)
        print("营销内容已生成")
        print("="*60)
        print(f"\n标题：{content['title']}\n")
        print(f"内容：\n{content['body']}\n")
        print(f"标签：{', '.join(content['tags'])}\n")
        print("="*60)
        print("发布指南")
        print("="*60)
        print("""
请手动复制以上内容，发布到以下平台：

1. GitHub
   - 地址：https://github.com
   - 方式：创建Discussion或在自己的Repo发布
   - 标签：ai, api, llm, openai

2. V2EX
   - 地址：https://www.v2ex.com
   - 方式：在"分享创造"或"程序员"节点发布
   - 注意：遵守社区规则，不要纯广告

3. 掘金
   - 地址：https://juejin.cn
   - 方式：写文章介绍服务
   - 标签：AI, API, 后端

4. 知乎
   - 地址：https://www.zhihu.com
   - 方式：回答问题或写文章
   - 话题：人工智能、API开发

5. 微信公众号/朋友圈
   - 方式：发朋友圈或公众号文章
   - 目标：开发者朋友

6. 技术微信群/QQ群
   - 方式：分享服务链接
   - 注意：先获得群主同意

7. 小红书
   - 方式：发图文介绍
   - 标签：#AI #API #程序员

8. 闲鱼
   - 方式：发布服务商品
   - 价格：按实际定价

重要提醒：
- 所有发布必须是真实内容
- 不要虚假宣传
- 确保服务可用后再推广
- 及时回复用户咨询
        """)
        
        # 保存到文件
        self.save_marketing_plan(content)
    
    def check_service_ready(self):
        """检查服务是否准备好接受真实用户"""
        try:
            response = requests.get(f"{self.service_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                if health.get('status') == 'healthy':
                    logging.info("✅ 服务健康，可以开始推广")
                    return True
            logging.warning("⚠️ 服务状态异常")
            return False
        except Exception as e:
            logging.error(f"❌ 无法连接到服务: {e}")
            return False

def main():
    poster = RealMarketingPoster()
    
    # 检查服务状态
    if not poster.check_service_ready():
        print("\n❌ 服务未准备好，请先确保服务正常运行")
        return
    
    # 生成并显示营销内容
    poster.print_publish_guide()
    
    print("\n" + "="*60)
    print("下一步操作")
    print("="*60)
    print("""
1. 复制上面的营销内容
2. 手动发布到各个平台
3. 等待真实用户访问您的服务
4. 服务地址：http://localhost:8000

注意：这是真实的营销推广，请确保：
- 服务已配置真实API密钥
- 可以处理真实用户请求
- 有客服渠道回复咨询
    """)

if __name__ == "__main__":
    main()
