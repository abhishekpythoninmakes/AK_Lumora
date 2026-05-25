"""Async SQLAlchemy database setup for SQLite."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

db_url = settings.DATABASE_URL

# Handle PostgreSQL driver translation for async SQLAlchemy
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

# Conditionally configure connection arguments
connect_args = {}
if "sqlite" in db_url:
    connect_args["check_same_thread"] = False
elif "postgresql" in db_url:
    # Ensure SSL is used for remote PostgreSQL connections (e.g. on Railway)
    connect_args["ssl"] = "require"

engine = create_async_engine(
    db_url,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


async def get_db():
    """Dependency that yields an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables on startup."""
    # Ensure all models are loaded in memory so SQLAlchemy registers them
    import app.models
    
    # 1. Create all tables in a single transaction
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # 2. Run schema alterations in separate transactions.
    # In PostgreSQL, any failed query in a transaction aborts and rolls back the entire transaction.
    # By running each alter statement in its own transaction block, failures (e.g. if column already exists) won't impact other tables.
    from sqlalchemy import text
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE drive_configs ADD COLUMN account_email VARCHAR(255)"))
    except Exception:
        pass
        
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE watched_folders ADD COLUMN drive_config_id INTEGER REFERENCES drive_configs(id)"))
    except Exception:
        pass
        
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE upload_logs ADD COLUMN thumbnail_url VARCHAR"))
    except Exception:
        pass
        
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE face_embeddings ADD COLUMN drive_file_id VARCHAR(255)"))
    except Exception:
        pass
        
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE person_clusters ADD COLUMN label VARCHAR(255)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN studio_name VARCHAR(255)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN profile_image VARCHAR(500)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN phone_number VARCHAR(20)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN country_code VARCHAR(10)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN display_name VARCHAR(255)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN profile_completed BOOLEAN DEFAULT FALSE"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN drive_configured BOOLEAN DEFAULT FALSE"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN first_login_tutorial BOOLEAN DEFAULT FALSE"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN instagram_link VARCHAR(500)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN facebook_link VARCHAR(500)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN address VARCHAR(500)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN contact_numbers VARCHAR(500)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN website_link VARCHAR(500)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN whatsapp_number VARCHAR(30)"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN bio VARCHAR(1000)"))
    except Exception:
        pass

    # Google Drive memory efficiency rolling automatic cleanup columns
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE drive_configs ADD COLUMN cleanup_enabled BOOLEAN DEFAULT FALSE"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE drive_configs ADD COLUMN cleanup_keep_count INTEGER DEFAULT 50"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE watched_folders ADD COLUMN cleanup_enabled BOOLEAN DEFAULT FALSE"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE watched_folders ADD COLUMN cleanup_keep_count INTEGER DEFAULT 50"))
    except Exception:
        pass