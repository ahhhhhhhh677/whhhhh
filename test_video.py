import numpy as np
import cv2
import uuid
import os

print("Testing video generation...")

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

def generate_video(prompt, duration=3, fps=10):
    total_frames = duration * fps
    video_id = str(uuid.uuid4())[:8]
    output_path = f"test_video_{video_id}.mp4"
    
    print(f"Generating video: {output_path}")
    print(f"Total frames: {total_frames}")
    
    try:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (896, 512))
        
        for i in range(total_frames):
            frame = generate_frame(prompt, i)
            out.write(frame)
            if i % 5 == 0:
                print(f"Generated frame {i}/{total_frames}")
        
        out.release()
        print(f"Video generated successfully: {output_path}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
        return output_path
    except Exception as e:
        print(f"Error generating video: {e}")
        import traceback
        traceback.print_exc()
        return None

# Test the video generation
if __name__ == "__main__":
    video_path = generate_video("Test video generation", duration=2, fps=5)
    if video_path:
        print(f"Test completed. Video saved to: {video_path}")
    else:
        print("Test failed.")