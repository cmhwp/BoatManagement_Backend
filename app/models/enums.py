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
    APPROVED = "approved"   # 已批准
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
    PASSENGER = "passenger"     # 客船
    CARGO = "cargo"            # 货船
    FISHING = "fishing"        # 渔船
    SIGHTSEEING = "sightseeing" # 观光船
    SPEEDBOAT = "speedboat"    # 快艇


class ServiceType(str, Enum):
    """服务类型枚举"""
    BOAT_TOUR = "boat_tour"         # 船舶观光
    AGRICULTURE = "agriculture"     # 农业体验
    CULTURE = "culture"            # 文化体验
    FISHING = "fishing"            # 钓鱼体验
    DINING = "dining"              # 餐饮服务


class ServiceStatus(str, Enum):
    """服务状态枚举"""
    ACTIVE = "active"       # 激活
    INACTIVE = "inactive"   # 停用
    SEASONAL = "seasonal"   # 季节性


class ProductCategory(str, Enum):
    """农产品类别枚举"""
    VEGETABLES = "vegetables"   # 蔬菜
    FRUITS = "fruits"          # 水果
    GRAINS = "grains"          # 谷物
    SEAFOOD = "seafood"        # 海鲜
    DAIRY = "dairy"            # 乳制品
    PROCESSED = "processed"     # 加工品


class ProductStatus(str, Enum):
    """农产品状态枚举"""
    AVAILABLE = "available"     # 可售
    OUT_OF_STOCK = "out_of_stock" # 缺货
    SEASONAL = "seasonal"       # 季节性
    DISCONTINUED = "discontinued" # 停产


class OrderType(str, Enum):
    """订单类型枚举"""
    SERVICE = "service"         # 服务订单
    PRODUCT = "product"         # 产品订单
    COMBO = "combo"            # 组合订单


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"         # 待支付
    PAID = "paid"              # 已支付
    CONFIRMED = "confirmed"     # 已确认
    IN_PROGRESS = "in_progress" # 进行中
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消
    REFUNDED = "refunded"      # 已退款


class PaymentStatus(str, Enum):
    """支付状态枚举"""
    PENDING = "pending"         # 待支付
    SUCCESS = "success"         # 支付成功
    FAILED = "failed"          # 支付失败
    CANCELLED = "cancelled"     # 已取消
    REFUNDED = "refunded"      # 已退款


class PaymentMethod(str, Enum):
    """支付方式枚举"""
    WECHAT = "wechat"          # 微信支付
    ALIPAY = "alipay"          # 支付宝
    BANK_CARD = "bank_card"    # 银行卡
    CASH = "cash"              # 现金


class CertificateType(str, Enum):
    """证书类型枚举"""
    BUSINESS_LICENSE = "business_license"   # 营业执照
    BOAT_LICENSE = "boat_license"          # 船舶执照
    CREW_LICENSE = "crew_license"          # 船员证书
    FOOD_LICENSE = "food_license"          # 食品经营许可证
    SAFETY_CERTIFICATE = "safety_certificate" # 安全证书


class CertificateStatus(str, Enum):
    """证书状态枚举"""
    VALID = "valid"            # 有效
    EXPIRED = "expired"        # 已过期
    PENDING = "pending"        # 待审核
    REJECTED = "rejected"      # 已拒绝


class NotificationType(str, Enum):
    """通知类型枚举"""
    SYSTEM = "system"          # 系统通知
    ORDER = "order"            # 订单通知
    PAYMENT = "payment"        # 支付通知
    SCHEDULE = "schedule"      # 排班通知
    PROMOTION = "promotion"    # 促销通知


class NotificationStatus(str, Enum):
    """通知状态枚举"""
    UNREAD = "unread"          # 未读
    READ = "read"              # 已读
    ARCHIVED = "archived"      # 已归档


class CouponType(str, Enum):
    """优惠券类型枚举"""
    DISCOUNT = "discount"      # 折扣券
    CASH = "cash"             # 现金券
    FREE_SHIPPING = "free_shipping" # 免运费券


class CouponStatus(str, Enum):
    """优惠券状态枚举"""
    ACTIVE = "active"          # 激活
    INACTIVE = "inactive"      # 未激活
    EXPIRED = "expired"        # 已过期
    USED = "used"             # 已使用 