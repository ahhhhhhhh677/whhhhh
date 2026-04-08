from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random

app = FastAPI(title="高级AI视频生成器")

class GenReq(BaseModel):
    prompt: str
    duration: int = 4
    fps: int = 15
    style: str = "realistic"  # realistic, anime, painting, cyberpunk

# 高级图像生成函数
def generate_advanced_frame(prompt, frame_idx, total_frames, style="realistic"):
    """使用PIL生成高质量图像帧"""
    # 减小图像大小以减少内存使用
    width, height = 640, 480
    
    try:
        # 创建基础图像
        img = Image.new('RGB', (width, height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 根据风格选择颜色方案
        if style == "anime":
            colors = {
                'sky_top': (135, 206, 250),
                'sky_bottom': (255, 218, 185),
                'ground': (144, 238, 144),
                'sun': (255, 255, 0)
            }
        elif style == "cyberpunk":
            colors = {
                'sky_top': (10, 0, 40),
                'sky_bottom': (40, 0, 80),
                'ground': (20, 20, 40),
                'sun': (255, 0, 128)
            }
        elif style == "painting":
            colors = {
                'sky_top': (70, 130, 180),
                'sky_bottom': (255, 160, 122),
                'ground': (85, 107, 47),
                'sun': (255, 140, 0)
            }
        else:  # realistic
            colors = {
                'sky_top': (135, 206, 235),
                'sky_bottom': (255, 250, 205),
                'ground': (34, 139, 34),
                'sun': (255, 215, 0)
            }
        
        # 绘制渐变天空
        for y in range(height // 2):
            ratio = y / (height // 2)
            r = int(colors['sky_top'][0] * (1 - ratio) + colors['sky_bottom'][0] * ratio)
            g = int(colors['sky_top'][1] * (1 - ratio) + colors['sky_bottom'][1] * ratio)
            b = int(colors['sky_top'][2] * (1 - ratio) + colors['sky_bottom'][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # 绘制地面
        draw.rectangle([0, height // 2, width, height], fill=colors['ground'])
        
        # 绘制太阳/月亮
        sun_x = int(width * 0.8)
        sun_y = int(height * 0.15)
        sun_size = 40  # 减小太阳大小
        
        # 太阳光晕
        for i in range(3, 0, -1):  # 减少光晕层数
            halo_size = sun_size + i * 15
            draw.ellipse([sun_x - halo_size, sun_y - halo_size, 
                          sun_x + halo_size, sun_y + halo_size], 
                         fill=(colors['sun'][0], colors['sun'][1], colors['sun'][2]))
        
        # 太阳主体
        draw.ellipse([sun_x - sun_size, sun_y - sun_size, 
                      sun_x + sun_size, sun_y + sun_size], 
                     fill=colors['sun'])
        
        # 绘制云朵
        for i in range(3):  # 减少云朵数量
            cloud_x = int((frame_idx * 2 + i * 200) % (width + 200)) - 100
            cloud_y = 80 + i * 30
            cloud_color = (255, 255, 255) if style != "cyberpunk" else (100, 100, 120)
            
            # 云朵由多个圆组成
            for j in range(3):  # 减少云朵组成圆的数量
                offset_x = j * 25 - 50
                offset_y = random.randint(-8, 8)
                size = random.randint(20, 35)
                draw.ellipse([cloud_x + offset_x - size, cloud_y + offset_y - size,
                              cloud_x + offset_x + size, cloud_y + offset_y + size], 
                             fill=cloud_color)
        
        # 绘制山脉
        mountain_points = []
        for x in range(0, width + 50, 60):  # 减少山脉点数量
            mountain_height = height // 2 - random.randint(80, 150)
            mountain_points.append((x, mountain_height))
        mountain_points.extend([(width, height // 2), (0, height // 2)])
        
        mountain_color = (100, 100, 120) if style != "cyberpunk" else (40, 30, 60)
        draw.polygon(mountain_points, fill=mountain_color)
        
        # 绘制树木
        for i in range(5):  # 减少树木数量
            tree_x = i * (width // 5) + random.randint(-20, 20)
            tree_y = height // 2 + random.randint(-15, 15)
            
            # 树干
            trunk_color = (101, 67, 33)
            draw.rectangle([tree_x - 8, tree_y, tree_x + 8, tree_y + 45], fill=trunk_color)
            
            # 树冠
            foliage_color = (34, 139, 34) if style != "cyberpunk" else (0, 255, 128)
            draw.ellipse([tree_x - 30, tree_y - 60, tree_x + 30, tree_y + 15], fill=foliage_color)
        
        # 添加粒子效果（雪花、雨滴等）
        if "snow" in prompt.lower() or "雪" in prompt:
            for _ in range(50):  # 减少粒子数量
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(1, 2)
                draw.ellipse([x, y, x + size, y + size], fill=(255, 255, 255))
        
        if "rain" in prompt.lower() or "雨" in prompt:
            for _ in range(50):  # 减少粒子数量
                x = random.randint(0, width)
                y = random.randint(0, height)
                draw.line([(x, y), (x + 2, y + 8)], fill=(150, 150, 200), width=1)
        
        # 添加文字
        # 直接使用默认字体，避免字体文件问题
        font = ImageFont.load_default()
        
        # 添加半透明背景
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([15, 15, width - 15, 60], fill=(0, 0, 0, 128))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # 处理中文字符编码问题
        try:
            draw.text((20, 20), f"AI Generated: Prompt...", fill=(255, 255, 255), font=font)
            draw.text((20, 45), f"Frame: {frame_idx + 1}/{total_frames} | Style: {style}", fill=(255, 255, 255), font=font)
        except Exception as e:
            print(f"文字添加错误: {e}")
            # 跳过文字添加，避免编码问题
        
        # 应用后期处理效果
        if style == "painting":
            img = img.filter(ImageFilter.SMOOTH)
        elif style == "cyberpunk":
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)  # 减少对比度增强
        
        return np.array(img)
    except Exception as e:
        print(f"帧生成错误: {e}")
        # 返回默认帧
        default_frame = np.zeros((height, width, 3), dtype=np.uint8)
        default_frame[:] = (100, 100, 100)
        return default_frame

# 帧插值函数
def interpolate_frames(frames, target_count):
    """在帧之间插入过渡帧"""
    result = []
    n = len(frames)
    
    for i in range(n - 1):
        result.append(frames[i])
        # 插入过渡帧
        steps = target_count // (n - 1)
        for j in range(1, steps):
            alpha = j / steps
            blended = cv2.addWeighted(frames[i], 1 - alpha, frames[i + 1], alpha, 0)
            result.append(blended)
    
    result.append(frames[-1])
    return result[:target_count]

def create_ai_video(prompt, duration, fps, style):
    total_frames = duration * fps
    key_frames_count = 5  # 生成5个关键帧
    
    print(f"正在生成AI视频: {prompt}")
    print(f"参数: {duration}秒, {fps}fps, {style}风格")
    
    # 生成关键帧
    key_frames = []
    for i in range(key_frames_count):
        print(f"生成关键帧 {i + 1}/{key_frames_count}...")
        frame = generate_advanced_frame(prompt, i, key_frames_count, style)
        key_frames.append(frame)
    
    # 插值生成完整序列
    print("正在进行帧插值...")
    full_sequence = interpolate_frames(key_frames, total_frames)
    
    # 合成视频
    vid_id = str(uuid.uuid4())[:8]
    out_path = f"ai_video_{vid_id}.mp4"
    h, w = full_sequence[0].shape[:2]
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
    
    for i, frame in enumerate(full_sequence):
        # BGR转换
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        writer.write(frame_bgr)
        if (i + 1) % 10 == 0:
            print(f"写入帧 {i + 1}/{total_frames}")
    
    writer.release()
    print(f"视频生成完成: {out_path}")
    
    return out_path

@app.get("/")
def index():
    return FileResponse("index_advanced.html")

@app.post("/api/generate")
def gen_video(req: GenReq):
    try:
        path = create_ai_video(req.prompt, req.duration, req.fps, req.style)
        return {"success": True, "video": f"/{path}"}
    except Exception as e:
        print(f"错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{vid_name}")
def get_file(vid_name):
    if os.path.exists(vid_name):
        return FileResponse(vid_name)
    return {"error": "文件不存在"}

if __name__ == "__main__":
    import uvicorn
    print("启动高级AI视频生成器...")
    print("访问地址: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)