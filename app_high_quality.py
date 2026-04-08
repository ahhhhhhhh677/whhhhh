from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os
import cv2
import numpy as np
import torch
from PIL import Image
from diffusers import StableDiffusionPipeline
import imageio
import math

app = FastAPI(title="本地高级AI视频生成引擎")

class GenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = "blurry, lowres, pixelated, ugly, disfigured, bad anatomy, watermark, text, error, cropped"
    duration: int = 4
    fps: int = 15

# ==================== 加载 真实高清SD模型 ====================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"使用设备: {device}")

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    safety_checker=None
).to(device)

# ==================== 高清帧生成（真实AI画质） ====================
def generate_real_frame(prompt, neg_prompt, width=1024, height=768):
    image = pipe(
        prompt=prompt,
        negative_prompt=neg_prompt,
        width=width,
        height=height,
        num_inference_steps=30,
        guidance_scale=7.5
    ).images[0]
    
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

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
    uvicorn.run(app, host="0.0.0.0", port=8000)