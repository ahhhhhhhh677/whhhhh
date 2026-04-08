#!/usr/bin/env python3
"""
创建GitHub仓库脚本
"""

import requests
import json

def create_github_repo(token, repo_name, description=""):
    """创建GitHub仓库"""
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "description": description,
        "private": False,
        "auto_init": False
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        repo_info = response.json()
        print(f"✅ 仓库创建成功！")
        print(f"仓库地址: {repo_info['html_url']}")
        print(f"克隆地址: {repo_info['clone_url']}")
        return True
    elif response.status_code == 422:
        print("⚠️ 仓库已存在")
        return True
    else:
        print(f"❌ 创建失败: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("="*60)
    print("创建GitHub仓库")
    print("="*60)
    print("\n请提供您的GitHub Personal Access Token:")
    print("获取方式:")
    print("1. 访问 https://github.com/settings/tokens")
    print("2. 点击 'Generate new token (classic)'")
    print("3. 勾选 'repo' 权限")
    print("4. 生成并复制token")
    print()
    
    token = input("请输入您的GitHub Token: ").strip()
    
    if not token:
        print("❌ 未提供token")
        exit(1)
    
    repo_name = input("请输入仓库名称 (默认: ai-api-proxy): ").strip() or "ai-api-proxy"
    description = input("请输入仓库描述 (可选): ").strip()
    
    create_github_repo(token, repo_name, description)
