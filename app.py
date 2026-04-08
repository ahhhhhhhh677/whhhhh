from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import time
import os
import uuid
import cv2
import numpy as np

app = FastAPI(title="高质量AI视频生成")

class Request(BaseModel):
    prompt: str

# 调用智谱CogVideoX-Flash免费视频生成API
def generate_video_with_zhipu(prompt):
    print("正在使用智谱CogVideoX-Flash API生成视频...")
    
    # 智谱API配置
    # 使用用户提供的API密钥
    api_key = os.getenv("ZHIPU_API_KEY", "8ea804d75093481a89d3918bb62f8831.eS3M1oiaNqrRucEO")
    
    # 智谱CogVideoX-Flash API端点（根据官方文档）
    api_url = "https://open.bigmodel.cn/api/v1/videos/generations"
    
    print(f"使用API密钥: {api_key[:10]}...")
    print(f"API端点: {api_url}")
    print(f"生成提示词: {prompt}")
    
    # 构建请求参数（根据官方文档）
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "cogvideox-flash",  # 使用用户有权限的模型
        "prompt": prompt,
        "quality": "speed",  # 速度优先
        "with_audio": False,  # 不生成音效
        "watermark_enabled": True,  # 启用水印
        "size": "1280x720",  # 720p分辨率
        "fps": 30,  # 30帧率
        "duration": 5  # 5秒视频（文档支持的时长）
    }
    
    # 发送请求
    print("发送API请求...")
    response = requests.post(api_url, headers=headers, json=data, timeout=30)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    # 检查是否是限流错误
    if response.status_code == 429:
        # 重试机制，当遇到限流时等待并重试
        max_retries = 5
        retry_delay = 10  # 秒
        
        for retry in range(max_retries):
            print(f"API限流，等待 {retry_delay} 秒后重试 (重试 {retry+1}/{max_retries})...")
            time.sleep(retry_delay)
            retry_delay *= 1.5  # 指数退避
            
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code != 429:
                break
    
    # 检查是否是权限错误
    if response.status_code == 403:
        error_msg = response.json().get("error", {}).get("message", "权限错误")
        print(f"API权限错误: {error_msg}")
        raise Exception(f"视频生成失败: {error_msg}")
    
    response.raise_for_status()  # 检查响应状态
    
    result = response.json()
    print(f"解析响应: {result}")
    
    # 获取任务ID（根据文档）
    task_id = result.get("id")
    if not task_id:
        print("未获取到任务ID")
        raise Exception("视频生成失败: 未获取到任务ID")
    
    print(f"获取到任务ID: {task_id}")
    
    # 轮询获取结果（根据文档）
    status_url = f"https://open.bigmodel.cn/api/v1/videos/generations/{task_id}"
    for i in range(30):  # 最多等待150秒
        time.sleep(5)
        print(f"等待第 {i+1} 次...")
        status_response = requests.get(status_url, headers=headers, timeout=10)
        print(f"状态响应: {status_response.text}")
        
        # 检查是否是限流错误
        if status_response.status_code == 429:
            print("API限流，等待后重试...")
            time.sleep(10)
            continue
        
        # 检查是否是权限错误
        if status_response.status_code == 403:
            error_msg = status_response.json().get("error", {}).get("message", "权限错误")
            print(f"API权限错误: {error_msg}")
            raise Exception(f"视频生成失败: {error_msg}")
        
        status_response.raise_for_status()
        status_result = status_response.json()
        
        # 检查任务状态（根据文档）
        task_status = status_result.get("task_status")
        if task_status == "SUCCESS":
            # 从结果中获取视频URL
            video_url = status_result.get("data", {}).get("url")
            if video_url:
                print(f"视频生成完成，URL: {video_url}")
                return video_url
            else:
                print("未获取到视频URL，继续轮询...")
        elif task_status == "FAIL":
            error_msg = status_result.get("message", "视频生成失败")
            raise Exception(f"视频生成失败: {error_msg}")
        elif task_status == "PROCESSING":
            print("视频生成中，继续等待...")
        else:
            print(f"未知状态: {task_status}")
    
    # 未获取到视频URL
    print("视频生成超时")
    raise Exception("视频生成失败：超时")

# 本地生成高质量视频
def generate_video_locally(prompt):
    print("正在本地生成高质量视频...")
    
    h, w = 720, 1280
    duration = 3
    fps = 24
    total_frames = duration * fps
    
    vid_id = uuid.uuid4().hex[:6]
    out_path = f"high_quality_video_{vid_id}.mp4"
    
    # 解析提示词
    prompt_lower = prompt.lower()
    
    # 场景类型
    scene_type = "default"
    if "森林" in prompt or "forest" in prompt_lower:
        scene_type = "forest"
    elif "山脉" in prompt or "mountain" in prompt_lower:
        scene_type = "mountain"
    elif "海滩" in prompt or "beach" in prompt_lower:
        scene_type = "beach"
    
    # 时间类型
    time_type = "day"
    if "日落" in prompt or "sunset" in prompt_lower:
        time_type = "sunset"
    elif "夜晚" in prompt or "night" in prompt_lower:
        time_type = "night"
    
    # 生成关键帧
    key_frames = []
    key_count = 4
    for i in range(key_count):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        
        # 生成背景
        for y in range(h):
            if scene_type == "forest":
                if y < h * 0.5:
                    # 天空
                    if time_type == "sunset":
                        blue = 120 + int(30 * np.sin(i * 0.5))
                        green = 160 + int(20 * np.cos(i * 0.5))
                        red = 200 + int(40 * np.sin(i * 0.5))
                    else:
                        blue = 135 + int(20 * np.sin(i * 0.5))
                        green = 190 + int(15 * np.cos(i * 0.5))
                        red = 220 + int(10 * np.sin(i * 0.5))
                else:
                    # 森林地面
                    blue = 40 + int(10 * np.sin(i * 0.5))
                    green = 80 + int(20 * np.cos(i * 0.5))
                    red = 60 + int(10 * np.sin(i * 0.5))
            elif scene_type == "beach":
                if y < h * 0.5:
                    # 天空
                    if time_type == "sunset":
                        blue = 130 + int(30 * np.sin(i * 0.5))
                        green = 180 + int(20 * np.cos(i * 0.5))
                        red = 230 + int(40 * np.sin(i * 0.5))
                    else:
                        blue = 150 + int(20 * np.sin(i * 0.5))
                        green = 200 + int(15 * np.cos(i * 0.5))
                        red = 240 + int(10 * np.sin(i * 0.5))
                elif y < h * 0.7:
                    # 海洋
                    blue = 40 + int(40 * np.sin(i * 0.5))
                    green = 90 + int(30 * np.cos(i * 0.5))
                    red = 120 + int(15 * np.sin(i * 0.5))
                else:
                    # 沙滩
                    blue = 210 + int(15 * np.sin(i * 0.5))
                    green = 190 + int(15 * np.cos(i * 0.5))
                    red = 170 + int(15 * np.sin(i * 0.5))
            else:
                # 默认场景
                blue = 135 + int(20 * np.sin(i * 0.5 + y * 0.001))
                green = 180 + int(15 * np.cos(i * 0.5 + y * 0.001))
                red = 210 + int(10 * np.sin(i * 0.5 + y * 0.001))
            frame[y] = [blue, green, red]
        
        # 添加文字水印
        cv2.putText(frame, prompt[:30], (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, "HIGH QUALITY AI VIDEO", (30, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        key_frames.append(frame)
    
    # 插值补帧
    def blend_smooth(a, b, n=8):
        res = []
        for t in np.linspace(0, 1, n):
            res.append(cv2.addWeighted(a, 1 - t, b, t, 0))
        return res
    
    full_frames = []
    seg_frames = total_frames // (key_count - 1)
    
    for i in range(key_count - 1):
        interp = blend_smooth(key_frames[i], key_frames[i+1], seg_frames)
        full_frames.extend(interp)
    
    # 合成视频
    writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    
    for f in full_frames[:total_frames]:
        writer.write(f)
    
    writer.release()
    print(f"本地视频生成完成: {out_path}")
    return out_path

# 主视频生成函数
def generate_high_quality_video(prompt):
    # 只使用智谱API，不使用本地生成
    video_url = generate_video_with_zhipu(prompt)
    return video_url

# 前端页面
@app.get("/")
def index():
    return FileResponse("index.html")

@app.post("/generate")
def go(req: Request):
    try:
        url = generate_high_quality_video(req.prompt)
        return {"video": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{name}")
def get_file(name):
    return FileResponse(name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)