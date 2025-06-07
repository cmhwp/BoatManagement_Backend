from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from decimal import Decimal

from app.models.service import Service
from app.models.merchant import Merchant
from app.models.order import Order
from app.models.review import Review
from app.models.enums import ServiceStatus, ServiceType, OrderStatus
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse, ServiceListResponse


def get_service_by_id(db: Session, service_id: int) -> Optional[Service]:
    """根据ID获取服务"""
    return db.query(Service).filter(Service.id == service_id).first()


def get_service_detail(db: Session, service_id: int) -> Optional[ServiceResponse]:
    """获取服务详细信息"""
    # 查询服务及其关联的商家信息
    query = db.query(
        Service,
        Merchant.company_name.label('merchant_name'),
        func.count(Order.id).label('total_orders'),
        func.avg(Review.overall_rating).label('average_rating')
    ).outerjoin(
        Merchant, Service.merchant_id == Merchant.id
    ).outerjoin(
        Order, Service.id == Order.service_id
    ).outerjoin(
        Review, Order.id == Review.order_id
    ).filter(
        Service.id == service_id
    ).group_by(Service.id, Merchant.company_name).first()
    
    if not query:
        return None
    
    service, merchant_name, total_orders, average_rating = query
    
    return ServiceResponse(
        id=service.id,
        name=service.name,
        service_type=service.service_type,
        description=service.description,
        base_price=service.base_price,
        duration=service.duration,
        max_participants=service.max_participants,
        min_participants=service.min_participants,
        location=service.location,
        requirements=service.requirements,
        included_items=service.included_items,
        excluded_items=service.excluded_items,
        safety_instructions=service.safety_instructions,
        cancellation_policy=service.cancellation_policy,
        images=service.images,
        merchant_id=service.merchant_id,
        status=service.status,
        created_at=service.created_at,
        updated_at=service.updated_at,
        merchant_name=merchant_name,
        total_orders=total_orders or 0,
        average_rating=average_rating
    )


def get_services(
    db: Session,
    service_type: Optional[ServiceType] = None,
    merchant_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None
) -> List[ServiceListResponse]:
    """获取服务列表"""
    query = db.query(
        Service,
        Merchant.company_name.label('merchant_name'),
        func.count(Order.id).label('total_orders'),
        func.avg(Review.overall_rating).label('average_rating')
    ).outerjoin(
        Merchant, Service.merchant_id == Merchant.id
    ).outerjoin(
        Order, Service.id == Order.service_id
    ).outerjoin(
        Review, Order.id == Review.order_id
    )
    
    # 应用筛选条件
    filters = [Service.status == ServiceStatus.ACTIVE]
    
    if service_type:
        filters.append(Service.service_type == service_type)
    
    if merchant_id:
        filters.append(Service.merchant_id == merchant_id)
    
    if min_price:
        filters.append(Service.base_price >= Decimal(str(min_price)))
    
    if max_price:
        filters.append(Service.base_price <= Decimal(str(max_price)))
    
    if location:
        filters.append(Service.location.ilike(f"%{location}%"))
    
    if search:
        search_filter = or_(
            Service.name.ilike(f"%{search}%"),
            Service.description.ilike(f"%{search}%"),
            Service.location.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    query = query.filter(and_(*filters))
    query = query.group_by(Service.id, Merchant.company_name)
    query = query.offset(skip).limit(limit)
    
    results = query.all()
    
    services = []
    for service, merchant_name, total_orders, average_rating in results:
        services.append(ServiceListResponse(
            id=service.id,
            name=service.name,
            service_type=service.service_type,
            base_price=service.base_price,
            duration=service.duration,
            max_participants=service.max_participants,
            location=service.location,
            merchant_id=service.merchant_id,
            merchant_name=merchant_name,
            status=service.status,
            total_orders=total_orders or 0,
            average_rating=average_rating,
            images=service.images
        ))
    
    return services


def get_available_services(
    db: Session,
    service_type: Optional[ServiceType] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[ServiceListResponse]:
    """获取可用服务列表"""
    return get_services(
        db=db,
        service_type=service_type,
        location=location,
        skip=skip,
        limit=limit
    )


def get_services_by_merchant(
    db: Session,
    merchant_id: int,
    status: Optional[ServiceStatus] = None,
    skip: int = 0,
    limit: int = 20
) -> List[ServiceListResponse]:
    """获取商家的服务列表"""
    query = db.query(
        Service,
        Merchant.company_name.label('merchant_name'),
        func.count(Order.id).label('total_orders'),
        func.avg(Review.overall_rating).label('average_rating')
    ).outerjoin(
        Merchant, Service.merchant_id == Merchant.id
    ).outerjoin(
        Order, Service.id == Order.service_id
    ).outerjoin(
        Review, Order.id == Review.order_id
    ).filter(
        Service.merchant_id == merchant_id
    )
    
    if status:
        query = query.filter(Service.status == status)
    
    query = query.group_by(Service.id, Merchant.company_name)
    query = query.offset(skip).limit(limit)
    
    results = query.all()
    
    services = []
    for service, merchant_name, total_orders, average_rating in results:
        services.append(ServiceListResponse(
            id=service.id,
            name=service.name,
            service_type=service.service_type,
            base_price=service.base_price,
            duration=service.duration,
            max_participants=service.max_participants,
            location=service.location,
            merchant_id=service.merchant_id,
            merchant_name=merchant_name,
            status=service.status,
            total_orders=total_orders or 0,
            average_rating=average_rating,
            images=service.images
        ))
    
    return services


def create_service(db: Session, service_data: ServiceCreate, merchant_id: int) -> ServiceResponse:
    """创建服务"""
    db_service = Service(
        name=service_data.name,
        service_type=service_data.service_type,
        description=service_data.description,
        base_price=service_data.base_price,
        duration=service_data.duration,
        max_participants=service_data.max_participants,
        min_participants=service_data.min_participants,
        location=service_data.location,
        requirements=service_data.requirements,
        included_items=service_data.included_items,
        excluded_items=service_data.excluded_items,
        safety_instructions=service_data.safety_instructions,
        cancellation_policy=service_data.cancellation_policy,
        images=service_data.images,
        merchant_id=merchant_id,
        status=ServiceStatus.ACTIVE
    )
    
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    
    return get_service_detail(db, db_service.id)


def update_service(db: Session, service_id: int, service_data: ServiceUpdate) -> Optional[ServiceResponse]:
    """更新服务信息"""
    db_service = get_service_by_id(db, service_id)
    if not db_service:
        return None
    
    update_data = service_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_service, field, value)
    
    db.commit()
    db.refresh(db_service)
    
    return get_service_detail(db, service_id)


def delete_service(db: Session, service_id: int) -> bool:
    """删除服务"""
    db_service = get_service_by_id(db, service_id)
    if not db_service:
        return False
    
    db.delete(db_service)
    db.commit()
    return True


def has_active_orders(db: Session, service_id: int) -> bool:
    """检查服务是否有进行中的订单"""
    active_statuses = [
        OrderStatus.PENDING,
        OrderStatus.PAID,
        OrderStatus.PENDING_ASSIGNMENT,
        OrderStatus.CONFIRMED,
        OrderStatus.IN_PROGRESS
    ]
    
    count = db.query(Order).filter(
        Order.service_id == service_id,
        Order.status.in_(active_statuses)
    ).count()
    
    return count > 0


def get_active_services(db: Session, skip: int = 0, limit: int = 20) -> List[Service]:
    """获取活跃的服务列表"""
    return db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE
    ).offset(skip).limit(limit).all() 