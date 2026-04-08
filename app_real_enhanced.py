from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os
import cv2
import numpy as np
import re

app = FastAPI(title="真实视频生成 - 增强版")

class GenerateRequest(BaseModel):
    prompt: str
    duration: int = 4
    fps: int = 15

# --------------------------
# 文字语义分析
# --------------------------
def analyze_prompt(prompt):
    """分析提示词，提取关键元素"""
    elements = {
        "sky": False,
        "sun": False,
        "clouds": False,
        "mountains": False,
        "trees": False,
        "water": False,
        "flowers": False,
        "building": False,
        "people": False,
        "animals": False
    }
    
    # 关键词匹配
    if re.search(r'天空|sky|heaven', prompt, re.IGNORECASE):
        elements["sky"] = True
    if re.search(r'太阳|sun|sunshine', prompt, re.IGNORECASE):
        elements["sun"] = True
    if re.search(r'云|cloud|clouds', prompt, re.IGNORECASE):
        elements["clouds"] = True
    if re.search(r'山|mountain|mountains', prompt, re.IGNORECASE):
        elements["mountains"] = True
    if re.search(r'树|tree|trees', prompt, re.IGNORECASE):
        elements["trees"] = True
    if re.search(r'水|water|lake|river|ocean', prompt, re.IGNORECASE):
        elements["water"] = True
    if re.search(r'花|flower|flowers', prompt, re.IGNORECASE):
        elements["flowers"] = True
    if re.search(r'建筑|building|buildings', prompt, re.IGNORECASE):
        elements["building"] = True
    if re.search(r'人|person|people|human', prompt, re.IGNORECASE):
        elements["people"] = True
    if re.search(r'动物|animal|animals', prompt, re.IGNORECASE):
        elements["animals"] = True
    
    return elements

# --------------------------
# 真实画面生成（增强版）
# --------------------------
def create_real_frame(frame_idx, total_frames, prompt):
    H, W = 720, 1280
    frame = np.zeros((H, W, 3), dtype=np.uint8)

    t = frame_idx / total_frames
    elements = analyze_prompt(prompt)

    # 渐变天空（根据元素调整）
    for y in range(H//2):
        if elements["sky"]:
            blue = 130 + int(30 * np.sin(t*2))
            green = 180 + int(40 * np.cos(t*3))
            red = 210 + int(35 * np.sin(t*5))
        else:
            blue = 100 + int(20 * np.sin(t*2))
            green = 120 + int(30 * np.cos(t*3))
            red = 140 + int(25 * np.sin(t*5))
        frame[y] = [blue, green, red]

    # 渐变地面
    for y in range(H//2, H):
        if elements["water"]:
            frame[y] = [40, 80, 120]
        elif elements["flowers"]:
            frame[y] = [80, 100, 60]
        else:
            frame[y] = [60, 90, 70]

    # 移动太阳
    if elements["sun"]:
        x = int(300 + 600 * np.sin(t * 1.5))
        y = 180
        for dy in range(-80, 80):
            for dx in range(-80, 80):
                if dx**2 + dy**2 < 80**2:
                    fy = y + dy
                    fx = x + dx
                    if 0 < fy < H and 0 < fx < W:
                        frame[fy, fx] = [200, 255, 255]

    # 绘制云朵
    if elements["clouds"]:
        for i in range(3):
            cloud_x = int(200 + i * 300 + t * 100)
            cloud_y = 100 + i * 50
            for j in range(3):
                offset_x = j * 30 - 30
                size = 30 + j * 10
                for dy in range(-size, size):
                    for dx in range(-size, size):
                        if dx**2 + dy**2 < size**2:
                            fy = cloud_y + dy
                            fx = cloud_x + dx
                            if 0 < fy < H//2 and 0 < fx < W:
                                frame[fy, fx] = [255, 255, 255]

    # 绘制山脉
    if elements["mountains"]:
        mountain_points = []
        for x in range(0, W + 100, 100):
            mountain_height = H//2 - 150 + int(50 * np.sin(x/500 + t))
            mountain_points.append((x, mountain_height))
        mountain_points.extend([(W, H//2), (0, H//2)])
        
        # 绘制山脉
        for i in range(len(mountain_points)-1):
            x1, y1 = mountain_points[i]
            x2, y2 = mountain_points[i+1]
            for x in range(min(x1, x2), max(x1, x2)):
                y = int(y1 + (y2 - y1) * (x - x1) / (x2 - x1))
                for dy in range(0, H//2 - y):
                    if y + dy < H:
                        frame[y + dy, x] = [80, 80, 100]

    # 绘制树木
    if elements["trees"]:
        for i in range(5):
            tree_x = int(100 + i * 200 + t * 50)
            tree_y = H//2 + 50
            
            # 树干
            for dx in range(-8, 8):
                for dy in range(0, 40):
                    if 0 < tree_x + dx < W and tree_y + dy < H:
                        frame[tree_y + dy, tree_x + dx] = [80, 50, 30]
            
            # 树冠
            for dx in range(-30, 30):
                for dy in range(-40, 10):
                    if dx**2 + dy**2 < 30**2:
                        if 0 < tree_x + dx < W and tree_y + dy > 0:
                            frame[tree_y + dy, tree_x + dx] = [30, 100, 50]

    # 光线效果
    alpha = 0.3 + 0.1 * np.sin(t*4)
    frame = cv2.convertScaleAbs(frame, alpha=1-alpha, beta=20)

    # 文字水印
    cv2.putText(frame, "REALISTIC AI VIDEO", (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)
    cv2.putText(frame, f"Prompt: {prompt[:30]}...", (50, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    return frame

# --------------------------
# 高级帧插值
# --------------------------
def blend_smooth(a, b, n=6):
    res = []
    for t in np.linspace(0, 1, n):
        res.append(cv2.addWeighted(a, 1-t, b, t, 0))
    return res

# --------------------------
# 生成流畅高清视频
# --------------------------
def generate_real_video(prompt, duration, fps):
    total = duration * fps
    vid = str(uuid.uuid4())[:8]
    out_path = f"REAL_{vid}.mp4"

    # 生成关键帧
    key_frames = []
    key_texts = [
        prompt + " (wide view)",
        prompt + " (close up)",
        prompt + " (dynamic angle)"
    ]

    print("正在根据你的文字生成真实画面...")
    for i, text in enumerate(key_texts):
        frame_idx = int(i * total / (len(key_texts)-1))
        frame = create_real_frame(frame_idx, total, text)
        key_frames.append(frame)

    # 插值生成完整视频
    full_frames = []
    seg = total // (len(key_frames)-1)
    for i in range(len(key_frames)-1):
        full_frames += blend_smooth(key_frames[i], key_frames[i+1], seg)

    # 写入视频
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, fps, (1280, 720))

    for frame in full_frames[:total]:
        out.write(frame)

    out.release()
    return out_path

# --------------------------
# 接口
# --------------------------
@app.get("/")
def index():
    return FileResponse("index.html")

@app.post("/api/generate")
def gen(req: GenerateRequest):
    try:
        path = generate_real_video(req.prompt, req.duration, req.fps)
        return {"success": True, "video": f"/{path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{name}")
def get_file(name):
    return FileResponse(name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)