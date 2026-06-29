<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.herokuapp.com?font=Space+Grotesk&weight=700&size=28&pause=1000&color=7C3AED&center=true&vCenter=true&width=600&lines=TaskSphere+FastAPI;Async+REST+API+Backend;JWT+Auth+%7C+SQLAlchemy+2.0;Production-Grade+Python" alt="Typing SVG" /></a>

<p><strong>A Modern, Production-Ready Asynchronous Task Management REST API</strong></p>

<p>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy_2.0-306998?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Pydantic_V2-E92063?style=for-the-badge" />
  <img src="https://img.shields.io/badge/JWT_Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" />
  <img src="https://img.shields.io/badge/uv-Package_Manager-7C3AED?style=for-the-badge" />
</p>

<p>
  <img src="https://img.shields.io/badge/Status-Active-10b981?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-06b6d4?style=for-the-badge" />
</p>

</div>

---

## 🌟 Overview

**TaskSphere** is a full-featured, production-grade REST API backend demonstrating modern Python web development best practices. Built with **FastAPI**, it leverages async/await throughout the entire stack — from HTTP request handling to async database queries — making it capable of handling thousands of concurrent connections efficiently.

This project was built as a deep-dive FastAPI learning project, but is architected at a production level with real-world patterns.

---

## ✨ Features

| Feature | Detail |
|---|---|
| ⚡ **Async Core** | Full `async`/`await` from routes to DB — no thread blocking |
| 🔐 **JWT Auth** | Bearer token authentication with `bcrypt` password hashing |
| 🗄️ **Async ORM** | SQLAlchemy 2.0 + `aiosqlite` with eager loading patterns |
| ✅ **Validation** | Strict request/response validation via Pydantic V2 |
| 📁 **File Uploads** | Attachment support via multipart form data |
| 🎨 **Landing Page** | Glassmorphic, animated HTML landing page at `/` |
| 📖 **Interactive Docs** | Swagger UI at `/docs` + ReDoc at `/redoc` |
| 🔒 **Sub-route Scoping** | Clean route separation via FastAPI `APIRouter` |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) + [Starlette](https://www.starlette.io/) |
| Database | SQLite via [`aiosqlite`](https://github.com/omnilib/aiosqlite) |
| ORM | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async mode) |
| Validation | [Pydantic V2](https://docs.pydantic.dev/) |
| Auth | JWT (`python-jose`) + `bcrypt` (`passlib`) |
| Server | [Uvicorn](https://www.uvicorn.org/) (ASGI) |
| Package Manager | [uv](https://github.com/astral-sh/uv) |

---

## 🗂️ Project Structure

```
FastApi-Practice/
├── main.py                # Entry point — launches Uvicorn
├── app/
│   ├── app.py             # FastAPI app factory, middleware, CORS
│   ├── config.py          # Settings via pydantic-settings
│   ├── db.py              # Async engine + session factory
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── security.py        # JWT creation/verification, bcrypt
│   ├── dependencies.py    # FastAPI dependency injection
│   ├── exceptions.py      # Custom HTTP exception handlers
│   └── routes/            # APIRouter modules (auth, tasks, files)
├── .env                   # Environment variables (not committed)
├── pyproject.toml         # Project config + dependencies (uv)
└── FASTAPI_GUIDE.md       # Deep-dive architecture walkthrough
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) package manager

### 1. Clone
```bash
git clone https://github.com/Shivansh-mishraji/FastApi-Practice.git
cd FastApi-Practice
```

### 2. Set Environment Variables
Create a `.env` file:
```env
DATABASE_URL=sqlite+aiosqlite:///./practice.db
SECRET_KEY=your-strong-random-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Run the Server
```bash
uv run python main.py
```
Or directly via Uvicorn:
```bash
uv run uvicorn app.app:app --host 127.0.0.1 --port 8000 --reload
```

---

## 📖 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ | Register a new user |
| `POST` | `/auth/login` | ❌ | Get JWT access token |
| `GET` | `/tasks/` | ✅ | List all tasks |
| `POST` | `/tasks/` | ✅ | Create a task |
| `PUT` | `/tasks/{id}` | ✅ | Update a task |
| `DELETE` | `/tasks/{id}` | ✅ | Delete a task |
| `POST` | `/tasks/{id}/upload` | ✅ | Attach a file |

### Interactive Docs (when running locally)
- 🌐 **Landing Page**: http://localhost:8000/
- 📘 **Swagger UI**: http://localhost:8000/docs
- 📗 **ReDoc**: http://localhost:8000/redoc

---

## 📚 Deep Dive

Check out **[FASTAPI_GUIDE.md](./FASTAPI_GUIDE.md)** for a comprehensive walkthrough of the architecture, routing design, middleware, and async patterns used in this project.

---

## 👤 Author

**Shivansh Mishra** — ML Builder & AI Product Explorer  
📍 Lucknow, India · [GitHub](https://github.com/Shivansh-mishraji) · [LinkedIn](https://www.linkedin.com/in/shivansh-mishra-132b97358)

---

<div align="center">
  <i>Built as a production-grade FastAPI practice project — demonstrating async Python backend architecture.</i>
</div>
