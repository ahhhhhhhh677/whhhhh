from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
import time
import uuid

app = FastAPI(title="本地AI视频生成引擎")

class GenerateRequest(BaseModel):
    prompt: str
    duration: int = 3  # 秒
    fps: int = 10      # 帧率

# 核心：生成连续视频（模拟大模型视频生成）
def generate_video(prompt, duration=3, fps=10):
    total_frames = duration * fps
    video_id = str(uuid.uuid4())[:8]
    interval_ms = int(1000/fps)
    
    # 生成一个简单的HTML5视频页面
    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Generated Video</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .video-container { width: 100%; max-width: 896px; margin: 0 auto; }
        canvas { border: 1px solid #ccc; }
        .controls { margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Generated Video: ''' + prompt + '''</h1>
    <div class="controls">
        <button onclick="playVideo()">Play</button>
        <button onclick="pauseVideo()">Pause</button>
        <button onclick="stopVideo()">Stop</button>
        <span id="status">Ready</span>
    </div>
    <div class="video-container">
        <canvas id="videoCanvas" width="896" height="512"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('videoCanvas');
        const ctx = canvas.getContext('2d');
        const totalFrames = ''' + str(total_frames) + ''';
        const fps = ''' + str(fps) + ''';
        let currentFrame = 0;
        let isPlaying = false;
        let interval;
        
        function drawFrame(frameIndex) {
            // 清除画布
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 绘制背景
            const color1 = 100 + (frameIndex * 7) % 155;
            const color2 = 50 + (frameIndex * 13) % 200;
            const color3 = 150 + (frameIndex * 5) % 105;
            ctx.fillStyle = 'rgb(' + color1 + ', ' + color2 + ', ' + color3 + ')';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 绘制文字
            ctx.fillStyle = 'white';
            ctx.font = '24px Arial';
            ctx.fillText('Prompt: ''' + prompt[:20] + '''', 30, 60);
            ctx.fillText('Frame: ' + frameIndex, 30, 120);
            
            // 绘制移动的圆形
            const shift = (frameIndex * 5) % 50;
            ctx.fillStyle = 'rgb(255, 200, 150)';
            ctx.beginPath();
            ctx.arc(450 + shift, 256, 80, 0, Math.PI * 2);
            ctx.fill();
        }
        
        function showFrame(index) {
            drawFrame(index);
            document.getElementById('status').textContent = 'Frame ' + (index + 1) + '/' + totalFrames;
        }
        
        function playVideo() {
            if (!isPlaying) {
                isPlaying = true;
                interval = setInterval(function() {
                    currentFrame = (currentFrame + 1) % totalFrames;
                    showFrame(currentFrame);
                }, ''' + str(interval_ms) + ''');
            }
        }
        
        function pauseVideo() {
            isPlaying = false;
            clearInterval(interval);
        }
        
        function stopVideo() {
            isPlaying = false;
            clearInterval(interval);
            currentFrame = 0;
            showFrame(currentFrame);
        }
        
        // 显示第一帧
        showFrame(0);
    </script>
</body>
</html>
'''
    
    # 保存HTML页面
    html_path = f"video_{video_id}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"视频生成成功: {html_path}")
    return html_path

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
        print(f"错误: {e}")
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