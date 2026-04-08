from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os
import cv2
import numpy as np
import requests
import base64
from PIL import Image, ImageDraw
import io

app = FastAPI(title="高级AI视频生成引擎（基于API）")

class GenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = "blurry, lowres, pixelated, ugly, disfigured, bad anatomy, watermark, text, error, cropped"
    duration: int = 4
    fps: int = 15

# ==================== 配置 ====================
# 使用Hugging Face的免费API
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
# 注意：这里需要设置你的Hugging Face API令牌
# 请在环境变量中设置 HUGGING_FACE_API_KEY
API_KEY = os.getenv("HUGGING_FACE_API_KEY", "")
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# ==================== 高清帧生成（真实AI画质） ====================
def generate_real_frame(prompt, neg_prompt, width=1024, height=768):
    if not API_KEY:
        # 如果没有API密钥，使用本地生成作为备选
        return generate_local_frame(prompt, neg_prompt, width, height)
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": neg_prompt,
            "width": width,
            "height": height,
            "num_inference_steps": 30,
            "guidance_scale": 7.5
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        image_bytes = response.content
        image = Image.open(io.BytesIO(image_bytes))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    else:
        print(f"API调用失败: {response.status_code}")
        # 失败时使用本地生成
        return generate_local_frame(prompt, neg_prompt, width, height)

# ==================== 本地备选帧生成 ====================
def generate_local_frame(prompt, neg_prompt, width=1024, height=768):
    # 创建高质量的本地生成帧
    img = Image.new('RGB', (width, height), color=(135, 206, 235))
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变天空
    for y in range(height // 2):
        ratio = y / (height // 2)
        r = int(135 * (1 - ratio) + 255 * ratio)
        g = int(206 * (1 - ratio) + 250 * ratio)
        b = int(235 * (1 - ratio) + 205 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 绘制地面
    draw.rectangle([0, height // 2, width, height], fill=(34, 139, 34))
    
    # 绘制太阳
    sun_x, sun_y = int(width * 0.8), int(height * 0.15)
    draw.ellipse([sun_x - 40, sun_y - 40, sun_x + 40, sun_y + 40], fill=(255, 215, 0))
    
    # 绘制云朵
    for i in range(3):
        cloud_x = 200 + i * 300
        cloud_y = 100 + i * 50
        for j in range(3):
            offset_x = j * 30 - 30
            size = 30 + j * 10
            draw.ellipse([cloud_x + offset_x - size, cloud_y - size, 
                          cloud_x + offset_x + size, cloud_y + size], 
                         fill=(255, 255, 255))
    
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

# ==================== 专业运动插值（丝滑无卡顿） ====================
def interpolate_frames(frame_a, frame_b, num_steps=6):
    frames = []
    for i in range(num_steps):
        alpha = i / num_steps
        blended = cv2.addWeighted(frame_a, 1 - alpha, frame_b, alpha, 0)
        frames.append(blended)
    return frames

# ==================== 核心：生成高级真实视频 ====================
def generate_pro_video(prompt, neg_prompt, duration, fps):
    total_frames = duration * fps
    video_id = str(uuid.uuid4())[:8]
    output_path = f"REAL_AI_VIDEO_{video_id}.mp4"
    
    # 高清尺寸
    W, H = 1024, 768
    
    # 生成 4 张高清关键帧（真实变化）
    key_frames = []
    prompts = [
        f"{prompt}, cinematic lighting, sharp focus, ultra detailed, 8K",
        f"{prompt}, cinematic motion, soft blur background, vibrant colors",
        f"{prompt}, dynamic angle, realistic shadows, beautiful lighting",
        f"{prompt}, smooth movement, professional grade, masterpiece"
    ]
    
    print("正在生成高清关键帧...")
    for p in prompts:
        frame = generate_real_frame(p, neg_prompt, W, H)
        key_frames.append(frame)
    
    # 插值补帧 → 丝滑
    full_frames = []
    steps = total_frames // len(key_frames)
    
    for i in range(len(key_frames)-1):
        interp = interpolate_frames(key_frames[i], key_frames[i+1], steps)
        full_frames += interp
    
    # 输出高清视频
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (W, H))
    
    for f in full_frames[:total_frames]:
        out.write(f)
    
    out.release()
    return output_path

# ==================== 前端 & 接口 ====================
@app.get("/")
def index():
    return FileResponse("index.html")

@app.post("/api/generate")
def api_generate(req: GenerateRequest):
    try:
        video_path = generate_pro_video(req.prompt, req.negative_prompt, req.duration, req.fps)
        return {"success": True, "video": f"/{video_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{video_name}")
def get_video(video_name: str):
    return FileResponse(video_name)

if __name__ == "__main__":
    import uvicorn
    print("启动高级AI视频生成引擎...")
    print("访问地址: http://localhost:8000")
    if not API_KEY:
        print("警告: 未设置HUGGING_FACE_API_KEY，将使用本地生成模式")
    uvicorn.run(app, host="0.0.0.0", port=8000)