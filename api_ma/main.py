from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from core.config import load_configuration, initialize_tokens, start_file_watcher
from fastapi.middleware.cors import CORSMiddleware
from endpoints.general_qst import router as general_qst_router
from endpoints.request_data import router as request_data_router
from endpoints.general_v1 import router as general_v1_router
from endpoints.classify_intents import router as classify_intents_router
import threading
import asyncio
from contextlib import asynccontextmanager
import psutil
from utils.logging_config import logger

app = FastAPI()

# Middleware CORS


@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_configuration()
    await initialize_tokens()
    
    watcher_thread = threading.Thread(target=lambda: asyncio.run(start_file_watcher()), daemon=True)
    watcher_thread.start()

    
    yield  # This yield indicates that the application is running.

    # Cleanup actions can be placed here if necessary
    logger.info("Application is cleaning up resources.")

# Set the lifespan for the FastAPI app
app = FastAPI(lifespan=lifespan)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail} from IP: {request.client.host}")
    if exc.status_code == 400:
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": "Invalid request data"},
        )
    elif exc.status_code == 500:
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": "Internal Server Error"},
        )
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    
@app.middleware("http")
async def log_memory_usage(request: Request, call_next):
    # Log memory usage before the API call
    mem = psutil.virtual_memory()
    logger.info(f"Memory Usage: {mem.percent}% used, {mem.available / (1024 * 1024)} MB available")

    response = await call_next(request)

    # Log memory usage after the API call
    mem = psutil.virtual_memory()
    logger.info(f"Memory Usage after request: {mem.percent}% used, {mem.available / (1024 * 1024)} MB available")

    return response

@app.get("/health")
async def health_check():
    return {"status": "OK", "message": "API is running"}


@app.get("/")
async def root():
    return {"message": "Bienvenue #ADD "}

@app.get("/favicon.ico")
async def favicon():
    return {"message": "No ico avaible."}
    
origins = ["http://localhost:3000", "http://127.0.0.1:5500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(general_qst_router, prefix="/api")
app.include_router(request_data_router, prefix="/api")
app.include_router(general_v1_router, prefix="/api")
app.include_router(classify_intents_router, prefix="/api")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)