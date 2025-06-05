import os
import uuid
from datetime import datetime
from typing import Optional, List, Tuple
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosServiceError, CosClientError
from fastapi import UploadFile, HTTPException, status
from app.config.cos_config import cos_settings
import logging

logger = logging.getLogger(__name__)


class COSClient:
    """腾讯云COS客户端"""
    
    def __init__(self):
        """初始化COS客户端"""
        try:
            # 初始化COS配置
            config = CosConfig(
                Region=cos_settings.cos_region,
                SecretId=cos_settings.cos_secret_id,
                SecretKey=cos_settings.cos_secret_key,
                Scheme='https'
            )
            
            # 初始化COS客户端
            self.client = CosS3Client(config)
            self.bucket = cos_settings.cos_bucket
            
            logger.info("COS客户端初始化成功")
            
        except Exception as e:
            logger.error(f"COS客户端初始化失败: {str(e)}")
            raise Exception(f"COS初始化失败: {str(e)}")
    
    def _generate_file_key(self, prefix: str, file_extension: str, user_id: Optional[int] = None) -> str:
        """生成文件的COS键值"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        if user_id:
            filename = f"{user_id}_{timestamp}_{unique_id}.{file_extension}"
        else:
            filename = f"{timestamp}_{unique_id}.{file_extension}"
        
        return f"{prefix}{filename}"
    
    def _validate_image_file(self, file: UploadFile) -> str:
        """验证图片文件"""
        # 检查文件大小
        if hasattr(file, 'size') and file.size > cos_settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小超过限制 ({cos_settings.max_file_size / 1024 / 1024}MB)"
            )
        
        # 检查文件类型
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件名不能为空"
            )
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in cos_settings.allowed_image_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型，支持的类型: {', '.join(cos_settings.allowed_image_types)}"
            )
        
        return file_extension
    
    def upload_file(self, file: UploadFile, prefix: str, user_id: Optional[int] = None) -> str:
        """
        上传文件到COS
        
        Args:
            file: 上传的文件
            prefix: 文件路径前缀
            user_id: 用户ID（可选）
            
        Returns:
            str: 文件的完整URL
        """
        try:
            # 验证文件
            file_extension = self._validate_image_file(file)
            
            # 生成文件键值
            file_key = self._generate_file_key(prefix, file_extension, user_id)
            
            # 读取文件内容
            file_content = file.file.read()
            
            # 上传到COS
            response = self.client.put_object(
                Bucket=self.bucket,
                Body=file_content,
                Key=file_key,
                ContentType=file.content_type or 'image/jpeg'
            )
            
            # 构建文件URL
            file_url = f"{cos_settings.cos_domain}/{file_key}"
            
            logger.info(f"文件上传成功: {file_key}")
            return file_url
            
        except CosServiceError as e:
            logger.error(f"COS服务错误: {e.get_error_msg()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件上传失败: {e.get_error_msg()}"
            )
        except CosClientError as e:
            logger.error(f"COS客户端错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件上传失败: {str(e)}"
            )
        except Exception as e:
            logger.error(f"文件上传异常: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件上传失败: {str(e)}"
            )
        finally:
            # 重置文件指针
            file.file.seek(0)
    
    def upload_multiple_files(self, files: List[UploadFile], prefix: str, user_id: Optional[int] = None) -> List[str]:
        """
        批量上传文件
        
        Args:
            files: 文件列表
            prefix: 文件路径前缀
            user_id: 用户ID（可选）
            
        Returns:
            List[str]: 文件URL列表
        """
        urls = []
        for file in files:
            url = self.upload_file(file, prefix, user_id)
            urls.append(url)
        return urls
    
    def delete_file(self, file_url: str) -> bool:
        """
        删除COS中的文件
        
        Args:
            file_url: 文件URL
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 从URL中提取文件键值
            if file_url.startswith(cos_settings.cos_domain):
                file_key = file_url.replace(f"{cos_settings.cos_domain}/", "")
            else:
                # 如果是相对路径或其他格式
                file_key = file_url.split('/')[-1]
            
            # 删除文件
            response = self.client.delete_object(
                Bucket=self.bucket,
                Key=file_key
            )
            
            logger.info(f"文件删除成功: {file_key}")
            return True
            
        except CosServiceError as e:
            logger.error(f"删除文件COS服务错误: {e.get_error_msg()}")
            return False
        except CosClientError as e:
            logger.error(f"删除文件COS客户端错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"删除文件异常: {str(e)}")
            return False
    
    def delete_multiple_files(self, file_urls: List[str]) -> Tuple[int, int]:
        """
        批量删除文件
        
        Args:
            file_urls: 文件URL列表
            
        Returns:
            Tuple[int, int]: (成功删除数量, 失败数量)
        """
        success_count = 0
        fail_count = 0
        
        for url in file_urls:
            if self.delete_file(url):
                success_count += 1
            else:
                fail_count += 1
        
        return success_count, fail_count
    
    def get_file_info(self, file_url: str) -> Optional[dict]:
        """
        获取文件信息
        
        Args:
            file_url: 文件URL
            
        Returns:
            Optional[dict]: 文件信息
        """
        try:
            # 从URL中提取文件键值
            if file_url.startswith(cos_settings.cos_domain):
                file_key = file_url.replace(f"{cos_settings.cos_domain}/", "")
            else:
                file_key = file_url.split('/')[-1]
            
            # 获取文件信息
            response = self.client.head_object(
                Bucket=self.bucket,
                Key=file_key
            )
            
            return {
                "file_size": response.get('Content-Length', 0),
                "content_type": response.get('Content-Type', ''),
                "last_modified": response.get('Last-Modified', ''),
                "etag": response.get('ETag', '')
            }
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {str(e)}")
            return None
    
    def upload_avatar(self, file: UploadFile, user_id: int) -> str:
        """上传用户头像"""
        return self.upload_file(file, cos_settings.avatar_prefix, user_id)
    
    def upload_identity_image(self, file: UploadFile, user_id: int) -> str:
        """上传身份认证图片"""
        return self.upload_file(file, cos_settings.identity_prefix, user_id)
    
    def upload_boat_image(self, file: UploadFile, user_id: Optional[int] = None) -> str:
        """上传船艇图片"""
        return self.upload_file(file, cos_settings.boat_prefix, user_id)
    
    def upload_service_image(self, file: UploadFile, user_id: Optional[int] = None) -> str:
        """上传服务图片"""
        return self.upload_file(file, cos_settings.service_prefix, user_id)
    
    def upload_product_image(self, file: UploadFile, user_id: Optional[int] = None) -> str:
        """上传产品图片"""
        return self.upload_file(file, cos_settings.product_prefix, user_id)
    
    def upload_review_image(self, file: UploadFile, user_id: int) -> str:
        """上传评价图片"""
        return self.upload_file(file, cos_settings.review_prefix, user_id)


# 创建全局COS客户端实例
cos_client = COSClient() 