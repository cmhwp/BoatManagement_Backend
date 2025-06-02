import os
import uuid
import shutil
from typing import Optional, List
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image
import aiofiles


# 配置
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "application/msword", 
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}

# 创建上传目录
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "images").mkdir(exist_ok=True)
(UPLOAD_DIR / "documents").mkdir(exist_ok=True)
(UPLOAD_DIR / "avatars").mkdir(exist_ok=True)


async def upload_file(
    file: UploadFile,
    folder: str = "general",
    max_size: int = MAX_FILE_SIZE,
    allowed_types: Optional[List[str]] = None
) -> dict:
    """
    上传文件
    
    Args:
        file: 上传的文件
        folder: 存储文件夹
        max_size: 最大文件大小
        allowed_types: 允许的文件类型
    
    Returns:
        dict: 包含文件信息的字典
    """
    # 检查文件大小
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail="文件过大")
    
    # 检查文件类型
    if allowed_types and file.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="不支持的文件类型")
    
    # 生成唯一文件名
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # 创建目标文件夹
    target_dir = UPLOAD_DIR / folder
    target_dir.mkdir(exist_ok=True)
    
    # 保存文件
    file_path = target_dir / unique_filename
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # 如果是图片，生成缩略图
    thumbnail_url = None
    if file.content_type in ALLOWED_IMAGE_TYPES:
        thumbnail_url = await create_thumbnail(file_path, folder)
    
    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_path": str(file_path),
        "file_url": f"/uploads/{folder}/{unique_filename}",
        "thumbnail_url": thumbnail_url,
        "content_type": file.content_type,
        "file_size": len(content)
    }


async def create_thumbnail(file_path: Path, folder: str, size: tuple = (200, 200)) -> str:
    """创建缩略图"""
    try:
        with Image.open(file_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 生成缩略图文件名
            thumbnail_name = f"thumb_{file_path.name}"
            thumbnail_path = file_path.parent / thumbnail_name
            
            # 保存缩略图
            img.save(thumbnail_path, optimize=True, quality=85)
            
            return f"/uploads/{folder}/{thumbnail_name}"
    except Exception:
        return None


async def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if file_path.startswith("/uploads/"):
            # 删除主文件
            full_path = Path(file_path[1:])  # 去掉开头的斜杠
            if full_path.exists():
                full_path.unlink()
            
            # 删除缩略图（如果存在）
            thumbnail_path = full_path.parent / f"thumb_{full_path.name}"
            if thumbnail_path.exists():
                thumbnail_path.unlink()
            
            return True
    except Exception:
        pass
    return False


def get_file_url(file_path: str, base_url: str = "") -> str:
    """获取文件访问URL"""
    if file_path.startswith("http"):
        return file_path
    return f"{base_url}{file_path}"


async def upload_avatar(file: UploadFile) -> dict:
    """上传头像"""
    return await upload_file(
        file=file,
        folder="avatars",
        max_size=2 * 1024 * 1024,  # 2MB
        allowed_types=list(ALLOWED_IMAGE_TYPES)
    )


async def upload_image(file: UploadFile) -> dict:
    """上传图片"""
    return await upload_file(
        file=file,
        folder="images",
        max_size=5 * 1024 * 1024,  # 5MB
        allowed_types=list(ALLOWED_IMAGE_TYPES)
    )


async def upload_document(file: UploadFile) -> dict:
    """上传文档"""
    return await upload_file(
        file=file,
        folder="documents",
        max_size=20 * 1024 * 1024,  # 20MB
        allowed_types=list(ALLOWED_DOCUMENT_TYPES)
    )


def validate_file_type(file: UploadFile, allowed_types: List[str]) -> bool:
    """验证文件类型"""
    return file.content_type in allowed_types


def get_file_info(file_path: str) -> dict:
    """获取文件信息"""
    try:
        path = Path(file_path)
        if path.exists():
            stat = path.stat()
            return {
                "filename": path.name,
                "file_size": stat.st_size,
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "file_extension": path.suffix
            }
    except Exception:
        pass
    return {}


async def cleanup_orphaned_files(referenced_files: List[str]):
    """清理孤立文件"""
    try:
        for folder in ["images", "documents", "avatars"]:
            folder_path = UPLOAD_DIR / folder
            if folder_path.exists():
                for file_path in folder_path.iterdir():
                    if file_path.is_file():
                        file_url = f"/uploads/{folder}/{file_path.name}"
                        if file_url not in referenced_files:
                            # 删除孤立文件
                            file_path.unlink()
    except Exception as e:
        print(f"清理孤立文件时出错: {e}") 