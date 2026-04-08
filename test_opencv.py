import numpy as np
import cv2
import os

print("Testing OpenCV functionality...")

try:
    # Create a simple test image
    h, w = 512, 896
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:] = [100, 150, 200]  # Blue color
    
    # Add some text
    cv2.putText(frame, "Test Image", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    
    # Save as image
    image_path = "test_image.png"
    cv2.imwrite(image_path, frame)
    
    if os.path.exists(image_path):
        print(f"Test image saved successfully: {image_path}")
        print(f"File size: {os.path.getsize(image_path)} bytes")
    else:
        print("Failed to save test image")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed")