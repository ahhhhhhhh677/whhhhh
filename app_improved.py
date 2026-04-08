from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
import time
import uuid
import re

app = FastAPI(title="本地AI视频生成引擎")

class GenerateRequest(BaseModel):
    prompt: str
    duration: int = 3  # 秒
    fps: int = 10      # 帧率

# 分析提示词，提取关键词
def analyze_prompt(prompt):
    # 简单的关键词提取
    keywords = {
        "colors": [],
        "objects": [],
        "actions": [],
        "settings": []
    }
    
    # 颜色关键词
    color_words = ["红", "蓝", "绿", "黄", "紫", "橙", "粉", "黑", "白", "灰"]
    for color in color_words:
        if color in prompt:
            keywords["colors"].append(color)
    
    # 物体关键词
    object_words = ["猫", "狗", "鸟", "汽车", "飞机", "树", "花", "房子", "山", "河"]
    for obj in object_words:
        if obj in prompt:
            keywords["objects"].append(obj)
    
    # 动作关键词
    action_words = ["跑", "飞", "跳", "走", "游", "舞", "唱", "笑", "哭"]
    for action in action_words:
        if action in prompt:
            keywords["actions"].append(action)
    
    # 场景关键词
    setting_words = ["森林", "城市", "海滩", "太空", "草原", "山脉", "河流", "湖泊", "沙漠", "雪山"]
    for setting in setting_words:
        if setting in prompt:
            keywords["settings"].append(setting)
    
    return keywords

# 根据关键词生成颜色
def get_color_from_keyword(keyword):
    color_map = {
        "红": "255, 0, 0",
        "蓝": "0, 0, 255",
        "绿": "0, 255, 0",
        "黄": "255, 255, 0",
        "紫": "128, 0, 128",
        "橙": "255, 165, 0",
        "粉": "255, 192, 203",
        "黑": "0, 0, 0",
        "白": "255, 255, 255",
        "灰": "128, 128, 128"
    }
    return color_map.get(keyword, "100, 150, 200")

# 核心：生成连续视频（模拟大模型视频生成）
def generate_video(prompt, duration=3, fps=10):
    total_frames = duration * fps
    video_id = str(uuid.uuid4())[:8]
    interval_ms = int(1000/fps)
    
    # 分析提示词
    keywords = analyze_prompt(prompt)
    
    # 生成一个改进的HTML5视频页面
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
        .prompt-info { margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Generated Video: ''' + prompt + '''</h1>
    <div class="prompt-info">
        <h3>AI分析结果:</h3>
        <p><strong>关键词:</strong> ''' + ", ".join(keywords["colors"] + keywords["objects"] + keywords["actions"] + keywords["settings"]) + '''</p>
    </div>
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
        
        // 提示词分析结果
        const keywords = {
            colors: ''' + str(keywords["colors"]) + ''',
            objects: ''' + str(keywords["objects"]) + ''',
            actions: ''' + str(keywords["actions"]) + ''',
            settings: ''' + str(keywords["settings"]) + '''
        };
        
        // 颜色映射
        const colorMap = {
            "红": "255, 0, 0",
            "蓝": "0, 0, 255",
            "绿": "0, 255, 0",
            "黄": "255, 255, 0",
            "紫": "128, 0, 128",
            "橙": "255, 165, 0",
            "粉": "255, 192, 203",
            "黑": "0, 0, 0",
            "白": "255, 255, 255",
            "灰": "128, 128, 128"
        };
        
        // 绘制场景
        function drawScene(frameIndex) {
            // 清除画布
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 根据场景关键词绘制背景
            let bgColor = "135, 206, 235"; // 默认天空蓝
            if (keywords.settings.includes("森林")) {
                bgColor = "34, 139, 34";
            } else if (keywords.settings.includes("城市")) {
                bgColor = "128, 128, 128";
            } else if (keywords.settings.includes("海滩")) {
                bgColor = "135, 206, 250";
            } else if (keywords.settings.includes("太空")) {
                bgColor = "0, 0, 0";
            } else if (keywords.settings.includes("沙漠")) {
                bgColor = "238, 203, 173";
            }
            
            // 绘制背景
            ctx.fillStyle = "rgb(" + bgColor + ")";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 绘制太空星星
            if (keywords.settings.includes("太空")) {
                for (let i = 0; i < 100; i++) {
                    const x = Math.random() * canvas.width;
                    const y = Math.random() * canvas.height;
                    const size = Math.random() * 2;
                    ctx.fillStyle = "white";
                    ctx.beginPath();
                    ctx.arc(x, y, size, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            
            // 绘制地面
            if (!keywords.settings.includes("太空")) {
                let groundColor = "139, 69, 19";
                if (keywords.settings.includes("海滩")) {
                    groundColor = "255, 248, 220";
                } else if (keywords.settings.includes("草原")) {
                    groundColor = "34, 139, 34";
                }
                ctx.fillStyle = "rgb(" + groundColor + ")";
                ctx.fillRect(0, canvas.height * 0.7, canvas.width, canvas.height * 0.3);
            }
            
            // 绘制物体
            drawObjects(frameIndex);
            
            // 绘制文字
            ctx.fillStyle = "white";
            ctx.font = "24px Arial";
            ctx.fillText('Prompt: ''' + prompt[:30] + '''...', 30, 60);
            ctx.fillText('Frame: ' + frameIndex, 30, 120);
        }
        
        // 绘制物体
        function drawObjects(frameIndex) {
            // 绘制太阳
            if (!keywords.settings.includes("太空")) {
                const sunX = 100 + Math.sin(frameIndex * 0.1) * 50;
                const sunY = 100 + Math.cos(frameIndex * 0.1) * 30;
                ctx.fillStyle = "rgb(255, 255, 0)";
                ctx.beginPath();
                ctx.arc(sunX, sunY, 50, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // 绘制树木
            if (keywords.settings.includes("森林") || keywords.settings.includes("草原")) {
                for (let i = 0; i < 5; i++) {
                    const x = 150 + i * 180;
                    const y = canvas.height * 0.7;
                    
                    // 树干
                    ctx.fillStyle = "rgb(139, 69, 19)";
                    ctx.fillRect(x - 10, y - 100, 20, 100);
                    
                    // 树冠
                    ctx.fillStyle = "rgb(34, 139, 34)";
                    ctx.beginPath();
                    ctx.arc(x, y - 120, 50, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            
            // 绘制汽车
            if (keywords.objects.includes("汽车")) {
                const carX = (frameIndex * 5) % (canvas.width + 200) - 100;
                const carY = canvas.height * 0.65;
                
                // 车身
                ctx.fillStyle = "rgb(" + (keywords.colors.length > 0 ? colorMap[keywords.colors[0]] : "255, 0, 0") + ")";
                ctx.fillRect(carX, carY - 30, 100, 30);
                
                // 车顶
                ctx.fillStyle = "rgb(" + (keywords.colors.length > 0 ? colorMap[keywords.colors[0]] : "255, 0, 0") + ")";
                ctx.fillRect(carX + 20, carY - 40, 60, 10);
                
                // 车轮
                ctx.fillStyle = "rgb(0, 0, 0)";
                ctx.beginPath();
                ctx.arc(carX + 30, carY, 10, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(carX + 70, carY, 10, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // 绘制飞机
            if (keywords.objects.includes("飞机")) {
                const planeX = (frameIndex * 8) % (canvas.width + 200) - 100;
                const planeY = 150 + Math.sin(frameIndex * 0.2) * 50;
                
                // 机身
                ctx.fillStyle = "rgb(128, 128, 128)";
                ctx.fillRect(planeX, planeY, 80, 10);
                
                // 机翼
                ctx.fillStyle = "rgb(128, 128, 128)";
                ctx.fillRect(planeX + 30, planeY - 20, 20, 40);
                
                // 尾翼
                ctx.fillStyle = "rgb(128, 128, 128)";
                ctx.fillRect(planeX + 70, planeY - 10, 10, 20);
            }
            
            // 绘制猫
            if (keywords.objects.includes("猫")) {
                const catX = 200 + Math.sin(frameIndex * 0.1) * 50;
                const catY = canvas.height * 0.6;
                
                // 身体
                ctx.fillStyle = "rgb(" + (keywords.colors.length > 0 ? colorMap[keywords.colors[0]] : "169, 169, 169") + ")";
                ctx.beginPath();
                ctx.arc(catX, catY, 30, 0, Math.PI * 2);
                ctx.fill();
                
                // 头部
                ctx.beginPath();
                ctx.arc(catX - 25, catY - 15, 15, 0, Math.PI * 2);
                ctx.fill();
                
                // 耳朵
                ctx.beginPath();
                ctx.moveTo(catX - 35, catY - 25);
                ctx.lineTo(catX - 25, catY - 35);
                ctx.lineTo(catX - 15, catY - 25);
                ctx.fill();
                
                ctx.beginPath();
                ctx.moveTo(catX - 15, catY - 25);
                ctx.lineTo(catX - 5, catY - 35);
                ctx.lineTo(catX + 5, catY - 25);
                ctx.fill();
                
                // 尾巴
                const tailX = catX + 30 + Math.sin(frameIndex * 0.3) * 20;
                const tailY = catY + Math.cos(frameIndex * 0.3) * 10;
                ctx.beginPath();
                ctx.moveTo(catX + 30, catY);
                ctx.lineTo(tailX, tailY);
                ctx.lineWidth = 8;
                ctx.strokeStyle = "rgb(" + (keywords.colors.length > 0 ? colorMap[keywords.colors[0]] : "169, 169, 169") + ")";
                ctx.stroke();
                ctx.lineWidth = 1;
            }
            
            // 绘制狗
            if (keywords.objects.includes("狗")) {
                const dogX = 300 + Math.sin(frameIndex * 0.1) * 50;
                const dogY = canvas.height * 0.6;
                
                // 身体
                ctx.fillStyle = "rgb(" + (keywords.colors.length > 0 ? colorMap[keywords.colors[0]] : "139, 69, 19") + ")";
                ctx.beginPath();
                ctx.arc(dogX, dogY, 35, 0, Math.PI * 2);
                ctx.fill();
                
                // 头部
                ctx.beginPath();
                ctx.arc(dogX - 30, dogY - 10, 20, 0, Math.PI * 2);
                ctx.fill();
                
                // 耳朵
                ctx.beginPath();
                ctx.moveTo(dogX - 40, dogY - 20);
                ctx.lineTo(dogX - 30, dogY - 30);
                ctx.lineTo(dogX - 20, dogY - 20);
                ctx.fill();
                
                ctx.beginPath();
                ctx.moveTo(dogX - 20, dogY - 20);
                ctx.lineTo(dogX - 10, dogY - 30);
                ctx.lineTo(dogX, dogY - 20);
                ctx.fill();
                
                // 尾巴
                const tailX = dogX + 35 + Math.sin(frameIndex * 0.4) * 25;
                const tailY = dogY - 10 + Math.cos(frameIndex * 0.4) * 15;
                ctx.beginPath();
                ctx.moveTo(dogX + 35, dogY);
                ctx.lineTo(tailX, tailY);
                ctx.lineWidth = 10;
                ctx.strokeStyle = "rgb(" + (keywords.colors.length > 0 ? colorMap[keywords.colors[0]] : "139, 69, 19") + ")";
                ctx.stroke();
                ctx.lineWidth = 1;
            }
        }
        
        function drawFrame(frameIndex) {
            drawScene(frameIndex);
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