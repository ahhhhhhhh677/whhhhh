#!/usr/bin/env python3
"""
部署到Render的准备工作
Render提供免费的服务器部署，有固定域名
"""

import os

def create_render_config():
    """创建Render部署配置"""
    
    # 创建render.yaml
    render_yaml = """services:
  - type: web
    name: ai-api-proxy
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app_proxy:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
      - key: DATABASE_URL
        fromDatabase:
          name: proxy-db
          property: connectionString
"""
    
    with open("render.yaml", "w") as f:
        f.write(render_yaml)
    
    # 创建requirements.txt
    requirements = """fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
python-multipart==0.0.6
sqlite3
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Render部署配置已创建")
    print("\n文件列表：")
    print("- render.yaml: Render服务配置")
    print("- requirements.txt: Python依赖")
    
def print_deploy_guide():
    """打印部署指南"""
    print("\n" + "="*60)
    print("部署到Render（推荐）")
    print("="*60)
    print("""
Render提供免费的服务器部署，优势：
- ✅ 永久免费（有休眠机制）
- ✅ 固定域名（如 xxx.onrender.com）
- ✅ 无需内网穿透
- ✅ 专业稳定
- ✅ 支持自定义域名

部署步骤：

1. 注册Render账号
   - 访问 https://render.com
   - 用GitHub账号登录

2. 创建GitHub仓库
   - 访问 https://github.com/new
   - 创建新仓库（如 ai-api-proxy）
   - 上传项目代码

3. 在Render创建服务
   - 登录Render Dashboard
   - 点击 "New +" → "Web Service"
   - 选择GitHub仓库
   - 配置：
     * Name: ai-api-proxy
     * Runtime: Python 3
     * Build Command: pip install -r requirements.txt
     * Start Command: uvicorn app_proxy:app --host 0.0.0.0 --port $PORT
   - 点击 "Create Web Service"

4. 等待部署完成
   - 大约2-3分钟
   - 获得固定域名：xxx.onrender.com

5. 配置环境变量
   - 在Render Dashboard → Settings → Environment
   - 添加您的API密钥等配置

优点：
- 专业稳定，适合生产环境
- 有固定域名，可以配置自定义域名
- 免费额度足够初期使用

缺点：
- 免费版15分钟无访问会休眠（首次访问需等待唤醒）
- 需要GitHub账号

""")

def print_quick_solution():
    """打印快速解决方案"""
    print("\n" + "="*60)
    print("快速解决方案（立即可用）")
    print("="*60)
    print("""
如果您想立即让外部访问，可以使用以下方案：

方案1：使用Pagekite（简单，无需注册）
   pip install pagekite
   pagekite 8000 yourname.pagekite.me

方案2：使用Telebit（简单）
   npm install -g telebit
   telebit http 8000

方案3：使用Serveo（无需安装）
   ssh -R 80:localhost:8000 serveo.net

方案4：购买云服务器（最稳定）
   - 阿里云/腾讯云新人免费试用
   - 部署服务到公网IP
   - 获得固定访问地址

推荐：
- 测试阶段：使用Pagekite或Telebit
- 生产环境：部署到Render或购买云服务器
""")

if __name__ == "__main__":
    create_render_config()
    print_deploy_guide()
    print_quick_solution()
