# SQLAdmin Demo

A demonstration project showcasing SQLAdmin, a powerful admin interface for FastAPI applications using SQLAlchemy.

## Features

- FastAPI backend with SQLAlchemy ORM
- SQLAdmin interface for database management
- User and Site management
- SQLite database with async support
- Admin interface with filtering and search capabilities

## Models

### User
- id (Primary Key)
- name
- email (Unique)
- is_admin (Boolean)
- site_id (Foreign Key to Site)

### Site
- id (Primary Key)
- name
- users (Relationship to User)

## Setup

1. Clone the repository
2. Install dependencies using uv (recommended) or pip:

Using uv (faster):
```bash
uv pip install -r requirements.txt
```

Using pip:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Admin Interface

Access the admin interface at `http://localhost:8000/admin`

### User Management
- View, create, edit, and delete users
- Filter users by admin status, name, and site
- Search functionality

### Site Management
- View, create, edit, and delete sites
- View associated users

## API Endpoints

- `GET /`: Welcome message
- Admin interface available at `/admin`

## Dependencies

- FastAPI
- SQLAlchemy
- SQLAdmin
- aiosqlite
- uvicorn

## License

BSD 3-Clause License - see [LICENSE](LICENSE) for details
