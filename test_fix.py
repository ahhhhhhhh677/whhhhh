import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import sys

def test_pil():
    """测试PIL功能"""
    print("测试PIL功能...")
    try:
        # 创建测试图像
        img = Image.new('RGB', (640, 480), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 尝试添加文字
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 10), "Test", fill=(255, 255, 255), font=font)
        
        # 转换为numpy数组
        img_np = np.array(img)
        print(f"PIL测试成功，图像形状: {img_np.shape}")
        return True
    except Exception as e:
        print(f"PIL测试失败: {e}")
        return False

def test_opencv():
    """测试OpenCV功能"""
    print("测试OpenCV功能...")
    try:
        # 创建测试帧
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # 写入文字
        cv2.putText(frame, "Test", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 测试视频写入
        test_video = "test_opencv.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(test_video, fourcc, 10, (640, 480))
        
        for i in range(10):
            writer.write(frame)
        
        writer.release()
        
        if os.path.exists(test_video):
            print(f"OpenCV测试成功，生成视频: {test_video}")
            os.remove(test_video)
            return True
        else:
            print("OpenCV测试失败，视频文件未生成")
            return False
    except Exception as e:
        print(f"OpenCV测试失败: {e}")
        return False

def test_frame_generation():
    """测试帧生成功能"""
    print("测试帧生成功能...")
    try:
        # 导入帧生成函数
        sys.path.append('.')
        from app_advanced import generate_advanced_frame
        
        # 测试生成单帧
        frame = generate_advanced_frame("樱花飘落", 0, 10, "anime")
        print(f"帧生成测试成功，帧形状: {frame.shape}")
        
        # 保存测试帧
        test_frame = "test_frame.jpg"
        cv2.imwrite(test_frame, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        if os.path.exists(test_frame):
            print(f"测试帧保存成功: {test_frame}")
            os.remove(test_frame)
            return True
        else:
            print("测试帧保存失败")
            return False
    except Exception as e:
        print(f"帧生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_video():
    """测试完整视频生成"""
    print("测试完整视频生成...")
    try:
        # 导入视频生成函数
        sys.path.append('.')
        from app_advanced import create_ai_video
        
        # 测试生成短视频
        video_path = create_ai_video("樱花飘落", 1, 10, "anime")
        
        if os.path.exists(video_path):
            print(f"视频生成测试成功，生成视频: {video_path}")
            os.remove(video_path)
            return True
        else:
            print("视频生成测试失败，视频文件未生成")
            return False
    except Exception as e:
        print(f"视频生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试...")
    
    tests = [
        ("PIL功能", test_pil),
        ("OpenCV功能", test_opencv),
        ("帧生成功能", test_frame_generation),
        ("完整视频生成", test_full_video)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n===== {test_name} =====")
        if test_func():
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
            all_passed = False
    
    print(f"\n===== 测试结果 =====")
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，需要修复")
