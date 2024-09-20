from fastapi import APIRouter, HTTPException, Request, Depends
from schemas import GeneralEqst
from core.security import verify_api_key
from pydantic import ValidationError
from services.functions import general_qst_v1
from utils.logging_config import logger
from core.token_manager import get_current_valid_token, get_cipher_suite
from core.security import decrypt_string

router = APIRouter()


@router.post("/general_qst")
async def general_qst(request: GeneralEqst, http_request: Request, api_key: str = Depends(verify_api_key)):
    try:
        text = request.text
        token = request.token
        client_ip = http_request.client.host
        current_valid_token = get_current_valid_token()
        cipher_suite = get_cipher_suite()

        if token not in current_valid_token.values():
             
            logger.error(f"Unknown token: {token} from IP: {client_ip}")
            raise HTTPException(status_code=403, detail="Could not authenticate token")
        
        translated_string = decrypt_string(token, cipher_suite)

        # Placeholder for your actual classify_intent_v2 function
        response = general_qst_v1(text, translated_string)
        logger.info(f"POST /general_qst HTTP/1.1 200 OK  FROM IP: {client_ip}")
        
        
        return {"output": response}

    except ValidationError as e:
        logger.exception(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid request data")
    except ValueError as e:
        logger.exception(f"Value error: {e}")
        raise HTTPException(status_code=400, detail="Invalid input data")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
