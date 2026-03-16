from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.database.supabase_client import supabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify JWT against Supabase
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise credentials_exception
            
        return user_response.user
    except Exception as e:
        raise credentials_exception
