from passlib.context import CryptContext

# 创建密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def is_password_strong(password: str) -> tuple[bool, str]:
    """检查密码强度"""
    if len(password) < 8:
        return False, "密码长度至少为8位"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not has_upper:
        return False, "密码必须包含大写字母"
    if not has_lower:
        return False, "密码必须包含小写字母"
    if not has_digit:
        return False, "密码必须包含数字"
    if not has_special:
        return False, "密码必须包含特殊字符"
    
    return True, "密码强度合格" 