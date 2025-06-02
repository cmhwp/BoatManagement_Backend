from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
import json
from datetime import datetime, timedelta
import uuid

from app.crud.order import crud_order
from app.crud.service import crud_service
from app.crud.merchant import crud_merchant
from app.crud.user import crud_user
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    OrderStatusUpdate, RefundRequest, RefundProcess, OrderSearchFilter,
    OrderSummary, ParticipantDetail
)
from app.models.order import OrderStatus, OrderType, RefundStatus
from app.models.service import ServiceStatus
from app.models.user import UserRole
from app.utils.logger import logger
from app.utils.id_generator import generate_order_number


class OrderService:
    """订单业务逻辑类"""
    
    @staticmethod
    def create_order(db: Session, user_id: int, order_create: OrderCreate) -> OrderResponse:
        """创建订单"""
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证订单内容
        if order_create.order_type == OrderType.SERVICE:
            if not order_create.service_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="服务订单必须指定服务ID"
                )
            
            # 检查服务是否存在且可预订
            service = crud_service.get(db, id=order_create.service_id)
            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="指定的服务不存在"
                )
            
            if service.status != ServiceStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="服务当前不可预订"
                )
            
            # 验证参与人数
            if order_create.participant_count:
                if service.max_participants and order_create.participant_count > service.max_participants:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"参与人数超过服务限制（最大{service.max_participants}人）"
                    )
                
                if order_create.participant_count < service.min_participants:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"参与人数不足（最少{service.min_participants}人）"
                    )
            
            # 计算订单金额
            subtotal = service.price * (order_create.participant_count or 1)
            
        elif order_create.order_type == OrderType.PRODUCT:
            # TODO: 实现产品订单逻辑
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="产品订单功能暂未实现"
            )
        
        elif order_create.order_type == OrderType.BUNDLE:
            # TODO: 实现套餐订单逻辑
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="套餐订单功能暂未实现"
            )
        
        # TODO: 应用优惠券折扣
        discount_amount = Decimal('0.00')
        coupon_discount = Decimal('0.00')
        
        # 计算税费和服务费
        tax_amount = Decimal('0.00')  # 暂时不收税
        service_fee = subtotal * Decimal('0.05')  # 5%服务费
        
        total_amount = subtotal - discount_amount - coupon_discount + tax_amount + service_fee
        
        # 生成订单号
        order_number = generate_order_number()
        
        # 准备订单数据
        order_data = {
            "order_number": order_number,
            "user_id": user_id,
            "order_type": order_create.order_type,
            "service_id": order_create.service_id,
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "coupon_discount": coupon_discount,
            "tax_amount": tax_amount,
            "service_fee": service_fee,
            "total_amount": total_amount,
            "participant_count": order_create.participant_count,
            "booking_date": order_create.booking_date,
            "booking_time": order_create.booking_time,
            "delivery_address": order_create.delivery_address,
            "delivery_phone": order_create.delivery_phone,
            "delivery_contact": order_create.delivery_contact,
            "delivery_notes": order_create.delivery_notes,
            "customer_notes": order_create.customer_notes,
            "coupon_code": order_create.coupon_code,
            "status": OrderStatus.PENDING
        }
        
        # 处理参与者详情JSON字段
        if order_create.participant_details:
            order_data["participant_details"] = json.dumps(
                [detail.model_dump() for detail in order_create.participant_details], 
                ensure_ascii=False
            )
        
        # 处理产品ID列表
        if order_create.product_ids:
            order_data["product_ids"] = json.dumps(order_create.product_ids, ensure_ascii=False)
        
        order = crud_order.create(db, obj_in=order_data)
        
        logger.info(f"订单创建成功: {order_number}, 用户ID: {user_id}, 金额: {total_amount}")
        
        return OrderResponse.model_validate(order)
    
    @staticmethod
    def get_user_orders(
        db: Session, 
        user_id: int, 
        order_type: Optional[OrderType] = None,
        status: Optional[OrderStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> dict:
        """获取用户订单列表"""
        orders = crud_order.get_by_user(
            db, 
            user_id=user_id, 
            order_type=order_type,
            status=status,
            skip=skip, 
            limit=limit
        )
        
        total = crud_order.get_user_order_count(db, user_id=user_id)
        
        return {
            "orders": [OrderResponse.model_validate(order).model_dump() for order in orders],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_merchant_orders(
        db: Session, 
        user_id: int,
        order_type: Optional[OrderType] = None,
        status: Optional[OrderStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> dict:
        """获取商家订单列表"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看订单"
            )
        
        orders = crud_order.get_by_merchant(
            db, 
            merchant_id=merchant.id,
            order_type=order_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            skip=skip, 
            limit=limit
        )
        
        total = crud_order.get_merchant_order_count(db, merchant_id=merchant.id)
        
        return {
            "orders": [OrderResponse.model_validate(order).model_dump() for order in orders],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_order_detail(db: Session, user_id: int, order_id: int) -> OrderResponse:
        """获取订单详情"""
        order = crud_order.get(db, id=order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 检查权限：用户只能查看自己的订单，商家可以查看自己服务的订单
        user = crud_user.get(db, id=user_id)
        if order.user_id != user_id:
            # 检查是否是该订单对应服务的商家
            if order.service:
                merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
                if not merchant or order.service.merchant_id != merchant.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权限查看此订单"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权限查看此订单"
                )
        
        return OrderResponse.model_validate(order)
    
    @staticmethod
    def update_order(db: Session, user_id: int, order_id: int, order_update: OrderUpdate) -> OrderResponse:
        """更新订单信息"""
        order = crud_order.get(db, id=order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 只有订单创建者可以更新订单信息（且仅在特定状态下）
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此订单"
            )
        
        # 只有待支付状态的订单可以修改
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有待支付订单可以修改"
            )
        
        # 处理JSON字段
        update_data = order_update.model_dump(exclude_unset=True)
        if order_update.participant_details is not None:
            update_data["participant_details"] = json.dumps(
                [detail.model_dump() for detail in order_update.participant_details], 
                ensure_ascii=False
            )
        
        updated_order = crud_order.update(db, db_obj=order, obj_in=update_data)
        
        logger.info(f"订单信息更新: {order.order_number}")
        
        return OrderResponse.model_validate(updated_order)
    
    @staticmethod
    def cancel_order(db: Session, user_id: int, order_id: int, reason: Optional[str] = None) -> dict:
        """取消订单"""
        order = crud_order.get(db, id=order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 检查权限
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限取消此订单"
            )
        
        # 检查订单状态
        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单当前状态不允许取消"
            )
        
        # 更新订单状态
        updated_order = crud_order.update_status(db, order_id=order_id, status=OrderStatus.CANCELLED)
        
        # 如果已支付，需要申请退款
        if order.status in [OrderStatus.PAID, OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS]:
            crud_order.update_refund_status(
                db, 
                order_id=order_id, 
                refund_status=RefundStatus.REQUESTED,
                refund_amount=float(order.total_amount)
            )
        
        logger.info(f"订单取消: {order.order_number}, 原因: {reason}")
        
        return {"message": f"订单 {order.order_number} 取消成功"}
    
    @staticmethod
    def confirm_order(db: Session, user_id: int, order_id: int) -> dict:
        """确认订单（商家操作）"""
        order = crud_order.get(db, id=order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能确认订单"
            )
        
        # 检查是否是该订单对应服务的商家
        if not order.service or order.service.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限确认此订单"
            )
        
        # 检查订单状态
        if order.status != OrderStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有已支付订单可以确认"
            )
        
        updated_order = crud_order.update_status(db, order_id=order_id, status=OrderStatus.CONFIRMED)
        
        logger.info(f"订单确认: {order.order_number}, 商家: {merchant.business_name}")
        
        return {"message": f"订单 {order.order_number} 确认成功"}
    
    @staticmethod
    def complete_order(db: Session, user_id: int, order_id: int) -> dict:
        """完成订单（商家操作）"""
        order = crud_order.get(db, id=order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能完成订单"
            )
        
        # 检查是否是该订单对应服务的商家
        if not order.service or order.service.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限完成此订单"
            )
        
        # 检查订单状态
        if order.status not in [OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有已确认或进行中的订单可以完成"
            )
        
        updated_order = crud_order.update_status(db, order_id=order_id, status=OrderStatus.COMPLETED)
        
        # 更新服务预订次数
        if order.service:
            crud_service.increment_booking_count(db, service_id=order.service.id)
        
        logger.info(f"订单完成: {order.order_number}, 商家: {merchant.business_name}")
        
        return {"message": f"订单 {order.order_number} 完成成功"}
    
    @staticmethod
    def request_refund(db: Session, user_id: int, order_id: int, refund_request: RefundRequest) -> dict:
        """申请退款"""
        order = crud_order.get(db, id=order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 检查权限
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限申请退款"
            )
        
        # 检查订单状态
        if order.status not in [OrderStatus.PAID, OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单当前状态不支持退款"
            )
        
        # 检查是否已经申请过退款
        if order.refund_status != RefundStatus.NONE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单已申请过退款"
            )
        
        # 计算退款金额
        refund_amount = refund_request.amount or order.total_amount
        if refund_amount > order.total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="退款金额不能超过订单总额"
            )
        
        # 更新订单退款信息
        update_data = {
            "refund_reason": refund_request.reason,
            "refund_amount": refund_amount,
            "customer_notes": refund_request.notes
        }
        crud_order.update(db, db_obj=order, obj_in=update_data)
        
        # 更新退款状态
        crud_order.update_refund_status(
            db, 
            order_id=order_id, 
            refund_status=RefundStatus.REQUESTED
        )
        
        logger.info(f"退款申请: {order.order_number}, 金额: {refund_amount}")
        
        return {"message": f"订单 {order.order_number} 退款申请提交成功"}
    
    @staticmethod
    def get_order_summary(db: Session, user_id: int) -> OrderSummary:
        """获取用户订单统计"""
        summary = crud_order.get_order_summary_by_user(db, user_id=user_id)
        
        return OrderSummary(
            total_orders=summary["total_orders"],
            pending_orders=summary["pending_orders"],
            completed_orders=summary["completed_orders"],
            cancelled_orders=summary["cancelled_orders"],
            total_revenue=summary["total_amount"],
            refund_amount=Decimal('0.00')  # 用户视角不显示退款金额
        )
    
    @staticmethod
    def get_merchant_order_summary(db: Session, user_id: int) -> OrderSummary:
        """获取商家订单统计"""
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看订单统计"
            )
        
        summary = crud_order.get_order_summary_by_merchant(db, merchant_id=merchant.id)
        
        return OrderSummary(
            total_orders=summary["total_orders"],
            pending_orders=summary["pending_orders"],
            completed_orders=summary["completed_orders"],
            cancelled_orders=summary["cancelled_orders"],
            total_revenue=summary["total_revenue"],
            refund_amount=summary["refund_amount"]
        ) 