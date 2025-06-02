from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"          # 管理员
    MERCHANT = "merchant"    # 商家
    USER = "user"           # 普通用户
    CREW = "crew"           # 船员


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"       # 激活
    INACTIVE = "inactive"   # 未激活
    SUSPENDED = "suspended" # 暂停
    DELETED = "deleted"     # 已删除


class ApplicationStatus(str, Enum):
    """申请状态枚举"""
    PENDING = "pending"     # 待审核
    APPROVED = "approved"   # 已通过
    REJECTED = "rejected"   # 已拒绝
    CANCELLED = "cancelled" # 已取消


class BoatStatus(str, Enum):
    """船艇状态枚举"""
    AVAILABLE = "available"     # 可用
    IN_USE = "in_use"          # 使用中
    MAINTENANCE = "maintenance" # 维护中
    OUT_OF_SERVICE = "out_of_service"  # 停用


class BoatType(str, Enum):
    """船艇类型枚举"""
    TOURIST = "tourist"         # 观光船
    FISHING = "fishing"         # 渔船
    CARGO = "cargo"            # 货船
    SPEEDBOAT = "speedboat"    # 快艇


class ServiceStatus(str, Enum):
    """服务状态枚举"""
    ACTIVE = "active"       # 活跃
    INACTIVE = "inactive"   # 停用
    SEASONAL = "seasonal"   # 季节性


class ServiceType(str, Enum):
    """服务类型枚举"""
    BOAT_TOUR = "boat_tour"         # 船艇观光
    AGRICULTURE = "agriculture"     # 农业体验
    CULTURAL = "cultural"          # 文化体验
    FISHING = "fishing"            # 渔业体验
    DINING = "dining"              # 餐饮服务


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"         # 待付款
    PAID = "paid"              # 已付款
    CONFIRMED = "confirmed"     # 已确认
    IN_PROGRESS = "in_progress" # 进行中
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消
    REFUNDED = "refunded"      # 已退款


class OrderType(str, Enum):
    """订单类型枚举"""
    SERVICE = "service"         # 服务订单
    PRODUCT = "product"         # 产品订单


class PaymentStatus(str, Enum):
    """支付状态枚举"""
    PENDING = "pending"         # 待支付
    SUCCESS = "success"         # 成功
    FAILED = "failed"          # 失败
    REFUNDED = "refunded"      # 已退款


class PaymentMethod(str, Enum):
    """支付方式枚举"""
    WECHAT = "wechat"          # 微信支付
    ALIPAY = "alipay"          # 支付宝
    BANK_CARD = "bank_card"    # 银行卡
    CASH = "cash"              # 现金


class CertificateType(str, Enum):
    """证书类型枚举"""
    BOAT_LICENSE = "boat_license"       # 船艇执照
    CREW_LICENSE = "crew_license"       # 船员证书
    BUSINESS_LICENSE = "business_license" # 营业执照
    SAFETY_CERTIFICATE = "safety_certificate" # 安全证书


class NotificationType(str, Enum):
    """通知类型枚举"""
    SYSTEM = "system"           # 系统通知
    ORDER = "order"            # 订单通知
    PAYMENT = "payment"        # 支付通知
    PROMOTION = "promotion"    # 营销通知


class CouponType(str, Enum):
    """优惠券类型枚举"""
    DISCOUNT = "discount"       # 折扣券
    CASH = "cash"              # 代金券
    FREE_SHIPPING = "free_shipping" # 免邮券


class InventoryAction(str, Enum):
    """库存操作枚举"""
    IN = "in"                  # 入库
    OUT = "out"               # 出库
    ADJUST = "adjust"         # 调整 