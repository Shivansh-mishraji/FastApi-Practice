<div align="center">
  <h1>🚀 TaskSphere</h1>
  <p><strong>A Modern, Production-Ready Asynchronous Task Management REST API</strong></p>
</div>

---

## 🌟 Overview

**TaskSphere** is a premium, end-to-end backend service built on the modern Python ecosystem. It demonstrates best practices in building REST APIs by integrating asynchronous workflows, secure JWT authentication, sub-route scoping, file attachments, and a beautifully designed glassmorphic landing page.

Whether you're managing personal tasks or structuring complex workflows, TaskSphere provides a scalable, fast, and type-safe backend architecture.

## ✨ Features

- **Asynchronous Core**: Built on FastAPI and Starlette, taking full advantage of Python's `async`/`await` syntax to handle thousands of concurrent connections efficiently without thread blocking.
- **Robust Security**: Secured with enterprise-grade JWT (JSON Web Tokens) Bearer Authentication and `bcrypt` password hashing.
- **Modern Database**: Leveraging **SQLAlchemy 2.0 Async ORM** with `aiosqlite` for high-performance, non-blocking database operations, complete with eager loading and optimized query patterns.
- **Data Validation**: Strict serialization and validation via **Pydantic V2**.
- **Interactive UI**: Includes a beautifully crafted, responsive home page with micro-animations and a glassmorphism design system.
- **Interactive API Docs**: Built-in Swagger UI (`/docs`) and ReDoc (`/redoc`) for live API testing and schema exploration.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: SQLite (via `aiosqlite`)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async)
- **Data Validation**: [Pydantic V2](https://docs.pydantic.dev/)
- **Authentication**: JWT & `bcrypt`
- **Server**: Uvicorn
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

## 🚀 Getting Started

### Prerequisites

Ensure you have **Python 3.9+** and **uv** installed. 

### 1. Clone the repository
```bash
git clone https://github.com/Shivansh-mishraji/FastApi-Practice.git
cd FastApi-Practice
```

### 2. Environment Variables
Create a `.env` file in the root directory and add the following configuration:
```env
DATABASE_URL=sqlite+aiosqlite:///./practice.db
SECRET_KEY=generate-a-strong-random-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Install Dependencies
Using the fast `uv` package manager:
```bash
uv sync
```

### 4. Run the Development Server
Start the server using `main.py` which is pre-configured with Uvicorn:
```bash
uv run python main.py
```
Or run directly via Uvicorn:
```bash
uv run uvicorn app.app:app --host 127.0.0.1 --port 8000 --reload
```

## 📖 API Documentation

Once the server is running, navigate to the following endpoints in your browser to explore the API:

- **Landing Page**: [http://localhost:8000/](http://localhost:8000/)
- **Swagger UI (Interactive Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc (Static Specs)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📚 Deep Dive

Want to learn how this architecture was built from the ground up? Check out the [FASTAPI_GUIDE.md](./FASTAPI_GUIDE.md) included in this repository for a comprehensive walkthrough of the design decisions, routing, and middleware setups.
