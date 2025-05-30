#!/usr/bin/env python3
"""
绿色智能船艇农文旅服务平台启动脚本
"""
import uvicorn
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚢 启动绿色智能船艇农文旅服务平台...")
    print("📝 API文档地址: http://localhost:8000/docs")
    print("📊 ReDoc文档地址: http://localhost:8000/redoc")
    print("🔄 按 Ctrl+C 停止服务")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        access_log=True
    ) 