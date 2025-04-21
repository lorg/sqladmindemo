from sqlalchemy import Integer, String, select, Boolean
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Add test data
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(name="Test User", email="test@example.com")
            session.add(user)
            await session.commit()
    yield

app = FastAPI(title="SQLAdmin Demo", lifespan=lifespan)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Define User model
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

# Define User Admin View
class UserAdmin(ModelView, model=User):
    column_list = ["id", "name", "email"]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    identity = "user"
    
    async def scaffold_list(self):
        # Override to use our session
        return await self.session.execute(select(self.model))

# Setup SQLAdmin
admin = Admin(app, engine)

# Add views
admin.add_view(UserAdmin)

@app.get("/")
async def root():
    return {"message": "Welcome to SQLAdmin Demo"}

# Create tables
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Add test data
@app.on_event("startup")
async def create_test_data():
    async with async_session() as session:
        # Check if test user exists
        result = await session.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(name="Test User", email="test@example.com")
            session.add(user)
            await session.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
