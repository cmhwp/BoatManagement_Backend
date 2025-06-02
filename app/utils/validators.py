import re
from typing import Optional


def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_id_card(id_card: str) -> bool:
    """验证身份证号格式"""
    if len(id_card) != 18:
        return False
    
    # 前17位必须是数字
    if not id_card[:17].isdigit():
        return False
    
    # 最后一位是数字或X
    if not (id_card[17].isdigit() or id_card[17].upper() == 'X'):
        return False
    
    # 校验位验证
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_digits = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    sum_value = sum(int(id_card[i]) * weights[i] for i in range(17))
    check_index = sum_value % 11
    
    return id_card[17].upper() == check_digits[check_index]


def validate_password_strength(password: str) -> tuple[bool, str]:
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码长度至少为8位"
    
    if len(password) > 20:
        return False, "密码长度不能超过20位"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    strength_count = sum([has_upper, has_lower, has_digit, has_special])
    
    if strength_count < 3:
        return False, "密码必须包含大写字母、小写字母、数字、特殊字符中的至少3种"
    
    return True, "密码强度合格"


def validate_business_license(license_num: str) -> bool:
    """验证营业执照号格式（统一社会信用代码）"""
    if len(license_num) != 18:
        return False
    
    # 第一位必须是数字或大写字母
    if not (license_num[0].isdigit() or license_num[0].isupper()):
        return False
    
    # 后17位必须是数字或大写字母
    for char in license_num[1:]:
        if not (char.isdigit() or char.isupper()):
            return False
    
    return True


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """验证GPS坐标格式"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def validate_price(price: float) -> bool:
    """验证价格格式"""
    return price >= 0 and round(price, 2) == price


def validate_quantity(quantity: int) -> bool:
    """验证数量格式"""
    return quantity >= 0 