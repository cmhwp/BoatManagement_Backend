import random
import string
from datetime import datetime


def generate_order_no() -> str:
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"ORD{timestamp}{random_str}"


def generate_payment_no() -> str:
    """生成支付单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=8))
    return f"PAY{timestamp}{random_str}"


def generate_refund_no() -> str:
    """生成退款单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=8))
    return f"REF{timestamp}{random_str}"


def generate_service_no() -> str:
    """生成服务编号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"SRV{timestamp}{random_str}"


def generate_boat_registration_no() -> str:
    """生成船艇登记号"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"BOAT{timestamp}{random_str}"


def generate_merchant_code() -> str:
    """生成商家编码"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"MCH{timestamp}{random_str}"


def generate_verification_code(length: int = 6) -> str:
    """生成验证码"""
    return ''.join(random.choices(string.digits, k=length))


def generate_invite_code() -> str:
    """生成邀请码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def generate_coupon_code() -> str:
    """生成优惠券码"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"CPN{timestamp}{random_str}"


def generate_certificate_no() -> str:
    """生成证书编号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"CERT{timestamp}{random_str}" 