from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.config.database import get_db
from app.utils.deps import get_current_active_user, require_admin, require_crew
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.crew import (
    CrewCreate, CrewUpdate, CrewResponse, 
    CrewListResponse, CrewStatusUpdate
)
from app.schemas.common import PaginatedResponse, PaginationParams, ApiResponse, MessageResponse
from app.crud.crew import (
    create_crew, get_crew_by_id, get_crew_by_user_id,
    get_crew_by_id_card_no, get_crew_by_license_no, get_crews,
    get_available_crews, update_crew, update_crew_status,
    update_crew_rating, delete_crew
)

router = APIRouter(prefix="/api/v1/crews", tags=["crews"])


@router.post("/", response_model=ApiResponse[CrewResponse])
async def create_crew_info(
    crew: CrewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建船员信息"""
    # 检查用户角色
    if current_user.role not in [UserRole.ADMIN, UserRole.CREW]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员或船员用户可以创建船员信息"
        )
    
    # 普通船员只能创建自己的信息
    if current_user.role == UserRole.CREW and crew.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="船员只能创建自己的信息"
        )
    
    # 检查用户是否已有船员信息
    existing_crew = get_crew_by_user_id(db, crew.user_id)
    if existing_crew:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已有船员信息"
        )
    
    # 检查身份证号是否已存在
    existing_id_card = get_crew_by_id_card_no(db, crew.id_card_no)
    if existing_id_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="身份证号已存在"
        )
    
    # 检查证书号是否已存在（如果提供）
    if crew.license_no:
        existing_license = get_crew_by_license_no(db, crew.license_no)
        if existing_license:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="证书号已存在"
            )
    
    db_crew = create_crew(db, crew)
    return ApiResponse.success_response(data=db_crew, message="船员信息创建成功")


@router.get("/", response_model=PaginatedResponse[CrewListResponse])
async def list_crews(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    is_available: Optional[bool] = Query(None, description="是否可用"),
    license_type: Optional[str] = Query(None, description="证书类型"),
    min_experience: Optional[int] = Query(None, description="最少从业年限"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取船员列表（管理员）"""
    pagination = PaginationParams(page=page, page_size=page_size)
    crews, total = get_crews(
        db, pagination, is_available=is_available,
        license_type=license_type, min_experience=min_experience,
        search=search
    )
    
    return PaginatedResponse.create(
        items=crews, total=total, page=page, page_size=page_size
    )


@router.get("/available", response_model=PaginatedResponse[CrewListResponse])
async def list_available_crews(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    license_type: Optional[str] = Query(None, description="证书类型"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取可用船员列表"""
    # 商家和管理员可以查看可用船员
    if current_user.role not in [UserRole.ADMIN, UserRole.MERCHANT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    pagination = PaginationParams(page=page, page_size=page_size)
    crews, total = get_available_crews(
        db, pagination, license_type=license_type
    )
    
    return PaginatedResponse.create(
        items=crews, total=total, page=page, page_size=page_size
    )


@router.get("/me", response_model=ApiResponse[CrewResponse])
async def get_my_crew_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的船员信息"""
    crew = get_crew_by_user_id(db, current_user.id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到船员信息"
        )
    
    return ApiResponse.success_response(data=crew)


@router.get("/{crew_id}", response_model=ApiResponse[CrewResponse])
async def get_crew_detail(
    crew_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取船员详情"""
    crew = get_crew_by_id(db, crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船员不存在"
        )
    
    # 权限检查：管理员和商家可查看所有，船员只能查看自己的
    if (current_user.role not in [UserRole.ADMIN, UserRole.MERCHANT] and 
        crew.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return ApiResponse.success_response(data=crew)


@router.put("/me", response_model=ApiResponse[CrewResponse])
async def update_my_crew_info(
    crew_update: CrewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新当前用户的船员信息"""
    crew = get_crew_by_user_id(db, current_user.id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到船员信息"
        )
    
    # 如果更新证书号，检查是否已存在
    if crew_update.license_no:
        existing_license = get_crew_by_license_no(db, crew_update.license_no)
        if existing_license and existing_license.id != crew.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="证书号已存在"
            )
    
    updated_crew = update_crew(db, crew.id, crew_update)
    return ApiResponse.success_response(data=updated_crew, message="船员信息更新成功")


@router.put("/{crew_id}", response_model=ApiResponse[CrewResponse])
async def update_crew_info(
    crew_id: int,
    crew_update: CrewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新船员信息（管理员）"""
    crew = get_crew_by_id(db, crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船员不存在"
        )
    
    # 如果更新证书号，检查是否已存在
    if crew_update.license_no:
        existing_license = get_crew_by_license_no(db, crew_update.license_no)
        if existing_license and existing_license.id != crew.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="证书号已存在"
            )
    
    updated_crew = update_crew(db, crew_id, crew_update)
    return ApiResponse.success_response(data=updated_crew, message="船员信息更新成功")


@router.put("/{crew_id}/status", response_model=ApiResponse[CrewResponse])
async def update_crew_status_info(
    crew_id: int,
    status_update: CrewStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新船员状态"""
    crew = get_crew_by_id(db, crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船员不存在"
        )
    
    # 权限检查：管理员、商家或船员本人可以更新状态
    if (current_user.role not in [UserRole.ADMIN, UserRole.MERCHANT] and 
        crew.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    updated_crew = update_crew_status(
        db, crew_id, status_update.is_available, status_update.current_status
    )
    return ApiResponse.success_response(data=updated_crew, message="船员状态更新成功")


@router.put("/{crew_id}/rating", response_model=ApiResponse[CrewResponse])
async def update_crew_rating_info(
    crew_id: int,
    rating: float = Query(..., ge=0, le=5, description="评分(0-5)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新船员评分"""
    # 只有管理员和商家可以评分
    if current_user.role not in [UserRole.ADMIN, UserRole.MERCHANT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    crew = get_crew_by_id(db, crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船员不存在"
        )
    
    updated_crew = update_crew_rating(db, crew_id, rating)
    return ApiResponse.success_response(data=updated_crew, message="船员评分更新成功")


@router.delete("/{crew_id}", response_model=ApiResponse[MessageResponse])
async def delete_crew_info(
    crew_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除船员（管理员）"""
    success = delete_crew(db, crew_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船员不存在"
        )
    
    return ApiResponse.success_response(
        data=MessageResponse(message="船员删除成功"),
        message="船员删除成功"
    ) 