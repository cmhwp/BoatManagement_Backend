import random
import string
import time
from datetime import datetime
from typing import Optional


def generate_order_number(prefix: str = "ORD") -> str:
    """生成订单号"""
    timestamp = str(int(time.time()))
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_part}"


def generate_tracking_number(prefix: str = "TRK") -> str:
    """生成物流单号"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{timestamp}{random_part}"


def generate_payment_number(prefix: str = "PAY") -> str:
    """生成支付流水号"""
    timestamp = str(int(time.time() * 1000))  # 毫秒时间戳
    random_part = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{timestamp}{random_part}"


def generate_verification_code(length: int = 6) -> str:
    """生成验证码"""
    return ''.join(random.choices(string.digits, k=length))


def generate_coupon_code(length: int = 8) -> str:
    """生成优惠券代码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_boat_number(prefix: str = "BOAT") -> str:
    """生成船艇编号"""
    timestamp = datetime.now().strftime("%Y%m")
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_part}"


def generate_certificate_number(cert_type: str = "CERT") -> str:
    """生成证书编号"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{cert_type}{timestamp}{random_part}"


def generate_sku(category: str, length: int = 6) -> str:
    """生成产品SKU"""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{category.upper()}{random_part}"


def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_invite_code(length: int = 8) -> str:
    """生成邀请码"""
    # 排除容易混淆的字符
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    return ''.join(random.choices(chars, k=length)) 