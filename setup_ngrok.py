#!/usr/bin/env python3
"""
ngrok配置脚本
用于配置和启动ngrok内网穿透
"""

import subprocess
import time
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_ngrok_installed():
    """检查ngrok是否已安装"""
    ngrok_path = ".\\ngrok.exe"
    if os.path.exists(ngrok_path):
        try:
            result = subprocess.run([ngrok_path, "version"], capture_output=True, text=True)
            if result.returncode == 0:
                logging.info(f"ngrok已安装: {result.stdout.strip()}")
                return True
        except:
            pass
    logging.error("ngrok未安装")
    return False

def setup_ngrok():
    """配置ngrok"""
    print("="*60)
    print("ngrok内网穿透配置")
    print("="*60)
    print("""
要让外部用户访问您的本地服务，需要使用ngrok内网穿透。

步骤：
1. 访问 https://ngrok.com
2. 注册免费账号（可用GitHub/Google账号登录）
3. 登录后获取authtoken
4. 在下方输入您的authtoken

注意：
- 免费版有每月1GB流量限制
- 每次重启会分配新的URL
- 如需固定域名，需要付费版
    """)
    
    authtoken = input("\n请输入您的ngrok authtoken: ").strip()
    
    if not authtoken:
        print("未提供authtoken，无法继续")
        return False
    
    # 配置authtoken
    try:
        result = subprocess.run(
            [".\\ngrok.exe", "config", "add-authtoken", authtoken],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logging.info("✅ authtoken配置成功")
            return True
        else:
            logging.error(f"配置失败: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"配置出错: {e}")
        return False

def start_ngrok():
    """启动ngrok"""
    print("\n" + "="*60)
    print("启动ngrok内网穿透")
    print("="*60)
    
    try:
        # 启动ngrok
        process = subprocess.Popen(
            [".\\ngrok.exe", "http", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("ngrok正在启动...")
        print("请等待几秒...\n")
        
        # 等待ngrok启动
        time.sleep(5)
        
        # 获取公网URL
        try:
            import requests
            response = requests.get("http://localhost:4040/api/tunnels")
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                if tunnels:
                    public_url = tunnels[0].get('public_url')
                    print("="*60)
                    print("✅ ngrok启动成功！")
                    print("="*60)
                    print(f"\n🌐 公网访问地址：{public_url}")
                    print(f"\n📍 本地服务地址：http://localhost:8000")
                    print("\n✨ 现在外部用户可以通过公网地址访问您的服务了！")
                    print("\n⚠️ 重要提示：")
                    print("- 免费版每次重启URL会变")
                    print("- 每月1GB流量限制")
                    print("- 保持此窗口运行，不要关闭")
                    print("\n按Ctrl+C停止ngrok")
                    print("="*60)
                    
                    # 保存URL到文件
                    with open("ngrok_url.txt", "w") as f:
                        f.write(public_url)
                    
                    return public_url
        except Exception as e:
            logging.error(f"获取URL失败: {e}")
        
        print("\n⚠️ ngrok可能已启动，但无法获取URL")
        print("请访问 http://localhost:4040 查看状态")
        return None
        
    except Exception as e:
        logging.error(f"启动ngrok失败: {e}")
        return None

def main():
    """主函数"""
    # 检查ngrok是否安装
    if not check_ngrok_installed():
        print("\n❌ ngrok未安装")
        print("请先运行下载脚本")
        return
    
    # 配置ngrok
    if not setup_ngrok():
        print("\n❌ 配置失败")
        return
    
    # 启动ngrok
    public_url = start_ngrok()
    
    if public_url:
        print(f"\n📝 请将此地址更新到营销内容中：{public_url}")
        print("然后就可以发布到GitHub、V2EX等平台了！")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n停止ngrok")

if __name__ == "__main__":
    main()
