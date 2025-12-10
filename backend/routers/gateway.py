import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["git-gateway"])

# Gitea URL (Service name in docker-compose is 'gitea', but localhost for local run)
# In production/docker, this should be configurable.
GITEA_URL = "http://localhost:3000"

@router.get("/git/{path:path}")
@router.post("/git/{path:path}")
async def git_proxy(path: str, request: Request):
    """
    Proxy all requests starting with /git/ to Gitea.
    Example: /git/username/repo.git/info/refs -> http://localhost:3000/username/repo.git/info/refs
    """
    async with httpx.AsyncClient() as client:
        url = f"{GITEA_URL}/{path}"
        
        # Forward params
        params = dict(request.query_params)
        
        # Forward Headers (filter out host to avoid mismatch)
        headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
        
        # Stream the request body
        content = await request.body()
        
        try:
            proxy_req = client.build_request(
                request.method,
                url,
                params=params,
                headers=headers,
                content=content
            )
            
            response = await client.send(proxy_req, stream=True)
            
            return StreamingResponse(
                response.aiter_raw(),
                status_code=response.status_code,
                headers=dict(response.headers),
                background=None
            )
        except Exception as e:
            return Response(content=f"Gateway Error: {str(e)}", status_code=502)
