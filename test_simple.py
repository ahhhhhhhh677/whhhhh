import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# 测试基本PIL操作
def test_basic_pil():
    print("测试基本PIL操作...")
    try:
        img = Image.new('RGB', (640, 480), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Test", fill=(255, 255, 255))
        img_np = np.array(img)
        print(f"基本PIL操作成功，图像形状: {img_np.shape}")
        return True
    except Exception as e:
        print(f"基本PIL操作失败: {e}")
        return False

# 测试alpha_composite操作
def test_alpha_composite():
    print("测试alpha_composite操作...")
    try:
        img = Image.new('RGB', (640, 480), color=(0, 0, 0))
        overlay = Image.new('RGBA', (640, 480), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([15, 15, 625, 60], fill=(0, 0, 0, 128))
        # 这里可能是崩溃点
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        img_np = np.array(img)
        print(f"alpha_composite操作成功，图像形状: {img_np.shape}")
        return True
    except Exception as e:
        print(f"alpha_composite操作失败: {e}")
        return False

# 测试简化的帧生成
def test_simple_frame():
    print("测试简化的帧生成...")
    try:
        width, height = 640, 480
        img = Image.new('RGB', (width, height), color=(135, 206, 235))
        draw = ImageDraw.Draw(img)
        
        # 绘制简单的地面
        draw.rectangle([0, height // 2, width, height], fill=(34, 139, 34))
        
        # 绘制简单的太阳
        sun_x, sun_y = int(width * 0.8), int(height * 0.15)
        draw.ellipse([sun_x - 30, sun_y - 30, sun_x + 30, sun_y + 30], fill=(255, 215, 0))
        
        # 直接添加文字，不使用alpha_composite
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((20, 20), "Test Prompt", fill=(255, 255, 255), font=font)
        
        img_np = np.array(img)
        print(f"简化帧生成成功，图像形状: {img_np.shape}")
        
        # 保存测试图像
        test_frame = "test_simple_frame.jpg"
        cv2.imwrite(test_frame, cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
        if os.path.exists(test_frame):
            print(f"测试图像保存成功: {test_frame}")
            os.remove(test_frame)
            return True
        else:
            print("测试图像保存失败")
            return False
    except Exception as e:
        print(f"简化帧生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始简单测试...")
    
    tests = [
        ("基本PIL操作", test_basic_pil),
        ("alpha_composite操作", test_alpha_composite),
        ("简化帧生成", test_simple_frame)
    ]
    
    for test_name, test_func in tests:
        print(f"\n===== {test_name} =====")
        if test_func():
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
