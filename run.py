
import os
import sys
import uvicorn
from app.config import Config

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    print(f"Starting {Config.APP_NAME} in {Config.ENV} mode...")

    uvicorn.run(
        "app.main:app", 
        host="127.0.0.1", 
        port=8880, 
        reload=True,
        app_dir=project_root
    )