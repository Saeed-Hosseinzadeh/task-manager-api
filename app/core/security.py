from passlib.context import CryptContext

# Use pbkdf2_sha256 instead of bcrypt to avoid the 72-byte bcrypt limitation
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its stored hash.
    """
    return pwd_context.verify(password, hashed)
