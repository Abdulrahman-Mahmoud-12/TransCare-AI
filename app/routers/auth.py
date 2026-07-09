from app.dependancies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import UserRegister, UserLogin, Token
from app.services.auth_service import AuthService
from app.config import Config

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")

# --- HTML Template Renderers ---

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html", 
        context={"request": request}
    )
@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="register.html", 
        context={"request": request}
    )
@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role.value
    }

# --- API Processing Operations ---

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )
    
    # 2. NEW: Enforce Admin Passcode Check
    if user_in.role == "admin":
        if not user_in.admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin passcode key is required for registration."
            )
        
        # Enforce lookup against a key. You can make this 'ADMIN-IQ-2026' or load it from config.
        # Example validation check:
        if user_in.admin_id != "ADMIN-RETAILIQ-MASTER-KEY":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: The provided Admin Passcode Key is invalid."
            )

    # 3. Securely hash password and save
    hashed_password = AuthService.hash_password(user_in.password)
    
    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        password_hash=hashed_password,
        role=UserRole(user_in.role),
        # If customer, it sets column to NULL completely
        admin_id=user_in.admin_id if user_in.role == "admin" else None 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"status": "success", "message": "User registered successfully."}

@router.post("/login")
async def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not AuthService.verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="This account has been deactivated."
        )

    # Generate the access token token mapping out identity and permissions
    token_data = {"sub": user.email, "role": user.role.value}
    access_token = AuthService.create_access_token(data=token_data)
    
    response = JSONResponse(content={
        "status": "success", 
        "role": user.role.value
    })
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True
    )
    return response