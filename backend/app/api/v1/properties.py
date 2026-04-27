from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.core.auth import authenticate_request as get_current_user
from app.services.properties import get_properties_for_tenant

router = APIRouter()

@router.get("/properties")
async def get_properties(
    page: int = 1,
    page_size: int = 1000,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="No tenant context found")
    
    try: 
        return await get_properties_for_tenant(
            tenant_id=tenant_id,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        print(f"Error fetching properties: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch properties")
