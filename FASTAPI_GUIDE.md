# TaskSphere: A Comprehensive Guide to Modern FastAPI Development

This guide documents the design decisions, concepts, setup instructions, and step-by-step approach used to build **TaskSphere**—a production-grade, asynchronous Task Management REST API.

---

## Table of Contents
1. [Core FastAPI Concepts Covered](#1-core-fastapi-concepts-covered)
2. [Project Architecture & Directory Structure](#2-project-architecture--directory-structure)
3. [Step-by-Step Implementation Flow](#3-step-by-step-implementation-flow)
4. [Deep-Dive into FastAPI Architecture](#4-deep-dive-into-fastapi-architecture)
    - [Asynchronous Handling & Lifespan](#asynchronous-handling--lifespan)
    - [Modern Database Integration (SQLAlchemy 2.0 Async)](#modern-database-integration-sqlalchemy-20-async)
    - [Pydantic V2 Validations](#pydantic-v2-validations)
    - [Custom Middleware Architecture](#custom-middleware-architecture)
    - [Dependency Injection (`Depends`)](#dependency-injection-depends)
    - [JWT Security & OAuth2 Bearer Authentication](#jwt-security--oauth2-bearer-authentication)
    - [Form & File Upload Handling](#form--file-upload-handling)
    - [Global Exception Interceptors](#global-exception-interceptors)
    - [Background Tasks](#background-tasks)
5. [How to Run and Test the API](#5-how-to-run-and-test-the-api)

---

## 1. Core FastAPI Concepts Covered

This project serves as an educational and structural blueprint by demonstrating the following topics:

*   **Lifespan Management (`asynccontextmanager`)**: Clean setup and teardown of external resources (like database engines) during startup and shutdown.
*   **Asynchronous Database Operations**: Utilizing SQLAlchemy 2.0 Async ORM with SQLite (`aiosqlite`) to prevent blocking thread execution.
*   **Pydantic V2 Validation**: Implementing schemas, field constraints, default values, model configuration (`ConfigDict(from_attributes=True)`), and custom validators.
*   **FastAPI Dependency Injection (`Depends`)**: Structuring reusable dependencies for database sessions (`get_db`) and authentication scopes (`get_current_user`).
*   **JWT OAuth2 Flow**: Registering users, hashing passwords (via `bcrypt`), issuing JSON Web Tokens, and secure request checking.
*   **Parameter Validations**: Restricting routes using `Path` constraints (ranges, descriptions) and `Query` constraints (pagination, enums).
*   **Multipart Form & File Uploads**: Saving attachments locally using `UploadFile` and `File`.
*   **Custom Middleware**: Registering custom interceptors to capture runtime details (timing latency and log outputs).
*   **Background Tasks**: Offloading slow operations (like email sending simulations) using `BackgroundTasks`.
*   **Global Exception Handling**: Mapping custom Python application exceptions to custom structured JSON responses.

---

## 2. Project Architecture & Directory Structure

To ensure codebase scalability, we decoupled configurations, databases, routes, schemas, and custom exceptions.

```
FastApi-Practice/
├── app/
│   ├── routes/              # Routers (modular controller paths)
│   │   ├── auth.py          # Registration, login, token issue
│   │   ├── categories.py    # Category CRUD
│   │   ├── tasks.py         # Task CRUD with sorting, filters, pagination
│   │   └── uploads.py       # Multipart file attachments
│   ├── config.py            # Environment configurations (.env loading)
│   ├── db.py                # Async engine & session lifecycle setup
│   ├── models.py            # Database tables schema (SQLAlchemy 2.0)
│   ├── schemas.py           # Pydantic validation schemas (V2)
│   ├── security.py          # Password hashing (bcrypt) & JWT helpers
│   ├── dependencies.py      # Auth & DB sessions dependencies
│   ├── exceptions.py        # Custom App Exceptions & global error handlers
│   └── app.py               # App instantiation, middlewares, mount configurations
├── uploads/                 # Target folder for file attachments (ignored in git)
├── .env                     # Local environment settings
├── pyproject.toml           # Workspace requirements
├── main.py                  # Entrypoint for running Uvicorn server
└── FASTAPI_GUIDE.md         # This walkthrough & guide
```

---

## 3. Step-by-Step Implementation Flow

We constructed this system following a rigorous, bottom-up approach:

1.  **Configuration Establishment**: Implemented `app/config.py` using `python-dotenv` to bind local variables securely.
2.  **Database Connection Factory**: Configured `app/db.py` to create a `create_async_engine` wrapper around standard SQLite (`sqlite+aiosqlite`).
3.  **Relational Database Models**: Created the entities in `app/models.py` (Users -> Categories -> Tasks) incorporating cascades and index configurations.
4.  **Schema Serialization Definition**: Wrote the input/output schemas in `app/schemas.py`, using `field_validator` to enforce rules (like password complexity and status enums).
5.  **Cryptographic Security**: Programmed `app/security.py` using `bcrypt` and `pyjwt` to build JWT generators and verify tokens.
6.  **Dependency Injectors**: Set up token extraction and database scope handling in `app/dependencies.py` via `oauth2_scheme` and `Depends`.
7.  **Custom App Exceptions**: Created decoupled exceptions in `app/exceptions.py` and mapped them to global handler endpoints using `@app.exception_handler`.
8.  **Endpoint Routes**: Coded routing modules under `app/routes/` to support token exchanges, task queries, categories, and uploads.
9.  **Application Assembly**: Combined routers, middleware, file mounting, and lifespan management inside `app/app.py`.
10. **Application Server Binding**: Hooked Uvicorn reloading parameters in `main.py`.

---

## 4. Deep-Dive into FastAPI Architecture

### Asynchronous Handling & Lifespan
In modern web services, utilizing thread pools for blocking database queries reduces system throughput. FastAPI is built natively on **Starlette**, which supports asynchronous request loops.

We use the modern `lifespan` method (registered via `@asynccontextmanager`) inside `app/app.py` to run setup tasks before the application starts accepting web traffic:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup
    await init_db() 
    yield
    # Runs on shutdown
    await engine.dispose()
```

### Modern Database Integration (SQLAlchemy 2.0 Async)
SQLAlchemy 2.0 separates ORM mapping from active connections. We use an async session pipeline using `aiosqlite`:

```python
engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)
```

In `app/routes/tasks.py`, we implement **Eager Loading** using `selectinload` to prevent the N+1 query problem, fetching the related category record in the same database access block:

```python
query = select(Task).where(Task.owner_id == current_user.id).options(selectinload(Task.category))
```

### Pydantic V2 Validations
Pydantic V2 is written in Rust and operates significantly faster than V1. It enforces type-hints strictly.
*   **ConfigDict**: We use `model_config = ConfigDict(from_attributes=True)` to map SQLAlchemy instances directly into Pydantic JSON structures.
*   **Field Constraints**: Constraints like `ge=1` (greater or equal) and `le=5` (less or equal) are validated natively.
*   **Custom Validators**: We validate passwords using Pydantic's `@field_validator`:

```python
@field_validator("password")
@classmethod
def password_strength(cls, v: str) -> str:
    if not any(char.isdigit() for char in v):
        raise ValueError("Password must contain at least one digit.")
    return v
```

### Custom Middleware Architecture
Middleware processes requests before they hit routers, and intercepts responses before they reach the user. In `app/app.py`, we use the `@app.middleware("http")` hook to calculate timing latency:

```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response
```

### Dependency Injection (`Depends`)
Dependency Injection in FastAPI allows you to write reusable logic that resolves before hitting endpoint code.
FastAPI resolves dependencies hierarchically:
1.  Route requires `current_user: User = Depends(get_active_user)`.
2.  `get_active_user` requires `current_user: User = Depends(get_current_user)`.
3.  `get_current_user` requires `token: str = Depends(oauth2_scheme)` and `db: AsyncSession = Depends(get_async_session)`.

FastAPI manages the extraction, execution, caching, and cleanup automatically.

### JWT Security & OAuth2 Bearer Authentication
Our custom authentication uses OAuth2 bearer specifications:
1.  Clients request a token at `/api/v1/auth/token` by sending form data.
2.  The route verifies the user's hashed password (`bcrypt`).
3.  If verified, the server returns a signed JWT containing the user's identifier inside the `sub` claim.
4.  Subsequent requests send the header: `Authorization: Bearer <token>`.
5.  `OAuth2PasswordBearer` extracts this token automatically.

### Form & File Upload Handling
To upload file attachments to tasks, we use `python-multipart` parsing.
By utilizing `UploadFile`, files are streamed into memory or temp files rather than loaded all at once, preventing memory exhaustion on large file uploads.

```python
@router.post("/tasks/{task_id}/attachment")
async def upload_task_attachment(
    task_id: int = Path(..., gt=0),
    file: UploadFile = File(...)
):
    # Save the file stream in chunks
    with open(file_path, "wb") as buffer:
        while content := await file.read(1024 * 1024):
            buffer.write(content)
```

### Global Exception Interceptors
Instead of cluttering routes with `try-except` blocks, we raise custom errors like `EntityNotFoundException` or `AccessDeniedException`.
A registered exception handler catches these exceptions globally and transforms them into clean JSON responses:

```python
@app.exception_handler(EntityNotFoundException)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "NOT_FOUND", "message": exc.message},
    )
```

### Background Tasks
Tasks that require heavy processing (e.g. sending notification emails) are offloaded to background threads. This allows endpoints to return immediate success responses without waiting:

```python
@router.post("/register")
async def register(user_in: UserCreate, background_tasks: BackgroundTasks):
    # Code to save user...
    background_tasks.add_task(simulate_send_welcome_email, new_user.email)
    return new_user
```

---

## 5. How to Run and Test the API

### Environment Setup
Create a `.env` file in the project root:
```env
DATABASE_URL=sqlite+aiosqlite:///./practice.db
SECRET_KEY=generate-a-strong-random-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Run the Server
Start the development server using Uvicorn:
```bash
uv run python main.py
```
Or start Uvicorn directly from terminal:
```bash
uvicorn app.app:app --host 127.0.0.1 --port 8000 --reload
```

### Testing the Endpoints
FastAPI generates interactive Swagger documentation automatically:
1.  Navigate to `http://127.0.0.1:8000/docs` in your browser.
2.  Use the **Register** endpoint to create a user.
3.  Click the **Authorize** button in Swagger and log in with your email and password.
4.  Once authorized, you can test protected category, task, and upload routes.
