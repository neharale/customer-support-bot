from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.services.auth_service import authenticate_admin, create_access_token

router = APIRouter()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    is_valid = authenticate_admin(
        username=form_data.username,
        password=form_data.password
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    access_token = create_access_token(
        data={
            "sub": form_data.username,
            "role": "admin"
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }