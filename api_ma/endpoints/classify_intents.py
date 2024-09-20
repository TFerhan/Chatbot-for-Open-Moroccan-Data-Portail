from fastapi import APIRouter, HTTPException, Request, Depends
from schemas import ClassifyRequest
from core.security import verify_api_key
from services.functions import classify_intent_v4
from utils.logging_config import logger
from pydantic import ValidationError
from core.token_manager import get_current_valid_token

router = APIRouter()

@router.post("/classify_intent_v4")
async def classify_v4(request: ClassifyRequest, http_request: Request, api_key: str = Depends(verify_api_key)):
    try:
        text = request.text
        lang = request.lang
        token = request.token
        
        client_ip = http_request.client.host

        
            
        current_valid_token = get_current_valid_token()
        if "open_data" not in current_valid_token:
            logger.error(f"Token key 'open_data' not found from client ip {client_ip}")
            raise HTTPException(status_code=403, detail="Token not found")

        if current_valid_token["open_data"] != token:
            logger.error(f"Invalid token received {token} from client IP {client_ip}")
            raise HTTPException(status_code=403, detail="Invalid token")


	    # if len(text) >= 500:
        #     logger.error(f"Max characters 500 exceeded from IP : {client_ip}")
        #     return {"output": "Veuillez ne pas dépasser 500 carctères"}
        
        

        # Placeholder for your actual classify_intent_v2 function
        
        response = classify_intent_v4(text, lang)
        logger.info(f"POST /classify_intent_v4 HTTP/1.1 200 OK  FROM IP: {client_ip}")
        

        return response

    except ValidationError as e:
        logger.exception(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid request data")
    except ValueError as e:
        logger.exception(f"Value error: {e}")
        raise HTTPException(status_code=400, detail="Invalid input data")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
