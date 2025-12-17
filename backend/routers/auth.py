from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import httpx
import os
import secrets
from security import create_access_token
from dependencies import GITEA_API_URL

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Gitea Config
GITEA_ADMIN_USER = os.getenv("GITEA_ADMIN_USER", "matthew")
GITEA_ADMIN_PASS = os.getenv("GITEA_ADMIN_PASS", "password") # Ensure this is set in k8s secret

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates against Gitea, generates a Gitea API Token, then issues a GitForge JWT.
    """
    username = form_data.username
    password = form_data.password

    async with httpx.AsyncClient() as client:
        # 1. Verify Credentials (Basic Auth)
        auth = (username, password)
        resp = await client.get(f"{GITEA_API_URL}/user", auth=auth)
        
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Gitea credentials")
        
        # 2. Key Step: Generate a Gitea Access Token for this session
        # We need a unique token name
        token_name = f"gitforge-session-{secrets.token_hex(4)}"
        
        token_resp = await client.post(
            f"{GITEA_API_URL}/users/{username}/tokens",
            auth=auth,
            json={"name": token_name}
        )
        
        if token_resp.status_code != 201:
            # Fallback: maybe delete old tokens? For now, error out.
            raise HTTPException(status_code=500, detail="Failed to generate Gitea Session Token")
            
        gitea_token = token_resp.json()["sha1"]
        
        # 3. Mint JWT with embedded Gitea Token
        access_token = create_access_token(data={
            "sub": username,
            "gitea_token": gitea_token
        })
        
        return {"access_token": access_token, "token_type": "bearer", "username": username}

@router.post("/register", response_model=Token)
async def register(user: UserRegister):
    """
    Registration Wrapper:
    1. Admin creates user in Gitea.
    2. Auto-login the new user.
    """
    async with httpx.AsyncClient() as client:
        # 1. Create User via Admin API
        admin_auth = (GITEA_ADMIN_USER, GITEA_ADMIN_PASS)
        
        payload = {
            "username": user.username,
            "email": user.email,
            "password": user.password,
            "must_change_password": False
        }
        
        resp = await client.post(f"{GITEA_API_URL}/admin/users", auth=admin_auth, json=payload)
        
        if resp.status_code == 422:
             raise HTTPException(status_code=400, detail="Username or email already exists")
        elif resp.status_code != 201:
             raise HTTPException(status_code=500, detail=f"Gitea Registration Failed: {resp.text}")

        # 2. Auto-Login logic (Duplicate of Login)
        # Generate Token
        user_auth = (user.username, user.password)
        token_name = f"gitforge-init-{secrets.token_hex(4)}"
        
        token_resp = await client.post(
            f"{GITEA_API_URL}/users/{user.username}/tokens",
            auth=user_auth,
            json={"name": token_name}
        )
        
        gitea_token = token_resp.json()["sha1"]
        
        jwt_token = create_access_token(data={
            "sub": user.username,
            "gitea_token": gitea_token
        })
        
        return {"access_token": jwt_token, "token_type": "bearer", "username": user.username}
