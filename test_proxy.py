import requests
import json

API_BASE = "http://localhost:8000"

def test_create_user():
    print("测试创建用户...")
    response = requests.post(f"{API_BASE}/api/create-user")
    if response.status_code == 200:
        data = response.json()
        print(f"创建用户成功: {data}")
        return data['api_key']
    else:
        print(f"创建用户失败: {response.status_code} {response.text}")
        return None

def test_balance(api_key):
    print("\n测试查询余额...")
    headers = {'x-api-key': api_key}
    response = requests.get(f"{API_BASE}/api/balance", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"查询余额成功: {data}")
        return data['balance']
    else:
        print(f"查询余额失败: {response.status_code} {response.text}")
        return None

def test_topup(api_key, amount):
    print(f"\n测试充值 {amount} 元...")
    headers = {'x-api-key': api_key, 'Content-Type': 'application/json'}
    data = {'amount': amount}
    response = requests.post(f"{API_BASE}/api/topup", headers=headers, json=data)
    if response.status_code == 200:
        data = response.json()
        print(f"充值成功: {data}")
        return data['new_balance']
    else:
        print(f"充值失败: {response.status_code} {response.text}")
        return None

def test_add_provider_key(provider, api_key):
    print(f"\n测试添加 {provider} API密钥...")
    headers = {'Content-Type': 'application/json'}
    data = {'provider': provider, 'api_key': api_key}
    response = requests.post(f"{API_BASE}/api/add-provider-key", headers=headers, json=data)
    if response.status_code == 200:
        data = response.json()
        print(f"添加API密钥成功: {data}")
        return True
    else:
        print(f"添加API密钥失败: {response.status_code} {response.text}")
        return False

def test_proxy(api_key, provider, endpoint, test_data):
    print(f"\n测试代理 {provider} {endpoint}...")
    headers = {'x-api-key': api_key, 'Content-Type': 'application/json'}
    data = {
        'provider': provider,
        'endpoint': endpoint,
        'data': test_data
    }
    response = requests.post(f"{API_BASE}/api/proxy", headers=headers, json=data)
    if response.status_code == 200:
        data = response.json()
        print(f"代理请求成功")
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0].get('message', {}).get('content', '') or data['choices'][0].get('text', '')
            print(f"响应内容: {content[:100]}...")
        if 'usage' in data:
            print(f"Token使用: {data['usage']}")
        return True
    else:
        print(f"代理请求失败: {response.status_code} {response.text}")
        return False

def test_stats(api_key):
    print("\n测试查询统计...")
    headers = {'x-api-key': api_key}
    response = requests.get(f"{API_BASE}/api/stats", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"查询统计成功: {data}")
        return data
    else:
        print(f"查询统计失败: {response.status_code} {response.text}")
        return None

def main():
    print("=== AI服务中转代理测试 ===")
    
    # 创建用户
    api_key = test_create_user()
    if not api_key:
        return
    
    # 查询余额
    test_balance(api_key)
    
    # 充值
    test_topup(api_key, 100)
    
    # 添加API密钥（这里使用占位符，实际使用时需要替换为真实的API密钥）
    test_add_provider_key("openai", "sk-placeholder")
    test_add_provider_key("anthropic", "placeholder")
    test_add_provider_key("groq", "placeholder")
    
    # 测试代理请求
    test_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "你好，我是测试"}
        ],
        "temperature": 0.7
    }
    test_proxy(api_key, "openai", "chat/completions", test_data)
    
    # 查询统计
    test_stats(api_key)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()