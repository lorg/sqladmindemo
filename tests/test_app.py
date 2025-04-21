import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from sqladmin import Admin

from main import app, Base, User, UserAdmin

# Use SQLite in-memory database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create a test admin instance
test_admin = Admin(app, engine)
test_admin.add_view(UserAdmin)

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client():
    return TestClient(app)

@pytest_asyncio.fixture
async def db_session():
    async with async_session() as session:
        yield session

def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SQLAdmin Demo"}

def test_admin_interface(client: TestClient):
    response = client.get("/admin/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, 'html.parser')
    assert "Admin" in soup.get_text()

def test_user_list_empty(client: TestClient):
    response = client.get("/admin/user/list")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = soup.get_text(separator=' ', strip=True)
    # Check for the exact empty state message from SQLAdmin
    assert "Showing 1 to 0 of 0 items" in text_content

@pytest.mark.asyncio
async def test_create_and_list_user(client: TestClient, db_session: AsyncSession):
    # Create a test user
    try:
        user = User(name="Test User", email="test@example.com")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)  # Refresh to ensure we have the latest data

        # Give SQLAdmin a moment to see the changes
        await db_session.flush()
        
        # Check if user appears in the list
        response = client.get("/admin/user/list")
        assert response.status_code == 200
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Print the actual text content for debugging
        print(f"Text content: {text_content}")
        
        # Check for user data and pagination info
        assert str(user.id) in text_content  # Check for user ID
        assert "Test User" in text_content
        assert "test@example.com" in text_content
        assert "Showing 1 to 1 of 1 items" in text_content
    finally:
        await db_session.delete(user)
        await db_session.commit()