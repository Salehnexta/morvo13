# tests/conftest.py
from typing import AsyncGenerator
import pytest_asyncio
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# Built-ins
import asyncio
import os

# Force a lightweight in-memory SQLite DB for tests **before** anything imports application settings. Override any existing value.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

# Load environment variables from .env file
load_dotenv()

# Import all model modules so that they register with the shared Base before we create tables
import importlib

for _module in [
    "app.models.user",
    "app.models.business_profile",
    "app.models.seranking",
]:
    importlib.import_module(_module)

from app.models import Base as GlobalBase

# Import all models to ensure they are registered with SQLAlchemy Base.metadata
from app.models.user import Base as UserBase
from app.models.user import User
from app.models.business_profile import BusinessProfile

# Use the existing test database URL (the user is already named test_salehgazwani)
TEST_DATABASE_URL = os.environ["DATABASE_URL"]

from app.main import app
from app.api.deps import get_db
from app.core.config.settings import settings as app_settings

# Ensure settings reflect testing environment
app_settings.ENVIRONMENT = "testing"

# Ensure new test database for each run
if os.path.exists("./test.db"):
    os.remove("./test.db")

# Set environment to testing so health endpoint returns expected minimal response
os.environ["APP_ENV"] = "testing"

@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_db(test_engine: AsyncEngine) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(GlobalBase.metadata.create_all)

    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    yield TestingSessionLocal

    # Dropping tables at session end can lead to transaction conflicts during async tests.
    # Rely on the database to be cleaned automatically between test sessions or use separate schemas.


@pytest_asyncio.fixture(scope="function")
async def db_session(test_db: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    async with test_db() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Yield an AsyncClient for the FastAPI app with overridden database dependency."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def authorized_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override the database dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Register a user
        import uuid as _uuid
        email = f"auth_{_uuid.uuid4()}@example.com"
        user_data = {"email": email, "password": "testpassword"}
        response = await ac.post("/v1/auth/register", json=user_data)
        assert response.status_code == 200

        # Log in and get a token
        login_data = {"username": email, "password": "testpassword"}
        response = await ac.post("/v1/auth/login/access-token", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Set the authorization header
        ac.headers.update({"Authorization": f"Bearer {token}"})
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def sample_user(db_session: AsyncSession) -> User:
    user = User(email="sample@example.com", hashed_password="$2b$12$dummy_hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def sample_business_profile(db_session: AsyncSession, sample_user: User) -> BusinessProfile:
    profile = BusinessProfile(
        user_id=sample_user.id,
        name="Sample Business",
        website="https://sample.com",
        industry="Tech",
        company_size="1-10",
        target_audience=["SMB"],
        locations=["Riyadh"],
        description="A sample tech business.",
        marketing_goals=["Lead Generation"],
        competitors=["Comp1"],
        current_channels=["Social Media"],
        pain_points=["Low Traffic"],
        social_profiles={},  # Empty dict for now
        analytics_connected=False,
        brand_voice="Professional",
        brand_values=["Innovation"],
        usp="Unique Service",
        content_preferences={},
        automation_level="balanced",
        subscription_tier="premium",
        onboarding_completed=True,
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)
    return profile


# ---------------------------------------------------------------------------
# Async test event loop
# ---------------------------------------------------------------------------

# pytest-asyncio provides a default *function*-scoped ``event_loop`` fixture.  Our
# test suite also defines *session*-scoped fixtures (e.g. ``test_engine``) that
# need access to the same loop, which leads to a ``ScopeMismatch``.  We
# therefore override the default with a *session*-scoped implementation that is
# compatible with all other fixtures.


@pytest_asyncio.fixture(scope="session")
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:  # type: ignore[name-defined]
    """Create a session-wide event loop for asynchronous tests."""

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
