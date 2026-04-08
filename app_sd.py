from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os
import cv2
import numpy as np
from PIL import Image

# 加载SD离线模型
from diffusers import StableDiffusionPipeline
import torch

app = FastAPI(title="SD+RIFE 本地AI高清视频生成")

# ========= 全局模型只加载一次，提速 =========
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"当前设备：{device}")

# 轻量SD模型，低配电脑也能跑
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device=="cuda" else torch.float32,
    safety_checker=None
).to(device)

# 简单帧插值模拟（无额外复杂依赖，低配友好）
def simple_frame_interpolate(img1:np.ndarray, img2:np.ndarray, n:int=3):
    frames = []
    for t in np.linspace(0,1,n+2):
        blend = cv2.addWeighted(img1,1-t,img2,t,0)
        frames.append(blend)
    return frames

# 请求结构
class GenReq(BaseModel):
    prompt: str
    negative_prompt: str = "ugly,blur,lowres,mosaic,bad quality"
    duration: int = 4
    fps: int = 15

# 核心：SD生成关键帧 + AI插值补帧
def create_ai_video(prompt, neg_prompt, duration, fps):
    total_frames = duration * fps
    key_count = 3   # 只生成3张AI关键帧，省算力
    key_images = []

    # 1. Stable Diffusion 生成AI高清关键帧
    for i in range(key_count):
        print(f"正在AI生成关键帧 {i+1}/{key_count}")
        img = pipe(
            prompt = prompt,
            negative_prompt = neg_prompt,
            height = 768,
            width = 1024,
            num_inference_steps = 25
        ).images[0]
        key_images.append(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))

    # 2. 帧插值补齐所有帧
    full_sequence = []
    seg_frames = int(total_frames / (key_count-1))

    for i in range(key_count-1):
        interp = simple_frame_interpolate(key_images[i], key_images[i+1], seg_frames)
        full_sequence.extend(interp)

    # 3. 合成高清mp4
    vid_id = str(uuid.uuid4())[:8]
    out_path = f"ai_video_{vid_id}.mp4"
    h,w = key_images[0].shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w,h))
    for f in full_sequence[:total_frames]:
        writer.write(f)
    writer.release()

    return out_path

# 前端页面
@app.get("/")
def index():
    return FileResponse("index.html")

# 生成接口
@app.post("/api/generate")
def gen_video(req:GenReq):
    path = create_ai_video(req.prompt, req.negative_prompt, req.duration, req.fps)
    return {"success":True, "video":f"/{path}"}

# 访问视频
@app.get("/{vid_name}")
def get_file(vid_name):
    return FileResponse(vid_name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)