from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user_schema import UserCreate, Token
from app.database.supabase_client import supabase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    try:
        res = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })

        if res.user is None:
            raise HTTPException(status_code=400, detail="Registration failed")

        return {"id": res.user.id, "email": res.user.email}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })

        if not res.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {
            "access_token": res.session.access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))