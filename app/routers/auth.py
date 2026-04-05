from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user, require_admin
from app.schemas.auth import *
from app.services import auth as auth_service
from app.schemas.enums import UserRole

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    return auth_service.register_user(db, data)

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    return auth_service.login_user(db, data.email, data.password)

# OAuth2 form endpoint so Swagger's "Authorize" button works
@router.post("/login/form", response_model=Token)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_service.login_user(db, form.username, form.password)

@router.post("/refresh", response_model=Token)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(db, data.refresh_token)

@router.post("/logout", status_code=204)
def logout(data: RefreshRequest, db: Session = Depends(get_db)):
    auth_service.logout_user(db, data.refresh_token)

@router.post("/logout-all", status_code=204)
def logout_all(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    auth_service.logout_all(db, current_user.id)

@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return current_user

@router.patch("/me/password", status_code=204)
def change_password(data: PasswordChange, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    auth_service.change_password(db, current_user, data)

# Admin-only user management
@router.get("/users", response_model=list[UserResponse])
def list_users(role: UserRole = None, skip: int = 0, limit: int = 50,
               _=Depends(require_admin), db: Session = Depends(get_db)):
    return auth_service.list_users(db, role, skip, limit)

@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate,
                _=Depends(require_admin), db: Session = Depends(get_db)):
    return auth_service.update_user(db, user_id, data)

@router.post("/users/{user_id}/reset-password", status_code=204)
def reset_password(user_id: int, new_password: str,
                   _=Depends(require_admin), db: Session = Depends(get_db)):
    auth_service.admin_reset_password(db, user_id, new_password)