from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import secrets

from ...core.database import get_db
from ...core.security import hash_password, verify_password, create_access_token
from . import models, schemas

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# ==================== SCHOOL ENDPOINTS ====================

@router.post("/schools", response_model=schemas.School)
async def create_school(school: schemas.SchoolCreate, db: Session = Depends(get_db)):
    """Create a new school/tenant account"""
    
    # Check if school already exists
    db_school = db.query(models.School).filter(models.School.name == school.name).first()
    if db_school:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="School name already exists"
        )
    
    # Generate tenant_id from school name
    tenant_id = school.name.lower().replace(" ", "_").replace("-", "_")
    
    # Ensure tenant_id is unique
    existing_tenant = db.query(models.School).filter(models.School.tenant_id == tenant_id).first()
    if existing_tenant:
        tenant_id = f"{tenant_id}_{secrets.token_hex(4)}"
    
    # Create school
    new_school = models.School(
        name=school.name,
        tenant_id=tenant_id,
        admin_email=school.admin_email,
        admin_name=school.admin_name
    )
    
    db.add(new_school)
    db.commit()
    db.refresh(new_school)
    
    return new_school

@router.get("/schools/{tenant_id}", response_model=schemas.School)
async def get_school(tenant_id: str, db: Session = Depends(get_db)):
    """Get school details by tenant_id"""
    school = db.query(models.School).filter(models.School.tenant_id == tenant_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    return school

@router.get("/schools", response_model=List[schemas.School])
async def list_schools(db: Session = Depends(get_db)):
    """List all schools"""
    return db.query(models.School).filter(models.School.is_active == True).all()

# ==================== USER REGISTRATION & LOGIN ====================

@router.post("/register", response_model=schemas.Token)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user/school admin
    
    Flow:
    1. User provides username, password, school_name
    2. System creates a School entry if it doesn't exist
    3. System creates User entry with tenant_id
    4. System returns JWT token for immediate login
    """
    
    # Check if username already exists
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Generate or use existing school's tenant_id
    if user_data.school_name:
        school = db.query(models.School).filter(models.School.name == user_data.school_name).first()
        if school:
            tenant_id = school.tenant_id
        else:
            # Create new school automatically
            tenant_id = user_data.school_name.lower().replace(" ", "_").replace("-", "_")
            existing_tenant = db.query(models.School).filter(models.School.tenant_id == tenant_id).first()
            if existing_tenant:
                tenant_id = f"{tenant_id}_{secrets.token_hex(4)}"
            
            new_school = models.School(
                name=user_data.school_name,
                tenant_id=tenant_id,
                admin_email=user_data.email or f"admin@{user_data.school_name.lower().replace(' ', '')}",
                admin_name=user_data.username
            )
            db.add(new_school)
    else:
        tenant_id = f"user_{secrets.token_hex(6)}"
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        mobile=user_data.mobile,
        school_name=user_data.school_name,
        tenant_id=tenant_id,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=1440)  # 24 hours
    access_token = create_access_token(
        data={"sub": str(new_user.id), "tenant_id": tenant_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user,
        "tenant_id": tenant_id
    }

def _authenticate_user(credentials: schemas.UserLogin, db: Session):
    # Find user by username
    user = db.query(models.User).filter(models.User.username == credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


def _build_token_response(user: models.User):
    # Create access token
    access_token_expires = timedelta(minutes=1440)  # 24 hours
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": user.tenant_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "tenant_id": user.tenant_id
    }


@router.post("/login", response_model=schemas.Token)
async def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    User login

    Returns:
    - JWT token
    - User info
    - Tenant ID (for header in future requests)
    """
    user = _authenticate_user(credentials, db)
    return _build_token_response(user)


@router.post("/school-login", response_model=schemas.Token)
@router.post("/schools/login", response_model=schemas.Token)
async def school_login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """School portal login. Admin accounts must use the admin login page."""
    user = _authenticate_user(credentials, db)
    if user.tenant_id == "default" or user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please use /admin/login for admin access."
        )
    return _build_token_response(user)

@router.post("/impersonate/{user_id}", response_model=schemas.Token)
async def impersonate_user(
    user_id: int,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Allow the main admin tenant to open a school account directly."""
    if x_tenant_id != "default":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the default admin tenant can login as a school"
        )

    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    access_token_expires = timedelta(minutes=1440)
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": user.tenant_id},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "tenant_id": user.tenant_id
    }

# ==================== USER MANAGEMENT ====================

@router.get("/users", response_model=List[schemas.User])
async def get_users(
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get users for a tenant. The default admin tenant can manage all school accounts."""
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Tenant-ID header is required"
        )

    if x_tenant_id == "default":
        return db.query(models.User).filter(
            models.User.is_active == True,
            models.User.tenant_id != "default"
        ).all()

    return db.query(models.User).filter(models.User.tenant_id == x_tenant_id).all()

@router.get("/users/me", response_model=schemas.User)
async def get_current_user(
    x_user_id: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get current user info"""
    if not x_user_id or not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Headers X-User-ID and X-Tenant-ID are required"
        )
    
    user = db.query(models.User).filter(
        models.User.id == int(x_user_id),
        models.User.tenant_id == x_tenant_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Update a user. The default admin tenant can update any school account."""
    tenant_id = (x_tenant_id or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Tenant-ID header is required"
        )

    query = db.query(models.User).filter(models.User.id == user_id)
    if tenant_id != "default":
        query = query.filter(models.User.tenant_id == tenant_id)

    user = query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_data.username and user_data.username != user.username:
        existing_user = db.query(models.User).filter(
            models.User.username == user_data.username,
            models.User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        user.username = user_data.username

    if user_data.email is not None:
        user.email = user_data.email
    if user_data.mobile is not None:
        user.mobile = user_data.mobile
    if user_data.school_name is not None:
        user.school_name = user_data.school_name
        school = db.query(models.School).filter(models.School.tenant_id == user.tenant_id).first()
        if school:
            school.name = user_data.school_name
            school.admin_email = user.email or school.admin_email
            school.admin_name = user.username
    if user_data.password:
        user.password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Delete a user by marking it inactive so it disappears from admin lists."""
    tenant_id = (x_tenant_id or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Tenant-ID header is required"
        )
    
    query = db.query(models.User).filter(models.User.id == user_id)
    if tenant_id != "default":
        query = query.filter(models.User.tenant_id == tenant_id)

    user = query.first()
    
    if not user:
        if tenant_id == "default":
            return {"message": "User already deleted"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        return {"message": "User already deleted"}

    user.is_active = False

    if tenant_id == "default":
        school = db.query(models.School).filter(models.School.tenant_id == user.tenant_id).first()
        if school:
            school.is_active = False

    db.commit()
    db.refresh(user)

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete did not persist. Please try again."
        )

    return {"message": "User deleted successfully"}
