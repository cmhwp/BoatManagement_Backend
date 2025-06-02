from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta

from app.crud.base import CRUDBase
from app.models.payment import Payment, Refund
from app.schemas.payment import PaymentCreate, PaymentUpdate, RefundCreate, RefundUpdate, PaymentStatus, RefundStatus


class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    """支付CRUD操作类"""
    
    def get_by_payment_no(self, db: Session, *, payment_no: str) -> Optional[Payment]:
        """根据支付单号查询支付记录"""
        return db.query(Payment).filter(Payment.payment_no == payment_no).first()
    
    def get_by_order_id(self, db: Session, *, order_id: int) -> Optional[Payment]:
        """根据订单ID查询支付记录"""
        return db.query(Payment).filter(Payment.order_id == order_id).first()
    
    def get_by_user_id(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Payment]:
        """获取用户的支付记录列表"""
        return (
            db.query(Payment)
            .filter(Payment.user_id == user_id)
            .order_by(desc(Payment.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_status(
        self, 
        db: Session, 
        *, 
        status: PaymentStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Payment]:
        """根据状态查询支付记录"""
        return (
            db.query(Payment)
            .filter(Payment.status == status)
            .order_by(desc(Payment.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_payments(
        self,
        db: Session,
        *,
        user_id: Optional[int] = None,
        order_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        status: Optional[PaymentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """搜索支付记录"""
        query = db.query(Payment)
        
        # 用户筛选
        if user_id:
            query = query.filter(Payment.user_id == user_id)
        
        # 订单筛选
        if order_id:
            query = query.filter(Payment.order_id == order_id)
        
        # 支付方式筛选
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        
        # 状态筛选
        if status:
            query = query.filter(Payment.status == status)
        
        # 时间范围筛选
        if start_date:
            query = query.filter(Payment.created_at >= start_date)
        if end_date:
            query = query.filter(Payment.created_at <= end_date)
        
        # 金额范围筛选
        if min_amount:
            query = query.filter(Payment.amount >= min_amount)
        if max_amount:
            query = query.filter(Payment.amount <= max_amount)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    Payment.payment_no.contains(keyword),
                    Payment.description.contains(keyword),
                    Payment.transaction_id.contains(keyword)
                )
            )
        
        return (
            query
            .order_by(desc(Payment.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_pending_payments(self, db: Session, expired_minutes: int = 30) -> List[Payment]:
        """获取超时未支付的记录"""
        expired_time = datetime.now() - timedelta(minutes=expired_minutes)
        return (
            db.query(Payment)
            .filter(
                and_(
                    Payment.status == PaymentStatus.PENDING,
                    Payment.created_at <= expired_time
                )
            )
            .all()
        )
    
    def get_payment_statistics(
        self, 
        db: Session, 
        *, 
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取支付统计信息"""
        query = db.query(Payment)
        
        if user_id:
            query = query.filter(Payment.user_id == user_id)
        
        if start_date:
            query = query.filter(Payment.created_at >= start_date)
        if end_date:
            query = query.filter(Payment.created_at <= end_date)
        
        payments = query.all()
        
        if not payments:
            return {
                "total_amount": 0,
                "total_count": 0,
                "success_amount": 0,
                "success_count": 0,
                "success_rate": 0.0,
                "method_distribution": {}
            }
        
        total_amount = sum(p.amount for p in payments)
        total_count = len(payments)
        
        success_payments = [p for p in payments if p.status == PaymentStatus.SUCCESS]
        success_amount = sum(p.amount for p in success_payments)
        success_count = len(success_payments)
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        
        # 支付方式分布
        method_distribution = {}
        for payment in payments:
            method = payment.payment_method
            method_distribution[method] = method_distribution.get(method, 0) + 1
        
        return {
            "total_amount": total_amount,
            "total_count": total_count,
            "success_amount": success_amount,
            "success_count": success_count,
            "success_rate": round(success_rate, 2),
            "method_distribution": method_distribution
        }
    
    def get_daily_payment_amounts(
        self, 
        db: Session, 
        *, 
        days: int = 30,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取每日支付金额统计"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(
            func.date(Payment.created_at).label('date'),
            func.sum(Payment.amount).label('amount'),
            func.count(Payment.id).label('count')
        ).filter(
            and_(
                func.date(Payment.created_at) >= start_date,
                func.date(Payment.created_at) <= end_date,
                Payment.status == PaymentStatus.SUCCESS
            )
        )
        
        if user_id:
            query = query.filter(Payment.user_id == user_id)
        
        results = query.group_by(func.date(Payment.created_at)).all()
        
        # 创建完整的日期序列
        daily_amounts = []
        current_date = start_date
        result_dict = {r.date: {"amount": float(r.amount), "count": r.count} for r in results}
        
        while current_date <= end_date:
            data = result_dict.get(current_date, {"amount": 0.0, "count": 0})
            daily_amounts.append({
                "date": current_date.isoformat(),
                "amount": data["amount"],
                "count": data["count"]
            })
            current_date += timedelta(days=1)
        
        return daily_amounts
    
    def update_status(self, db: Session, *, payment_id: int, status: PaymentStatus) -> Optional[Payment]:
        """更新支付状态"""
        payment = self.get(db, id=payment_id)
        if payment:
            update_data = {"status": status}
            if status == PaymentStatus.SUCCESS:
                update_data["payment_time"] = datetime.now()
            
            return self.update(db, db_obj=payment, obj_in=update_data)
        return None


class CRUDRefund(CRUDBase[Refund, RefundCreate, RefundUpdate]):
    """退款CRUD操作类"""
    
    def get_by_refund_no(self, db: Session, *, refund_no: str) -> Optional[Refund]:
        """根据退款单号查询退款记录"""
        return db.query(Refund).filter(Refund.refund_no == refund_no).first()
    
    def get_by_payment_id(
        self, 
        db: Session, 
        *, 
        payment_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Refund]:
        """根据支付ID查询退款记录"""
        return (
            db.query(Refund)
            .filter(Refund.payment_id == payment_id)
            .order_by(desc(Refund.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_status(
        self, 
        db: Session, 
        *, 
        status: RefundStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Refund]:
        """根据状态查询退款记录"""
        return (
            db.query(Refund)
            .filter(Refund.status == status)
            .order_by(desc(Refund.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_payment_refund_amount(self, db: Session, *, payment_id: int) -> float:
        """获取支付记录的已退款总额"""
        result = (
            db.query(func.sum(Refund.refund_amount))
            .filter(
                and_(
                    Refund.payment_id == payment_id,
                    Refund.status == RefundStatus.SUCCESS
                )
            )
            .scalar()
        )
        return float(result) if result else 0.0
    
    def update_status(self, db: Session, *, refund_id: int, status: RefundStatus) -> Optional[Refund]:
        """更新退款状态"""
        refund = self.get(db, id=refund_id)
        if refund:
            update_data = {"status": status}
            if status == RefundStatus.SUCCESS:
                update_data["refund_time"] = datetime.now()
            
            return self.update(db, db_obj=refund, obj_in=update_data)
        return None


# 创建CRUD实例
crud_payment = CRUDPayment(Payment)
crud_refund = CRUDRefund(Refund) 