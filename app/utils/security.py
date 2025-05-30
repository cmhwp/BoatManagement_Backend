from passlib.context import CryptContext
from typing import Union

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def generate_unique_code(length: int = 8) -> str:
    """生成唯一验证码"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length)) 