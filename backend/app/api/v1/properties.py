from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.core.secure_client import SecureClient
from app.core.auth import authenticate_request as get_current_user
from app.core.tenant_context import set_tenant_id

router = APIRouter()

@router.get("/properties")
async def get_properties(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="No tenant context found")
    set_tenant_id(tenant_id)
    
    try: 
        properties = await SecureClient.get_properties()
    
        return properties        
    except Exception as e:
        print(f"Error fetching properties: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch properties")
