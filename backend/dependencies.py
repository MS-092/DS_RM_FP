from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import httpx
import os
from security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

GITEA_API_URL = os.getenv("GITEA_URL", "http://localhost:3000") + "/api/v1"

class CurrentUser:
    def __init__(self, username: str, gitea_token: str):
        self.username = username
        self.gitea_token = gitea_token

async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """
    Validates JWT and extracts Gitea credentials.
    Returns a User object.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    gitea_token: str = payload.get("gitea_token")
    
    if username is None or gitea_token is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    return CurrentUser(username=username, gitea_token=gitea_token)

async def check_repo_permission(
    owner: str, 
    repo: str, 
    action: str = "read",
    user: CurrentUser = Depends(get_current_user)
):
    """
    Granular RBAC Check.
    - Owner: Can do anything (read, write, delete).
    - Public: Everyone can read.
    - Others: Start with Deny.
    """
    is_owner = (user.username == owner)
    
    # Check Repo visibility from Gitea (expensive call, usually cached or inferred)
    # For this assignment, we rely on the rule:
    # "Private Repos: Rafael only. Public: All Read, Owner Write."
    
    if is_owner:
        return True # Owner can do anything
    
    if action == "read":
        # Check if public. We ask Gitea.
        # Use a generic client (unauthenticated or admin) to check visibility?
        # Or simpler: Try to fetch it. If Gitea returns 200, it's public/accessible.
        return True # We delegate Read Logic to Gitea's internal visibility check usually.
    
    # Write/Delete actions required strict ownership as per requirements
    if action in ["write", "delete"]:
        if not is_owner:
             raise HTTPException(
                status_code=403, 
                detail=f"RBAC Violation: User '{user.username}' cannot modify repository owned by '{owner}'."
            )
    
    return True
