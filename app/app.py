# app.py: Assemble the FastAPI application, middleware, exceptions, and routers
import time
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.config import settings
from app.db import init_db, engine
from app.exceptions import register_exception_handlers
from app.routes import auth, categories, tasks, uploads

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that handles startup and shutdown tasks.
    Replaces deprecated startup/shutdown events.
    """
    # 1. Startup: Initialize tables in database asynchronously
    print("[LIFESPAN] Starting up application, running migrations...")
    await init_db()
    
    yield  # API serves traffic here
    
    # 2. Shutdown: Dispose of the database engine connection pool
    print("[LIFESPAN] Shutting down application, cleaning connection pools...")
    await engine.dispose()

# Instantiate FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An end-to-end production-grade Task Management REST API showcasing all FastAPI features.",
    version=settings.VERSION,
    lifespan=lifespan
)

# --- MIDDLEWARE ---

# 1. Standard CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Custom Timing Middleware to measure request execution latency
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Custom middleware that measures duration of each incoming request
    and attaches an 'X-Process-Time' header to the response.
    """
    start_time = time.time()
    
    # Process the request through routers/endpoints
    response = await call_next(request)
    
    # Calculate processing latency
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    
    # Log information (simple representation)
    print(f"[MIDDLEWARE LOG] {request.method} {request.url.path} processed in {process_time:.4f}s")
    
    return response


# --- STATIC FILES MOUNT ---
# Serves uploaded files statically so users can view attachments directly
app.mount(
    "/static/uploads",
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads"
)


# --- EXCEPTION HANDLERS ---
# Register global exception handlers for clean client error JSON responses
register_exception_handlers(app)


# --- ROUTER REGISTRATION ---
# Include modular routers under a clean API prefix namespace
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(tasks.router, prefix=settings.API_V1_STR)
app.include_router(uploads.router, prefix=settings.API_V1_STR)


# --- HEALTH CHECK ENDPOINT ---
@app.get("/health", tags=["System Health"], summary="Verify server is alive")
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# --- HOME PAGE LANDING ROUTE ---
@app.get("/", response_class=HTMLResponse, tags=["Landing Page"], summary="Serve landing page")
async def home_page():
    """
    Serves the beautiful index.html landing page for TaskSphere.
    """
    template_path = Path(__file__).resolve().parent / "templates" / "index.html"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Welcome to TaskSphere API</h1><p>Visit <a href='/docs'>/docs</a> for API docs.</p>")