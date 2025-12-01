from functools import wraps
from typing import Callable, Optional, Union
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging

from ..crud import crud_audit
from .. import models
from ..database import get_db

logger = logging.getLogger(__name__)

def audit_log(action: str, resource_type: str, resource_id_src: Optional[Union[str, Callable]] = None):
    """
    A decorator for FastAPI endpoints to automatically create audit logs.
    `resource_id_src`:
        - If a string, it's treated as a key in kwargs (e.g., path parameter name).
        - If a callable, it will be called with (*args, **kwargs) to determine the ID.
        - Otherwise, attempts to extract 'id' from the response data.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get('request')
            current_user: models.User = kwargs.get('current_user')

            # Smart DB session extraction
            db = kwargs.get('db')
            if not db:
                # Try to find db in services
                for arg in kwargs.values():
                    if hasattr(arg, 'db') and isinstance(arg.db, AsyncSession):
                        db = arg.db
                        break
            
            # If still no DB or user (e.g. anonymous endpoints), we might skip audit or log error
            # For now, we assume authenticated endpoints with some DB access
            if not db or not current_user:
                # logger.warning(f"Skipping audit log for {action} {resource_type}: Missing db or current_user")
                return await func(*args, **kwargs)

            # Execute the original function first
            response_data = await func(*args, **kwargs)

            resource_id = None
            if isinstance(resource_id_src, str) and resource_id_src in kwargs:
                resource_id = str(kwargs[resource_id_src])
            elif callable(resource_id_src):
                try:
                    resource_id = str(resource_id_src(*args, **kwargs))
                except Exception as e:
                    logger.error(f"Error calling resource_id_src callable for audit log: {e}")
            elif hasattr(response_data, "id"):
                resource_id = str(response_data.id)
            elif isinstance(response_data, dict) and "id" in response_data:
                resource_id = str(response_data["id"])
            
            log_details = {
                "request_body": None,
                "response_data": None
            }
            try:
                if request and request.method in ["POST", "PUT", "DELETE"]:
                    if request.headers.get("content-type") == "application/json":
                        try:
                            body = await request.json()
                            log_details["request_body"] = body
                        except json.JSONDecodeError:
                            log_details["request_body"] = "Non-JSON body or empty body for JSON type"
                
                if hasattr(response_data, "model_dump_json"):
                    log_details["response_data"] = json.loads(response_data.model_dump_json())
                elif isinstance(response_data, (dict, list)):
                    log_details["response_data"] = response_data

            except Exception as e:
                logger.error(f"Error extracting details for audit log: {e}")
            
            await crud_audit.create(
                db=db,
                obj_in={
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "details": log_details
                },
                user_id=current_user.id,
                ip_address=request.client.host if request and request.client else None
            )
            return response_data
        return wrapper
    return decorator
