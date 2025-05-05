from werkzeug.security import generate_password_hash, check_password_hash


def generate_password(password: str) -> str:
    return generate_password_hash(password, method="pbkdf2")


def check_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)
