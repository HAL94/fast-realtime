from typing import Any, AsyncGenerator, Callable
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from fastapi import APIRouter, FastAPI
from app.core.config import AppSettings, PostgresSettings
from app.core.db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware


async def create_tables() -> None:
    try:
        async with engine.begin() as conn:
            print("Starting table creation...")
            await conn.run_sync(Base.metadata.create_all)
            print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")


def applifespan_factory(
    settings: AppSettings, create_tables_on_start: bool = True
) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        if isinstance(settings, PostgresSettings) and create_tables_on_start:
            await create_tables()

        yield

        await engine.dispose()

    return lifespan


def create_application(
    api_router: APIRouter,
    ws_router: APIRouter,
    settings: AppSettings,
    create_tables_on_start: bool = True,
    **kwargs: Any,
) -> FastAPI:
    lifespan = applifespan_factory(
        settings, create_tables_on_start=create_tables_on_start
    )

    application = FastAPI(lifespan=lifespan, **kwargs)

    application.include_router(api_router)
    application.include_router(ws_router)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5173/"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    return application
