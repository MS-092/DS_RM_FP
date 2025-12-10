from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import os
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/repositories", tags=["repositories"])

# Gitea configuration
GITEA_URL = os.getenv("GITEA_URL", "http://localhost:3000")
GITEA_API_URL = f"{GITEA_URL}/api/v1"

# Pydantic models for responses
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

class FileEntry(BaseModel):
    name: str
    path: str
    type: str  # "file" or "dir"
    size: int
    download_url: Optional[str] = None

class FileContent(BaseModel):
    name: str
    path: str
    content: str
    encoding: str
    size: int

@router.get("/", response_model=List[Repository])
async def list_repositories():
    """
    List all public repositories from Gitea.
    Fetches from known users (hardcoded for now).
    """
    try:
        async with httpx.AsyncClient() as client:
            all_repos = []
            
            # Known users to fetch repos from (can be made configurable)
            users = ["AdrielMS"]  # Add more usernames as needed
            
            for username in users:
                try:
                    response = await client.get(
                        f"{GITEA_API_URL}/users/{username}/repos",
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        user_repos = response.json()
                        all_repos.extend(user_repos)
                except:
                    continue
            
            # Transform Gitea response to our schema
            return [
                Repository(
                    id=repo.get("id"),
                    name=repo.get("name"),
                    full_name=repo.get("full_name"),
                    description=repo.get("description", ""),
                    private=repo.get("private", False),
                    html_url=repo.get("html_url"),
                    clone_url=repo.get("clone_url"),
                    ssh_url=repo.get("ssh_url"),
                    default_branch=repo.get("default_branch", "main"),
                    created_at=repo.get("created_at"),
                    updated_at=repo.get("updated_at"),
                    stars_count=repo.get("stars_count", 0),
                    forks_count=repo.get("forks_count", 0),
                    open_issues_count=repo.get("open_issues_count", 0),
                    size=repo.get("size", 0)
                )
                for repo in all_repos
            ]
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Gitea service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{owner}/{repo}", response_model=Repository)
async def get_repository(owner: str, repo: str):
    """
    Get details of a specific repository.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITEA_API_URL}/repos/{owner}/{repo}",
                timeout=10.0
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Repository not found")
            elif response.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to fetch repository from Gitea")
            
            repo_data = response.json()
            
            return Repository(
                id=repo_data.get("id"),
                name=repo_data.get("name"),
                full_name=repo_data.get("full_name"),
                description=repo_data.get("description", ""),
                private=repo_data.get("private", False),
                html_url=repo_data.get("html_url"),
                clone_url=repo_data.get("clone_url"),
                ssh_url=repo_data.get("ssh_url"),
                default_branch=repo_data.get("default_branch", "main"),
                created_at=repo_data.get("created_at"),
                updated_at=repo_data.get("updated_at"),
                stars_count=repo_data.get("stars_count", 0),
                forks_count=repo_data.get("forks_count", 0),
                open_issues_count=repo_data.get("open_issues_count", 0),
                size=repo_data.get("size", 0)
            )
    except HTTPException:
        raise
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Gitea service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{owner}/{repo}/contents/{path:path}", response_model=List[FileEntry])
async def get_repository_contents(owner: str, repo: str, path: str = ""):
    """
    Browse repository contents (files and directories).
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"{GITEA_API_URL}/repos/{owner}/{repo}/contents/{path}"
            response = await client.get(url, timeout=10.0)
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Path not found in repository")
            elif response.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to fetch contents from Gitea")
            
            contents = response.json()
            
            # Handle both single file and directory listing
            if isinstance(contents, dict):
                # Single file
                return [
                    FileEntry(
                        name=contents.get("name"),
                        path=contents.get("path"),
                        type="file",
                        size=contents.get("size", 0),
                        download_url=contents.get("download_url")
                    )
                ]
            else:
                # Directory listing
                return [
                    FileEntry(
                        name=item.get("name"),
                        path=item.get("path"),
                        type=item.get("type"),
                        size=item.get("size", 0),
                        download_url=item.get("download_url")
                    )
                    for item in contents
                ]
    except HTTPException:
        raise
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Gitea service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{owner}/{repo}/file/{path:path}")
async def get_file_content(owner: str, repo: str, path: str):
    """
    Get the content of a specific file.
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"{GITEA_API_URL}/repos/{owner}/{repo}/contents/{path}"
            response = await client.get(url, timeout=10.0)
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="File not found")
            elif response.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to fetch file from Gitea")
            
            file_data = response.json()
            
            # Check if it's a file
            if file_data.get("type") != "file":
                raise HTTPException(status_code=400, detail="Path is not a file")
            
            return {
                "name": file_data.get("name"),
                "path": file_data.get("path"),
                "content": file_data.get("content", ""),
                "encoding": file_data.get("encoding", "base64"),
                "size": file_data.get("size", 0),
                "download_url": file_data.get("download_url")
            }
    except HTTPException:
        raise
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Gitea service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
