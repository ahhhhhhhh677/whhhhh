import sys
print("Python version:", sys.version)

try:
    import fastapi
    print("FastAPI installed:", fastapi.__version__)
except ImportError:
    print("FastAPI not installed")

try:
    import uvicorn
    print("Uvicorn installed:", uvicorn.__version__)
except ImportError:
    print("Uvicorn not installed")

try:
    import cv2
    print("OpenCV installed:", cv2.__version__)
except ImportError:
    print("OpenCV not installed")

try:
    import numpy
    print("NumPy installed:", numpy.__version__)
except ImportError:
    print("NumPy not installed")

print("Test completed")