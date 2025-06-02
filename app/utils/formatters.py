from datetime import datetime
from decimal import Decimal
from typing import Optional, Union
import re


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """格式化日期时间"""
    if not dt:
        return None
    return dt.strftime(format_str)


def format_date(dt: Optional[datetime], format_str: str = "%Y-%m-%d") -> Optional[str]:
    """格式化日期"""
    if not dt:
        return None
    return dt.strftime(format_str)


def format_price(price: Union[float, Decimal, int], currency: str = "¥") -> str:
    """格式化价格"""
    if price is None:
        return f"{currency}0.00"
    return f"{currency}{float(price):.2f}"


def format_phone(phone: Optional[str]) -> Optional[str]:
    """格式化手机号（隐藏中间4位）"""
    if not phone:
        return None
    if len(phone) == 11:
        return f"{phone[:3]}****{phone[-4:]}"
    return phone


def format_id_card(id_card: Optional[str]) -> Optional[str]:
    """格式化身份证号（隐藏中间部分）"""
    if not id_card:
        return None
    if len(id_card) == 18:
        return f"{id_card[:6]}********{id_card[-4:]}"
    return id_card


def format_email(email: Optional[str]) -> Optional[str]:
    """格式化邮箱（隐藏用户名部分）"""
    if not email:
        return None
    parts = email.split('@')
    if len(parts) == 2:
        username = parts[0]
        if len(username) > 3:
            return f"{username[:2]}***@{parts[1]}"
        else:
            return f"{username[0]}***@{parts[1]}"
    return email


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f}{size_names[i]}"


def format_duration(seconds: int) -> str:
    """格式化时长"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}分钟"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{hours}小时"


def format_distance(meters: float) -> str:
    """格式化距离"""
    if meters < 1000:
        return f"{int(meters)}米"
    else:
        km = meters / 1000
        return f"{km:.1f}公里"


def format_percentage(value: float, total: float) -> str:
    """格式化百分比"""
    if total == 0:
        return "0%"
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"


def camel_to_snake(name: str) -> str:
    """驼峰命名转下划线命名"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(name: str) -> str:
    """下划线命名转驼峰命名"""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def format_address(address: str, max_length: int = 20) -> str:
    """格式化地址（截断过长地址）"""
    if not address:
        return ""
    if len(address) <= max_length:
        return address
    return f"{address[:max_length-3]}..." 