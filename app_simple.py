from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import numpy as np
import os
import time
import uuid
import subprocess
from PIL import Image, ImageDraw, ImageFont

app = FastAPI(title="本地AI视频生成引擎")

class GenerateRequest(BaseModel):
    prompt: str
    duration: int = 3  # 秒
    fps: int = 10      # 帧率

# 生成单帧图像（模拟大模型文生图）
def generate_frame(prompt, frame_idx, output_path):
    h, w = 512, 896
    
    # 创建图像
    image = Image.new('RGB', (w, h), color=(100 + (frame_idx * 7) % 155, 50 + (frame_idx * 13) % 200, 150 + (frame_idx * 5) % 105))
    draw = ImageDraw.Draw(image)
    
    # 添加文字
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((30, 60), f"Prompt: {prompt[:20]}", font=font, fill=(255, 255, 255))
    draw.text((30, 120), f"Frame: {frame_idx}", font=font, fill=(255, 255, 255))
    
    # 模拟运动效果（帧间变化）
    shift = frame_idx * 5 % 50
    draw.ellipse([(450 + shift - 80, 256 - 80), (450 + shift + 80, 256 + 80)], fill=(255, 200, 150))
    
    # 保存图像
    image.save(output_path)

# 核心：生成连续视频（模拟大模型视频生成）
def generate_video(prompt, duration=3, fps=10):
    total_frames = duration * fps
    video_id = str(uuid.uuid4())[:8]
    frames_dir = f"frames_{video_id}"
    output_path = f"video_{video_id}.mp4"
    
    try:
        # 创建临时目录
        os.makedirs(frames_dir, exist_ok=True)
        
        # 生成帧
        for i in range(total_frames):
            frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
            generate_frame(prompt, i, frame_path)
        
        # 使用ffmpeg合成视频
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(frames_dir, "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_path
        ]
        
        print(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"ffmpeg error: {result.stderr}")
            raise Exception(f"视频合成失败: {result.stderr}")
        
        # 清理临时文件
        for file in os.listdir(frames_dir):
            os.remove(os.path.join(frames_dir, file))
        os.rmdir(frames_dir)
        
        # 检查文件是否创建成功
        if not os.path.exists(output_path):
            raise Exception("视频文件未创建")
        
        if os.path.getsize(output_path) < 100:
            raise Exception("视频文件为空")
        
        print(f"视频生成成功: {output_path}")
        return output_path
    except Exception as e:
        print(f"视频生成错误: {e}")
        # 清理临时文件
        if os.path.exists(frames_dir):
            for file in os.listdir(frames_dir):
                os.remove(os.path.join(frames_dir, file))
            os.rmdir(frames_dir)
        raise

# 前端页面
@app.get("/")
def index():
    return FileResponse("index.html")

# 视频生成接口
@app.post("/api/generate")
def api_generate(req: GenerateRequest):
    try:
        video_path = generate_video(req.prompt, req.duration, req.fps)
        return {
            "success": True,
            "video": f"/{video_path}",
            "message": "视频生成完成"
        }
    except Exception as e:
        raise HTTPException(detail=f"错误：{str(e)}", status_code=500)

# 提供视频文件访问
@app.get("/{video_name}")
def get_video(video_name: str):
    if os.path.exists(video_name):
        return FileResponse(video_name)
    return {"error": "文件不存在"}

if __name__ == "__main__":
    print("启动本地AI视频生成引擎...")
    print("正在导入依赖...")
    
    try:
        import uvicorn
        print("依赖导入成功")
        print("启动服务器...")
        print("访问地址: http://localhost:8000")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        print(f"启动错误: {e}")
        import traceback
        traceback.print_exc()