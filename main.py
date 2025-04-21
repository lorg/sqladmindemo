from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from fastapi import FastAPI
from sqladmin import Admin, ModelView

# Create FastAPI app
app = FastAPI(title="SQLAdmin Demo")

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create Base class for SQLAlchemy models
Base = declarative_base()

# Define User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True, unique=True)

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
