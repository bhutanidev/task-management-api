from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from app.core.db import get_db
from app.schemas import auth as schemas
from app.services import auth as service
from app.utils import jwt as jwt_utils
from app.models.user import User

from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme for access token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# HTTPBearer for refresh token
security = HTTPBearer()

limiter = Limiter(key_func=get_remote_address)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from access token
    """
    # Verify access token
    payload = jwt_utils.verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database
    user = await service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: schemas.UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    existing_user = await service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    new_user = await service.create_user(db, user_data)
    return new_user


@router.post("/login", response_model=schemas.TokenResponse)
@limiter.limit("5/minute") 
async def login(
    request: Request,
    credentials: schemas.UserLogin,  # Simple JSON body
    db: AsyncSession = Depends(get_db)
):
    """
    Login user with email and password
    Returns access_token and refresh_token
    """
    user = await service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create tokens
    access_token = jwt_utils.create_access_token(data={"sub": str(user.id)})
    refresh_token = jwt_utils.create_refresh_token(data={"sub": str(user.id)})
    
    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    refresh_token = credentials.credentials
    
    payload = jwt_utils.verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")
    user = await service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    new_access_token = jwt_utils.create_access_token(data={"sub": str(user.id)})
    new_refresh_token = jwt_utils.create_refresh_token(data={"sub": str(user.id)})
    
    return schemas.TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )