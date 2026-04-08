import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# 测试步骤1: 创建基础图像
def test_step1():
    print("测试步骤1: 创建基础图像...")
    try:
        width, height = 640, 480
        img = Image.new('RGB', (width, height), color=(135, 206, 235))
        print("✅ 步骤1通过")
        return img
    except Exception as e:
        print(f"❌ 步骤1失败: {e}")
        return None

# 测试步骤2: 绘制地面
def test_step2(img):
    if img is None:
        return None
    print("测试步骤2: 绘制地面...")
    try:
        draw = ImageDraw.Draw(img)
        height = img.height
        draw.rectangle([0, height // 2, img.width, height], fill=(34, 139, 34))
        print("✅ 步骤2通过")
        return img, draw
    except Exception as e:
        print(f"❌ 步骤2失败: {e}")
        return None, None

# 测试步骤3: 绘制太阳
def test_step3(img, draw):
    if img is None or draw is None:
        return None
    print("测试步骤3: 绘制太阳...")
    try:
        width, height = img.width, img.height
        sun_x, sun_y = int(width * 0.8), int(height * 0.15)
        draw.ellipse([sun_x - 30, sun_y - 30, sun_x + 30, sun_y + 30], fill=(255, 215, 0))
        print("✅ 步骤3通过")
        return img
    except Exception as e:
        print(f"❌ 步骤3失败: {e}")
        return None

# 测试步骤4: 添加文字
def test_step4(img):
    if img is None:
        return None
    print("测试步骤4: 添加文字...")
    try:
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            print("使用arial.ttf字体")
        except:
            font = ImageFont.load_default()
            print("使用默认字体")
        draw.text((20, 20), "Test Prompt", fill=(255, 255, 255), font=font)
        print("✅ 步骤4通过")
        return img
    except Exception as e:
        print(f"❌ 步骤4失败: {e}")
        return None

# 测试步骤5: 转换为numpy数组
def test_step5(img):
    if img is None:
        return None
    print("测试步骤5: 转换为numpy数组...")
    try:
        img_np = np.array(img)
        print(f"✅ 步骤5通过，形状: {img_np.shape}")
        return img_np
    except Exception as e:
        print(f"❌ 步骤5失败: {e}")
        return None

# 测试步骤6: 保存图像
def test_step6(img_np):
    if img_np is None:
        return False
    print("测试步骤6: 保存图像...")
    try:
        test_frame = "test_step_frame.jpg"
        cv2.imwrite(test_frame, cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
        if os.path.exists(test_frame):
            print(f"✅ 步骤6通过，保存成功: {test_frame}")
            os.remove(test_frame)
            return True
        else:
            print("❌ 步骤6失败，保存失败")
            return False
    except Exception as e:
        print(f"❌ 步骤6失败: {e}")
        return False

if __name__ == "__main__":
    print("开始逐步测试...")
    
    # 执行测试步骤
    img = test_step1()
    img, draw = test_step2(img)
    img = test_step3(img, draw)
    img = test_step4(img)
    img_np = test_step5(img)
    success = test_step6(img_np)
    
    print(f"\n===== 测试结果 =====")
    if success:
        print("✅ 所有步骤测试通过！")
    else:
        print("❌ 部分步骤测试失败")
