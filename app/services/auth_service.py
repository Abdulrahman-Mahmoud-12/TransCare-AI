import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from app.config import Config  # Or wherever your SECRET_KEY / ALGORITHM are stored

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        return hashed_bytes.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        """
        Generates a secure JWT access token for authentication sessions.
        """
        to_encode = data.copy()
        
        # Use fallback values if they aren't explicitly inside your Config class
        secret_key = getattr(Config, "SECRET_KEY", "YOUR_SUPER_SECRET_KEY_DONT_SHARE")
        algorithm = getattr(Config, "ALGORITHM", "HS256")
        expire_minutes = getattr(Config, "ACCESS_TOKEN_EXPIRE_MINUTES", 30)
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt