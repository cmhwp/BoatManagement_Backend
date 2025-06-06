from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session, joinedload
from decimal import Decimal
import uuid

from app.models.order import Order
from app.models.user import User
from app.models.merchant import Merchant
from app.models.service import Service
from app.models.crew_info import CrewInfo
from app.models.boat import Boat
from app.models.enums import OrderStatus, OrderType
from app.schemas.order import OrderCreate, OrderUpdate, OrderAssignCrew, OrderStatusUpdate


def generate_order_no() -> str:
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4()).replace("-", "")[:6].upper()
    return f"ORD{timestamp}{random_suffix}"


def create_order(db: Session, order_data: OrderCreate, user_id: int, merchant_id: int) -> Order:
    """创建订单"""
    # 获取服务信息以计算价格
    service = None
    unit_price = Decimal('0.00')
    
    if order_data.service_id:
        service = db.query(Service).filter(Service.id == order_data.service_id).first()
        if service:
            unit_price = service.base_price
    
    # 计算金额
    subtotal = unit_price * order_data.quantity
    discount_amount = Decimal('0.00')  # 后续可以添加优惠券逻辑
    total_price = subtotal - discount_amount
    
    # 创建订单对象
    db_order = Order(
        order_no=generate_order_no(),
        user_id=user_id,
        merchant_id=merchant_id,
        order_type=order_data.order_type,
        service_id=order_data.service_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        unit_price=unit_price,
        subtotal=subtotal,
        discount_amount=discount_amount,
        total_price=total_price,
        scheduled_at=order_data.scheduled_at,
        participants=order_data.participants,
        contact_name=order_data.contact_name,
        contact_phone=order_data.contact_phone,
        special_requirements=order_data.special_requirements,
        notes=order_data.notes,
        coupon_id=order_data.coupon_id,
        status=OrderStatus.PENDING
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    """根据ID获取订单详情"""
    return db.query(Order).options(
        joinedload(Order.user),
        joinedload(Order.merchant),
        joinedload(Order.service),
        joinedload(Order.crew),
        joinedload(Order.boat)
    ).filter(Order.id == order_id).first()


def get_orders_by_user(
    db: Session, 
    user_id: int, 
    status: Optional[OrderStatus] = None,
    skip: int = 0, 
    limit: int = 20
) -> List[Order]:
    """获取用户的订单列表"""
    query = db.query(Order).filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.options(
        joinedload(Order.service),
        joinedload(Order.merchant),
        joinedload(Order.crew)
    ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()


def get_orders_by_merchant(
    db: Session, 
    merchant_id: int, 
    status: Optional[OrderStatus] = None,
    skip: int = 0, 
    limit: int = 20
) -> List[Order]:
    """获取商家的订单列表"""
    query = db.query(Order).filter(Order.merchant_id == merchant_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.options(
        joinedload(Order.user),
        joinedload(Order.service),
        joinedload(Order.crew),
        joinedload(Order.boat)
    ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()


def get_orders_by_crew(
    db: Session, 
    crew_id: int, 
    status: Optional[OrderStatus] = None,
    skip: int = 0, 
    limit: int = 20
) -> List[Order]:
    """获取船员的订单列表"""
    query = db.query(Order).filter(Order.crew_id == crew_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.options(
        joinedload(Order.user),
        joinedload(Order.service),
        joinedload(Order.merchant),
        joinedload(Order.boat)
    ).order_by(desc(Order.scheduled_at)).offset(skip).limit(limit).all()


def assign_crew_to_order(db: Session, order_id: int, assign_data: OrderAssignCrew) -> Optional[Order]:
    """为订单指派船员（核心派单功能）"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    
    # 检查船员是否可用
    crew = db.query(CrewInfo).filter(
        CrewInfo.id == assign_data.crew_id,
        CrewInfo.is_available == True
    ).first()
    if not crew:
        return None
    
    # 检查船员在该时间段是否有冲突
    conflict_order = db.query(Order).filter(
        Order.crew_id == assign_data.crew_id,
        Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS]),
        Order.scheduled_at == order.scheduled_at
    ).first()
    if conflict_order:
        return None
    
    # 更新订单
    order.crew_id = assign_data.crew_id
    order.boat_id = assign_data.boat_id
    order.status = OrderStatus.CONFIRMED
    order.assigned_at = datetime.now()
    if assign_data.notes:
        order.notes = f"{order.notes or ''}\n派单备注: {assign_data.notes}".strip()
    
    db.commit()
    db.refresh(order)
    return order


def update_order_status(db: Session, order_id: int, status_data: OrderStatusUpdate) -> Optional[Order]:
    """更新订单状态"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    
    old_status = order.status
    order.status = status_data.status
    
    # 根据状态更新相应的时间字段
    now = datetime.now()
    if status_data.status == OrderStatus.CONFIRMED and old_status != OrderStatus.CONFIRMED:
        order.confirmed_at = now
    elif status_data.status == OrderStatus.IN_PROGRESS and old_status != OrderStatus.IN_PROGRESS:
        order.started_at = now
    elif status_data.status == OrderStatus.COMPLETED and old_status != OrderStatus.COMPLETED:
        order.completed_at = now
    elif status_data.status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
        order.cancelled_at = now
    
    if status_data.notes:
        order.notes = f"{order.notes or ''}\n状态变更备注: {status_data.notes}".strip()
    
    db.commit()
    db.refresh(order)
    return order


def update_order(db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    """更新订单信息"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    return order


def cancel_order(db: Session, order_id: int, reason: str = None) -> Optional[Order]:
    """取消订单"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    
    # 只有特定状态的订单可以取消
    if order.status not in [OrderStatus.PENDING, OrderStatus.PAID, OrderStatus.PENDING_ASSIGNMENT, OrderStatus.CONFIRMED]:
        return None
    
    order.status = OrderStatus.CANCELLED
    order.cancelled_at = datetime.now()
    
    if reason:
        order.notes = f"{order.notes or ''}\n取消原因: {reason}".strip()
    
    db.commit()
    db.refresh(order)
    return order


def get_merchant_order_stats(db: Session, merchant_id: int) -> Dict[str, Any]:
    """获取商家订单统计"""
    today = date.today()
    
    # 基础统计查询
    stats_query = db.query(
        func.count(Order.id).label('total_orders'),
        func.sum(Order.total_price).label('total_revenue')
    ).filter(Order.merchant_id == merchant_id)
    
    result = stats_query.first()
    total_orders = result.total_orders or 0
    total_revenue = result.total_revenue or Decimal('0.00')
    
    # 按状态统计
    status_stats = db.query(
        Order.status,
        func.count(Order.id).label('count')
    ).filter(Order.merchant_id == merchant_id).group_by(Order.status).all()
    
    status_counts = {status.value: 0 for status in OrderStatus}
    for stat in status_stats:
        status_counts[stat.status.value] = stat.count
    
    # 今日统计
    today_stats = db.query(
        func.count(Order.id).label('today_orders'),
        func.sum(Order.total_price).label('today_revenue')
    ).filter(
        Order.merchant_id == merchant_id,
        func.date(Order.created_at) == today
    ).first()
    
    return {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': status_counts.get('pending', 0),
        'paid_orders': status_counts.get('paid', 0),
        'pending_assignment_orders': status_counts.get('pending_assignment', 0),
        'confirmed_orders': status_counts.get('confirmed', 0),
        'in_progress_orders': status_counts.get('in_progress', 0),
        'completed_orders': status_counts.get('completed', 0),
        'cancelled_orders': status_counts.get('cancelled', 0),
        'today_orders': today_stats.today_orders or 0,
        'today_revenue': today_stats.today_revenue or Decimal('0.00')
    }


def get_available_crews_for_order(db: Session, order_id: int) -> List[CrewInfo]:
    """获取订单可用的船员列表"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return []
    
    # 查找可用且在指定时间没有冲突的船员
    available_crews = db.query(CrewInfo).filter(
        CrewInfo.is_available == True
    ).all()
    
    # 过滤掉在同一时间段有其他订单的船员
    filtered_crews = []
    for crew in available_crews:
        conflict_order = db.query(Order).filter(
            Order.crew_id == crew.id,
            Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS]),
            Order.scheduled_at == order.scheduled_at
        ).first()
        
        if not conflict_order:
            filtered_crews.append(crew)
    
    return filtered_crews 