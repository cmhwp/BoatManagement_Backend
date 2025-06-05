from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.deps import get_current_user, get_current_active_user
from app.utils.cos_client import cos_client
from app.models.user import User
from app.schemas.common import ApiResponse
from app.crud.user import update_user
from app.schemas.user import UserUpdate

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])


@router.post("/avatar", response_model=ApiResponse[dict])
async def upload_avatar(
    file: UploadFile = File(..., description="头像文件"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    上传用户头像
    
    - 支持格式: jpg, jpeg, png, gif, webp
    - 最大文件大小: 10MB
    - 自动替换旧头像
    """
    try:
        # 上传头像到COS
        avatar_url = cos_client.upload_avatar(file, current_user.id)
        
        # 删除旧头像（如果存在）
        if current_user.avatar:
            cos_client.delete_file(current_user.avatar)
        
        # 更新用户头像URL
        user_update = UserUpdate(avatar=avatar_url)
        updated_user = update_user(db, current_user.id, user_update)
        
        return ApiResponse.success_response(
            data={
                "avatar_url": avatar_url,
                "user_id": current_user.id
            },
            message="头像上传成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"头像上传失败: {str(e)}"
        )


@router.post("/identity/front", response_model=ApiResponse[dict])
async def upload_identity_front_image(
    file: UploadFile = File(..., description="身份证正面照片"),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传身份证正面照片
    
    用于实名认证
    """
    try:
        image_url = cos_client.upload_identity_image(file, current_user.id)
        
        return ApiResponse.success_response(
            data={
                "image_url": image_url,
                "image_type": "front",
                "user_id": current_user.id
            },
            message="身份证正面照片上传成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"身份证正面照片上传失败: {str(e)}"
        )


@router.post("/identity/back", response_model=ApiResponse[dict])
async def upload_identity_back_image(
    file: UploadFile = File(..., description="身份证背面照片"),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传身份证背面照片
    
    用于实名认证
    """
    try:
        image_url = cos_client.upload_identity_image(file, current_user.id)
        
        return ApiResponse.success_response(
            data={
                "image_url": image_url,
                "image_type": "back",
                "user_id": current_user.id
            },
            message="身份证背面照片上传成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"身份证背面照片上传失败: {str(e)}"
        )


@router.post("/boat/images", response_model=ApiResponse[dict])
async def upload_boat_images(
    files: List[UploadFile] = File(..., description="船艇图片列表"),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传船艇图片（批量）
    
    - 支持多张图片上传
    - 用于船艇信息展示
    """
    try:
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="一次最多上传10张图片"
            )
        
        image_urls = cos_client.upload_multiple_files(files, cos_client.cos_settings.boat_prefix, current_user.id)
        
        return ApiResponse.success_response(
            data={
                "image_urls": image_urls,
                "count": len(image_urls),
                "user_id": current_user.id
            },
            message=f"成功上传 {len(image_urls)} 张船艇图片"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"船艇图片上传失败: {str(e)}"
        )


@router.post("/service/images", response_model=ApiResponse[dict])
async def upload_service_images(
    files: List[UploadFile] = File(..., description="服务图片列表"),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传服务图片（批量）
    
    - 支持多张图片上传
    - 用于服务信息展示
    """
    try:
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="一次最多上传10张图片"
            )
        
        image_urls = cos_client.upload_multiple_files(files, cos_client.cos_settings.service_prefix, current_user.id)
        
        return ApiResponse.success_response(
            data={
                "image_urls": image_urls,
                "count": len(image_urls),
                "user_id": current_user.id
            },
            message=f"成功上传 {len(image_urls)} 张服务图片"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务图片上传失败: {str(e)}"
        )


@router.post("/product/images", response_model=ApiResponse[dict])
async def upload_product_images(
    files: List[UploadFile] = File(..., description="产品图片列表"),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传农产品图片（批量）
    
    - 支持多张图片上传
    - 用于农产品信息展示
    """
    try:
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="一次最多上传10张图片"
            )
        
        image_urls = cos_client.upload_multiple_files(files, cos_client.cos_settings.product_prefix, current_user.id)
        
        return ApiResponse.success_response(
            data={
                "image_urls": image_urls,
                "count": len(image_urls),
                "user_id": current_user.id
            },
            message=f"成功上传 {len(image_urls)} 张产品图片"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"产品图片上传失败: {str(e)}"
        )


@router.post("/review/images", response_model=ApiResponse[dict])
async def upload_review_images(
    files: List[UploadFile] = File(..., description="评价图片列表"),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传评价图片（批量）
    
    - 支持多张图片上传
    - 用于评价展示
    """
    try:
        if len(files) > 9:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="一次最多上传9张图片"
            )
        
        image_urls = cos_client.upload_multiple_files(files, cos_client.cos_settings.review_prefix, current_user.id)
        
        return ApiResponse.success_response(
            data={
                "image_urls": image_urls,
                "count": len(image_urls),
                "user_id": current_user.id
            },
            message=f"成功上传 {len(image_urls)} 张评价图片"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评价图片上传失败: {str(e)}"
        )


@router.delete("/file", response_model=ApiResponse[dict])
async def delete_file(
    file_url: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    删除指定的文件
    
    - 只能删除自己上传的文件
    """
    try:
        # 检查文件URL是否属于当前用户
        if f"/{current_user.id}_" not in file_url:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能删除自己上传的文件"
            )
        
        success = cos_client.delete_file(file_url)
        
        if success:
            return ApiResponse.success_response(
                data={"deleted_file": file_url},
                message="文件删除成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="文件删除失败"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {str(e)}"
        )


@router.get("/file/info", response_model=ApiResponse[dict])
async def get_file_info(
    file_url: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取文件信息
    """
    try:
        file_info = cos_client.get_file_info(file_url)
        
        if file_info:
            return ApiResponse.success_response(
                data=file_info,
                message="获取文件信息成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件信息失败: {str(e)}"
        ) 