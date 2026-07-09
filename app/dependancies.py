from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from jose import jwt
from app.database import get_db
from app.models.user import User, UserRole
from app.config import Config

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Extracts the authentication token directly from browser cookies 
    to support seamless backend HTML route rendering.
    """
    # Grab the access token cookie we set during login
    token_cookie = request.cookies.get("access_token")
    
    if not token_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Missing session cookie."
        )
        
    try:
        # If your cookie string is formatted as "Bearer <JWT>", split out the "Bearer " prefix
        if token_cookie.startswith("Bearer "):
            token = token_cookie.split(" ")[1]
        else:
            token = token_cookie
            
        # Decode using the verified configuration naming attributes
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims.")
            
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials."
        )
        
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures that the authenticated user is currently active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="This account has been deactivated."
        )
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Ensures that the authenticated active user is a Manager/Admin.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This workspace is reserved for administrators."
        )
    return current_user

def require_role(allowed_roles: list[str]):
    """
    A dependency factory that ensures the logged-in user possesses 
    the necessary role privileges (e.g., ['admin', 'manager']) to access an endpoint.
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        # If using an ORM model later, this becomes: current_user.role
        user_role = current_user.get("role")
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource."
            )
        return current_user
    return role_checker