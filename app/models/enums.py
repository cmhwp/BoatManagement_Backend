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


class BoatStatus(str, Enum):
    """船艇状态枚举"""
    AVAILABLE = "available"     # 可用
    IN_USE = "in_use"          # 使用中
    MAINTENANCE = "maintenance" # 维护中
    OUT_OF_SERVICE = "out_of_service"  # 停用 