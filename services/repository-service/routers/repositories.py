from fastapi import APIRouter, HTTPException
import httpx
import os
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/repositories", tags=["repositories"])
GITEA_URL = os.getenv("GITEA_URL", "http://gitea:3000")
GITEA_API_URL = f"{GITEA_URL}/api/v1"

class Repository(BaseModel):
    id: int
    name: str
    full_name: str
    description: Optional[str]
    private: bool
    html_url: str
    clone_url: str
    ssh_url: str
    default_branch: str
    created_at: str
    updated_at: str
    stars_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    size: int = 0

@router.get("/", response_model=List[Repository])
async def list_repositories():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GITEA_API_URL}/repos")
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch from Gitea")
        repos = response.json()
        return [Repository(**repo) for repo in repos]