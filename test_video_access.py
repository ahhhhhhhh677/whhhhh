import requests
import os

def test_video_access():
    """测试视频文件访问"""
    print("测试视频文件访问...")
    
    # 获取最新生成的视频文件
    video_files = [f for f in os.listdir('.') if f.startswith('REAL_AI_VIDEO_') and f.endswith('.mp4')]
    if not video_files:
        print("❌ 没有找到生成的视频文件")
        return False
    
    # 按修改时间排序，获取最新的视频
    video_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_video = video_files[0]
    print(f"最新生成的视频: {latest_video}")
    
    # 测试直接访问视频文件
    video_url = f"http://localhost:8000/{latest_video}"
    print(f"测试访问: {video_url}")
    
    try:
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            print(f"✅ 视频文件访问成功，状态码: {response.status_code}")
            print(f"视频大小: {len(response.content)} bytes")
            
            # 测试下载视频
            download_path = f"test_download_{latest_video}"
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            
            if os.path.exists(download_path):
                print(f"✅ 视频下载成功，保存为: {download_path}")
                print(f"下载文件大小: {os.path.getsize(download_path)} bytes")
                os.remove(download_path)
                return True
            else:
                print("❌ 视频下载失败")
                return False
        else:
            print(f"❌ 视频文件访问失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试视频访问...")
    success = test_video_access()
    
    if success:
        print("\n✅ 视频访问测试通过！")
    else:
        print("\n❌ 视频访问测试失败")
