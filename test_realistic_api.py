import requests
import json

# 测试真实感AI视频生成API
def test_realistic_video_generation():
    print("测试真实感AI视频生成API...")
    
    # API端点
    url = "http://localhost:8000/api/generate"
    
    # 测试数据
    test_data = {
        "prompt": "樱花飘落，realistic，8K，cinematic lighting",
        "negative_prompt": "blurry, lowres, pixelated, cartoon, painting, anime, ugly, disfigured, bad anatomy",
        "duration": 2,
        "fps": 10
    }
    
    try:
        print(f"发送请求: {test_data}")
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API调用成功: {result}")
            
            if result.get("success"):
                video_url = result.get("video")
                print(f"视频URL: {video_url}")
                
                # 测试视频文件是否可访问
                video_full_url = f"http://localhost:8000{video_url}"
                print(f"测试视频访问: {video_full_url}")
                
                video_response = requests.get(video_full_url)
                if video_response.status_code == 200:
                    print("✅ 视频文件可访问")
                    print(f"视频大小: {len(video_response.content)} bytes")
                    return True
                else:
                    print(f"❌ 视频文件访问失败: {video_response.status_code}")
                    return False
            else:
                print(f"❌ API返回失败: {result}")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试真实感AI视频生成...")
    success = test_realistic_video_generation()
    
    if success:
        print("\n✅ 真实感AI视频生成测试通过！")
    else:
        print("\n❌ 真实感AI视频生成测试失败")
