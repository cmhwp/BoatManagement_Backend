from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
import json
import random
import string
from datetime import datetime, timedelta

from app.crud.payment import crud_payment, crud_refund
from app.crud.order import crud_order
from app.crud.user import crud_user
from app.schemas.payment import (
    PaymentCreate, PaymentUpdate, PaymentResponse, PaymentListResponse,
    RefundCreate, RefundUpdate, RefundResponse, PaymentCallback,
    PaymentStatistics, PaymentSearchFilter, PaymentLinkResponse,
    PaymentStatus, PaymentMethod, RefundStatus
)
from app.models.order import OrderStatus
from app.models.user import UserRole
from app.utils.logger import logger
from app.utils.id_generator import generate_payment_no, generate_refund_no


class PaymentService:
    """支付业务逻辑类"""
    
    @staticmethod
    def create_payment(db: Session, user_id: int, payment_create: PaymentCreate) -> PaymentLinkResponse:
        """创建支付记录并生成支付链接"""
        # 检查用户是否存在
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查订单是否存在且属于该用户
        order = crud_order.get(db, id=payment_create.order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能支付自己的订单"
            )
        
        # 检查订单状态是否为待支付
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单状态不允许支付"
            )
        
        # 检查是否已存在支付记录
        existing_payment = crud_payment.get_by_order_id(db, order_id=payment_create.order_id)
        if existing_payment and existing_payment.status in [PaymentStatus.SUCCESS, PaymentStatus.PROCESSING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单已有支付记录"
            )
        
        # 如果存在失败的支付记录，创建新的支付记录
        payment_no = generate_payment_no()
        
        # 准备支付数据
        payment_data = {
            "payment_no": payment_no,
            "order_id": payment_create.order_id,
            "user_id": user_id,
            "amount": order.total_amount,
            "payment_method": payment_create.payment_method,
            "status": PaymentStatus.PENDING,
            "description": payment_create.description or f"订单{order.order_no}支付"
        }
        
        # 创建支付记录
        payment = crud_payment.create(db, obj_in=payment_data)
        
        # 生成模拟支付链接
        payment_url = PaymentService._generate_payment_link(payment, payment_create.payment_method)
        qr_code_url = PaymentService._generate_qr_code_url(payment_no) if payment_create.payment_method in [PaymentMethod.WECHAT_PAY, PaymentMethod.ALIPAY] else None
        
        logger.info(f"支付记录创建成功: 用户{user_id}对订单{payment_create.order_id}发起支付, 支付单号{payment_no}")
        
        return PaymentLinkResponse(
            payment_id=payment.id,
            payment_no=payment_no,
            payment_url=payment_url,
            qr_code_url=qr_code_url,
            expires_at=datetime.now() + timedelta(minutes=30)  # 30分钟过期
        )
    
    @staticmethod
    def get_user_payments(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> dict:
        """获取用户的支付记录列表"""
        payments = crud_payment.get_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
        
        # 计算总数（简化处理）
        all_payments = crud_payment.get_by_user_id(db, user_id=user_id, skip=0, limit=1000)
        total = len(all_payments)
        
        return {
            "payments": [PaymentListResponse.model_validate(payment).model_dump() for payment in payments],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_payment_detail(db: Session, user_id: int, payment_id: int) -> PaymentResponse:
        """获取支付详情"""
        payment = crud_payment.get(db, id=payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        # 检查权限（用户只能查看自己的支付记录）
        user = crud_user.get(db, id=user_id)
        if payment.user_id != user_id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限查看此支付记录"
            )
        
        # 获取关联的退款记录
        refunds = crud_refund.get_by_payment_id(db, payment_id=payment_id)
        
        response = PaymentResponse.model_validate(payment)
        response.refunds = [RefundResponse.model_validate(refund).model_dump() for refund in refunds]
        
        return response
    
    @staticmethod
    def search_payments(
        db: Session,
        user_id: int,
        filter_params: PaymentSearchFilter,
        skip: int = 0,
        limit: int = 100
    ) -> dict:
        """搜索支付记录"""
        # 非管理员只能查看自己的支付记录
        user = crud_user.get(db, id=user_id)
        search_user_id = user_id if user.role != UserRole.ADMIN else filter_params.user_id
        
        payments = crud_payment.search_payments(
            db,
            user_id=search_user_id,
            order_id=filter_params.order_id,
            payment_method=filter_params.payment_method,
            status=filter_params.status,
            start_date=filter_params.start_date,
            end_date=filter_params.end_date,
            min_amount=float(filter_params.min_amount) if filter_params.min_amount else None,
            max_amount=float(filter_params.max_amount) if filter_params.max_amount else None,
            keyword=filter_params.keyword,
            skip=skip,
            limit=limit
        )
        
        # 简化处理，获取总数
        all_payments = crud_payment.search_payments(
            db,
            user_id=search_user_id,
            order_id=filter_params.order_id,
            payment_method=filter_params.payment_method,
            status=filter_params.status,
            start_date=filter_params.start_date,
            end_date=filter_params.end_date,
            min_amount=float(filter_params.min_amount) if filter_params.min_amount else None,
            max_amount=float(filter_params.max_amount) if filter_params.max_amount else None,
            keyword=filter_params.keyword,
            skip=0,
            limit=1000
        )
        total = len(all_payments)
        
        return {
            "payments": [PaymentListResponse.model_validate(payment).model_dump() for payment in payments],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def cancel_payment(db: Session, user_id: int, payment_id: int) -> dict:
        """取消支付"""
        payment = crud_payment.get(db, id=payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        # 检查权限
        if payment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限取消此支付"
            )
        
        # 检查支付状态
        if payment.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前状态不允许取消支付"
            )
        
        # 更新支付状态
        crud_payment.update_status(db, payment_id=payment_id, status=PaymentStatus.CANCELLED)
        
        logger.info(f"支付取消: 用户{user_id}取消支付{payment_id}")
        
        return {"message": "支付已取消"}
    
    @staticmethod
    def handle_payment_callback(db: Session, callback_data: PaymentCallback) -> dict:
        """处理支付回调（模拟）"""
        payment = crud_payment.get_by_payment_no(db, payment_no=callback_data.payment_no)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        # 模拟支付成功处理
        if callback_data.status == PaymentStatus.SUCCESS:
            # 更新支付状态
            update_data = {
                "status": PaymentStatus.SUCCESS,
                "payment_time": datetime.now(),
                "third_party_transaction_id": callback_data.third_party_transaction_id
            }
            
            if callback_data.amount:
                # 验证支付金额
                if abs(float(payment.amount) - float(callback_data.amount)) > 0.01:
                    logger.error(f"支付金额不匹配: 订单金额{payment.amount}, 实际支付{callback_data.amount}")
                    update_data["status"] = PaymentStatus.FAILED
                    crud_payment.update(db, db_obj=payment, obj_in=update_data)
                    return {"message": "支付金额不匹配", "success": False}
            
            crud_payment.update(db, db_obj=payment, obj_in=update_data)
            
            # 更新订单状态
            order = crud_order.get(db, id=payment.order_id)
            if order:
                crud_order.update(db, db_obj=order, obj_in={"status": OrderStatus.PAID})
            
            logger.info(f"支付成功: 支付单号{callback_data.payment_no}")
            return {"message": "支付成功", "success": True}
        
        elif callback_data.status == PaymentStatus.FAILED:
            crud_payment.update_status(db, payment_id=payment.id, status=PaymentStatus.FAILED)
            logger.info(f"支付失败: 支付单号{callback_data.payment_no}")
            return {"message": "支付失败", "success": False}
        
        return {"message": "回调处理完成", "success": True}
    
    @staticmethod
    def simulate_payment_success(db: Session, payment_no: str) -> dict:
        """模拟支付成功（仅用于测试）"""
        payment = crud_payment.get_by_payment_no(db, payment_no=payment_no)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        if payment.status != PaymentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="支付状态不允许模拟成功"
            )
        
        # 模拟回调数据
        callback_data = PaymentCallback(
            payment_no=payment_no,
            status=PaymentStatus.SUCCESS,
            third_party_transaction_id=PaymentService._generate_transaction_id(),
            amount=payment.amount
        )
        
        return PaymentService.handle_payment_callback(db, callback_data)
    
    @staticmethod
    def create_refund(db: Session, user_id: int, refund_create: RefundCreate) -> RefundResponse:
        """创建退款申请"""
        # 检查支付记录是否存在
        payment = crud_payment.get(db, id=refund_create.payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        # 检查权限
        if payment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限申请退款"
            )
        
        # 检查支付状态
        if payment.status != PaymentStatus.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能对成功支付的记录申请退款"
            )
        
        # 检查退款金额
        already_refunded = crud_refund.get_payment_refund_amount(db, payment_id=refund_create.payment_id)
        if already_refunded + float(refund_create.refund_amount) > float(payment.amount):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="退款金额超过可退金额"
            )
        
        # 创建退款记录
        refund_data = {
            "refund_no": generate_refund_no(),
            "payment_id": refund_create.payment_id,
            "refund_amount": refund_create.refund_amount,
            "reason": refund_create.reason,
            "status": RefundStatus.PENDING
        }
        
        refund = crud_refund.create(db, obj_in=refund_data)
        
        logger.info(f"退款申请创建成功: 用户{user_id}申请退款{refund_create.refund_amount}元")
        
        return RefundResponse.model_validate(refund)
    
    @staticmethod
    def process_refund(db: Session, user_id: int, refund_id: int, refund_update: RefundUpdate) -> RefundResponse:
        """处理退款申请（管理员操作）"""
        # 检查管理员权限
        user = crud_user.get(db, id=user_id)
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        
        refund = crud_refund.get(db, id=refund_id)
        if not refund:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="退款记录不存在"
            )
        
        if refund.status != RefundStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="退款状态不允许处理"
            )
        
        # 更新退款状态
        update_data = refund_update.model_dump(exclude_unset=True)
        if refund_update.status == RefundStatus.SUCCESS:
            update_data["refund_time"] = datetime.now()
        
        updated_refund = crud_refund.update(db, db_obj=refund, obj_in=update_data)
        
        # 如果退款成功，更新支付状态
        if refund_update.status == RefundStatus.SUCCESS:
            payment = crud_payment.get(db, id=refund.payment_id)
            already_refunded = crud_refund.get_payment_refund_amount(db, payment_id=refund.payment_id)
            
            if already_refunded >= float(payment.amount):
                crud_payment.update_status(db, payment_id=payment.id, status=PaymentStatus.REFUNDED)
            else:
                crud_payment.update_status(db, payment_id=payment.id, status=PaymentStatus.PARTIAL_REFUNDED)
        
        logger.info(f"退款处理: 管理员{user_id}处理退款{refund_id}, 状态{refund_update.status}")
        
        return RefundResponse.model_validate(updated_refund)
    
    @staticmethod
    def get_payment_statistics(
        db: Session, 
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PaymentStatistics:
        """获取支付统计信息"""
        # 非管理员只能查看自己的统计
        user = crud_user.get(db, id=user_id)
        stats_user_id = user_id if user.role != UserRole.ADMIN else None
        
        # 获取基础统计
        stats = crud_payment.get_payment_statistics(
            db, 
            user_id=stats_user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # 获取退款统计
        if stats_user_id:
            user_payments = crud_payment.get_by_user_id(db, user_id=stats_user_id, skip=0, limit=1000)
            payment_ids = [p.id for p in user_payments]
        else:
            payment_ids = [p.id for p in crud_payment.get_multi(db, skip=0, limit=1000)]
        
        refund_amount = 0
        refund_count = 0
        for payment_id in payment_ids:
            refunds = crud_refund.get_by_payment_id(db, payment_id=payment_id)
            success_refunds = [r for r in refunds if r.status == RefundStatus.SUCCESS]
            refund_amount += sum(float(r.refund_amount) for r in success_refunds)
            refund_count += len(success_refunds)
        
        # 获取每日统计
        daily_amounts = crud_payment.get_daily_payment_amounts(
            db, 
            days=30,
            user_id=stats_user_id
        )
        
        return PaymentStatistics(
            total_amount=Decimal(str(stats["total_amount"])),
            total_count=stats["total_count"],
            success_amount=Decimal(str(stats["success_amount"])),
            success_count=stats["success_count"],
            success_rate=stats["success_rate"],
            refund_amount=Decimal(str(refund_amount)),
            refund_count=refund_count,
            method_distribution=stats["method_distribution"],
            daily_amounts=daily_amounts
        )
    
    @staticmethod
    def _generate_payment_link(payment, payment_method: PaymentMethod) -> str:
        """生成模拟支付链接"""
        base_url = "https://mock-payment.example.com"
        
        if payment_method == PaymentMethod.WECHAT_PAY:
            return f"{base_url}/wechat/pay?payment_no={payment.payment_no}&amount={payment.amount}"
        elif payment_method == PaymentMethod.ALIPAY:
            return f"{base_url}/alipay/pay?payment_no={payment.payment_no}&amount={payment.amount}"
        elif payment_method == PaymentMethod.BANK_CARD:
            return f"{base_url}/bank/pay?payment_no={payment.payment_no}&amount={payment.amount}"
        else:
            return f"{base_url}/pay?payment_no={payment.payment_no}&amount={payment.amount}"
    
    @staticmethod
    def _generate_qr_code_url(payment_no: str) -> str:
        """生成模拟二维码URL"""
        return f"https://mock-qrcode.example.com/qr/{payment_no}.png"
    
    @staticmethod
    def _generate_transaction_id() -> str:
        """生成模拟第三方交易号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"TXN{timestamp}{random_str}" 