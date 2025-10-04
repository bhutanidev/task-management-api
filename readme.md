# Task Management REST API

A production-ready Task Management REST API built with FastAPI, featuring JWT authentication, PostgreSQL database, and Docker deployment. Similar to simplified versions of Trello/Asana.

## Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **Task Management**: Full CRUD operations for tasks with advanced filtering
- **Category System**: Organize tasks with custom categories
- **Status Tracking**: Track task progress (pending, in_progress, completed)
- **Priority Levels**: Assign priority (low, medium, high) to tasks
- **Search & Filter**: Filter tasks by status, category, priority, and due date
- **Input Validation**: Comprehensive validation using Pydantic models
- **Rate Limiting**: Protection against brute-force attacks on authentication endpoints
- **Database Migrations**: Alembic for database schema management
- **Docker Support**: Full containerization with Docker Compose

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 15 with SQLAlchemy (async)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Validation**: Pydantic v2 with custom validators
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose

## Project Structure

```
.
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   └── db.py              # Database setup
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py
│   │   ├── tasks.py
│   │   └── categories.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── categories.py
│   ├── services/              # Business logic
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── categories.py
│   ├── routers/               # API endpoints
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── categories.py
│   └── utils/
│       └── jwt.py             # JWT utilities
├── alembic/                   # Database migrations
├── tests/                     # Unit tests
├── main.py                    # Application entry point
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Installation & Setup

### Option 1: Docker Deployment
1. **Clone the repository**
```bash
git clone <repository-url>
cd Deeplure_Research
```

2. **Create environment file**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
DB_USER=app_user
DB_PASSWORD=app_password
DB_NAME=app_db
DB_HOST=postgres
DB_PORT=5432

JWT_SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8080`

4. **View logs**
```bash
docker-compose logs -f backend
```

5. **Stop the services**
```bash
docker-compose down
```

### Option 2: Local Development

1. **Install dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup PostgreSQL database**
```bash
# Install PostgreSQL and create database
createdb app_db
```

3. **Run migrations**
```bash
alembic upgrade head
```

4. **Start the server**
```bash
uvicorn main:app --reload --port 8080
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and get tokens | No |
| POST | `/auth/refresh` | Refresh access token | Yes |

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tasks` | List all tasks (with filters) | Yes |
| POST | `/tasks` | Create a new task | Yes |
| GET | `/tasks/{task_id}` | Get single task | Yes |
| PUT | `/tasks/{task_id}` | Update a task | Yes |
| DELETE | `/tasks/{task_id}` | Delete a task | Yes |

**Query Parameters for Filtering:**
- `status`: Filter by status (pending, in_progress, completed)
- `priority`: Filter by priority (low, medium, high)
- `category`: Filter by category name
- `due_date`: Filter by due date

### Categories

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/categories` | List all categories | Yes |
| POST | `/categories` | Create a new category | Yes |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health/db` | Check database connection |

## Input Validation & Features

### Password Validation
Strong password requirements enforced:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*(),.?":{}|<>)

### Category Name Validation
- Minimum 3 characters
- Automatically converted to lowercase
- Whitespace trimmed
- Unique constraint enforced

### Task Validation
- **Title**: 1-255 characters (required)
- **Description**: Optional text field
- **Priority**: Enum (low, medium, high) - defaults to medium
- **Status**: Enum (pending, in_progress, completed)
- **Due Date**: Optional datetime field
- **Category**: Automatically defaults to "personal" if not provided

### Color Code Validation (Categories)
- Hex color format: `#RRGGBB`
- Pattern: `^#[0-9A-Fa-f]{6}$`


## Database Migrations

Create and apply migrations using Alembic:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Separate access (30 min) and refresh (7 days) tokens
- **Rate Limiting**: 5 login attempts per minute per IP
- **Input Validation**: Comprehensive Pydantic validation on all inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **Authentication Dependency injection**: Token validation on protected routes

## Rate Limiting

The `/auth/login` endpoint is rate-limited to prevent brute-force attacks:
- **Limit**: 5 requests per minute per IP address
- **Response**: 429 Too Many Requests when exceeded

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate resource (e.g., email already exists)
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USER` | Database username | `app_user` |
| `DB_PASSWORD` | Database password | `app_password` |
| `DB_NAME` | Database name | `app_db` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `JWT_SECRET_KEY` | Secret key for JWT | Required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `30` |

## Future Enhancements

- [ ] **Better Logging**: Implement structured logging with log levels, request tracing, and centralized log management (e.g., ELK stack, Grafana Loki)
- [ ] **Enhanced Rate Limiting**: Add more granular rate limiting fields (per-user limits, endpoint-specific limits, sliding window algorithm)
- [ ] **Redis for Token Management**: Use Redis for refresh token storage with automatic expiration, blacklisting, and session management

## Screenshots

### 1. API Documentation (Swagger UI)
*Interactive API documentation available at `/docs`*

<img width="1447" height="747" alt="Image" src="https://github.com/user-attachments/assets/48cd90a3-aabb-4b9e-926d-06c0548a1eab" />
<img width="1443" height="465" alt="Image" src="https://github.com/user-attachments/assets/7148b47b-38e4-4bf0-991c-3322c525897d" />

### 2. User Authentication
*Password validation*
<img width="789" height="728" alt="Image" src="https://github.com/user-attachments/assets/e8167ca5-c4b1-400a-87ee-09e6ef800e94" />

### 3. Task Management
*Creating , updating and deleting tasks with validation*
<img width="820" height="677" alt="Image" src="https://github.com/user-attachments/assets/598af350-67e7-4aa1-8d86-801e3ddcb3a4" />
<img width="820" height="686" alt="Image" src="https://github.com/user-attachments/assets/7ae545f2-17a3-4547-b161-dfee5f234f62" />
<img width="830" height="682" alt="Image" src="https://github.com/user-attachments/assets/f8a375dc-41eb-43cf-ae8c-618bf3c03bd5" />
<img width="816" height="444" alt="Image" src="https://github.com/user-attachments/assets/29cad2f3-b5c7-465a-9e24-5866d09deff1" />


### 4. Task Filtering
*Filter tasks by status, priority, and category*

<img width="829" height="662" alt="Image" src="https://github.com/user-attachments/assets/61953566-e6a6-45a9-b5e1-1498d0e5151b" />
<img width="845" height="634" alt="Image" src="https://github.com/user-attachments/assets/621075de-b7e1-42a6-99d7-020f919f8f11" />

### 5. Category Management
*Create and list categories with color codes*

<img width="819" height="601" alt="Image" src="https://github.com/user-attachments/assets/9f318235-57c5-404f-991f-ebcef6da9bda" />
<img width="805" height="507" alt="Image" src="https://github.com/user-attachments/assets/d504c55d-876d-4084-86a8-ad59ffbe8ad3" />
<img width="820" height="646" alt="Image" src="https://github.com/user-attachments/assets/fd207cd8-d4af-4739-8347-8a410dcff2e3" />

### 6. Rate Limiting in Action
*Rate limit protection on login endpoint*
<img width="731" height="132" alt="Image" src="https://github.com/user-attachments/assets/18f2be06-0595-455f-9680-ebc121420354" />
