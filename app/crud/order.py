from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, date, timedelta
from app.crud.base import CRUDBase
from app.models.order import Order, OrderStatus, OrderType, RefundStatus
from app.schemas.order import OrderCreate, OrderUpdate


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    """订单CRUD操作类"""
    
    def get_by_order_number(self, db: Session, *, order_number: str) -> Optional[Order]:
        """根据订单号获取订单"""
        return db.query(Order).filter(Order.order_number == order_number).first()
    
    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        order_type: Optional[OrderType] = None,
        status: Optional[OrderStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Order]:
        """获取用户的订单列表"""
        query = db.query(Order).filter(Order.user_id == user_id)
        
        if order_type:
            query = query.filter(Order.order_type == order_type)
        
        if status:
            query = query.filter(Order.status == status)
        
        return query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    def get_by_service(
        self, 
        db: Session, 
        *, 
        service_id: int, 
        status: Optional[OrderStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Order]:
        """获取指定服务的订单列表"""
        query = db.query(Order).filter(Order.service_id == service_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        return query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    def get_by_merchant(
        self, 
        db: Session, 
        *, 
        merchant_id: int,
        order_type: Optional[OrderType] = None,
        status: Optional[OrderStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Order]:
        """获取商家的订单列表（通过服务关联）"""
        query = db.query(Order).join(Order.service).filter(
            Order.service.has(merchant_id=merchant_id)
        )
        
        if order_type:
            query = query.filter(Order.order_type == order_type)
        
        if status:
            query = query.filter(Order.status == status)
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        return query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    def get_pending_orders(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Order]:
        """获取待处理订单"""
        return db.query(Order).filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.PAID])
        ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    def get_orders_by_status(
        self, 
        db: Session, 
        *, 
        status: OrderStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Order]:
        """根据状态获取订单列表"""
        return db.query(Order).filter(
            Order.status == status
        ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    def get_orders_by_date_range(
        self, 
        db: Session, 
        *, 
        start_date: datetime, 
        end_date: datetime,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Order]:
        """获取指定日期范围的订单"""
        return db.query(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    def get_refund_orders(
        self, 
        db: Session, 
        *, 
        refund_status: Optional[RefundStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Order]:
        """获取退款订单列表"""
        query = db.query(Order).filter(Order.refund_status != RefundStatus.NONE)
        
        if refund_status:
            query = query.filter(Order.refund_status == refund_status)
        
        return query.order_by(desc(Order.refund_requested_at)).offset(skip).limit(limit).all()
    
    def search_orders(
        self,
        db: Session,
        *,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """搜索订单"""
        return self.search(
            db,
            keyword=keyword,
            search_fields=["order_number", "customer_notes", "delivery_contact"],
            skip=skip,
            limit=limit
        )
    
    def get_user_order_count(self, db: Session, *, user_id: int) -> int:
        """获取用户订单总数"""
        return db.query(Order).filter(Order.user_id == user_id).count()
    
    def get_merchant_order_count(self, db: Session, *, merchant_id: int) -> int:
        """获取商家订单总数"""
        return db.query(Order).join(Order.service).filter(
            Order.service.has(merchant_id=merchant_id)
        ).count()
    
    def get_order_summary_by_user(self, db: Session, *, user_id: int) -> dict:
        """获取用户订单统计"""
        orders = db.query(Order).filter(Order.user_id == user_id).all()
        
        total_orders = len(orders)
        pending_orders = len([o for o in orders if o.status == OrderStatus.PENDING])
        completed_orders = len([o for o in orders if o.status == OrderStatus.COMPLETED])
        cancelled_orders = len([o for o in orders if o.status == OrderStatus.CANCELLED])
        total_amount = sum([o.total_amount for o in orders if o.status != OrderStatus.CANCELLED])
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "total_amount": total_amount
        }
    
    def get_order_summary_by_merchant(self, db: Session, *, merchant_id: int) -> dict:
        """获取商家订单统计"""
        orders = db.query(Order).join(Order.service).filter(
            Order.service.has(merchant_id=merchant_id)
        ).all()
        
        total_orders = len(orders)
        pending_orders = len([o for o in orders if o.status in [OrderStatus.PENDING, OrderStatus.PAID]])
        completed_orders = len([o for o in orders if o.status == OrderStatus.COMPLETED])
        cancelled_orders = len([o for o in orders if o.status == OrderStatus.CANCELLED])
        total_revenue = sum([o.total_amount for o in orders if o.status == OrderStatus.COMPLETED])
        refund_amount = sum([o.refund_amount for o in orders])
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "total_revenue": total_revenue,
            "refund_amount": refund_amount
        }
    
    def update_status(self, db: Session, *, order_id: int, status: OrderStatus) -> Optional[Order]:
        """更新订单状态"""
        order = self.get(db, id=order_id)
        if order:
            update_data = {"status": status}
            
            # 设置相应的时间戳
            if status == OrderStatus.CONFIRMED:
                update_data["confirmed_at"] = datetime.now()
            elif status == OrderStatus.COMPLETED:
                update_data["completed_at"] = datetime.now()
            elif status == OrderStatus.CANCELLED:
                update_data["cancelled_at"] = datetime.now()
            
            order = self.update(db, db_obj=order, obj_in=update_data)
        return order
    
    def update_refund_status(
        self, 
        db: Session, 
        *, 
        order_id: int, 
        refund_status: RefundStatus,
        refund_amount: Optional[float] = None
    ) -> Optional[Order]:
        """更新退款状态"""
        order = self.get(db, id=order_id)
        if order:
            update_data = {"refund_status": refund_status}
            
            if refund_status == RefundStatus.REQUESTED:
                update_data["refund_requested_at"] = datetime.now()
            elif refund_status == RefundStatus.COMPLETED:
                update_data["refund_processed_at"] = datetime.now()
                if refund_amount:
                    update_data["refund_amount"] = refund_amount
            
            order = self.update(db, db_obj=order, obj_in=update_data)
        return order
    
    def get_orders_need_confirmation(self, db: Session, *, limit: int = 100) -> List[Order]:
        """获取需要确认的订单（已支付超过一定时间）"""
        # 获取已支付但未确认的订单
        return db.query(Order).filter(
            and_(
                Order.status == OrderStatus.PAID,
                Order.created_at < datetime.now() - timedelta(hours=2)  # 超过2小时
            )
        ).limit(limit).all()
    
    def get_today_orders(self, db: Session, *, merchant_id: Optional[int] = None) -> List[Order]:
        """获取今日订单"""
        today = date.today()
        query = db.query(Order).filter(
            func.date(Order.created_at) == today
        )
        
        if merchant_id:
            query = query.join(Order.service).filter(
                Order.service.has(merchant_id=merchant_id)
            )
        
        return query.order_by(desc(Order.created_at)).all()


# 创建CRUD实例
crud_order = CRUDOrder(Order) 