from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import numpy as np
import cv2
import os
import time
import uuid

app = FastAPI(title="本地AI视频生成引擎")

class GenerateRequest(BaseModel):
    prompt: str
    duration: int = 3  # 秒
    fps: int = 10      # 帧率

# 生成单帧图像（模拟大模型文生图）
def generate_frame(prompt, frame_idx):
    h, w = 512, 896
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    
    # 模拟AI根据文字生成画面
    color1 = int(100 + (frame_idx * 7) % 155)
    color2 = int(50 + (frame_idx * 13) % 200)
    color3 = int(150 + (frame_idx * 5) % 105)
    
    frame[:] = [color1, color2, color3]
    
    # 添加文字
    cv2.putText(frame, f"Prompt: {prompt[:20]}", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    cv2.putText(frame, f"Frame: {frame_idx}", (30, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    
    # 模拟运动效果（帧间变化）
    shift = frame_idx * 5 % 50
    cv2.circle(frame, (450 + shift, 256), 80, (255, 200, 150), -1)
    
    return frame

# 核心：生成连续视频（模拟大模型视频生成）
def generate_video(prompt, duration=3, fps=10):
    total_frames = duration * fps
    video_id = str(uuid.uuid4())[:8]
    output_path = f"video_{video_id}.avi"  # 使用AVI格式更兼容
    
    try:
        # 使用XVID编码，更通用
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, fps, (896, 512))
        
        for i in range(total_frames):
            frame = generate_frame(prompt, i)
            out.write(frame)
        
        out.release()
        
        # 检查文件是否创建成功
        if not os.path.exists(output_path):
            raise Exception("视频文件未创建")
        
        if os.path.getsize(output_path) < 100:
            raise Exception("视频文件为空")
        
        return output_path
    except Exception as e:
        print(f"视频生成错误: {e}")
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