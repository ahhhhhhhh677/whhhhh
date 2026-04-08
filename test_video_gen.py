import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont

print("Testing video generation...")

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
    try:
        image.save(output_path)
        print(f"Saved frame {frame_idx} to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving frame {frame_idx}: {e}")
        return False

# Test frame generation
test_dir = "test_frames"
os.makedirs(test_dir, exist_ok=True)

print("Generating test frames...")
for i in range(5):
    frame_path = os.path.join(test_dir, f"test_frame_{i:04d}.png")
    success = generate_frame("Test video", i, frame_path)
    if not success:
        print("Frame generation failed!")
        sys.exit(1)

print("Frame generation successful!")
print(f"Generated {len(os.listdir(test_dir))} frames in {test_dir}")

# Check if frames were created
if len(os.listdir(test_dir)) == 5:
    print("Test passed! All frames were generated successfully.")
else:
    print("Test failed! Not all frames were generated.")

print("Test completed.")